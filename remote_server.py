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
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002

def move_mouse(dx, dy):
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    user32.SetCursorPos(pt.x + int(dx), pt.y + int(dy))

def click_mouse():
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def press_key(key):
    vk = user32.VkKeyScanW(ord(key))
    if vk == -1:
        print(f"Unsupported key: {key}")
        return
    scan = user32.MapVirtualKeyW(vk & 0xFF, 0)
    user32.keybd_event(vk & 0xFF, scan, 0, 0)
    user32.keybd_event(vk & 0xFF, scan, KEYEVENTF_KEYUP, 0)

# Input queue
input_queue = queue.Queue()

def input_worker():
    while True:
        item = input_queue.get()
        if item["type"] == "move":
            move_mouse(item["dx"], item["dy"])
        elif item["type"] == "press":
            click_mouse()
        elif item["type"] == "key":
            press_key(item["key"])
        input_queue.task_done()

threading.Thread(target=input_worker, daemon=True).start()

# WebSocket handler
async def handler(websocket):
    async for msg in websocket:
        try:
            data = json.loads(msg)
            if data.get("type") == "move":
                dx = data.get("dx", 0) * SENSITIVITY
                dy = data.get("dy", 0) * SENSITIVITY
                input_queue.put({"type": "move", "dx": dx, "dy": dy})
            elif data.get("type") == "press":
                input_queue.put({"type": "press"})
            elif data.get("type") == "key":
                input_queue.put({"type": "key", "key": data.get("key", "")})
        except json.JSONDecodeError:
            print("Invalid JSON received")

# WebSocket server
async def main():
    print(f"WebSocket server running at ws://{NETWORK['host']}:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
