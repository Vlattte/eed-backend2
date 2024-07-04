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

    return equipments_normative_config