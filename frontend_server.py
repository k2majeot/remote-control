from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                with open("index.html", "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)

            elif self.path == "/config.json":
                with open("config.json", "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(content)

            elif self.path == "/send-input.js":
                with open("send-input.js", "rb") as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "application/javascript")
                self.end_headers()
                self.wfile.write(content)
                
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"500 Internal Server Error")

with open("config.json", "r") as file:
    CONFIG = json.load(file)
    NETWORK = CONFIG["network"]

server = HTTPServer(("0.0.0.0", NETWORK["frontend_port"]), MyHandler)
print(f"Serving at http://localhost:{NETWORK['frontend_port']}")
server.serve_forever()
