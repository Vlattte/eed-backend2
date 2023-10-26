""" manage equipment functions """

# database
import scripts.dbconnection as db

# operations with image
import scripts.image_operations as img_ops

# для таблицы "sessions" нужен id пользователя (user_id) =>
#   - сначала проверяем существует ли уже подключение в таблице "sessions"
#   - если есть то получаем user_id => соединение уже есть
#   - иначе создаем пользователя в таблице "user_data", оттуда берем user_id
#       и сохраняем данные по соединению в "sessions"
def establish_connection(session_hash):
    """ save new session_hash """
    #FIXME:: сложная и нагруженная функция
    #TODO:: удалять session hash отовсюду, когда чел выходит
    db_con_var = db.DbConnection()
    user_id = check_connection(session_hash)

    # если нет такого пользователя, то добавляем и получаем  его id с помощью запроса returning
    if user_id == -1:
        # добавляем новую сессию для полученного id пользователя (user_id)
        user_id = create_new_user()
        db_con_var.add_element_and_get_id(table_name="sessions", session_hash=session_hash,
                                          user_id=user_id, session_exercise_id=-1)

    status = user_id > 0  # если добавилось, то все окей
    back_answer = {"status": status}
    return back_answer


def create_new_user(login="test", password="123", role=1):
    """
        creates new user with given params in table "user_data"
        :return user_id
    """
    db_con_var = db.DbConnection()
    user_id = db_con_var.add_element_and_get_id(table_name="user_data", login=login, role=1, password=password)
    return user_id


def check_connection(session_hash):
    """
        tries to find user by session_hash in table "sessions"
        :return if found user_id, else -1
    """
    db_con_var = db.DbConnection()

    where_statement = f"session_hash='{session_hash}'".format(session_hash=session_hash)
    user_ids_tuple = db_con_var.get_data_with_where_statement(table_name="sessions", user_id='user_id',
                                                              where_statement=where_statement)
    if len(user_ids_tuple) > 0:
        user_id = user_ids_tuple[0][0]
        return user_id
    return -1


def add_equipment_name(message_dict):
    """ save equipment name and equipment description from current session hash """
    # проверка наличия оборудования с таким именем в базе
    status = False

    db_con_var = db.DbConnection()
    # TODO:: придумать как ипользовать session_hash
    equipment_names = db_con_var.add_element_and_get_id(table_name="apparats",
                                                        name=message_dict["apparat_name"],
                                                        apparat_description=message_dict["apparat_description"])
    equipment_id = equipment_names[0]
    status = True

    back_answer = {"status": status, "apparat_id": equipment_id, "error": "no-error"}
    return back_answer


def add_block(message_dict):
    """ add block to equipment """
    status = False

    # процессинг изображения
    image = img_ops.binary_2_image(message_dict["src"])
    message_dict["width"], message_dict["height"] = img_ops.get_image_params(image)

    db_con_var = db.DbConnection()

    # запись блока в бд, получение id добавленного блока 
    block_names = db_con_var.add_element_and_get_id(table_name="apparat_blocks",
                                                    apparat_id=message_dict["apparat_id"],
                                                    name=message_dict["block_name"],
                                                    width=message_dict["width"],
                                                    height=message_dict["height"])
    
    block_id = block_names[0]

    # сохранение изображения
    block_path = f'./../eed-frontend/public/apparats/{message_dict["apparat_id"]}_{block_id}.png'
    img_ops.save_image(image, block_path)
    where_statement = f"id={block_id}"

    db_con_var.update_rows(table_name="apparat_blocks", where_statement=where_statement,
                           src=block_path)

    status = True

    back_answer = {"status": status, "block_id": block_id, "error": "no-error"}
    return back_answer


def find_block(block_name):
    """ tries to find block by name in table "apparat_blocks" """
    db_con_var = db.DbConnection()
    where_statement = f"name='{block_name}'".format(block_name=block_name)
    blocks_names = db_con_var.get_data_with_where_statement(table_name="apparat_blocks", name=block_name,
                                                            where_statement=where_statement)
    is_block_added = len(blocks_names) > 0
    return is_block_added


def find_equipment(equipment_name):
    """ tries to find equipment by name in table "apparats" """
    db_con_var = db.DbConnection()
    where_statement = f"name='{equipment_name}'".format(equipment_name=equipment_name)
    equipment_names = db_con_var.get_data_with_where_statement(table_name="apparats", name=equipment_name,
                                                               where_statement=where_statement)
    is_equipment_added = len(equipment_names) > 0
    return is_equipment_added
