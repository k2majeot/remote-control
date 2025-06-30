# Remote Control

This project provides a simple remote control mechanism for a Windows machine using a WebSocket server and a small touch friendly web client.

## Features
- **remote_server.py** – listens for WebSocket messages and converts them into mouse and keyboard events via the Windows API.
- **frontend_server.py** – serves the web client (`index.html` and `send-input.js`) and a `config.json` file.
- **send-input.js** – communicates with the remote server from the browser and sends touch or keyboard input.
- Touch-friendly scroll bar on the right side of the page for sending scroll events.

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
       "throttle_ms": 16
     }
   }
   ```
3. Run the WebSocket server (Windows only):
   ```bash
   python remote_server.py
   ```
4. In a separate terminal start the HTTP server:
   ```bash
   python frontend_server.py
   ```
5. Open a browser to `http://<host>:<frontend_port>` on your phone or another device to control the machine running the servers.

## Notes
- The `remote_server.py` script relies on the Windows user32 API and must be run on a Windows machine.
- The `frontend_server.py` can be served from any environment that can reach the WebSocket server.
