# connection
import websockets
import asyncio

# data structures
import json

# handlers
import scripts.request_handler as req


async def handler(websocket):

    # message = await websocket.recv()
    message = json.dumps("{\"operation\": \"connect\", \"session_hash\": \"47\" }")
    print("message: ")
    print(message)
    # request = json.loads(message)
    return_json = req.request_handler(message)
    await websocket.send(json.dumps(return_json, ensure_ascii=False))

def test_handler():
    message = json.loads("{\"operation\": \"connect\", \"session_hash\": \"47\" }")
    print("message: ")
    print(message)
    # request = json.loads(message)
    return_json = req.request_handler(message)


async def main():
    print("SERVER ON")
    test_handler()
    # async with websockets.serve(handler, "", 8083):
    #     await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
