""" handle exercises:
    choose exercise
    training
    exam
"""

import scripts.dbconnection as db
import scripts.map_parser as map_parser


def choose_exercise_type(message_dict):
    """ экзамен или тренировка"""
    # если нет session_id, то ошибка в запросе
    if "session_id" not in message_dict:
        print("\t[ERROR] no session id in message from front")
        return {"error": "no session_id"}

    session_hash = message_dict["session_id"]

    # если только начали упражнение, то обновляем данные в базе
    if "norm" in message_dict:
        print("\n[FIX DEBUG] norm")
        configure_norm(message_dict)

    # TODO добавить эту проверку, и не писать поля с подсветкой и аннотацией в ответ
    # if "is_training" in message_dict:

    return_json = training_exercise(message_dict)
    return return_json


def configure_norm(message_dict):
    """ инициализация норматива для конкретной сессии """
    try:
        # подключаемся к БД
        db_con_var = db.DbConnection()
        session_hash = message_dict["session_id"]  # хэш сессии
        map_id = message_dict["ex_id"]  # id норматива
        stage_id = message_dict["norm"]  # id упражнения в нормативе

        # получаем id для новой группы подшагов
        step_id = db_con_var.add_values_and_get_id(
            table_name="step_group_status", step_order=0, sub_step_order=0)

        # добавляем в таблицу "exercises_status" данные по началу прохождения карты
        session_exercise_id = db_con_var.add_values_and_get_id(
            table_name="exercises_status", map_id=map_id, stage_id=stage_id,
            step_id=step_id)

        # добавляем сессию в таблицу, если такой нет
        add_session(session_hash, session_exercise_id)
    except Exception as error:
        print("Ошибка в инициализации норматива:\n", error)


def training_exercise(message_dict):
    """ обрабатывает упражнение для тренировки """
    session_hash = message_dict["session_id"]

    # получаем текущий шаг пользователя
    table_step = map_parser.get_next_step(session_hash)

    # записываем все подшаги из шага в бд, если новый шаг (step, а не sub_step)
    write_substeps(session_hash, table_step)

    # формируем ответ в виде словаря
    answer = create_default_answer(table_step)
    answer["session_id"] = session_hash

    # получаем эталонные данные по шагу и исправляем флаги в словаре ответа answer
    status_flags = validate_step(message_dict)
    answer["finish"] = status_flags["stage_finish"]
    answer["status"] = status_flags["status"]
    answer["validation"] = status_flags["step_finish"]
    answer["fail"] = status_flags["attempt_fail"]

    print("\t[DEBUG] table_step: ", table_step)
    # проверяем, кончился ли stage
    if answer["validation"]:
        # если кончился шаг и count_next == 0, то stage кончился
        if table_step["count_next"] == 0:
            answer["is_norm_finish"] = True  

    # 

    answer.update(status_flags)
    
    return answer


def write_substeps(session_hash, cur_step):
    """ пишет все подшаги из текущего подшага в бд """
    # получаем id группы подшагов
    step_id = get_step_id(session_hash)

    # проверяем, нужно ли записывать новые подшаги (если еще есть подшаги, то не надо)
    db_con_var = db.DbConnection()
    where_statement = f"step_id={step_id}"
    prev_sub_steps = db_con_var.get_data_with_where_statement(
        table_name="sub_steps", where_statement=where_statement)
    print("\t[DEBUG] prev_sub_steps", prev_sub_steps)
    
    # TODO если пусто, то получаем словарь "name": "nan"
    # TODO переделать, так как проверять тип это ужас
    if len(prev_sub_steps) > 0:
            return  # ничего не пишем, т.к. прошлый шаг еще не кончился

    # если нет под шагов в карте, то и писать нечего
    zero_sub_step = cur_step["sub_steps"][0]
    if "name" in zero_sub_step:
        if zero_sub_step["name"] == "nan":
            return

    # TODO можно переделать на executescript
    # само добавление под шагов в таблицу sub_steps
    for sub_step in cur_step["sub_steps"]:
        # если несколько подшагов, то порядок не важен
        sub_step_order = -1
        if len(cur_step["sub_steps"]) > 0:
            sub_step_order = sub_step["sub_step"]

        db_con_var.add_values_and_get_id(
            table_name="sub_steps", step_id=step_id,
            element_id=sub_step["action_id"],
            correct_value=sub_step["current_value"],
            tag=sub_step["tag"],
            sub_step_order=sub_step_order)
    print("\t[LOG] записаны новые подшаги: ", cur_step["sub_steps"])


