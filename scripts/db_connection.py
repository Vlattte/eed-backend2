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

    def add_elements(self, table_name, **kwargs):
        """
        Получает имя таблицы и записывает в него значения

        kwargs - словарь, где ключи - названия полей, значения в них - то, что нужно добавить
        """

        # создаем список из ключей и их значений
        keys = []
        values = []

        for key, value in kwargs.items():
            keys.append(key)
            # если тип значения - строка, то добавим кавычки
            if type(value) is str: 
                value = f"'{value}'"
            values.append(value)

        # добавление в таблицу значений
        cursor = self.connection.cursor()
        cursor.execute(f"""
                        INSERT INTO {table_name} ({', '.join(keys)})
                        VALUES({', '.join(map(str, values))})
                        """
        )
        cursor.close()
        self.connection.commit()


    def del_user(table_name, user_session_hash):
        pass