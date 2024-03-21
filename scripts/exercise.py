""" handle exercises:
    choose exercise
    training
    exam
"""

import scripts.dbconnection as db


def choose_exercise_type(message_dict):
    """ define exercise type """
    if "is_training" in message_dict:
        configure_exercise(message_dict)



def configure_exercise(message_dict):
    """ first apparat request: configure exercise data"""

    db_con_var = db.DbConnection()
    table_name = "sessions"
    session_hash = message_dict["session_hash"]
    session_exercise_id = message_dict["map_id"]

    db_con_var.add_values_and_get_id(table_name=table_name, user_id=0, session_hash=session_hash,
                                     session_exercise_id=session_exercise_id)

    # front->back:
    # {
    #     "session_hash": string,
    #     "apparat_id": integer,
    #     "map_id": integer,
    #     "is_training": bool
    # }




