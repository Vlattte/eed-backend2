import json
import os

def get_equipment_config(equipment_name: str):
    """
    :param equipment_name: название аппаратуры
    """
    equipment_name = equipment_name.replace('-', '').replace('_', '').capitalize()

    equipment_configs_folder = './equipment_configs/'
    equipment_name = equipment_name + '.json'
    equipment_config_path = os.path.join(equipment_configs_folder, equipment_name)
    with open(equipment_config_path, encoding='utf-8') as f:
        equipment_config =  json.load(f)
    
    return equipment_config

def get_list_equipments_normatives():    
    equipments_normative_config_path = "./configs/equipment_config.json"
    with open(equipments_normative_config_path, encoding='utf-8') as f:
        equipments_normative_config = json.load(f)

    equipments_normative_config['isAdmin'] = True
    return equipments_normative_config

def get_id_to_type_config(path):
    with open(path, encoding='utf-8') as f:
        map_config = json.load(f)
    
    blocks = map_config['blocks']

    tags = []

    id_to_type_config = {
        'button': {
            "all_values": True,
            "values": [ "on", "off"],
            "values_arr_size": 2,
            "ids": []
            },
        "tumbler": {
            "all_values": True,
            "values": [ "off", "on"],
            "values_arr_size": 2,
            "ids": []
            },
        "cabel_head": {
            "all_values": True,
            "values": ["off", "on"],
            "values_arr_size": 2,
            "ids": []
            },
        "cabel": {
            "all_values": True,
            "values": [ "none", "cabel"],
            "values_arr_size": 2,
            "elements": []
            },
        "lever": {
            "all_values": True,
            "values": [ "up", "center", "down"],
            "values_arr_size": 3,
            "ids": []
            },
        "jumper": {
            "all_values": True,
            "values": ["off", "on"],
            "values_arr_size": 2,
            "ids": []
            },
        "rotator": {
            "all_values": False,
            "elements": []
            },
        "channel": {
            "all_values": False,
            "elements": []
            },
        "mover": {
            "all_values": False,
            "elements": []
            },
        "arrow": {
            "all_values": False,
            "elements": []
            }
    }
    

    for block in blocks: 
        for component in block['components']:
            component_id = component['id']
            component_tag = component['name']
            component_ids = component['ids'] if 'ids' in component.keys() else []

            component_values = [value_dict['value'] for value_dict in component['valuesAndPhotos']]
            component_photos = [value_dict['photo'] for value_dict in component['valuesAndPhotos']]
            
            tags.append(component_tag)

            if component_tag == 'button_pressed':
                id_to_type_config['button']['ids'].append(component_id)
            elif "lever" in component_tag and sorted(component_values) == ['off', 'on']:
                id_to_type_config['tumbler']['ids'].append(component_id)
            elif component_values[0] == 'off' and component_photos[0] == ' ' and component_values[1] == 'on' and 'cabel_head' in component_photos[1]:
                id_to_type_config['cabel_head']['ids'].append(component_id)
            elif component_values[0] == 'none' and component_values[1] == 'cabel':
                id_to_type_config['cabel']['elements'].append({
                    'id': component_id, 
                    'heads': component_ids
                    })
            elif 'lever' in component_tag and sorted(component_values) == ["center", "down", "up"]:
                id_to_type_config['lever']['ids'].append(component_id)
            elif component_tag == 'cable_head4':
                id_to_type_config['jumper']['ids'].append(component_id)
            elif component_tag == 'rotator': 
                id_to_type_config['rotator']['elements'].append({
                    'id': component_id, 
                    'values': component_values
                    })
            elif component_tag == 'channel':
                id_to_type_config['channel']['elements'].append({
                    'id': component_id, 
                    'values': component_values
                    })
            elif component_tag == 'mover':
                id_to_type_config['mover']['elements'].append({
                    'id': component_id, 
                    'values': component_values
                    })
            elif component_tag == 'arrow':
                id_to_type_config['arrow']['elements'].append({
                    'id': component_id, 
                    })


    return id_to_type_config


def get_id_by_type(id, equipment_name: str):
    with open(f'./init_jsons/id2type_{equipment_name}.json', 'r', encoding='utf-8') as f:
        type_2_id_data = json.load(f)

    id_to_type_dict = {}
    for type, data in type_2_id_data.items():
        if "ids" in data:
            if id in data["ids"]:
                return type
        if "elements" in data:
            for element in data['elements']:
                if id == element['id']:
                    return type
    return 'unknown_type'


if __name__ == "__main__":
    print(get_id_by_type(6006, "P302O"))
    
    # id_to_type_config = get_id_to_type_config("./equipment_configs/P302O.json")

    # json_object = json.dumps(id_to_type_config, indent=4)

    # with open('./init_jsons/id2type_P302O.json', 'w', encoding='utf-8') as f:
    #     f.write(json_object)


