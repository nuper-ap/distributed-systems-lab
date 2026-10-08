import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            unhealthy = os.getenv("UNHEALTHY", "false").lower() == "true"

            if unhealthy:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"status": "error"}).encode()
                )
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "ok"}).encode()
            )
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass


server = HTTPServer(("0.0.0.0", 9000), Handler)

print("Dependency listening on port 9000")

server.serve_forever()
