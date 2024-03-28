""" Подключение к базе данных из конфига db_connection.yaml """

import os
import psycopg2
import yaml
from psycopg2 import Error

# FIXME: поменять комментарии, так как возвращаются уже словари
# FIXME: поменять columns_from_kwargs, values_from_kwargs на columns_values_from_kwargs, так как проходиться по значениям словаря, 
# минуя ключи - не очень корректно 


class DbConnection:
    """
    Создание подключения к базе данных

    Создает соединение с БД, а если оно уже есть, то соединение будет ссылаться на уже созданное.
    """

    def __new__(cls):
        try:
            if not hasattr(cls, 'instance'):
                cls.instance = super(DbConnection, cls).__new__(cls)
                print(os.getcwd())
                with open('./configs/db_connection.yaml', 'r') as config_file:
                    connect_params = yaml.safe_load(config_file)['connect_params']

                cls.connection = psycopg2.connect(**connect_params)
            return cls.instance
        except (Exception, Error) as error:
            print("Ошибка подключения к PostgreSQL", error)

    def update_rows(self, table_name, where_statement, **kwargs):
        """ обновляет данные в выбранной строке """
        # создаем список из столбцов и их значений
        columns = self.columns_from_kwargs(**kwargs)
        values = self.values_from_kwargs(**kwargs)

        query = [f'{column} = {value}'for column, value in zip(columns, values)]
        query = ', '.join(query)

        request_string = f"""
                            UPDATE {table_name} SET {query} 
                            WHERE {where_statement}                   
                          """

        self.send_request(request_string, is_return_data=False, is_return_column_names=False)

    def add_values_and_get_id(self, table_name, **kwargs):
        """
                Получает имя таблицы, записывает в него значения и возвращает id добавленной строки

                kwargs - словарь, где ключи - названия полей, значения в них - то, что нужно добавить
        """
        # TODO:: добавить проверку на ошибку и возвращать статус
        # создаем список из столбцов и их значений
        columns = self.columns_from_kwargs(**kwargs)
        values = self.values_from_kwargs(**kwargs)

        # формирование запроса к БД
        columns_string = ', '.join(map(str, columns))
        values_string = ', '.join(map(str, values))
        request_string = f"""
                            INSERT INTO {table_name} ({columns_string}) 
                            VALUES({values_string}) returning id                  
                          """

        request_id = self.send_request(request_string)
        print(request_id)
        return request_id[0]['id']

    def get_data_with_where_statement(self, table_name, where_statement, **kwargs):
        """
            получает имя таблицы и выбранные колонки

            where_statement: полный where запрос (example: "id = 47")
            :return: словарь с данными из таблицы
        """
        # создаем список из столбцов и их значений
        columns = self.columns_from_kwargs(**kwargs)
        columns_string = ', '.join(map(str, columns))
        if "all" in kwargs or len(kwargs) == 0:
            columns_string = '*'

        request_string = f"""
                            SELECT {columns_string} FROM {table_name}             
                            WHERE {where_statement}          
                          """
        print("REQUEST: ", request_string)
        chosen_data = self.send_request(request_string)

        # если только один элемент в массиве, то возвращаем его
        if len(chosen_data) == 1:
            return chosen_data[0]

        return chosen_data

    # FIXME: по хорошему мы к значениям можем обращаться только по ключам
    def columns_from_kwargs(self, **kwargs):
        """ получает kwargs(именнованые аргументы) и возвращает массив столбцов """
        columns = []
        for col in kwargs.keys():
            columns.append(col)

        return columns
    
    # FIXME: по хорошему мы к значениям можем обращаться только по ключам
    def values_from_kwargs(self, **kwargs):
        """ получает kwargs(именнованые аргументы) и возвращает массив значений """
        values = []
        for value in kwargs.values():
            # если тип значения - строка, то добавим кавычки
            if type(value) is str:
                value = f"'{value}'"
            values.append(value)

        return values

    def columns_values_from_kwargs(self, **kwargs):
        """ получает kwargs(именнованые аргументы) и возвращает список столбцов, список значений"""
        columns, values = [], []
        for col, value in kwargs.items():
            columns.append(col)
            values.append(value)

        return columns, values

    def send_request(self, request_string, is_return_data=True, is_return_column_names=True):
        # добавление в таблицу значений
        try:
            cursor = self.connection.cursor()
            cursor.execute(request_string)
            column_names = []
            if is_return_data:
                return_data = cursor.fetchall()
                column_names = [column.name for column in cursor.description]
                return_data = self.parse_returned_data(return_data, *column_names)

            cursor.close()
            self.connection.commit()
        
        except Exception as E:
            return_data = [{"id": -1, "error": E}]
            print("ERROR:", E)
            if type(E) == psycopg2.errors.UniqueViolation:
                print('Попытка добавить одинаковую пару значений')
                cursor.close()
                self.connection.commit()

        return return_data

    def get_data_request(self, table_name, **kwargs):
        """
            получает имя таблицы и выбранные колонки

            возвращает кортеж с данными из таблицы
        """
        # TODO:: сделать функцию для вызова в ней всех запросов, чтобы не дублировать код
        # создаем список из столбцов и их значений и формирование запроса к БД
        columns = self.columns_from_kwargs(**kwargs)
        columns_string = ', '.join(map(str, columns))
        if "all" in kwargs:
            columns_string = '*'

        request_string = f"""
                        SELECT {columns_string} FROM {table_name}                       
                        """
        return_data = self.send_request(request_string)
        return return_data

    def del_user(self, table_name, user_session_hash):
        pass

    def parse_returned_data(self, data, *column_names):
        """
        Функция принимает на вход кортеж из строк таблицы. Каждый элемент кортежа содержит в себе массив с элементами строки
        
        Возвращает словарь, где ключи - названия столбцов, либо индексы (если не переданы названия колонок), элементы - списки со 
        значениями в столбцах
        """

        # перевод данных в формат {"column_name": column_values}

        # return_data = dict()
        #
        # if len(data) == 0:
        #     return return_data
        #
        # if len(column_names) != len(data[0]):
        #     column_names = [i for i in range(len(data[0]))]
        #
        # for row in data:
        #     for column_name, column_value in zip(column_names, row):
        #         if column_name not in return_data.keys():
        #             return_data[column_name] = []
        #         return_data[column_name].append(column_value)

        # перевод данных в формат [{"column_name": column_value_i}, {"column_name": column_value_i}, ...]
        return_data = [{column_name: row[i] for i, column_name in enumerate(column_names)} for row in data]
        return return_data

    def check_exist(self, table_name, key, value):
        where_statement = f"{key} = {value}"
        
        data = self.get_data_with_where_statement(table_name=table_name, id='id', where_statement=where_statement)
        if len(data): 
            return True
        return False