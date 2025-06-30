# Remote Control

This project provides a simple remote control mechanism for a Windows machine using a WebSocket server and a small touch friendly web client.

## Features
- **remote_server.py** – listens for WebSocket messages and converts them into mouse and keyboard events via the Windows API.
- **http_server.py** – serves the web client (`index.html` and `send-input.js`) and a `config.json` file.
- **send-input.js** – communicates with the remote server from the browser and sends touch or keyboard input.
- Two finger drag on the touch area sends scroll events.
- Long press and drag simulates a mouse drag.

## Quick start
1. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `config.json` file. A minimal example:
   ```json
   {
     "network": {
       "host": "localhost",
       "remote_port": 9000,
       "frontend_port": 8000
     },
    "settings": {
      "sensitivity": 4,
      "throttle_ms": 16,
      "scroll_sensitivity": 1,
      "press_threshold_ms": 500
    }
   }
   ```
3. Start the servers (Windows):
   ```cmd
   remote.cmd
   ```
   This launches both `remote_server.py` and `http_server.py`.
   On other platforms run them manually:
   ```bash
   python src/remote_server.py
   python src/http_server.py
   ```
4. Open a browser to `http://<host>:<frontend_port>` on your phone or another device to control the machine running the servers.

## Notes
- The `remote_server.py` script relies on the Windows user32 API and must be run on a Windows machine.
- The `http_server.py` can be served from any environment that can reach the WebSocket server.
