"""
FastAPI + WebSocket online server.

Run with:
    uvicorn ur.online.server:app --host 0.0.0.0 --port 8765 --reload

Or via Makefile:
    make online-server
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from ur.game.engine import Engine, Player
from ur.game.rules import P1_PATH, P2_PATH
from ur.storage.saves import generate_game_name

app = FastAPI()

_HTML = Path(__file__).parent / "web_client.html"


# ── Game room ─────────────────────────────────────────────────────────────────

@dataclass
class GameRoom:
    game_id: str
    game_name: str
    host_name: str
    host_color: str       # hex string, e.g. "#d42020"
    host_ws: WebSocket
    host_mq: asyncio.Queue
    created_at: float


# ── Global state ──────────────────────────────────────────────────────────────

_rooms: dict[str, GameRoom] = {}
_lobby_watchers: list[WebSocket] = []
_state_lock: Optional[asyncio.Lock] = None


def _lock() -> asyncio.Lock:
    global _state_lock
    if _state_lock is None:
        _state_lock = asyncio.Lock()
    return _state_lock


# ── Helpers ───────────────────────────────────────────────────────────────────

def _new_game_id() -> str:
    return uuid.uuid4().hex[:8]


def _games_payload() -> dict:
    return {
        "type": "games",
        "games": [
            {
                "game_id": r.game_id,
                "game_name": r.game_name,
                "host_name": r.host_name,
                "host_color": r.host_color,
                "created_at": r.created_at,
            }
            for r in _rooms.values()
        ],
    }


async def _send_games(ws: WebSocket) -> None:
    try:
        await ws.send_json(_games_payload())
    except Exception:
        pass


async def _broadcast_games() -> None:
    payload = _games_payload()
    for ws in list(_lobby_watchers):
        try:
            await ws.send_json(payload)
        except Exception:
            pass


# ── HTTP ──────────────────────────────────────────────────────────────────────

@app.get("/")
async def index():
    try:
        return HTMLResponse(_HTML.read_text())
    except FileNotFoundError:
        return HTMLResponse("<h1>web_client.html not found</h1>", status_code=404)


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/api/games")
async def api_games():
    return _games_payload()


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    move_queue: asyncio.Queue[int] = asyncio.Queue()
    in_lobby = True
    hosted_game_id: Optional[str] = None

    async with _lock():
        _lobby_watchers.append(ws)
    await ws.send_json({"type": "lobby"})
    await _send_games(ws)

    try:
        async for data in ws.iter_json():
            msg_type = data.get("type")

            if in_lobby:
                if msg_type == "list":
                    await _send_games(ws)

                elif msg_type == "create":
                    in_lobby = False
                    async with _lock():
                        if ws in _lobby_watchers:
                            _lobby_watchers.remove(ws)
                        game_id = _new_game_id()
                        game_name = generate_game_name()
                        _rooms[game_id] = GameRoom(
                            game_id=game_id,
                            game_name=game_name,
                            host_name=data.get("name", "Player"),
                            host_color=data.get("color", "#d42020"),
                            host_ws=ws,
                            host_mq=move_queue,
                            created_at=time.time(),
                        )
                        hosted_game_id = game_id
                    await ws.send_json({
                        "type": "waiting",
                        "game_id": game_id,
                        "game_name": game_name,
                    })
                    await _broadcast_games()

                elif msg_type == "join":
                    game_id = data.get("game_id", "")
                    async with _lock():
                        room = _rooms.pop(game_id, None)
                        if ws in _lobby_watchers:
                            _lobby_watchers.remove(ws)
                    if room is None:
                        async with _lock():
                            _lobby_watchers.append(ws)
                        await ws.send_json({"type": "error", "msg": "Game not found or already started"})
                        await _send_games(ws)
                    else:
                        in_lobby = False
                        hosted_game_id = None
                        asyncio.create_task(_run_game(
                            room, ws, move_queue,
                            guest_name=data.get("name", "Player"),
                            guest_color=data.get("color", "#2060d4"),
                        ))
                        await _broadcast_games()

            else:
                # In game phase — only moves matter
                if msg_type == "move":
                    await move_queue.put(data["piece_id"])

    except (WebSocketDisconnect, Exception):
        pass
    finally:
        async with _lock():
            if ws in _lobby_watchers:
                _lobby_watchers.remove(ws)
            if hosted_game_id and hosted_game_id in _rooms:
                del _rooms[hosted_game_id]
        asyncio.create_task(_broadcast_games())


# ── Game loop ─────────────────────────────────────────────────────────────────

async def _run_game(
    room: GameRoom,
    guest_ws: WebSocket,
    guest_mq: asyncio.Queue,
    guest_name: str,
    guest_color: str,
) -> None:
    """Server-authoritative game loop for one match."""
    game_name = room.game_name
    p1 = Player(0, room.host_name, P1_PATH)
    p2 = Player(1, guest_name, P2_PATH)
    engine = Engine(p1, p2)

    sockets = [room.host_ws, guest_ws]
    queues = [room.host_mq, guest_mq]

    async def send(idx: int, msg: dict) -> None:
        try:
            await sockets[idx].send_json(msg)
        except Exception:
            pass

    async def broadcast(msg: dict) -> None:
        for w in sockets:
            try:
                await w.send_json(msg)
            except Exception:
                pass

    # Notify each player of their index and both players' colors/names
    await send(0, {
        "type": "matched",
        "player_idx": 0,
        "game_name": game_name,
        "you": {"name": room.host_name, "color": room.host_color},
        "opponent": {"name": guest_name, "color": guest_color},
    })
    await send(1, {
        "type": "matched",
        "player_idx": 1,
        "game_name": game_name,
        "you": {"name": guest_name, "color": guest_color},
        "opponent": {"name": room.host_name, "color": room.host_color},
    })

    while not engine.winner:
        roll = engine.roll_dice()
        valid_moves = engine.get_valid_moves(roll)
        cur = engine.current_idx

        if not valid_moves:
            engine.skip_turn(roll)
            await broadcast({
                "type": "no_moves",
                "board": engine.snapshot(),
                "last_action": asdict(engine.last_action),
            })
            continue

        await send(cur, {
            "type": "your_turn",
            "roll": roll,
            "valid_moves": [m.piece.identifier for m in valid_moves],
            "board": engine.snapshot(),
            "last_action": asdict(engine.last_action),
        })
        await send(1 - cur, {
            "type": "rolling",
            "roll": roll,
            "board": engine.snapshot(),
            "last_action": asdict(engine.last_action),
        })

        piece_id = await queues[cur].get()
        chosen = next((m for m in valid_moves if m.piece.identifier == piece_id), None)
        if chosen is None:
            continue

        engine.execute_move(chosen, roll)

        if engine.winner:
            await broadcast({
                "type": "game_over",
                "winner_idx": engine.winner.player_idx,
                "board": engine.snapshot(),
                "last_action": asdict(engine.last_action),
            })
        else:
            await broadcast({
                "type": "state",
                "board": engine.snapshot(),
                "last_action": asdict(engine.last_action),
            })
