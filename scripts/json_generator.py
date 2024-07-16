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
        equipment_id = message["equipment_id"]
        norm_id = message["norm_id"]        
        order = message["order"]
        sub_steps = message["sub_steps"]
        array_actions = message["array_actions"]
        annotation = message["annotation"]
    except KeyError:
        print("\t[KeyError] один из ключей equipment_id, step, order, sub_steps, array_actions, annotation не был указан в входящем сообщении")

    # получаем данные по уже существующему нормативу
    normative_path = get_normative_path(message)
    print("Normative path = ", normative_path)
    normative_data = {}

    # если файла нет, то создаем
    if not os.path.exists(normative_path):
        with open(normative_path, encoding='utf-8', mode="w"):
            pass
    
    # читаем все данные по выбранному нормативу
    with open(normative_path, encoding='utf-8', mode="r") as norm_file:
        normative_data = json.load(norm_file)

    print("[DEBUG] norm norm \n\t", normative_data)
    prev_step_num = f"step_{step-1}"
    step_num = f"step_{step}"
    
    # если есть шаг до этого, надо ему добавить массив next_actions и поле count_next
    if step-1 >= 0:        
        normative_data[prev_step_num]["next_actions"] = get_next_actions(array_actions)

    # TODO есть штука next_stage_num, она содержит id следующего stage
    # TODO надо понять нужна ли она тут, так как предполагается только 1 stage

    # меняем/добавляем новый шаг
    editing_step = {}    
    editing_step["step"] = step     
    editing_step["count_action"] = len(array_actions)
    editing_step["array_actions"] = array_actions
    editing_step["actions_for_step"] = len(sub_steps)
    editing_step["sub_steps"] = sub_steps
    editing_step["count_acions"] = 0
    editing_step["next_actions"] = [ { "name": "nan" } ]
    editing_step["annotation"] = annotation
    normative_data[step_num] = editing_step

    with open(normative_path, encoding='utf-8', mode="w") as norm_file:
        json.dump(normative_data, norm_file)


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


def get_next_actions(array_actions):
    """ получаем массив следующих шагов (тех что надо подсветить) """
    next_actions = []
    for action in array_actions:
        cur_action = {}
        cur_action["apparat_id"] = action["apparat_id"]
        cur_action["next_id"] = action["action_id"]
        cur_action["tag"] = action["tag"]
        next_actions.append(cur_action)

    return next_actions

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
    
    msg_new_step = {
        "equipment_id": 2,       
        "norm_id": 2,
        "step": 0,
        "order": True,
        "sub_steps": [
        {
            "sub_step": 0,
            "action_id": 11012,
            "current_value": "on",
            "tag": "lever",
            "array_actions": [ ]
        },
        {
            "sub_step": 1,
            "action_id": 1019,
            "current_value": "on",
            "tag": "lever",
            "array_actions": [ ]
        },
        {
            "sub_step": 2,
            "action_id": 9010,
            "current_value": "on",
            "tag": "lever",
            "array_actions":[
                {
                "action_id": 9018,
                "action_value": "on",
                "apparat_id": 9,
                "tag": "lamp"
                }
            ]
        },
        {
            "sub_step": 3,
            "action_id": 4000,
            "current_value": "on",
            "tag": "lever",
            "array_actions": [ ]
        },
        {
            "sub_step": 4,
            "action_id": 4001,
            "current_value": "on",
            "tag": "lever",
            "array_actions": [ ]
        }
        ],    
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
        ],
        "annotation": ""
    }
    # set_init_norm_config(msg)
    add_new_step(msg_new_step)
    