def add_session(session_hash, session_exercise_id):
    """ если такой сессии еще нет в таблице, то добавляем """
    if session_exists(session_hash):
        return

    # добавляем в таблицу "sessions" данные по новой сессии, если такой нет
    db_con_var = db.DbConnection()
    db_con_var.add_values_and_get_id(
        table_name="sessions", user_id=0, session_hash=session_hash,
        session_exercise_id=session_exercise_id)


def session_exists(session_hash):
    """ проверка на существовании записи о сессии """
    db_con_var = db.DbConnection()
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
        table_name="sessions", where_statement=where_statement)
    # print("\t[DEBUG] session_data", session_data)

    # если name == nan, то запрос вернул пустой массив
    if len(session_data) == 0:
        return False
    return True


def create_default_answer(cur_step):
    """ формируем ответ для фронта """
    return_json = dict()
    has_action = cur_step["count_action"] > 0

    return_json["annotation"] = cur_step["annotation"]

    # actions - применимые действия, зажечь лампы, передвинуть рычаг вручную
    return_json["has_action"] = has_action  # есть ли ответные дейтсвия (зажечь лампу и т.п.)
    return_json["count_action"] = cur_step["count_action"]  # количество ответных дейтсвий
    return_json["array_actions"] = cur_step["array_actions"]

    # next_actions - элементы для подсветки
    return_json["count_next"] = cur_step["count_next"]    # число элементов для подсветки
    return_json["next_actions"] = cur_step["next_actions"]  # массив данных по элементам для подсветки

    # рандом TODO понять надо ли
    return_json["is_random_step"] = False
    return_json["random_values"] = [{'name': 'nan'}]

    # flags - координируют переход между шагами, нормативами и т.д.
    return_json["finish"] = False           # закончен ли шаг
    return_json["status"] = "progres"       # progres - элемент еще не в свое положении, не убираем подсветку, correct - убираем подсветку, элемент в нужном положении
    return_json["validation"] = False       # закончился ли шаг
    return_json["fail"] = False             # провалена ли попытка
    return_json["is_norm_finish"] = False   # закончился ли норматив
    return return_json


def validate_step(message_dict):
    """ проверка переданных данных на правильность """
    session_hash = message_dict["session_id"]
    db_con_var = db.DbConnection()
    
    # флаги для статуса шага
    status_flags = {"attempt_fail": False,  # fail
                    "step_finish": False,   # validation
                    "stage_finish": False,  # finish
                    "status": "progres"}    # progress - не убирать подсветку, correct - убрать подсветку и удалить подшаг

    # если начальный шаг, то значений нет
    if "currentValue" not in message_dict:
        print("\t[LOG] увеличиваем шаг: был обработан начальный шаг без проверки действия пользователя")
        update_step(session_hash)
        return status_flags

    sub_steps_data, sub_step_order = get_sub_steps(message_dict["session_id"])
    
    # ищем элемент с переданным id
    interected_el = {"name": "nan"}  # подшаг из базы, у которого совпал id с тем, что нажал пользователь
    for el in sub_steps_data:   
        if el["element_id"] == message_dict["id"]:            
            interected_el = el

    # проверяем, нашли ли такой элемент среди подшагов
    if is_invalid(interected_el):
        print(f"\t[BAD MOVE] элемента с id = {message_dict["id"]} не найдено")
        status_flags["attempt_fail"] = True
        return status_flags

    # совпадает ли порядок шага, если влияет порядок
    if interected_el["sub_step_order"] != sub_step_order and sub_step_order != -1:
        # print(f"\t[BAD MOVE] не совпал номер шага: под шаг в базе = {interected_el["sub_step_order"]}, порядок элемента = {sub_step_order}")
        status_flags["attempt_fail"] = True  # TODO проверка на число ошибок, пока 1 ошибка == смерть
        return status_flags

    # если порядок верный и теперь элемент в нужном положении => снимаем подсветку
    if interected_el["correct_value"] == message_dict["currentValue"]:
        print("\t[GOOD MOVE] status == CORRECT")
        # убираем подсветку
        status_flags["status"] = "correct"
        
        # удаляем запись об этом подшаге, так как он в нужном положении
        where_statement = f"id={interected_el["id"]}"
        db_con_var.delete_data_where(
            table_name="sub_steps", where_statement=where_statement
        ) 

    # если попытка провалена, удаляем подшаги из таблицы
    step_id = get_step_id(session_hash)
    if status_flags["attempt_fail"]:
        print("\t[BAD MOVE] sub steps deleted")
        where_statement = f"step_id={step_id}"
        db_con_var.delete_data_where(
            table_name="sub_steps", where_statement=where_statement
        )

    # проверить, закончились ли подшаги в текущем шаге        
    where_statement = f"step_id={step_id}"
    cur_sub_steps = db_con_var.get_data_with_where_statement(
        table_name="sub_steps", where_statement=where_statement
    )

    # увеличиваем номер шага, если подшаги кончились
    if len(cur_sub_steps) == 0:
        status_flags["step_finish"] = True
        print("\t[LOG] STEP FINISHED")  

    # если шаг кончился, то переходим на следующий шаг, иначе увеличиваем номер подшага
    step_inc = False
    if status_flags["step_finish"]:
        step_inc = True
    update_step(session_hash, step_inc)

    return status_flags

        
