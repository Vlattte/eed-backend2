""" request handler file """

# data structures
import json

# handlers
from exercise import choose_exercise_type
from equipment_creator import choose_equipment_operation



def request_handler(message):
    """ decide which module will handle message """
    message_dict = json.loads(message)

    # is request == authorization
    # NOT USED
    if "login" in message_dict:
        return

    # is request == exercise
    if "session_hash" in message_dict:
        choose_exercise_type(message_dict)

    # if request == equipment_creator
    if "operation" in message_dict:
        choose_equipment_operation(message_dict)
