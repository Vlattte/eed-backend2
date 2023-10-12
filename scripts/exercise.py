""" handle exercises:
    choose exercise
    training
    exam
"""

# import db_connection

def choose_exercise_type(message_dict):
    """ define exercise type """
    if "is_training" in message_dict:
        configure_exercise(message_dict)


def configure_exercise(message_dict):
    """ first apparat request: configure exercise data"""
    # front->back:
    # {
    #     "session_hash": string,
    #     "apparat_id": integer,
    #     "map_id": integer,
    #     "is_training": bool
    # }
    return