def is_invalid(check_dict):
    """ проверяет является ли словарь словарем вида {"name": "nan"} """
    if check_dict == {"name": "nan"}:
        return True
    return False


def get_sub_steps(session_hash):
    """ получает массив подшагов для этого шага """
    # получаем id группы шагов
    step_id = get_step_id(session_hash)

    db_con_var = db.DbConnection()

    # получаем текущий номер шага (если порядок ообще важен)
    where_statement = f"id={step_id}"
    step_data = db_con_var.get_data_with_where_statement(
        table_name="step_group_status", where_statement=where_statement)
    
    sub_step_order = step_data["sub_step_order"]

    # получаем все данные про подшаги из текущего шага
    where_statement = f"step_id={step_id}"
    sub_steps_data = db_con_var.get_data_with_where_statement(
        table_name="sub_steps", where_statement=where_statement, is_return_arr=True)
    print("\t[LOG] sub_steps_data = ", sub_steps_data)

    return sub_steps_data, sub_step_order


def update_step(session_hash, step_inc=True):
    """ сдвигает шаг или подшаг """
    db_con_var = db.DbConnection()
    step_id = get_step_id(session_hash)

    # получаем номер шага
    where_statement = f"id={step_id}"
    step_data = db_con_var.get_data_with_where_statement(
        table_name="step_group_status", where_statement=where_statement
    )    
    step_order = step_data["step_order"]   # e.g{"step_order": 2}
    sub_step_order = step_data["sub_step_order"] + 1

    # увеличиваем шаг
    if step_inc:
        step_order += 1
    
    # если новый шаг
    if step_inc:
        sub_step_order = 0

    print(f"\t[LOG] увеличился шаг с id = {step_id}, шаг теперь {step_order}, подшаг теперь {sub_step_order}")
    where_statement = f"id={step_id}"
    db_con_var.update_rows(
        table_name="step_group_status", where_statement=where_statement,
        step_order=step_order, sub_step_order=sub_step_order
    )

def get_step_id(session_hash):
    db_con_var = db.DbConnection()

    # из таблицы "sessions" получаем session_exercise_id
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
        table_name="sessions", where_statement=where_statement)

    # из таблицы "exercises_status" статус текущего шага
    where_statement = f"id={session_data['session_exercise_id']}"
    exercises_data = db_con_var.get_data_with_where_statement(
        table_name="exercises_status", where_statement=where_statement)

    # из таблицы "step_group_status" id группы шагов
    # TODO тут кажется этот шаг лишний FIX
    where_statement = f"id={exercises_data['step_id']}"
    step_id = db_con_var.get_data_with_where_statement(
        table_name="step_group_status", where_statement=where_statement,
        id="id")
    
    return step_id["id"]

