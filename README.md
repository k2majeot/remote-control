# Remote Control

This project provides a simple remote control mechanism for a Windows machine using a WebSocket server and a small touch friendly web client.

## Features

- **backend/remote_server.py** – listens for WebSocket messages and converts them into mouse and keyboard events via the Windows API.
- **backend/http_server.py** – serves the static frontend and enforces an IP whitelist.
- **frontend/js/send-input.js** – communicates with the remote server from the browser and sends touch or keyboard input.
- A scroll bar on the right side sends scroll events when dragged.
- Two finger tap on the touch area triggers a right click.
- Long press and drag simulates a mouse drag.

## Quick start

1. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `server_config.json` file in the base directory (the same folder as this README) and configure the servers:
   ```json
   {
     "host": "localhost",
     "remote_port": 9000,
     "frontend_port": 8000,
     "whitelist": ["127.0.0.1"]
   }
   ```
3. Adjust the frontend settings in `frontend/settings.json`:
   ```json
   {
     "sensitivity": 4,
     "throttle_ms": 16,
     "scroll_sensitivity": 1,
     "press_threshold_ms": 500
   }
   ```
   The `host` and `remote_port` values are automatically injected from
   `server_config.json` when the settings are served.
4. Start the servers (Windows):
   ```cmd
   remote.cmd
   ```
   This runs `backend/run_servers.py` which launches both `remote_server.py` and `http_server.py` and prints their logs in the current console.
   On other platforms run them manually:
   ```bash
   python backend/remote_server.py
   python backend/http_server.py
   ```
5. Open a browser to `http://<host>:<frontend_port>` on your phone or another device to control the machine running the servers.

## Notes

- The `remote_server.py` script relies on the Windows user32 API and must be run on a Windows machine.
- The `http_server.py` can be served from any environment that can reach the WebSocket server.

## Credits

[Remote-control icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/remote-control "remote-control icons")
