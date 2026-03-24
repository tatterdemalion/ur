"""HTTP + Server-Sent Events server for web browser clients.

Exposes the same send() / recv() / wait_for_client() / close() interface
as ``Server``, so ``HostProtocol`` works with zero changes.
"""
from __future__ import annotations

import json
import queue
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB_PORT = 55380
_HTML = Path(__file__).parent / "web_client.html"


class WebServer:
    def __init__(self) -> None:
        self._recv_queue: queue.Queue[dict] = queue.Queue()
        self._sse_lock = threading.Lock()
        self._sse_queues: list[queue.Queue] = []
        self._latest_msg: str | None = None
        self._client_connected = threading.Event()
        self._httpd: ThreadingHTTPServer | None = None

    # ── Public interface (mirrors Server) ─────────────────────────────────

    def start(self) -> None:
        handler = _make_handler(self)
        self._httpd = ThreadingHTTPServer(("", WEB_PORT), handler)
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()

    def wait_for_client(self) -> str:
        self._client_connected.wait()
        return "browser"

    def send(self, msg: dict) -> None:
        data = json.dumps(msg)
        with self._sse_lock:
            self._latest_msg = data
            for q in self._sse_queues:
                q.put(data)

    def recv(self) -> dict:
        return self._recv_queue.get()

    def close(self) -> None:
        with self._sse_lock:
            for q in self._sse_queues:
                q.put(None)
        if self._httpd:
            threading.Thread(target=self._httpd.shutdown, daemon=True).start()


def _make_handler(server: WebServer):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                try:
                    html = _HTML.read_bytes()
                except FileNotFoundError:
                    self.send_error(404, "web_client.html not found")
                    return
                self._respond(200, "text/html; charset=utf-8", html)
            elif self.path == "/events":
                self._handle_sse()
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path == "/move":
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                try:
                    server._recv_queue.put(json.loads(body))
                    self._respond(200, "application/json", b"{}")
                except (json.JSONDecodeError, ValueError):
                    self.send_error(400)
            else:
                self.send_error(404)

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def _respond(self, code: int, ctype: str, body: bytes):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _handle_sse(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self._cors()
            self.end_headers()

            q: queue.Queue = queue.Queue()
            with server._sse_lock:
                server._sse_queues.append(q)
                if server._latest_msg is not None:
                    q.put(server._latest_msg)
            server._client_connected.set()

            try:
                while True:
                    data = q.get()
                    if data is None:
                        break
                    self.wfile.write(f"data: {data}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with server._sse_lock:
                    if q in server._sse_queues:
                        server._sse_queues.remove(q)

    return Handler


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
