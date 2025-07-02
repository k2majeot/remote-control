from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
FRONTEND_DIR = BASE_DIR / "frontend"

CONFIG_PATH = BASE_DIR / "server_config.json"
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
    WHITELIST = set(CONFIG.get("whitelist", []))
    FRONTEND_PORT = CONFIG.get("frontend_port", 8000)


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if WHITELIST and self.client_address[0] not in WHITELIST:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden")
            return
        try:
            path = self.path.lstrip("/") or "index.html"
            file_path = FRONTEND_DIR / path
            if file_path.is_file():
                content_type, _ = mimetypes.guess_type(str(file_path))
                if content_type is None:
                    content_type = "application/octet-stream"
                if content_type.startswith("text/"):
                    content_type += "; charset=utf-8"
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(content)
                return
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"500 Internal Server Error: {str(e)}".encode())


server = HTTPServer(("0.0.0.0", FRONTEND_PORT), MyHandler)
print(f"Serving at http://localhost:{FRONTEND_PORT}")
server.serve_forever()
