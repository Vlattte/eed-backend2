'''
 request handler file

'''

# data structures
import json


def request_handler(message):
    message_dict = json.loads(message)

    # is request == authorization
    if "login" in message_dict:
        return


