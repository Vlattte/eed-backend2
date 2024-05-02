""" функции для валидации действий пользователя """

import scripts.dbconnection as db
import scripts.db_fast_scripts as db_script

def validate_step(message_dict, table_step):
    """ проверка переданных данных на правильность """
    session_hash = message_dict["session_id"]
    db_con_var = db.DbConnection()
    
    # флаги для статуса шага
    status_flags = {"attempt_fail": False,  # fail
                    "step_finish": False,   # validation
                    "stage_finish": False,  # finish
                    "status": "progres",    # progress - не убирать подсветку, correct - убрать подсветку и удалить подшаг
                    "array_actions": [ {"name": "nan"} ],     # действия после подшага
                    "is_norm_finish": False # кончился ли норматив
                    } 

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
        print(f"\t[BAD MOVE] элемента с id = {message_dict['id']} не найдено")
        status_flags["attempt_fail"] = True
        return status_flags

    # совпадает ли порядок шага, если влияет порядок
    if interected_el["sub_step_order"] != sub_step_order and sub_step_order != -1:
        # print(f"\t[BAD MOVE] не совпал номер шага: под шаг в базе = {interected_el["sub_step_order"]}, порядок элемента = {sub_step_order}")
        status_flags["attempt_fail"] = True  # TODO проверка на число ошибок, пока 1 ошибка == смерть
        return status_flags

    ####### STATUS == STATUS #######

    # если порядок верный и теперь элемент в нужном положении => снимаем подсветку    
    if interected_el["correct_value"] == str(message_dict["currentValue"]):
        print("\t[GOOD MOVE] status == CORRECT")
        # убираем подсветку
        status_flags["status"] = "correct"
        
        # добавляем действия после подшага из таблицы sub_step_action
        where_statement=f"sub_step_id={interected_el['id']}"
        sub_step_actions = db_con_var.get_data_with_where_statement(
            table_name="sub_step_actions",
            where_statement=where_statement,
            is_return_arr=True
        )

        # если есть действия после подшага отсылаем их на фронт
        if len(sub_step_actions) > 0:            
            status_flags["array_actions"].clear()
            for action in sub_step_actions:                  
                action_to_append = {
                    "apparat_id": action["apparat_id"],
                    "action_id": action["element_id"],
                    "action_value": action["correct_value"],
                    "tag": action["tag"]
                }
                status_flags["array_actions"].append(action_to_append)            
        
        # удаляем запись об этом подшаге, так как он в нужном положении
        where_statement = f"id={interected_el['id']}"
        db_con_var.delete_data_where(
            table_name="sub_steps", where_statement=where_statement
        )         

    ####### ATTEMPT_FAIL == FAIL #######

    # если попытка провалена, удаляем подшаги из таблицы
    step_id = db_script.get_step_id(session_hash)
    if status_flags["attempt_fail"]:
        print("\t[BAD MOVE] sub steps deleted")
        where_statement = f"step_id={step_id}"
        db_con_var.delete_data_where(
            table_name="sub_steps", where_statement=where_statement
        )
    
    ####### STEP_FINISH == VALIDATION #######

    # проверить, закончились ли подшаги в текущем шаге        
    where_statement = f"step_id={step_id}"
    cur_sub_steps = db_con_var.get_data_with_where_statement(
        table_name="sub_steps", where_statement=where_statement
    )

    # увеличиваем номер шага, если подшаги кончились
    if len(cur_sub_steps) == 0:
        status_flags["step_finish"] = True
        print("\t[LOG] STEP FINISHED")

    ####### STAGE FINISHED == FINISH #######
    # если шаг кончился, то переходим на следующий шаг, иначе увеличиваем номер подшага
    step_inc = False
    if status_flags["step_finish"]:
        step_inc = True

        # если кончился шаг и count_next == 0, то stage кончился
        if table_step["count_next"] == 0:
            status_flags["stage_finish"] = True
            print("\t[LOG] STAGE FINISHED")

            # увеличиваем номер stage (потом id stage) в таблице exercises_status
            status_flags["is_norm_finish"] = increase_stage(session_hash)            
        
    # обновляем статус шага
    update_step(session_hash, step_inc)
    return status_flags

def update_step(session_hash, step_inc=True):
    """ сдвигает шаг или подшаг """
    db_con_var = db.DbConnection()
    step_id = db_script.get_step_id(session_hash)

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

def get_sub_steps(session_hash):
    """ получает массив подшагов для этого шага """
    # получаем id группы шагов
    step_id = db_script.get_step_id(session_hash)

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


def increase_stage(session_hash):
    db_con_var = db.DbConnection()

    # из таблицы "sessions" получаем session_exercise_id
    where_statement = f"session_hash='{session_hash}'"
    session_data = db_con_var.get_data_with_where_statement(
        table_name="sessions",
        where_statement=where_statement)

    # получаем номер текущего stage и номер последнего stage в карте
    where_statement = f"id={session_data['session_exercise_id']}"
    exercise_data = db_con_var.get_data_with_where_statement(
        table_name="exercises_status",
        where_statement=where_statement)
    
    # кончился ли норматив
    is_norm_finish = False
    stage_num = exercise_data["stage_id"] + 1    
    if stage_num > exercise_data["last_stage_num"]:
        is_norm_finish = True
        return is_norm_finish

    # обновляем номер stage
    where_statement = f"id={session_data['session_exercise_id']}"
    db_con_var.update_rows(
        table_name="exercises_status", 
        where_statement=where_statement,
        stage_id=stage_num)
    return is_norm_finish


def is_invalid(check_dict):
    """ проверяет является ли словарь словарем вида {"name": "nan"} """
    if check_dict == {"name": "nan"}:
        return True
    return False
