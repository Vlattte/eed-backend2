# connection
import websockets
import asyncio

# data structures
import json

# handlers
import scripts.request_handler as req


async def handler(websocket):

    # message = await websocket.recv()
    message = json.dumps("{\"hui\": 47}")
    print("message: ")
    print(message)
    # request = json.loads(message)
    return_json = req.request_handler(message)
    await websocket.send(json.dumps(return_json, ensure_ascii=False))


async def main():
    print("SERVER ON")
    async with websockets.serve(handler, "", 8083):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
