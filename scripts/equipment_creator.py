""" manage equipment functions """

# database
import scripts.dbconnection as db


def choose_equipment_operation(message_dict):
    """ define equipment operation """


    # connection establishing
    if message_dict["operation"] == "connect":
        establish_connection(message_dict["session_hash"])
    # add equipment
    elif message_dict["operation"] == "addApparat":
        add_equipment_name(message_dict)
    # add block
    elif message_dict["operation"] == "addBlock":
        add_block(message_dict)
    #
    # elif message_dict["operation"] == "add":


#   message from front:
# "session_hash": string,
# "operation": "connect"
#   answer to front:
# status - статус записи в БД
def establish_connection(session_hash):
    """ save new session_hash """
    # для таблицы "sessions" нужен id пользователя (user_id) =>
    #   - сначала проверяем есть ли уже такой пользователь в таблице "sessions"
    #   - если есть то получаем user_id
    #   - иначе создаем пользователя в таблице "user_data" и оттуда берем user_id

    #fixme:: сложная и нагруженная функция
    #TODO:: удалять session hash отовсюду, когда чел выходит
    db_con_var = db.DbConnection()
    user_id = find_user_id(session_hash)

    # если нет такого пользователя, то добавляем
    # и получаем id этого пользователя по логину (????)
    if user_id == -1:
        user_id = create_new_user()

    # добавляем новую сессию для полученного id пользователя (user_id)
    db_con_var.add_elements(table_name="sessions", session_hash=session_hash, session_exercise_id=-1)

    back_answer = "{\"status\": true}"
    return back_answer

def create_new_user(login="student", password="123", role=1):
    db_con_var = db.DbConnection()
    db_con_var.add_elements(table_name="user_data", login=login, role=1, password=password)
    user_data = db_con_var.get_data_with_where(table_name="user_data", where_statement="login", user_id="user")
    return user_data["id"]


def find_user_id(session_hash):
    """ tries to find user by session_hash in table "sessions" """
    db_con_var = db.DbConnection()
    is_user_found = True

    user_data = db_con_var.get_data_request(table_name="sessions", session_hash=session_hash)
    if session_hash in user_data:
        user_id = user_data[session_hash]
        return user_id
    return -1


def find_equipment(equipment_name):
    """ tries to find equipment by name in table "apparats" """
    db_con_var = db.DbConnection()
    status = db_con_var.get_data(table_name="apparats", name=equipment_name)
    return status


#   message from front:
# "session_hash": string,
# "apparat_name": string,
# "apparat_description": string,
# "operation": "addApparat"
def add_equipment_name(message_dict):
    """ save equipment name and equipment description from current session hash """
    equipment_added = find_equipment(message_dict["apparat_name"])

    back_answer = "{\"status\": {equipment_added}}}".format(equipment_added)
    return back_answer


def add_block(message_dict):
    """ add block """

    return


