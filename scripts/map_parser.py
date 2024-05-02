import json
import scripts.dbconnection as db
from scripts.randomize_instruction import randomize_elements

import os


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
    cur_step, last_stage_num = get_map_data(map_id, step_order, session_hash)

    # запоминаем номер последнего stage в нормативе    
    db_con_var.update_rows(
        table_name="exercises_status",
        where_statement=where_statement,
        last_stage_num=last_stage_num)

    # TODO упростить !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # # из таблицы "sessions" получаем session_exercise_id
    # where_statement = f"session_hash='{session_hash}'"
    # session_data = db_con_var.get_data_with_where_statement(
    #     table_name="sessions", where_statement=where_statement)

    # # из таблицы "exercises_status" статус текущего шага
    # where_statement = f"id={session_data['session_exercise_id']}"
    # exercises_data = db_con_var.get_data_with_where_statement(
    #     table_name="exercises_status", where_statement=where_statement)
    
    # если порядок шагов не важен, пишем об этом в таблицу step_group_status
    if cur_step["order"] == False:
        where_statement = f"id={exercises_data['step_id']}"
        db_con_var.update_rows(
            table_name="step_group_status", where_statement=where_statement,
            sub_step_order=-1)

    return cur_step


def get_map_data(map_id, step_order, session_hash):
    # карта в виде словаря
    map_dict, last_step_order = map_from_id(map_id, session_hash)
    # print("\t[DEBUG] текущая карта: ", map_dict)

    # получаем шаг из карты
    step_num = f"step_{step_order}"
    # TODO если шага нет в карте, то не ломаемся
    cur_step = map_dict[str(step_num)]
    print("\t[LOG] текущий подшаг из карты: ", cur_step)
    return cur_step, last_step_order


def map_from_id(norm_id, session_hash):
    """ получаем карту в формате словаря по id норматива (TODO потом переделать под БД) """
    # получаем название файла для текущей карты норматива
    id_json_file = open("configs/id_json.json", encoding='utf-8')    

    # TODO проверить, есть ли файл
    id_to_json = json.load(id_json_file)
    
    # номер последнего stage в нормативе
    norm_id_str = str(norm_id)
    norm_name = "norm_" + norm_id_str[0] 
    last_stage_num = id_to_json["last_stage_num"][norm_name]

    map_file_name = id_to_json[str(norm_id)]
    id_json_file.close()

    # парсим файл в json
    print("\t[LOG] файл с картой: ", map_file_name)
    map_file = open(map_file_name, encoding='utf-8')
    map_dict = json.load(map_file)

    if os.path.basename(map_file_name) == 'ex_1.2.0.json':
        print('RANDOM')
        map_dict = randomize_elements('P302O', map_dict['step_0'], session_hash)

    return map_dict, last_stage_num
