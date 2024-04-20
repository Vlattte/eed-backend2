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
    print("\t[DEBUG] exercise status:", exercises_data)  # [{'id': 18, 'map_id': 11, 'stage_id': 0, 'group_steps_id': 0}]

    # из таблицы "step_group_status" порядковый номер шага
    where_statement = f"id={exercises_data['step_id']}"
    step_data = db_con_var.get_data_with_where_statement(
        table_name="step_group_status",
        where_statement=where_statement,
        step_order="step_order",
        sub_step_order=0)

    # получаем карту по ее id
    map_id = exercises_data["stage_id"]
    step_order = step_data["step_order"]
    cur_step, last_step_num = get_map_data(map_id, step_order)

    # TODO упростить

    db_con_var = db.DbConnection()
    # из таблицы "sessions" получаем session_exercise_id
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
        table_name="sessions", where_statement=where_statement)

    # из таблицы "exercises_status" статус текущего шага
    where_statement = f"id={session_data['session_exercise_id']}"
    exercises_data = db_con_var.get_data_with_where_statement(
        table_name="exercises_status", where_statement=where_statement)

    print("\t[DEBUG] exercise_data = ", exercises_data)
    print(f"\t last = {last_step_num}")
    where_statement = f"id={exercises_data["step_id"]}"
    db_con_var.update_rows(
        table_name="step_group_status", where_statement=where_statement,
        last_step_num=last_step_num
    )
    
    # если порядок шагов не важен, пишем об этом в таблицу step_group_status
    if cur_step["order"] == False:
        where_statement = f"id={exercises_data['step_id']}"
        db_con_var.update_rows(
            table_name="step_group_status",  where_statement=where_statement,
            sub_step_order=-1
        )

    return cur_step


def get_map_data(map_id, step_order):
    # карта в виде словаря
    map_dict, last_step_order = map_from_id(map_id)
    print("\t[DEBUG] текущая карта: ", map_dict)

    # получаем шаг из карты
    step_num = f"step_{step_order}"
    cur_step = map_dict[str(step_num)]
    print("\t[LOG] текущий подшаг из карты: ", cur_step)
    return cur_step, last_step_order


def map_from_id(norm_id):
    """ получаем карту в формате словаря по id норматива (TODO потом переделать под БД) """
    # получаем название файла для текущей карты норматива
    id_json_file = open("configs/id_json.json", encoding='utf-8')

    # TODO добработать это, когда фронт будет присылать имя норматива
    # TODO может сломаться при обновлении страницы
    norm_name = norm_id
    if norm_id == 11:
        norm_name = "norm_1"
    print("aaaaaa, ", norm_name)

    # TODO проверить, есть ли файл

    id_to_json = json.load(id_json_file)
    print("\t\t\t[DEBUG] json_file = ", id_to_json)
    
    # номер последнего шага
    norm_id_str = str(norm_id)
    norm_name = "norm_" + norm_id_str[0]       
    last_step_num = id_to_json["last_step_num"][norm_name]

    map_file_name = id_to_json[str(norm_id)]
    id_json_file.close()

    # парсим файл в json
    print("\t[LOG] файл с картой: ", map_file_name)
    map_file = open(map_file_name, encoding='utf-8')
    map_dict = json.load(map_file)
    return map_dict, last_step_num
