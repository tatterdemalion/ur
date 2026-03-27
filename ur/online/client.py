"""
Synchronous WebSocket client and message protocol for the CLI online match.

Requires:  pip install "websockets>=12"
"""
from __future__ import annotations

import json
from typing import Callable, Optional

import websockets.sync.client as _ws_sync

ONLINE_PORT = 8765
DEFAULT_HOST = "localhost"

# (display_name, ANSI_code, hex_for_server)
ONLINE_COLORS: list[tuple[str, str, str]] = [
    ("Red",    "\033[38;5;196m", "#d42020"),
    ("Blue",   "\033[38;5;33m",  "#1a6dd4"),
    ("Green",  "\033[38;5;40m",  "#1fa84c"),
    ("Purple", "\033[38;5;129m", "#8020c8"),
    ("Orange", "\033[38;5;208m", "#d47020"),
    ("Teal",   "\033[38;5;45m",  "#00b8b8"),
    ("Pink",   "\033[38;5;205m", "#d420a0"),
    ("Gold",   "\033[38;5;220m", "#c09800"),
]


class OnlineSocket:
    """
    Thin wrapper that gives the same .send() / .recv() interface
    as the LAN Server/Client, so OnlineMatch can reuse protocol logic.
    """

    def __init__(self, url: str):
        self._url = url
        self._conn = None

    def connect(self) -> None:
        self._conn = _ws_sync.connect(self._url)

    def send(self, msg: dict) -> None:
        self._conn.send(json.dumps(msg))

    def recv(self) -> dict:
        return json.loads(self._conn.recv())

    def close(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass


class ClientProtocol:
    """
    Drives one complete game as the client side.

    Accepts any object with .send() / .recv() so it works with both
    OnlineSocket (WebSocket) and future transports.
    """

    def __init__(
        self,
        client,
        engine,
        on_rolling: Callable[[dict, int, dict], None],
        on_state: Callable[[dict, dict], None],
        on_no_moves: Callable[[dict, dict], None],
        on_your_turn: Callable[[dict, int, list, dict], Optional[int]],
        on_game_over: Callable[[dict, int, dict], None],
    ):
        self.client = client
        self.engine = engine
        self.on_rolling = on_rolling
        self.on_state = on_state
        self.on_no_moves = on_no_moves
        self.on_your_turn = on_your_turn
        self.on_game_over = on_game_over

    def run(self) -> bool:
        while True:
            msg = self.client.recv()
            msg_type = msg["type"]

            if msg_type == "rolling":
                self.on_rolling(msg["board"], msg["roll"], msg["last_action"])

            elif msg_type == "state":
                self.on_state(msg["board"], msg["last_action"])

            elif msg_type == "no_moves":
                self.on_no_moves(msg["board"], msg["last_action"])

            elif msg_type == "your_turn":
                piece_id = self.on_your_turn(
                    msg["board"], msg["roll"], msg["valid_moves"], msg["last_action"]
                )
                if piece_id is None:
                    return False
                self.client.send({"type": "move", "piece_id": piece_id})

            elif msg_type == "game_over":
                self.on_game_over(msg["board"], msg["winner_idx"], msg["last_action"])
                return True
