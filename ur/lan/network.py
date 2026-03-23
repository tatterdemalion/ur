"""
Minimal TCP networking layer for the Royal Game of Ur.

Protocol: newline-delimited JSON messages over a single persistent TCP connection.

Message types (server -> client):
  {"type": "state",     "last_action": str, "stats": {...}, "board": {...}}
  {"type": "your_turn", "roll": int, "valid_moves": [piece_id, ...]}
  {"type": "no_moves",  "roll": int}
  {"type": "game_over", "winner_idx": int}

Message types (client -> server):
  {"type": "move", "piece_id": int}
"""

import json
import queue
import socket
import threading
from typing import Optional

HOST = "0.0.0.0"
PORT = 55378
BUFFER = 4096

# Sentinel placed on the recv queue when the socket closes or errors out.
_DISCONNECTED = object()


class Connection:
    """
    Wraps a socket with a background reader thread and a thread-safe queue.

    A dedicated daemon thread drains the socket continuously, parsing
    newline-delimited JSON messages and placing them on an internal queue.
    This means the main game-loop thread is never blocked waiting on the
    network while it is also waiting on user input.

    send() is safe to call from the main thread at any time; socket.sendall()
    is already atomic for reasonable message sizes.

    recv() blocks until the next message arrives. If the remote end closes
    the connection, recv() raises ConnectionError regardless of whether the
    caller is currently inside input() — the error surfaces on the *next*
    recv() call after input() returns.
    """

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._queue: queue.Queue = queue.Queue()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self):
        buf = b""
        try:
            while True:
                chunk = self._sock.recv(BUFFER)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    self._queue.put(json.loads(line.decode()))
        except (OSError, json.JSONDecodeError):
            pass
        finally:
            self._queue.put(_DISCONNECTED)

    def send(self, msg: dict):
        data = json.dumps(msg) + "\n"
        self._sock.sendall(data.encode())

    def recv(self) -> dict:
        item = self._queue.get()
        if item is _DISCONNECTED:
            # Re-enqueue so subsequent recv() calls also raise immediately.
            self._queue.put(_DISCONNECTED)
            raise ConnectionError("Connection closed.")
        return item

    def close(self):
        self._sock.close()


class Server:
    def __init__(self, port: int = PORT):
        self.port = port
        self._server_sock: Optional[socket.socket] = None
        self._conn: Optional[Connection] = None

    def start(self):
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((HOST, self.port))
        self._server_sock.listen(1)

    def wait_for_client(self) -> str:
        """Block until a client connects. Returns client's IP address."""
        conn_sock, addr = self._server_sock.accept()
        self._conn = Connection(conn_sock)
        return addr[0]

    def send(self, msg: dict):
        self._conn.send(msg)

    def recv(self) -> dict:
        return self._conn.recv()

    def close(self):
        if self._conn:
            self._conn.close()
        if self._server_sock:
            self._server_sock.close()


class Client:
    def __init__(self, host: str, port: int = PORT):
        self.host = host
        self.port = port
        self._conn: Optional[Connection] = None

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self._conn = Connection(sock)

    def send(self, msg: dict):
        self._conn.send(msg)

    def recv(self) -> dict:
        return self._conn.recv()

    def close(self):
        if self._conn:
            self._conn.close()
