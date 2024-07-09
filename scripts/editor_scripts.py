import json
import os

def get_equipment_config(equipment_name: str):
    """
    :param equipment_name: назваие аппаратуры
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
            "ids": []}
         }
    

    for block in blocks: 
        for component in block['components']:
            component_id = component['id']
            component_tag = component['name']

            component_values = [value_dict['value'] for value_dict in component['valuesAndPhotos']]    
            
            tags.append(component_tag)

            if component_tag == 'button_pressed':
                id_to_type_config['button']['ids'].append(component_id)
            elif "lever" in component_tag and sorted(component_values) == ['off', 'on']:
                id_to_type_config['tumbler']['ids'].append(component_id)

    print(set(tags))
    print()
    print(id_to_type_config)
    print(sorted(id_to_type_config['tumbler']['ids']) == [1013, 1019,
              2001, 2002, 2009, 2010, 2011, 2012, 2013, 2014, 2021,
              3022,
              4000, 4001,
              5009, 5010,
              6002,
              9010,
              11012])

        


if __name__ == "__main__":
    get_id_to_type_config("./equipment_configs/P302O.json")
