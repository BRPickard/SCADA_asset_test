"""Serve the simple local HTML page for the SCADA Asset Enrichment MVP."""

from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8080
WEB_DIR = Path(__file__).resolve().parent / "web"


class StaticHandler(SimpleHTTPRequestHandler):
    """Serve static files from the web directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)


if __name__ == "__main__":
    print(f"Serving {WEB_DIR} at http://localhost:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), StaticHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
