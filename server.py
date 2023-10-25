# connection
import websockets
import asyncio

# data structures
import json

# handlers
import scripts.request_handler as req


async def handler(websocket):
    message = await websocket.recv()
    # message = json.dumps("{\"operation\": \"addApparat\", \"session_hash\": \"47\", \"apparat_name\": \"P320-OO\" }")
    request = json.loads(message)
    return_json = req.request_handler(message)
    await websocket.send(json.dumps(return_json, ensure_ascii=False), max_size=1000000)


def test_handler():
    message = json.loads("{\"operation\": \"addConditionPositions\", \"session_hash\": \"47\", \"element_id\": 1,"
                         "\"conditions\": {\"condition_id\"}"
                         "\"element\": {\"type\": \"rotator\", \"src\":  \"beb\"}}")
    answer_json = req.request_handler(message)
    print(answer_json)
    return answer_json


async def main():
    print("SERVER ON")
    # test_handler()
    async with websockets.serve(handler, "", 8083, max_size=1000000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
