#!/usr/bin/env python3
"""ER Bed Board — Shared Backend Server
Stores patient data in a JSON file. All clients sync via REST API.
Run: python3 server.py  (listens on port 8765, all interfaces)
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
PORT = 8765


def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save(patients):
    with open(DATA_FILE, "w") as f:
        json.dump(patients, f, indent=2)


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/patients":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            data = load()
            self.wfile.write(json.dumps(data).encode())
        elif path == "/health":
            self.send_response(200)
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/patients":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                patients = json.loads(body)
                if not isinstance(patients, list):
                    raise ValueError("Must be array")
                save(patients)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "count": len(patients)}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == "__main__":
    print(f"🏥 ER Bed Board Server")
    print(f"   Local:  http://localhost:{PORT}/api/patients")
    print(f"   Health: http://localhost:{PORT}/health")
    print(f"   Data:   {DATA_FILE}")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
