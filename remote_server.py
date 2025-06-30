import asyncio
import websockets
import json
import threading
import queue
import ctypes
import ctypes.wintypes

# Load config
with open("config.json", "r") as file:
    CONFIG = json.load(file)
    NETWORK = CONFIG["network"]
    SETTINGS = CONFIG["settings"]

SENSITIVITY = SETTINGS.get("sensitivity", 4)
PORT = NETWORK.get("remote_port", 9000)

# Set up Windows API
user32 = ctypes.windll.user32

def move_mouse(dx, dy):
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    user32.SetCursorPos(pt.x + int(dx), pt.y + int(dy))

# Input queue
input_queue = queue.Queue()

def input_worker():
    while True:
        dx, dy = input_queue.get()
        move_mouse(dx, dy)
        input_queue.task_done()

threading.Thread(target=input_worker, daemon=True).start()

# WebSocket handler
async def handler(websocket):
    async for msg in websocket:
        try:
            data = json.loads(msg)
            dx = data.get("dx", 0) * SENSITIVITY
            dy = data.get("dy", 0) * SENSITIVITY
            input_queue.put((dx, dy))
        except json.JSONDecodeError:
            print("Invalid JSON received")

# WebSocket server
async def main():
    print(f"WebSocket server running at ws://{NETWORK['host']}:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
