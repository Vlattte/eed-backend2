""" часто используемые запросы к бд """

import scripts.dbconnection as db


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

    # из таблицы "step_group_status" id группы шагов
    # TODO тут кажется этот шаг лишний FIX
    where_statement = f"id={exercises_data['step_id']}"
    step_id = db_con_var.get_data_with_where_statement(
        table_name="step_group_status", where_statement=where_statement,
        id="id")
    
    return step_id["id"]
