import json
import os

def get_apparat_config(apparat_name: str):
    """
    :param apparat_name: назваие аппаратуры
    """
    apparat_configs_folder = './apparat_configs/'
    apparat_name = apparat_name + '.json'
    apparat_config_path = os.path.join(apparat_configs_folder, apparat_name)
    with open(apparat_config_path, encoding='utf-8') as f:
        apparat_config =  json.load(f)
    
    return apparat_config

def get_list_apparats():    
    apparats_normative_config_path = "./configs/apparat_config.json"
    with open(apparats_normative_config_path, encoding='utf-8') as f:
        apparats_normative_config = json.load(f)

    for apparat in apparats_normative_config_path["apparats"]:
        pass

if __name__ == "__main__":
    get_list_apparats()