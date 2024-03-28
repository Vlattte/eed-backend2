""" handle exercises:
    choose exercise
    training
    exam
"""

import scripts.dbconnection as db
import scripts.map_parser as map_parser


def choose_exercise_type(message_dict):
    """ экзамен или тренировка"""
    if "is_training" in message_dict:
        return_json = training_exercise(message_dict)
        return return_json


def training_exercise(message_dict):
    """ обрабатывает упражнение для тренировки """

    # если только начинаем прохождение норматива, создаем первую запись о нормативе
    if "norm" in message_dict:
        configure_norm(message_dict)
        session_hash = message_dict["session_id"]

        # получаем эталонные данные по шагу
        cur_step = map_parser.get_next_step(session_hash)
        validation = validate_step(cur_step, message_dict)


        return_json = {"session_id": session_hash, "validation": validation}
        return return_json


def configure_norm(message_dict):
    """ инициализация норматива для конкретной сессии """
    try:
        # подключаемся к БД
        db_con_var = db.DbConnection()
        session_hash = message_dict["session_id"]  # хэш сессии
        map_id = message_dict["norm"]  # id норматива
        stage_id = 0  # id упражнения в нормативе

        # добавляем в таблицу "exercises_status" данные по началу прохождения карты
        table_name = "exercises_status"
        session_exercise_id = db_con_var.add_values_and_get_id(
            table_name=table_name, map_id=map_id, stage_id=stage_id,
            group_steps_id=0, steps_id=0)

        # добавляем в таблицу "sessions" данные по новой сессии
        # session_id - вроде не нужен
        table_name = "sessions"
        print("session_hash = ", session_hash)
        db_con_var.add_values_and_get_id(
            table_name=table_name, user_id=0, session_hash=session_hash,
            session_exercise_id=session_exercise_id)

    except (Exception, Error) as error:
        print("Ошибка в инициализации норматива:\n", error)


def validate_step(cur_step, message_dict):
    """ проверка переданных данных на правильность """
    # если начальный шаг, то значений нет
    if "current_value" not in message_dict:
        return False

    # проверяем соответсвие id шага и его порядка, если важен порядок


