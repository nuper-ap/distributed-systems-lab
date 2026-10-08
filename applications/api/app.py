from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
import json
import os


DEPENDENCY_URL = os.getenv(
    "DEPENDENCY_URL",
    "http://dependency:9000/health",
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.respond(200, {
                "status": "ok",
                "hostname": os.uname().nodename,
            })

        elif self.path == "/dependency":
            self.check_dependency()

        else:
            self.send_response(404)
            self.end_headers()

    def check_dependency(self):
        try:
            with urlopen(DEPENDENCY_URL, timeout=2) as response:
                dependency_response = json.loads(response.read())

            self.respond(200, {
                "status": "ok",
                "dependency": dependency_response,
            })

        except Exception as exc:
            self.respond(503, {
                "status": "error",
                "dependency": "unavailable",
                "error": str(exc),
            })

    def respond(self, status_code, payload):
        body = json.dumps(payload).encode()

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = HTTPServer(("0.0.0.0", 8080), Handler)

print("API listening on port 8080")

server.serve_forever()
