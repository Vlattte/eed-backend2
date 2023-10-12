""" manage equipment functions """

# database
import db_connection

def choose_equipment_operation(message_dict):
    """ define equipment operation """

    # connection establishing
    if message_dict["operation"] == "connect":
        establish_connection(message_dict["session_hash"])
    # add equipment
    elif message_dict["operation"] == "addApparat":
        add_equipment(message_dict)
    # add block
    elif message_dict["operation"] == "addBlock":
        add_block(message_dict)
    #
    # elif message_dict["operation"] == "add":


def establish_connection(session_hash):
    """ save new session_hash """
    db_connection.add_elements("sessions", session_hash=session_hash)

def add_equipment(message_dict):
    """ add equipment """
    
    return


def add_block(message_dict):
    """ add block """

    return


