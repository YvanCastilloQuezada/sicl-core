#!/usr/bin/env python3
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sicl.layout.http_api import LayoutHttpService

service = LayoutHttpService()


class Handler(BaseHTTPRequestHandler):
    def _write(self, status: int, value):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if value is not None:
            self.wfile.write(json.dumps(value, ensure_ascii=False).encode())

    def do_GET(self):
        status, value = service.handle("GET", self.path)
        self._write(status, value)

    def do_DELETE(self):
        status, value = service.handle("DELETE", self.path)
        self._write(status, value)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        status, value = service.handle("POST", self.path, payload)
        self._write(status, value)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print(f"RFC-034.1 layout HTTP server listening on 0.0.0.0:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
