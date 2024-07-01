import json
import os

def get_aparat_config(aparat_name: str):
    """
    :param apparat_name: назваие аппаратуры
    """
    aparat_configs_folder = './aparat_configs/'
    apparat_name = apparat_name + '.json'
    apparat_config_path = os.path.join(aparat_configs_folder, aparat_name)
    with open(apparat_config_path, encoding='utf-8') as f:
        aparat_config =  json.load(f)
    
    return aparat_config