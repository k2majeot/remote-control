from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import mimetypes

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "public"))

CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
    NETWORK = CONFIG["network"]
    WHITELIST = set(NETWORK.get("whitelist", []))


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if WHITELIST and self.client_address[0] not in WHITELIST:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden")
            return

        try:
            path = self.path.lstrip("/") or "index.html"
            file_path = os.path.join(PUBLIC_DIR, path)

            if os.path.isfile(file_path):
                content_type, _ = mimetypes.guess_type(file_path)
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


server = HTTPServer(("0.0.0.0", NETWORK["frontend_port"]), MyHandler)
print(f"Serving at http://localhost:{NETWORK['frontend_port']}")
server.serve_forever()
