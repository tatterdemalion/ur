"""
Minimal TCP networking layer for the Royal Game of Ur.

Protocol: newline-delimited JSON messages over a single persistent TCP connection.

Message types (server -> client):
  {"type": "state",     "last_action": str, "stats": {...}, "board": {...}}
  {"type": "your_turn", "roll": int, "valid_moves": [piece_id, ...]}
  {"type": "no_moves",  "roll": int}
  {"type": "game_over", "winner": str}

Message types (client -> server):
  {"type": "move", "piece_id": int}
"""

import json
import socket


HOST = "0.0.0.0"
PORT = 55378
BUFFER = 4096


class Connection:
    """Wraps a socket with a persistent read buffer so messages are never lost."""

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._buf = b""

    def send(self, msg: dict):
        data = json.dumps(msg) + "\n"
        self._sock.sendall(data.encode())

    def recv(self) -> dict:
        while b"\n" not in self._buf:
            chunk = self._sock.recv(BUFFER)
            if not chunk:
                raise ConnectionError("Connection closed.")
            self._buf += chunk
        line, self._buf = self._buf.split(b"\n", 1)
        return json.loads(line.decode())

    def close(self):
        self._sock.close()


class Server:
    def __init__(self, port: int = PORT):
        self.port = port
        self._server_sock: socket.socket | None = None
        self._conn: Connection | None = None

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
        self._conn: Connection | None = None

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
