""" manage elements functions (add elements, send elements, the same with cables) """

# database
import scripts.dbconnection as db


# "session_hash": string,
# "operation": "loadElements"

#       return::
# "status": bool,
# "error": string,
# "elements": [
#     {
#         "id": integer,
#         "type": string,
#         "original_src": text, // берём отсюда width и height
#         "conditions": [
#             {
#                 "condition_id": integer,
# vvv пустой ли выбранный массив состояний, редактировать доступные шаблоны нельзя, но можно добавлять vvv
#                 "is_new_condition": bool,
#                 "condition_positions": [
#                     {
#                         "condition_position_id": integer,
#                         "angle": integer, -- --> градусы
#                         "order": integer, -- --> порядок переключения состояний
#                         "src": text, -- --> ОТНОСИТЕЛЬНЫЙ путь до оригинальной фотографии
#                     }
#                 ]
#             }
#         ]
#     }
# ]
def load_elements(message_dict):
    """ получает элементы из БД и отправляет их в редактор оборудования """
    status = False
    error = "no-error"
    #TODO:: добавить conditions
    db_con_var = db.DbConnection()
    elements = db_con_var.get_data_request(table_name="elements", all="*")

    # проверяем, есть ли вообще елементы в таблице "block_elements"
    if len(elements) == 0:
        error = "no-elements-in-database"

    back_answer = {"status": status, "error": error, "elements": elements}
    return back_answer


# ДОБАВЛЕНИЕ CONDISION
#front->back: {
#   "session_hash": string,
#   "operation": "addCondision",
#   "element_id": integer
def add_condition(message_dict):
    """ добавление состояний в таблицу "element_group_condition" """
    db_con_var = db.DbConnection()
    condition_ids = db_con_var.add_element_and_get_id(table_name="element_group_condition",
                                                      element_id=message_dict["element_id"])
    # TODO:: убрать все обращения к нулевому элементу в бд скрипт,
    #  на этом уровне астракции не понятно что происходит
    condition_id = condition_ids[0]
    status = True
    error = "condition added"
    back_answer = {"status": status, "condition_id": condition_id, "error": error}
    return back_answer


# ДОБАВЛЕНИЕ ЭЛЕМЕНТА В НАБОР
def add_element(message_dict):
    """ добавление элементов в БД (таблица "elements") """
    status = False
    error = "element redefinition"
    element_id = -1

    # получаем id типа элемента по его названию
    type_id = add_type(message_dict["element"]["type"])
    # проверяем, есть ли уже такой елемент в таблице "elements" по id типа
    is_element_in_base = find_element(type_id)
    if not is_element_in_base:
        db_con_var = db.DbConnection()
        elements_names = db_con_var.add_element_and_get_id(table_name="elements",
                                                           type_id=type_id,
                                                           original_src=message_dict["element"]["src"])
        element_id = elements_names[0]
        status = True
        error = "no error"

    back_answer = {"status": status, "element_id": element_id, "error": error}
    return back_answer


def add_type(type_name):
    """ добавление нового типа в таблицу "types" """
    # нужно сопоставить название типа с его номером, либо добавить его, если такого нет
    type_ids = find_id_by_name("types", type_name)
    if type_ids == -1:
        db_con_var = db.DbConnection()
        type_ids = db_con_var.add_element_and_get_id(table_name="types", name=type_name)
    type_id = type_ids[0]

    return type_id


def find_id_by_name(table_name, param_name):
    """ tries to find any param by name in table "table_name" """
    db_con_var = db.DbConnection()
    where_statement = f"name='{param_name}'".format(param_name=param_name)
    param_names = db_con_var.get_data_with_where_statement(table_name=table_name, id="id",
                                                           where_statement=where_statement)

    param_id = -1  # значит такого нет и нужно добавить в БД
    if len(param_names) > 0:
        param_id = param_names[0]
    return param_id


def find_element(type_id):
    """ tries to find block by name in table "apparat_blocks" """
    db_con_var = db.DbConnection()
    where_statement = f"type_id='{type_id}'".format(type_id=type_id)
    element_names = db_con_var.get_data_with_where_statement(table_name="elements", type_id=type_id,
                                                             where_statement=where_statement)
    is_element_added = len(element_names) > 0
    return is_element_added


def find_type_name(type_name):
    """ tries to find type by name in table "types" """
    db_con_var = db.DbConnection()
    where_statement = f"name='{type_name}'".format(type_name=type_name)
    type_names = db_con_var.get_data_with_where_statement(table_name="types", name=type_name,
                                                          where_statement=where_statement)
    is_type_added = len(type_names) > 0
    return is_type_added

