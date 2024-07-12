""" генератор файлов типа json """

import os.path
import json


def set_init_norm_config(message):
    """ принимаем массив элементов и их положений для задания начальной конфигурации """    
    # TODO подумать, надо ли вообще как-то тут так извращаться или всегда переписывать в нулевом шаге array_actions
    if "array_actions" not in message:
        print("\t\t[KeyError] ключ array_acions не был указан в входящем сообщении")

    array_actions = message["array_actions"]            

    norm_config = {}
    # если файл окажется пустым, то дабавим конфигураци в нулевой шаг
    normative_path = get_normative_path(message)
    if not os.path.exists(normative_path):
        norm_config = {"step_0": {
                       "array_actions": array_actions,
                       "count_action": len(array_actions)}}    
    else:
        read_config = open(normative_path, encoding='utf-8', mode="r")
        norm_config = json.load(read_config)
        norm_config["step_0"]["array_actions"] = array_actions
        norm_config["step_0"]["count_action"] = len(array_actions)            
    
    config_file = open(normative_path, encoding='utf-8', mode="w")
    json.dump(norm_config, config_file)
    config_file.close()
    return {"status": "OK"}


def add_new_step(message):
    """ добавление нового шага в норматив, а также добавление списка next_actions в предыдущий шаг """
    #  проверка всех нужных для добавления шага элементов
    try:        
        step = message["step"]
        order = message["order"]
        sub_steps = message["sub_steps"]
        array_actions = message["array_actions"]
        annotation = message["annotation"]
    except KeyError:
        print("\t\t[KeyError] один из ключей equipment_id, step, order, sub_steps, array_actions, annotation не был указан в входящем сообщении")

    # получаем данные по уже существующему нормативу
    normative_path = get_normative_path(message)
    normative_data = {}

    # если файла нет, то создаем
    if not os.path.exists(normative_path):
        with open(normative_path, encoding='utf-8', mode="w"):
            pass
    
    with open(normative_path, encoding='utf-8', mode="r") as norm_file:
        normative_data = json.load(norm_file)

    step_num = f"step_{step}"
    
    # если меняем уже добавленный шаг
    # if step_num in normative_data:
    #         ...



def get_normative_path(message):
    try:
        equipment_id = message["equipment_id"]
        norm_id = message["norm_id"]        
    except KeyError:
        print("\t\t[KeyError] один из ключей equipment_id, norm_id не был указан в входящем сообщении")
    
    # посмотрим есть ли уже такой json, если есть, то обновляем, а не создаем TODO(????)
    equipment_folder = f"normatives\\equipment_{equipment_id}"

    if not os.path.isdir(equipment_folder):
        os.mkdir(equipment_folder)

    normative_path = os.path.join(equipment_folder, f"norm_{norm_id}")
    return normative_path


if __name__ == "__main__":    
    msg = {
        "operation": "setInitNormConfig", 
        "equipment_id": 2,        
        "norm_id": 2,
        "array_actions": [
        {
                "apparat_id": 2,
                "action_id": 4401,
                "action_value": "up",
                "tag": "lever"
            },
            {
                "apparat_id": 3,
                "action_id": 7047,
                "action_value": "down",
                "tag": "lever"
            },
            {
                "apparat_id": 4,
                "action_id": 4401,
                "action_value": "up",
                "tag": "lever"
            }
    ]
    }
    set_init_norm_config(msg)
    

