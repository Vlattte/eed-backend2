""" request handler file """

# data structures
import json

# handlers
from scripts.exercise import choose_exercise_type
import scripts.equipment_creator as equipment_creator

# elements scripts
import scripts.elements_handler as elements_handler
from scripts import norm_creation


# TODO вынести в сервер ??
def request_handler(message_dict):
    """ decide which module will handle message """
    # message_dict = json.dumps(message_dict)

    # is request == authorization
    # NOT USED
    if "login" in message_dict:
        return

    # is request == exercise
    if "session_id" in message_dict:
        answer = choose_exercise_type(message_dict)
        return answer

    # if request == equipment_creator
    if "operation" in message_dict:
        answer = choose_equipment_operation(message_dict)
        return answer

def choose_equipment_operation(message_dict):
    """ define equipment operation """
    if message_dict["operation"] == "connect":          # connection establishing
        connection_status = equipment_creator.establish_connection(message_dict["session_hash"])
        return connection_status
    elif message_dict["operation"] == "addApparat":     # add equipment name
        adding_equipment_status = equipment_creator.add_equipment_name(message_dict)
        return adding_equipment_status
    elif message_dict["operation"] == "addBlock":       # add block
        adding_block_status = equipment_creator.add_block(message_dict)
        return adding_block_status
    # TODO протестить
    elif message_dict["operation"] == "loadElements":
        loading_elements_status = elements_handler.load_elements(message_dict)
        print(loading_elements_status)
        return loading_elements_status
    elif message_dict["operation"] == "addElement":
        adding_elements_status = elements_handler.add_element(message_dict)
        return adding_elements_status
    elif message_dict["operation"] == "addCondition":
        adding_condition_status = elements_handler.add_condition(message_dict)
        return adding_condition_status
    # TODO протестить
    elif message_dict["operation"] == "addConditionPositions":
        adding_positions_status = elements_handler.add_positions_to_condition(message_dict)
        return adding_positions_status
    elif message_dict["opetation"] == "getApparatConfig":
        apparat_config = norm_creation.get_apparat_config(message_dict["apparat_name"])
        return apparat_config

    else:
        print("UNKNOWN OPERATION")
        return {"error": "unknown-operation"}

