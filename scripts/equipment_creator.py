""" manage equipment functions """

# database
import scripts.dbconnection as db


def choose_equipment_operation(message_dict):
    """ define equipment operation """
    if message_dict["operation"] == "connect":          # connection establishing
        connection_status = establish_connection(message_dict["session_hash"])
        return connection_status
    elif message_dict["operation"] == "addApparat":     # add equipment name
        adding_equipment_status = add_equipment_name(message_dict)
        return adding_equipment_status
    elif message_dict["operation"] == "addBlock":       # add block
        add_block(message_dict)


# для таблицы "sessions" нужен id пользователя (user_id) =>
#   - сначала проверяем существует ли уже подключение в таблице "sessions"
#   - если есть то получаем user_id => соединение уже есть
#   - иначе создаем пользователя в таблице "user_data", оттуда берем user_id
#       и сохраняем данные по соединению в "sessions"
def establish_connection(session_hash):
    """ save new session_hash """
    #fixme:: сложная и нагруженная функция
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


#   message from front:
# "session_hash": string,
# "apparat_name": string,
# "apparat_description": string,
# "operation": "addApparat"
def add_equipment_name(message_dict):
    """ save equipment name and equipment description from current session hash """
    # проверка наличия оборудования с таким именем в базе
    is_equipment_in_base = find_equipment(message_dict["apparat_name"])
    status = False
    equipment_id = -1

    if not is_equipment_in_base:
        db_con_var = db.DbConnection()
        # TODO:: придумать как ипользовать session_hash
        equipment_names = db_con_var.add_element_and_get_id(table_name="apparats",
                                                         # session_hash=message_dict["session_hash"],
                                                         name=message_dict["apparat_name"],
                                                         apparat_description=message_dict["apparat_description"])
        equipment_id = equipment_names[0]
        status = True



    back_answer = {"status": status, "equipment_id": equipment_id, "error": "no-error"}
    return back_answer



def find_equipment(equipment_name):
    """ tries to find equipment by name in table "apparats" """
    db_con_var = db.DbConnection()
    where_statement = f"name='{equipment_name}'".format(equipment_name=equipment_name)
    equipment_names = db_con_var.get_data_with_where_statement(table_name="apparats", name=equipment_name,
                                                               where_statement=where_statement)
    is_equipment_added = len(equipment_names) > 0
    return is_equipment_added


def add_block(message_dict):
    """ add block """

    return


