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
#     "elements": {
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
#         }
# }
def load_elements(message_dict):
    """ получает элементы из БД и отправляет их в редактор оборудования """
    status = False
    error = "no-error"
    # TODO:: добавить conditions

    directory = '../eed-frontend/src/views/editor/control'
    dir_names = [dir_name for dir_name in os.listdir(directory)]

    apparat_id = message_dict["apparat_id"]
    block_id = message_dict["block_id"]
    apparat_src = f"apparats/{apparat_id}_{block_id}.png"

    # тут лежит тип и изначальная фотка элемента
    db_con_var = db.DbConnection()
    table_elements = db_con_var.get_data_request(table_name="elements", all="*")

    # type_match = [{'id': 1, 'name': 'rotator'}, {'id': 2, 'name': 'lever'}, ..]
    type_match = db_con_var.get_data_request(table_name="types", all="*")

    # type_match_dict = {1: 'rotator', 2: 'lever'}
    type_match_dict = {}
    for type_match_i in type_match:
        type_id = type_match_i['id']
        type_name = type_match_i['name']
        type_match_dict[type_id] = type_name

    # elements = {'rotator': [], 'lever': []}
    elements = {el["name"]: [] for el in type_match}

    # здесь получаем группы состояний по каждому элементу
    for element in table_elements:
        element_type = type_match_dict[element['type_id']]

        # уберем type_id
        element.pop("type_id", element["type_id"])

        element["conditions"] = []

        where_statement = f"element_id = {element['id']}"
        condition_groups = db_con_var.get_data_with_where_statement(table_name="element_group_condition", id="id",
                                                                    where_statement=where_statement)

        for condition in condition_groups:
            condition['condition_id'] = condition.pop("id", condition["id"])

            where_statement = f"condition_group_id = {condition['condition_id']}"
            element_positions = db_con_var.get_data_with_where_statement(table_name="element_condition_positions",
                                                                         all="*",
                                                                         where_statement=where_statement)

            condition["is_new_condition"] = False
            if len(element_positions) > 0:
                condition["is_new_condition"] = True

            for pos in range(len(element_positions)):
                element_positions[pos]["order"] = \
                    element_positions[pos].pop("condition_order", element_positions[pos]["condition_order"])
                element_positions[pos].pop("id", element_positions[pos]["id"])
            print(element_positions)

            condition['condition_positions'] = element_positions
            element["conditions"].append(condition)

        elements[element_type].append(element)

    print("***")
    print(elements)
    print("***")

    # проверяем, есть ли вообще елементы в таблице "block_elements"
    if len(table_elements) == 0:
        error = "no-elements-in-database"
        status = False

    back_answer = {"status": status, "error": error, "src": apparat_src, "elements": elements}
    return back_answer


# ДОБАВЛЕНИЕ CONDITION
# front->back: {
#   "session_hash": string,
#   "operation": "addCondision",
#   "element_id": integer
def add_condition(message_dict):
    """ добавление состояний в таблицу "element_group_condition" """
    db_con_var = db.DbConnection()

    condition_id = -1
    status = False
    error = f"element with id ({message_dict['element_id']}) doesn't exist"

    if db_con_var.check_exist(table_name="elements", key="id", value=message_dict["element_id"]):
        condition_id = db_con_var.add_values_and_get_id(table_name="element_group_condition",
                                                        element_id=message_dict["element_id"])
        status = True
        error = "condition added"

    # TODO:: убрать все обращения к нулевому элементу в бд скрипт,
    #  на этом уровне астракции не понятно что происходит

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
    error = "condition group with such id doesn't exist"

    db_con_var = db.DbConnection()
    if db_con_var.check_exist(table_name="element_group_condition", key="id", value=message_dict["condition_id"]):
        condition_id = message_dict["condition_id"]
        positions = message_dict["positions"]

        status = True
        error = "positions added"

        # проходимся по позициям
        for pos in positions:
            returned_id = db_con_var.add_values_and_get_id(table_name="element_condition_positions",
                                                           condition_group_id=condition_id,
                                                           angle=pos["positions"]["angle"],
                                                           condition_order=pos["order"])
            if returned_id == -1:
                error = "one or more positions was previously added"

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

    element_id = db_con_var.add_values_and_get_id(table_name="elements", type_id=type_id,
                                                  width=width, height=height)

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
    type_id = find_id_by_name("types", type_name)
    if type_id == -1:
        db_con_var = db.DbConnection()
        type_id = db_con_var.add_values_and_get_id(table_name="types", name=type_name)

    return type_id


def find_id_by_name(table_name, param_name):
    """ tries to find any param by name in table "table_name" """
    db_con_var = db.DbConnection()
    where_statement = f"name='{param_name}'"
    param_dict = db_con_var.get_data_with_where_statement(table_name=table_name, id="id",
                                                          where_statement=where_statement)

    param_id = -1  # значит такого нет и нужно добавить в БД
    print(param_dict)
    if len(param_dict) > 0:
        param_id = param_dict[0]["id"]

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
