# connection
import websockets
import asyncio

# data structures
import json

# handlers
import scripts.request_handler as req


from fastapi import FastAPI, WebSocket
import uvicorn


app = FastAPI()


def send_format(json_data):
    return json.dumps(json_data, ensure_ascii=False)


async def handler(websocket):
    # получаем сообщение от клиента
    message = await websocket.recv()
    print("front message:\n", message)

    # отправляем сообщение, что приняли сообщение в обработку
    return_json = {"process_status": "processing"}
    await websocket.send(send_format(return_json))

    # преобразуем json к словарю для удобной обработки
    request = dict(json.loads(message))
    return_json = req.request_handler(request)
    # if return_json:
        # return_json["process_status"] = "done"
    print("\t[LOG] data for front: ", return_json)

    # отправляем результат обработки
    await websocket.send(send_format(return_json))


def test_handler(message_type):
    message = {"is_training": True, "session_hash": 4747, "apparat_id": 1, "map_id": 1}

    # message = {"operation": "connect", "session_hash": "47", 'apparat_id': 1, 'block_id': 2}


    src = "data:image/png;base64,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"

    # message = json.loads("{\"operation\": \"loadElements\", \"session_hash\": \"47\",  \"apparat_id\": 1, \"block_id\":3,"
    #                      "\"element\": {\"type\": \"penis\", \"src\": "
    #                      "\"data:image/png;base64,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\"}}")

    # message = json.loads("{\"operation\": \"addElement\", \"session_hash\": \"47\",  \"apparat_id\": 1, \"block_id\":3,"
    #                      "\"element_id\":  6,\"element\": {\"type\": \"lever\", \"src\": "
    #                      "\"data:image/png;base64,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\"}}")

    # message = {"operation": "addCondition", "session_hash": "47",  "element_id": 5}
    # message = {'operation': 'addConditionPositions', 'session_hash': '47', 'apparat_id': 1, 'block_id': 2, 'condition_id':  4, 
    #      'positions':[{'position':{'angle': 3, 'src': {src} }, 'order': 0}, {'position': {'angle': 55, 'src': src }, 'order': 1}, {'position': {'angle': 99, 'src': src }, 'order': 2}], 'element': {'type': 'penis', 'src': {src} } }

    connection_message = {"operation": "connect", "session_hash": "47", 'apparat_id': 1, 'block_id': 2}
    add_apparat_message = {"operation": "addApparat", "session_hash": "47", "apparat_name": "some_apparat_1",
                           "apparat_description": "описание аппарата 1"}
    add_block_message = {"operation": "addBlock", "session_hash": "47", 'apparat_id': 3, #block_id = 3
                         'block_name': "блок 1 аппарата 1", "src": src}
    add_element_message = {"operation": "addElement", "session_hash": "47",
                           "element": {"type": "кнока тип 1",
                                       "src": src}}
    add_condition_message = {"operation": "addCondition", "session_hash": "47", "element_id": 14}

    add_condition_positions_message = {
                                       "operation": "addConditionPositions", "session_hash": "47",
                                       "element_id": 14, "condition_id": 6,
                                       "positions": [
                                           {"positions": {"angle": 11},
                                            "order": 0,
                                            "src": "путь до картиночки"},
                                           {"positions": {"angle": 12},
                                            "order": 1,
                                            "src": "путь до картиночки"},
                                           {"positions": {"angle": 13},
                                            "order": 2,
                                            "src": "путь до картиночки"}
                                       ]
                                       }

    # if message_type == 'connect':
    #     message = connection_message
    # elif message_type == 'addApparat':
    #     message = add_apparat_message
    # elif message_type == 'addBlock':
    #     message = add_block_message
    # elif message_type == 'addElement':
    #     message = add_element_message
    # elif message_type == 'addCondition':
    #     message = add_condition_message
    # elif message_type == 'addConditionPositions':
    #     message = add_condition_positions_message

    # message = {"operation": "addElement", "session_hash": "47", "element": {"type": "penis", "src": src}}

    # _str = json.dumps(_str)
    # message = json.loads(_str)

    answer_json = req.request_handler(message)
    print(answer_json)
    return answer_json


@app.websocket('/')
async def main(websocket: WebSocket):   
    print("SERVER ON") 
    await websocket.accept()
    while True:

        # получаем сообщение от клиента
        message = await websocket.receive_json()

        # преобразуем json к словарю для удобной обработки
        request = dict(message)
        print("\n\n\t[DATA FROM FRONT] ", request)
        answer = req.request_handler(request)
        print("\t[DATA FOR FRONT] ", answer)

        await websocket.send_json(answer)
        # команда запуска
        # uvicorn server:app --reload --port 8083


if __name__ == "__main__":
    print("SERVER ON")
    asyncio.run(main())    
    # uvicorn.run(app, host="localhost", port=8083)
