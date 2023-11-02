""" manage elements functions (add elements, send elements, the same with cables) """

# database
import scripts.dbconnection as db

# обработчик изображений
import scripts.image_operations as img_ops

import os
import os.path


# "session_hash": string,
# "operation": "loadElements"
# "apparat_id": integer
# "block_id": integer

#       return::
# {
#     "status": bool,
#     "error": string,
#     "src": string, # путь до фотки блока
#     "elements": [
#         "buttons": [
#             {
#                 "id": integer,
#                 "original_src": text, // берём отсюда width и height
#                 "conditions": [
#                     {
#                         "condition_id": integer,
#                         "is_new_condition": bool, // пустой ли выбранный массив состояний, редактировать доступные шаблоны нельзя, но можно добавлять
#                         "condition_positions": [
#                             {
#                                 "condition_position_id": integer,
#                                 "angle": integer, -- --> градусы
#                                 "order": integer, -- --> порядок переключения состояний
#                                 "src": text, -- --> ОТНОСИТЕЛЬНЫЙ путь до оригинальной фотографии
#                             }
#                         ]
#                     }
#                 ]
#             }
#         ],
#         "levers": [...],
#         "rotators": [...],
#         "cables": [...],
#         "bolts": [...],
#         "jumpers": [...],
#         "lights": [...], 
#         "arrows": [...]
#         ]
# }
def load_elements(message_dict):
    """ получает элементы из БД и отправляет их в редактор оборудования """
    status = False
    error = "no-error"
    #TODO:: добавить conditions
    db_con_var = db.DbConnection()

    elements = []
    directory = '../eed-frontend/src/views/editor/control'
    dir_names = [dir_name for dir_name in os.listdir(directory)]

    apparat_id = message_dict["apparat_id"]
    block_id = message_dict["block_id"]
    src = f"apparats/{apparat_id}_{block_id}.png"

    # тут лежит тип и изначальная фотка элемента
    elements = db_con_var.get_data_request(table_name="elements", all="*")
    # здесь получаем группы состояний по каждому элементу
    print("elements = ", elements)
    for element_id in elements["id"]:
        cur_element = {"is_new_condition": False, "condition_positions": []}
       
        where_statement = f"element_id = {element_id}"
        condition_ids = db_con_var.get_data_with_where_statement(table_name="element_group_condition", id="id",
                                                                 where_statement=where_statement)
        # есть ли вообще позиции у элемента
        if len(condition_ids) > 0:
            cur_element["is_new_condition"] = True

        for cond_id in condition_ids:
            where_statement = f"condition_group_id = {cond_id}"
            element_positions = db_con_var.get_data_with_where_statement(table_name="element_condition_positions", all="*",
                                                                         where_statement=where_statement)
            print(element_positions)
            # condition_positions = []
            # position = []
            # cur_element["condition_positions"].append(condition_positions)
    

    # проверяем, есть ли вообще елементы в таблице "block_elements"
    if len(elements) == 0:
        error = "no-elements-in-database"
        status = False

    back_answer = {"status": status, "error": error, "elements": elements, "src": src}
    return back_answer


# ДОБАВЛЕНИЕ CONDISION
# front->back: {
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


# ДОБАВЛЕНИЕ СОСТОЯНИЙ ЭЛЕМЕНТА
# "session_hash": string,
# "element_id": integer,
# "condition_id": integer,
# "positions": [
#       "position": {
#           "angle": integer, -- --> градусы
#           "src": text, -- --> ОТНОСИТЕЛЬНЫЙ путь до оригинальной фотографии
#       },
#       "order": integer,
#       "src": string,
# ],
# "operation": "addCondisionPositions",
def add_positions_to_condition(message_dict):
    """добавление позиций элемента,который находится в определенном состоянии в таблицу"element_condition_positions" """
    status = False
    error = "condition position not added"

    condition_id = message_dict["conditions"]["condition_id"]
    positions = message_dict["conditions"]["positions"]

    db_con_var = db.DbConnection()
    # проходимся по позициям
    for pos in positions:
        db_con_var.add_elements(table_name="element_condition_positions",
                                condition_group_id=condition_id,
                                angle=pos["position"]["angle"],
                                src=pos["position"]["angle"],
                                condition_order=pos["order"])

    status = True
    error = "condition position successfully added"
    back_answer = {"status": status, "error": error}
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

    db_con_var = db.DbConnection()
    image = img_ops.binary_2_image(message_dict["element"]["src"])
    width, height = img_ops.get_image_params(image)

    elements_ids = db_con_var.add_element_and_get_id(table_name="elements",
                                                     type_id=type_id,
                                                     width=width,
                                                     height=height)
    element_id = elements_ids[0]

    # сохранение изображения
    element_path = f'./../eed-frontend/public/elements/{element_id}_{message_dict["element"]["type"]}.png'
    img_ops.save_image(image, element_path)
    where_statement = f"id={element_id}"

    db_con_var.update_rows(table_name="elements", where_statement=where_statement,
                           original_src=element_path)

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

def parse_returned_data(data, *column_names):
    """
    Функция принимает на вход кортеж из строк таблицы. Каждый элемент кортежа содержит в себе массив с элементами строки
    
    Возвращает словарь, где ключи - названия столбцов, либо индексы (если не переданы названия колонок), элементы - списки со 
    значениями в столбцах
    """

    return_data = dict()

    if len(column_names) != len(data[0]):
        column_names = [i for i in range(len(data[0]))]
    
    for row in data:
        for column_name, column_value in zip(column_names, row):
            if column_name not in return_data.keys():
                return_data[column_name] = []
            return_data[column_name].append(column_value)
    
    return return_data
