create database vuc;
create user vuc with encrypted password '123456';

----------------------------------
-- ТАБЛИЦЫ ДЛЯ ХРАНЕНИЯ АППАРАТУРЫ:
----------------------------------

CREATE TABLE apparats (
	id serial, -- --> apparat_id
	name text,
    apparat_description text,
	CONSTRAINT apparats_pkey PRIMARY KEY (id)
);

CREATE TABLE apparat_blocks (
	id serial, -- --> block_id
	apparat_id integer,
	name text,
	width integer, -- --> оригинальный размер фотографии блока в пикселях
	height integer, -- --> оригинальный размер фотографии блока в пикселях
	src text, -- --> ОТНОСИТЕЛЬНЫЙ путь до фотографии блока
	CONSTRAINT apparat_blocks_pkey PRIMARY KEY (id)
);

CREATE TABLE block_elements (
	id serial,
	condition_group_id integer,
	block_id integer,
	x double precision, -- --> координата x относительно оригинальной width apparat_blocks в процентах
	y double precision, -- --> координата y относительно оригинальной height apparat_blocks в процентах
	width double precision, -- --> ширина относительно оригинальной width apparat_blocks в процентах
	height double precision, -- --> высота относительно оригинальной height apparat_blocks в процентах
	CONSTRAINT block_elements_pkey PRIMARY KEY (id)
);

CREATE TABLE block_cables (
	id serial,
	condition_group_id integer,
	start_element_id integer, -- --> block_elements -> head_cable
	end_element_id integer, -- --> block_elements -> head_cable
	-- src text, -- --> ОТНОСИТЕЛЬНЫЙ путь до фотографии кабеля
	CONSTRAINT block_cables_pkey PRIMARY KEY (id)
);

CREATE TABLE elements (
	id serial, -- --> element_id
	type_id integer,
	original_src text, -- --> ОТНОСИТЕЛЬНЫЙ путь до фотографии елемента
	width double precision, -- --> ширина относительно оригинальной width
	height double precision, -- --> высота относительно оригинальной height
	CONSTRAINT element_to_type_pkey PRIMARY KEY (id)
);

CREATE TABLE element_group_condition(
	id serial, -- --> condition_group_id
	element_id integer, -- --> block_elements -> rotator
	CONSTRAINT element_conditions_pkey PRIMARY KEY (id)
);

CREATE TABLE element_condition_positions (
	id serial, -- --> condition_position_id
	condition_group_id integer, -- --> element_group_condition 
	angle integer, -- --> градусы
	condition_order integer, -- --> порядок переключения состояний
	src text, -- --> ОТНОСИТЕЛЬНЫЙ путь до оригинальной фотографии
	UNIQUE (condition_group_id, condition_order), 
	CONSTRAINT element_condition_positions_pkey PRIMARY KEY (id)
);

CREATE TABLE types (
	id serial, -- --> type_id
	name text, -- --> имя типа: button / lever / rotator / draggable / head_cable / lights
	CONSTRAINT types_pkey PRIMARY KEY (id)
);

----------------------------------
----------------------------------



----------------------------------
-- ТАБЛИЦЫ ДЛЯ ХРАНЕНИЯ КАРТЫ:
----------------------------------

CREATE TABLE maps (
	id serial, -- --> map_id
	apparat_id integer,
	name text, -- --> ПР: УПРАЖНЕНИЕ N. Настройка очка тов. полковника КАЛАЧА на частоту УКВ радиосети
	CONSTRAINT maps_pkey PRIMARY KEY (id)
);

CREATE TABLE map_elements_init (
	id serial,
	map_id integer,
	element_id integer,
	init_condition_id integer, -- --> condition_group_id из element_conditions
	CONSTRAINT map_elements_init_pkey PRIMARY KEY (id)
);

CREATE TABLE stages ( 
	id serial, -- --> stage_id
	map_id integer, -- --> идентификатор карты
	title text, -- --> ПР: ЭТАП 1. Воткнуть антену
	stage_order integer, -- --> порядковый номер этапа
	CONSTRAINT stages_pkey PRIMARY KEY (id)
);

CREATE TABLE group_steps (
	id serial, -- --> group_steps_id
	group_id integer, -- --> group_id
	action_id integer,
	stage_id integer, -- --> идентификатор группы steps, В РАМКАХ КОТОРОГО должны происходить действия
	steps_order integer, -- --> порядковый номер шаг, или: -1 если порядок неважен
	CONSTRAINT group_steps_pkey PRIMARY KEY (id)
);

