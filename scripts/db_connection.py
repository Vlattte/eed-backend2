'''
Подключение к базе данных из конфига db_connection.yaml
'''

import psycopg2
import yaml

class db_connection():
    """
    Создание подключения к базе данных

    Создает соединение с БД, а если оно уже есть, то соединение будет ссылаться на уже созданное.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(db_connection, cls).__new__(cls)

            with open('./configs/db_connection.yaml', 'r') as config_file:
                connect_params = yaml.safe_load(config_file)['connect_params']

            cls.connection = psycopg2.connect(**connect_params)
        return cls.instance


