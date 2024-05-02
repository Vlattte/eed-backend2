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
        step_id = db_con_var.add_values_and_get_id(
            table_name="step_group_status", step_order=0, sub_step_order=0)

        # добавляем в таблицу "exercises_status" данные по началу прохождения карты
        session_exercise_id = db_con_var.add_values_and_get_id(
            table_name="exercises_status", map_id=map_id, stage_id=stage_id,
            step_id=step_id)

        # добавляем сессию в таблицу, если такой нет
        add_session(session_hash, session_exercise_id)
    except Exception as error:
        print("Ошибка в инициализации норматива:\n", error)


def training_exercise(message_dict):
    """ обрабатывает упражнение для тренировки """
    session_hash = message_dict["session_id"]

    # получаем текущий шаг пользователя
    table_step = map_parser.get_next_step(session_hash)

    # записываем все подшаги из шага в бд, если новый шаг (step, а не sub_step)
    write_substeps(session_hash, table_step)

    # формируем ответ в виде словаря
    answer = create_default_answer(table_step)
    answer["session_id"] = session_hash

    # получаем эталонные данные по шагу и исправляем флаги в словаре ответа answer
    status_flags = validate_step(message_dict, table_step)
    answer["finish"] = status_flags["stage_finish"]
    answer["status"] = status_flags["status"]
    answer["validation"] = status_flags["step_finish"]
    answer["fail"] = status_flags["attempt_fail"]
    answer["is_norm_finish"] = status_flags["is_norm_finish"]
    
    # если есть что-то кроме "name": "nan", то размер это вот это
    if status_flags["array_actions"] != [{"name":"nan"}]:        
        answer["array_actions"].extend(status_flags["array_actions"])
        answer["count_action"] += len(status_flags["array_actions"])
    
    return answer


def write_substeps(session_hash, cur_step):
    """ пишет все подшаги из текущего подшага в бд """
    # получаем id группы подшагов
    step_id = get_step_id(session_hash)

    # проверяем, нужно ли записывать новые подшаги (если еще есть подшаги, то не надо)
    db_con_var = db.DbConnection()
    where_statement = f"step_id={step_id}"
    prev_sub_steps = db_con_var.get_data_with_where_statement(
        table_name="sub_steps", where_statement=where_statement)
        
    if len(prev_sub_steps) > 0:
        return  # ничего не пишем, т.к. прошлый шаг еще не кончился

    # если нет под шагов в карте, то и писать нечего
    if len(cur_step["sub_steps"]) == 0:
        return

    # TODO можно переделать на executescript
    # само добавление под шагов в таблицу sub_steps
    for sub_step in cur_step["sub_steps"]:
        # если несколько подшагов, то порядок не важен
        sub_step_order = -1
        if len(cur_step["sub_steps"]) > 0:
            sub_step_order = sub_step["sub_step"]

        # пишем данные по подшагам
        sub_step_id = db_con_var.add_values_and_get_id(
            table_name="sub_steps", 
            step_id=step_id,
            element_id=sub_step["action_id"],
            correct_value=sub_step["current_value"],
            tag=sub_step["tag"],
            sub_step_order=sub_step_order)
                
        # действия вызываемые после данного подшага (если они есть)
        if not "array_actions" in sub_step: # TODO заглушка, пока не переделаем все json для нормативов                        
            continue

        array_actions = sub_step["array_actions"]
        # если нет дейтсвий, то не пишем их в базу
        if len(array_actions) == 0:                        
            continue
        
        # добавляем ответные действия после подшага
        for action in array_actions:            
            db_con_var.add_values_and_get_id(
                table_name="sub_step_actions",
                sub_step_id=sub_step_id,
                element_id=action["action_id"],
                correct_value=action["action_value"],
                apparat_id=action["apparat_id"],
                tag=action["tag"]
            )
    print("\t[LOG] В БД записаны под шаги и действия для подшагов:\n\t", cur_step["sub_steps"])


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

    # если name == nan, то запрос вернул пустой массив
    if len(session_data) == 0:
        return False
    return True


def create_default_answer(cur_step):
    """ формируем ответ для фронта """
    return_json = dict()
    has_action = cur_step["count_action"] > 0

    return_json["annotation"] = cur_step["annotation"]

    # actions - применимые действия, зажечь лампы, передвинуть рычаг вручную
    return_json["has_action"] = has_action  # есть ли ответные действия (зажечь лампу и т.п.)
    return_json["count_action"] = cur_step["count_action"]  # количество ответных действий
    return_json["array_actions"] = cur_step["array_actions"]

    # next_actions - элементы для подсветки
    return_json["count_next"] = cur_step["count_next"]    # число элементов для подсветки
    return_json["next_actions"] = cur_step["next_actions"]  # массив данных по элементам для подсветки

    # рандом TODO понять надо ли
    return_json["is_random_step"] = False
    return_json["random_values"] = [{'name': 'nan'}]

    # flags - координируют переход между шагами, нормативами и т.д.
    return_json["finish"] = False           # закончен ли шаг
    return_json["status"] = "progres"       # progres - элемент еще не в свое положении, не убираем подсветку, correct - убираем подсветку, элемент в нужном положении
    return_json["validation"] = False       # закончился ли шаг
    return_json["fail"] = False             # провалена ли попытка
    return_json["is_norm_finish"] = False   # закончился ли норматив
    return return_json


def is_invalid(check_dict):
    """ проверяет является ли словарь словарем вида {"name": "nan"} """
    if check_dict == {"name": "nan"}:
        return True
    return False


def get_sub_steps(session_hash):
    """ получает массив подшагов для этого шага """
    # получаем id группы шагов
    step_id = get_step_id(session_hash)

    db_con_var = db.DbConnection()

    # получаем текущий номер шага (если порядок ообще важен)
    where_statement = f"id={step_id}"
    step_data = db_con_var.get_data_with_where_statement(
        table_name="step_group_status", where_statement=where_statement)
    
    sub_step_order = step_data["sub_step_order"]

    # получаем все данные про подшаги из текущего шага
    where_statement = f"step_id={step_id}"
    sub_steps_data = db_con_var.get_data_with_where_statement(
        table_name="sub_steps", where_statement=where_statement, is_return_arr=True)
    print("\t[LOG] sub_steps_data = ", sub_steps_data)

    return sub_steps_data, sub_step_order
