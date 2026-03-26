"""
Synchronous WebSocket client for the CLI online match.

Requires:  pip install "websockets>=12"
"""
from __future__ import annotations

import json

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
