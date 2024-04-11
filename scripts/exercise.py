""" handle exercises:
    choose exercise
    training
    exam
"""

import scripts.dbconnection as db
import scripts.map_parser as map_parser


def choose_exercise_type(message_dict):
    """ экзамен или тренировка"""
    # если нет session_id, то ошибка в запросе
    if "session_id" not in message_dict:
        print("\t[ERROR] no session id in message from front")
        return {"error": "no session_id"}

    session_hash = message_dict["session_id"]

    # если только начали упражнение, то обновляем данные в базе
    if "norm" in message_dict:
        configure_norm(message_dict)

    # TODO добавить эту проверку, и не писать поля с подсветкой и аннотацией в ответ
    # if "is_training" in message_dict:

    return_json = training_exercise(message_dict)
    return return_json


def configure_norm(message_dict):
    """ инициализация норматива для конкретной сессии """
    try:
        # подключаемся к БД
        db_con_var = db.DbConnection()
        session_hash = message_dict["session_id"]  # хэш сессии
        map_id = message_dict["ex_id"]  # id норматива
        stage_id = message_dict["norm"]  # id упражнения в нормативе

        # получаем id для новой группы подшагов
        table_name = "step_group_status"
        step_id = db_con_var.add_values_and_get_id(
            table_name=table_name, step_order=0)

        # добавляем в таблицу "exercises_status" данные по началу прохождения карты
        table_name = "exercises_status"
        session_exercise_id = db_con_var.add_values_and_get_id(
            table_name=table_name, map_id=map_id, stage_id=stage_id,
            step_id=step_id)

        # добавляем сессию в таблицу, если такой нет
        add_session(session_hash, session_exercise_id)

    except Exception as error:
        print("Ошибка в инициализации норматива:\n", error)


def training_exercise(message_dict):
    """ обрабатывает упражнение для тренировки """
    session_hash = message_dict["session_id"]

    # получаем текущий шаг пользователя
    cur_step = map_parser.get_next_step(session_hash)

    # записываем все подшаги из шага в бд
    write_substeps(session_hash, cur_step)

    # формируем ответ в виде словаря
    answer = create_default_answer(cur_step)
    answer["session_id"] = session_hash

    # получаем эталонные данные по шагу
    validation = validate_step(cur_step, message_dict)

    return answer


def write_substeps(session_hash, cur_step):
    """ пишет все подшаги из текущего подшага в бд """
    # получаем id группы подшагов
    step_id = get_step_id(session_hash)

    print("\t\t\tcur_step", cur_step)
    db_con_var = db.DbConnection()
    # TODO можно переделать на executescript
    # for i in len(cur_step[])
    # db_con_var.add_values_and_get_id(
        # table_name="sub_steps", step_id=step_id,
    #
    # )


def get_step_id(session_hash):
    db_con_var = db.DbConnection()

    # из таблицы "sessions" получаем session_exercise_id
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
        table_name="sessions", where_statement=where_statement)

    # из таблицы "exercises_status" статус текущего шага
    where_statement = f"id={session_data['session_exercise_id']}"
    exercises_data = db_con_var.get_data_with_where_statement(
        table_name="exercises_status", where_statement=where_statement)

    # из таблицы "step_group_status" порядковый номер шага
    where_statement = f"id={exercises_data['step_id']}"
    step_id = db_con_var.get_data_with_where_statement(
        table_name="step_group_status",
        where_statement=where_statement,
        step_order="id")
    print("\t[LOG] step_id = ", step_id)
    return step_id


def add_session(session_hash, session_exercise_id):
    """ если такой сессии еще нет в таблице, то добавляем """
    if session_exists(session_hash):
        return

    # добавляем в таблицу "sessions" данные по новой сессии, если такой нет
    db_con_var = db.DbConnection()
    db_con_var.add_values_and_get_id(
        table_name="sessions", user_id=0, session_hash=session_hash,
        session_exercise_id=session_exercise_id)


def session_exists(session_hash):
    """ проверка на существовании записи о сессии """
    db_con_var = db.DbConnection()
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
        table_name="sessions", where_statement=where_statement)
    print("\t[LOG] session_data", session_data)

    # если name == nan, то запрос вернул пустой массив
    if "name" in session_data:
        return session_data["name"] != "nan"
    return True


def create_default_answer(cur_step):
    """ формируем ответ для фронта """
    return_json = dict()
    has_action = cur_step["count_action"] > 0

    return_json["annotation"] = cur_step["annotation"]

    # actions - применимые действия, зажечь лампы, передвинуть рычаг вручную
    return_json["has_action"] = has_action  # есть ли ответные дейтсвия (зажечь лампу и т.п.)
    return_json["count_action"] = cur_step["count_action"]  # количество ответных дейтсвий
    return_json["array_actions"] = cur_step["array_actions"]

    # next_actions - элементы для подсветки
    return_json["count_next"] = cur_step["count_next"]    # число элементов для подсветки
    return_json["next_actions"] = cur_step["next_actions"]  # массив данных по элементам для подсветки

    # рандом TODO понять надо ли
    return_json["is_random_step"] = False
    return_json["random_values"] = [{'name': 'nan'}]


    # flags - координируют переход между шагами, нормативами и т.д.
    return_json["finish"] = False       # закончен ли шаг
    return_json["status"] = "progres"   # progres - элемент еще не в свое положении, не убираем подсветку, correct - убираем подсветку, элемент в нужном положении
    return_json["validation"] = False   # правильно ли было сделано действие
    return_json["fail"] = False         # провалена ли ошибка
    return return_json


def validate_step(cur_step, message_dict):
    """ проверка переданных данных на правильность """
    # если начальный шаг, то значений нет
    if "current_value" not in message_dict:
        return False

    # проверяем соответсвие id шага и его порядка, если важен порядок
    print("\t[LOG] validation cur step:\n\t", cur_step)
    print("\t[LOG] validation message dict:\n\t", message_dict)

