import os
import json

import random

def load_id_type_values_data(app_name, id_type_values_dir='init_jsons'):
    """
    id_type_values_dir: папка с файлами, содржащими типы элементов, их id, возможные значения
    """

    id_type_values_file_path = os.path.join(id_type_values_dir, f'id2type_{app_name}.json')
    with open(id_type_values_file_path, encoding="utf-8") as id_type_values_file:
        id_type_values_data = json.load(id_type_values_file)

    id_type_values_data = create_formated_id_type_values_data(id_type_values_data)

    return id_type_values_data

def get_instruction(norm_path): #app - название аппаратура, step_id - номер шага
    with open(norm_path, encoding='utf-8') as instruction_path:
        instruction = json.load(instruction_path)

    return instruction

def parse_instruction_ids(instruction):
    """
    ринимает на вход инструкцию и возвращает список ID, которые использовались в инструкции.
    Необходима, чтобы рандомить только отслеживаемые в инструкции элементы
    """
    id_list = []

    for action in instruction['array_actions']:
        action_id = action['action_id']
        if action_id not in id_list  and str(action_id).isnumeric():
            id_list.append(int(action_id))

    print('id_list')
    print(id_list)
    return id_list

def create_formated_id_type_values_data(id_type_values_data):
    """
    Функция принимает на вход данные о возможных положениях элементов, возвращает 
    словарь с одинаковым форматом данных:

    {
        "rotator":
            {"all_values": false,
             "elements": [
                {"id": 1003,
                 "values": [-150, -120, -90, -55, -30, 0, 25, 55, 90, 120, 150]},
                {"id": 1004,
                 "values": [-35, -15, 15, 35]}
                ] 
            }
    }
    
    """
    id_type_values_data_formated = {}

    for tag in id_type_values_data:  
        if tag == 'cabel': 
            continue

        tag_values = id_type_values_data[tag]

        # если все возможные положения элементов одинаковы
        # например, для всех тумблеров положения только on и off => all_values == True, 
        # а в случае ротаторов - для каждого id могут быть свои положения
        if tag_values["all_values"]:
            values = tag_values['values']

            tag_values_formated = {'all_values': False, 
                                   'elements': []}
            
            for id in tag_values["ids"]:
                tag_values_formated['elements'].append({'id': id, 'values': values})

            tag_values = tag_values_formated
        
        id_type_values_data_formated[tag] = tag_values 

    return id_type_values_data_formated

def get_right_element_value(instruction, element_id):
    """
    Cравнивает соответсвует ли рандомизированное значение с нужным из карты
    """
    
    right_element_value = -1

    # колличество подшагов
    steps = instruction["array_actions"]

    # проходимся по всем подшагам
    for step in steps:
        # когда найдем шаг связанный с нужным элементом
        # сравниваем соответсвует ли рандомизированное значение с нужным из карты
        if not str(step["action_id"]).isnumeric():
            continue

        if int(step["action_id"]) == int(element_id):
            element_value = step["action_value"]
            right_element_value = int(element_value) if str(element_value).isnumeric() else str(element_value)
            break

    return right_element_value


def randomize_elements(app_name, instruction, session_hash):
    """
    app_name - название аппаратуры
    instruction - норматив

    функция принимает на вход инструкцию с устанокой начальных положений, 
    устанавливает эти элементы в случайные положения
    """
    random.seed(session_hash)

    sub_step_counter = 0
    
    id_type_values_data = load_id_type_values_data(app_name=app_name)
    instruction_id_list = parse_instruction_ids(instruction)

    array_actions = []
    next_actions = []
    sub_steps = []

    for tag in id_type_values_data:
        tag_elements = id_type_values_data[tag]
        # NOTE: УБРАТЬ JUMPER, КОГДА ИХ ДОБАВЯТ ПОЛНОЦЕННО НА ФРОНТЕ
        # эти элементы пока не сделаны, пропускаем
        if tag == "cabel" or tag == "cabel_head" or tag == "jumper" or tag == "mover":
            continue

        print(tag)
        print(tag_elements)
        print()

        for element in tag_elements["elements"]:
            element_id = element['id']
            if element_id not in instruction_id_list:
                continue
            
            values_count = len(element['values'])
            state_id = random.randint(0,  values_count-1)
            state = element["values"][state_id]
            state = int(state) if str(state).isnumeric() else str(state)
            apparat_id = element_id // 1000

            right_element_value = get_right_element_value(instruction=instruction, element_id=element_id)

            new_array_action = {"apparat_id": apparat_id, 
                                "action_id": element_id, 
                                "current_value": state, 
                                "tag": tag}
            array_actions.append(new_array_action)
            
            if right_element_value != state:
                new_next_action = {"apparat_id": apparat_id, 
                                   "next_id": element_id, 
                                   "current_value": right_element_value, 
                                   "tag": tag}

                new_sub_step = {"sub_step": sub_step_counter, 
                                "action_id": element_id, 
                                "current_value": right_element_value,
                                "tag": tag}
                
                next_actions.append(new_next_action)
                sub_steps.append(new_sub_step)

                sub_step_counter += 1
    
    random_instruction = {
        "step_0": {
            "step": 0, 
            "actions_for_step": 0,
            "count_action": len(array_actions),
            "count_next": len(next_actions), 
            "order": False,
            "sub_steps": [],
            "array_actions": array_actions, 
            "next_actions": next_actions,
            "annotation": instruction["annotation"]
            }, 
        "step_1": {
            "step": 1, 
            "actions_for_step": len(sub_steps),
            "count_action": 0,
            "count_next": 0, 
            "order": False,
            "sub_steps": sub_steps,
            "array_actions": [], 
            "next_actions": [],
            "annotation": "Аппаратура подготовлена"
            }
    }

    return random_instruction
    
if __name__ == '__main__':
    norm_path = 'film_norm/ex_2.1.0.json'
    instruction = get_instruction(norm_path=norm_path)
    instruction = instruction['step_0']

    random_instruction = randomize_elements('P302O', instruction=instruction, session_hash=42)
    print("randomized")
    print(random_instruction)