CREATE TABLE step_to_group (
	id serial,
	group_id integer,
	step_id integer,
	step_order integer, -- --> порядковый номер шаг, или: -1 если порядок неважен
	CONSTRAINT step_to_group_pkey PRIMARY KEY (id)
);

CREATE TABLE steps (
	id serial, -- --> step_id
	condition_group_id integer, -- --> condition_group_id из element_conditions
	CONSTRAINT steps_pkey PRIMARY KEY (id)
);

CREATE TABLE actions (
	id serial, -- --> step_id
	stage_id integer, -- --> идентификатор stage, ПОСЛЕ КОТОРОГО должны происходить действия
	condition_group_id integer, -- --> condition_group_id из element_conditions
	action_order integer, -- --> порядковый номер шаг, или: -1 если порядок неважен
	CONSTRAINT actions_pkey PRIMARY KEY (id)
);


-- CREATE TABLE map_pairs (
-- 	id serial,
-- 	map_id
-- 	CONSTRAINT map_double_pkey PRIMARY KEY (id)
-- );

----------------------------------
----------------------------------



----------------------------------
-- ТАБЛИЦЫ ДЛЯ ХРАНЕНИЯ СОСТОЯНИЙ:
----------------------------------

-- таблица нужна, чтобы не создавать при каждом соединении нового пользователя
-- просто по session_hash получаем id нужного пользователя по полученному session_hash
CREATE TABLE user_data (
	id serial, -- --> user_id
	login text UNIQUE,
	role integer,
	password text,
	CONSTRAINT user_pkey PRIMARY KEY (id)
);

CREATE TABLE sessions (
	id serial, -- --> session_id
	user_id integer,
	session_hash text,
	session_exercise_id integer, -- --> используется, если работаем с упражнениями, иначе -1
	CONSTRAINT sessions_pkey PRIMARY KEY (id)
);

-- храним статус прохождения карты
CREATE TABLE exercises_status(
	id serial, -- --> session_exercise_id
	map_id integer,      -- --> номер карты (норматива: либо фильм, либо первый норматив)
	stage_id integer,    -- --> stage - длится от одной аннотации "ВЫПОЛНЕНО" до другой (один json)
	step_id integer,     -- --> смена группы шагов == смена аннотации (набор шагов)
	CONSTRAINT exercises_status_pkey PRIMARY KEY (id)
);

-- состояние шага (объединяет подшаги шаги в группу)
CREATE TABLE step_group_status(
    id serial, -- --> step_group_status_id
    step_order integer, -- текущий номер шага в группе, либо -1, если порядок не важен
    CONSTRAINT step_id PRIMARY KEY (id)
);

-- состояние подшага (содержит ожидаемые данные для этого подшага)
CREATE TABLE sub_steps(
    id serial, -- --> sub_step_id
    step_id integer,    -- id группы sub_steps
    element_id integer, -- id элемента на аппаратуре
    correct_value text, -- верное положение элемента
    tag text,           -- тэг элемента (button, lever)
    order integer       -- очередность шагов, либо -1, если ее нет
    CONSTRAINT sub_step_id PRIMARY KEY (id)
);

CREATE TABLE mistakes(
	id serial, -- --> mistakes_id
	condition_group_id integer,
	condition_order integer,
	CONSTRAINT mistakes_pkey PRIMARY KEY (id)
);



CREATE TABLE rooms (
	id serial,
	key text UNIQUE, -- --> ключ комнаты, по которому users заходят в комнату
	creator_id integer, -- --> user.id
	max_user_count integer,
	CONSTRAINT rooms_pkey PRIMARY KEY (id)
);

CREATE TABLE rooms_users (
	id serial,
	room_id integer,
	user_id integer,
	CONSTRAINT rooms_users_pkey PRIMARY KEY (id)
);

-- CREATE TABLE rooms_users (
-- 	id serial,
-- 	room_id integer,
-- 	user_count integer,
-- 	CONSTRAINT rooms_users_pkey PRIMARY KEY (id)
-- );



GRANT ALL PRIVILEGES ON DATABASE vuc TO vuc;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vuc;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vuc;