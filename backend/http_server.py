from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
from pathlib import Path
import ssl

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
FRONTEND_DIR = BASE_DIR / "frontend"

CONFIG_PATH = BASE_DIR / "server_config.json"
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
    WHITELIST = set(CONFIG.get("whitelist", []))
    FRONTEND_PORT = CONFIG.get("frontend_port", 8000)
    CERT_FILE = CONFIG.get("certfile")
    KEY_FILE = CONFIG.get("keyfile")


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if WHITELIST and self.client_address[0] not in WHITELIST:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden")
            return
        try:
            path = self.path.lstrip("/") or "index.html"

            if path == "settings.json":
                file_path = FRONTEND_DIR / "settings.json"
                with open(file_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                settings["host"] = CONFIG.get("host", settings.get("host", "localhost"))
                settings["remote_port"] = CONFIG.get("remote_port", settings.get("remote_port", 9000))
                settings["secure"] = bool(CERT_FILE and KEY_FILE)
                content = json.dumps(settings).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(content)
                return

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
scheme = "http"
if CERT_FILE and KEY_FILE:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    scheme = "https"
print(f"Serving at {scheme}://localhost:{FRONTEND_PORT}")
server.serve_forever()
