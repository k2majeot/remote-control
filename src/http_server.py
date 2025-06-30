from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                file_path = os.path.join(SCRIPT_DIR, "index.html")
                with open(file_path, "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)

            elif self.path == "/config.json":
                file_path = os.path.join(SCRIPT_DIR, "config.json")
                with open(file_path, "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(content)

            elif self.path == "/send-input.js":
                file_path = os.path.join(SCRIPT_DIR, "send-input.js")
                with open(file_path, "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "application/javascript")
                self.end_headers()
                self.wfile.write(content)

            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            error_msg = f"500 Internal Server Error: {str(e)}"
            self.wfile.write(error_msg.encode())
            print(f"Error while serving {self.path}: {e}")

CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
    NETWORK = CONFIG["network"]

server = HTTPServer(("0.0.0.0", NETWORK["frontend_port"]), MyHandler)
print(f"Serving at http://localhost:{NETWORK['frontend_port']}")
server.serve_forever()
