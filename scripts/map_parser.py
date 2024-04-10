import json
import scripts.dbconnection as db


def get_next_step(session_hash):
    """ получаем следующий шаг исходя из хэша сессии """

    db_con_var = db.DbConnection()

    # из таблицы "sessions" получаем session_exercise_id, который id в таблице "exercises_status"
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
                    table_name="sessions",
                    where_statement=where_statement)

    # из таблицы "exercises_status" статус текущего шага
    where_statement = f"id={session_data['session_exercise_id']}"
    exercises_data = db_con_var.get_data_with_where_statement(
                    table_name="exercises_status",
                    where_statement=where_statement)
    print(exercises_data)  # [{'id': 18, 'map_id': 11, 'stage_id': 0, 'group_steps_id': 0}]

    # из таблицы "step_group_status" порядковый номер шага
    where_statement = f"id={exercises_data['group_steps_id']}"
    step_data = db_con_var.get_data_with_where_statement(
        table_name="step_group_status",
        where_statement=where_statement,
        step_order="step_order")
    print("\t[LOG] step_order = ", step_data)

    # получаем карту по ее id
    map_id = exercises_data["stage_id"]
    step_order = step_data["step_order"]
    cur_step = get_map(map_id, step_order)
    return cur_step


def get_map(map_id, step_order):
    # карта в виде словаря
    map_dict = map_from_id(map_id)
    print("\t[LOG] словарь с текущим шагом: ", map_dict)

    # получаем шаг из карты
    step_num = f"step_{step_order}"
    cur_step = map_dict[str(step_num)]
    print("\t[LOG] номер текущего подшага: ", cur_step)
    return cur_step


def map_from_id(norm_id):
    """ получаем карту в формате словаря по id норматива (TODO потом переделать под БД) """
    # получаем название файла для текущей карты норматива
    id_json_file = open("configs/id_json.json", encoding='utf-8')
    id_to_json = json.load(id_json_file)
    print("AAAAAAA: ", norm_id)
    map_file_name = id_to_json[str(norm_id)]
    id_json_file.close()

    # парсим файл в json
    print("\t[LOG] norm file name: ", map_file_name)
    map_file = open(map_file_name, encoding='utf-8')
    map_dict = json.load(map_file)
    return map_dict

