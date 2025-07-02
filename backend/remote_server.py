import asyncio
import json
import threading
import queue
import ctypes
from ctypes import wintypes
from pathlib import Path
import ssl

import websockets

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
CONFIG_PATH = BASE_DIR / "server_config.json"

with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
    WHITELIST = set(CONFIG.get("whitelist", []))
    HOST = CONFIG.get("host", "localhost")
    PORT = CONFIG.get("remote_port", 9000)
    CERT_FILE = CONFIG.get("certfile")
    KEY_FILE = CONFIG.get("keyfile")

SSL_CONTEXT = None
if CERT_FILE and KEY_FILE:
    SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    SSL_CONTEXT.load_cert_chain(CERT_FILE, KEY_FILE)

SCROLL_FACTOR = 120

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


def scroll_mouse(dy):
    delta = int(-dy * SCROLL_FACTOR)
    user32.mouse_event(0x0800, 0, 0, delta, 0)


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
        elif item["type"] == "down":
            user32.mouse_event(0x0002, 0, 0, 0, 0)
        elif item["type"] == "up":
            user32.mouse_event(0x0004, 0, 0, 0, 0)
        elif item["type"] == "right_press":
            user32.mouse_event(0x0008, 0, 0, 0, 0)
            user32.mouse_event(0x0010, 0, 0, 0, 0)
        elif item["type"] == "scroll":
            scroll_mouse(item["dy"])
        input_queue.task_done()


def start_worker():
    threading.Thread(target=input_worker, daemon=True).start()


async def handler(websocket):
    ip = websocket.remote_address[0]
    if WHITELIST and ip not in WHITELIST:
        print(f"Rejected connection from {ip}")
        await websocket.close()
        return
    try:
        async for msg in websocket:
            try:
                data = json.loads(msg)
                if data["type"] == "move":
                    dx = data.get("dx", 0)
                    dy = data.get("dy", 0)
                    input_queue.put({"type": "move", "dx": dx, "dy": dy})
                elif data["type"] == "key":
                    input_queue.put({"type": "key", "key": data.get("key", "")})
                elif data["type"] == "press":
                    input_queue.put({"type": "press"})
                elif data["type"] == "down":
                    input_queue.put({"type": "down"})
                elif data["type"] == "up":
                    input_queue.put({"type": "up"})
                elif data["type"] == "right_press":
                    input_queue.put({"type": "right_press"})
                elif data["type"] == "scroll":
                    input_queue.put({"type": "scroll", "dy": data.get("dy", 0)})
            except json.JSONDecodeError:
                print("Invalid JSON")
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Connection from {ip} closed")
    except (websockets.exceptions.ConnectionClosedError, ConnectionResetError, OSError) as e:
        print(f"Connection from {ip} lost: {e}")


async def main():
    protocol = "wss" if SSL_CONTEXT else "ws"
    print(f"WebSocket server running at {protocol}://{HOST}:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT, ssl=SSL_CONTEXT):
        await asyncio.Future()


if __name__ == "__main__":
    start_worker()
    asyncio.run(main())
