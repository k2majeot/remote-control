import asyncio
import websockets
import json
import threading
import queue
import ctypes
from ctypes import wintypes
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
    NETWORK = CONFIG["network"]
    SETTINGS = CONFIG["settings"]

SENSITIVITY = SETTINGS.get("sensitivity", 4)
PORT = NETWORK.get("remote_port", 9000)

user32 = ctypes.WinDLL("user32", use_last_error=True)

input_queue = queue.Queue()

SPECIAL_KEYS = {
    "Backspace": 0x08,
    "Tab": 0x09,
    "Enter": 0x0D,
    "Shift": 0x10,
    "Control": 0x11,
    "Alt": 0x12,
    "Escape": 0x1B,
    "Space": 0x20,
    "ArrowLeft": 0x25,
    "ArrowUp": 0x26,
    "ArrowRight": 0x27,
    "ArrowDown": 0x28,
    "Delete": 0x2E,
}

def move_mouse(dx, dy):
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    user32.SetCursorPos(pt.x + int(dx), pt.y + int(dy))

def press_key(key: str):
    if len(key) == 1:
        vk = user32.VkKeyScanW(ord(key))
    elif key in SPECIAL_KEYS:
        vk = SPECIAL_KEYS[key]
    else:
        print(f"Unsupported key: {key}")
        return
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, 2, 0)

def input_worker():
    while True:
        item = input_queue.get()
        if item["type"] == "move":
            move_mouse(item["dx"], item["dy"])
        elif item["type"] == "key":
            press_key(item["key"])
        elif item["type"] == "press":
            user32.mouse_event(0x0002, 0, 0, 0, 0)
            user32.mouse_event(0x0004, 0, 0, 0, 0)
        input_queue.task_done()

threading.Thread(target=input_worker, daemon=True).start()

async def handler(websocket):
    async for msg in websocket:
        try:
            data = json.loads(msg)
            if data["type"] == "move":
                dx = data.get("dx", 0) * SENSITIVITY
                dy = data.get("dy", 0) * SENSITIVITY
                input_queue.put({"type": "move", "dx": dx, "dy": dy})
            elif data["type"] == "key":
                input_queue.put({"type": "key", "key": data.get("key", "")})
            elif data["type"] == "press":
                input_queue.put({"type": "press"})
        except json.JSONDecodeError:
            print("Invalid JSON")

async def main():
    print(f"WebSocket server running at ws://{NETWORK['host']}:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
