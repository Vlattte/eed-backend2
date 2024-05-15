""" парсер карты """

import json
import scripts.dbconnection as db
import scripts.db_fast_scripts as db_script


def get_next_step(session_hash):
    """ получаем следующий шаг исходя из хэша сессии """
    db_con_var = db.DbConnection()

    # карта в виде словаря и номер последней стадии
    stage_id = db_script.get_stage_id(session_hash)
    map_dict, last_stage_num = map_from_id(stage_id)        
    if map_dict == {}:
        return map_dict

    step_data = db_script.get_step_data(session_hash)    
    step_order = step_data["step_order"]
    step_id = step_data["id"]

    # обновляем номер последней стадии
    update_last_stage_order(last_stage_num, step_id)

    # получаем текущий шаг из карты    
    table_step = get_current_step(map_dict, step_order)
    if table_step == {}:
        return table_step    

    # если порядок шагов не важен, пишем об этом в таблицу step_group_status
    if table_step["order"]:
        return table_step
    
    # запоминаем, что порядок не важен
    where_statement = f"id={step_id}"
    db_con_var.update_rows(
        table_name="step_group_status", 
        where_statement=where_statement,
        sub_step_order=-1)

    return table_step


def update_last_stage_order(last_stage_num, step_id):
    """ обновляем номер последней стадии в нормативе """
    db_con_var = db.DbConnection()
    
    # запоминаем номер последнего stage в нормативе  
    where_statement = f"id={step_id}"
    db_con_var.update_rows(
        table_name="exercises_status",
        where_statement=where_statement,
        last_stage_num=last_stage_num)    


def get_current_step(map_dict, step_order):     
    # получаем шаг из карты
    step_num = f"step_{step_order}"

    # если шага нет в карте
    if str(step_num) not in map_dict:
        print(f"\t[ERROR] шага с номером {step_num} нет в карте")
        return {}
    
    table_step = map_dict[str(step_num)]
    print("\t[LOG] текущий подшаг из карты: ", table_step)
    return table_step


def map_from_id(norm_id):
    """ получаем карту в формате словаря по id норматива (TODO потом переделать под БД) """
    # получаем название файла для текущей карты норматива
    id_json_file = open("configs/id_json.json", encoding='utf-8')        
    id_to_json = json.load(id_json_file)
    
    # номер последнего stage в нормативе
    norm_id_str = str(norm_id)
    norm_name = "norm_" + norm_id_str[0] 
    last_stage_num = id_to_json["last_stage_num"][norm_name]

    # проверяем есть ли такая карта в "id_json"
    if str(norm_id) not in id_to_json:
        print("\t[ERROR] no such norm_id: ", norm_id)
        return {}, last_stage_num

    map_file_name = id_to_json[str(norm_id)]
    id_json_file.close()

    # парсим файл в json
    print("\t[LOG] файл с картой: ", map_file_name)
    map_file = open(map_file_name, encoding='utf-8')
    map_dict = json.load(map_file)
    return map_dict, last_stage_num
    print("aaaa")