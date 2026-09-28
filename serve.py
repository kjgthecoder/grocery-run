#!/usr/bin/env python3
"""Static server for the Grocery Run PWA.

    python3 serve.py [port]        # default 8000, binds 0.0.0.0

Plain http.server with three fixes it needs to host a PWA:
  * "/" serves index.html, so manifest start_url "." works
  * explicit MIME types for .json / .js (never trust the system mime table)
  * no-store on the HTML and sw.js, so the browser HTTP cache can't hide
    a version bump from you
"""
import http.server
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = "index.html"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"   # keep-alive; ngrok is happier with it

    extensions_map = {
        "": "application/octet-stream",
        ".html": "text/html; charset=utf-8",
        ".js": "text/javascript",
        ".json": "application/json",
        ".webmanifest": "application/manifest+json",
        ".css": "text/css; charset=utf-8",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".txt": "text/plain; charset=utf-8",
        ".md": "text/plain; charset=utf-8",
    }

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def translate_path(self, path):
        p = super().translate_path(path)
        if os.path.isdir(p):
            index = os.path.join(p, "index.html")
            return index if os.path.exists(index) else os.path.join(p, APP)
        return p

    def end_headers(self):
        self.send_header("Service-Worker-Allowed", "/")
        if self.path.rstrip("/") == "" or self.path.endswith((".html", "sw.js", ".json")):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s  %s\n" % (self.log_date_time_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        print("Grocery Run  ->  http://localhost:%d/" % PORT)
        print("serving %s   (ctrl-c to stop)" % ROOT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
