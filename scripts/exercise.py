""" handle exercises:
    choose exercise
    training
    exam
"""

import scripts.dbconnection as db


def choose_exercise_type(message_dict):
    """ экзамен или тренировка"""
    if "is_training" in message_dict:
        training_exercise(message_dict)


def training_exercise(message_dict):
    """ обрабатывает упражнение для тренировки """

    # если только начинаем прохождение норматива, создаем первую запись о нормативе
    if "norm" in message_dict:
        configure_norm(message_dict)
        return_json = {"session_id": session_hash, "validation": False}

    # front->back:
    # {
    #     "session_hash": string,
    #     "apparat_id": integer,
    #     "map_id": integer,
    #     "is_training": bool
    # }


def configure_norm(message_dict):
    # подключаемся к БД
    db_con_var = db.DbConnection()
    table_name = "exercises_status"
    session_hash = message_dict["session_id"]  # хэш сессии
    map_id = message_dict["norm"]  # id норматива
    stage_id = message_dict["ex_id"]  # id упражнения в нормативе

    # добавляем в таблицу "exercises_status" данные по началу прохождения карты
    session_exercise_id = db_con_var.add_values_and_get_id(
        table_name=table_name, map_id=map_id, stage_id=stage_id,
        group_steps_id=0, steps_id=0)

    # добавляем в таблицу "sessions" данные по новой сессии
    # session_id - вроде не нужен
    db_con_var.add_values_and_get_id(
        table_name=table_name, user_id=0, session_hash=session_hash,
        session_exercise_id=session_exercise_id)


