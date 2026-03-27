"""
FastAPI + WebSocket online server — supports 2- and 3-player games.

Run with:
    uvicorn ur.online.server:app --host 0.0.0.0 --port 8765 --reload

Or via Makefile:
    make online-server
"""
from __future__ import annotations

import asyncio
import queue as _queue
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ur.game.engine import Engine, Player
from ur.game.rules import P1_PATH, P2_PATH
from ur.game.rules_cross import (
    CROSS_ROSETTAS_3P,
    P1_PATH_CROSS,
    P2_PATH_CROSS,
    P3_PATH_CROSS,
    PIECES_PER_PLAYER as CROSS_PIECES_PER_PLAYER,
)
from ur.storage.saves import generate_game_name

app = FastAPI()

_DIST = Path(__file__).parent / "dist"
_HTML = _DIST / "index.html"

_2P_PATHS = [P1_PATH, P2_PATH]
_3P_PATHS = [P1_PATH_CROSS, P2_PATH_CROSS, P3_PATH_CROSS]


# ── Room data structures ──────────────────────────────────────────────────────

@dataclass
class JoinerSlot:
    """Holds info for one non-host player who has joined but game hasn't started."""
    name: str
    color: str
    ws: WebSocket
    mq: _queue.Queue
    loop: asyncio.AbstractEventLoop


@dataclass
class GameRoom:
    game_id: str
    game_name: str
    player_count: int          # total players needed (2 or 3)
    host_name: str
    host_color: str
    host_ws: WebSocket
    host_mq: _queue.Queue
    host_loop: asyncio.AbstractEventLoop
    created_at: float
    joiners: list = field(default_factory=list)  # list[JoinerSlot]

    @property
    def slots_filled(self) -> int:
        return 1 + len(self.joiners)

    @property
    def is_full(self) -> bool:
        return self.slots_filled >= self.player_count


# ── Global state ──────────────────────────────────────────────────────────────

_rooms: dict[str, GameRoom] = {}
_lobby_watchers: list[WebSocket] = []
_state_lock: threading.Lock = threading.Lock()


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
                "player_count": r.player_count,
                "slots_filled": r.slots_filled,
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
        return HTMLResponse(
            "<h1>Frontend not built</h1>"
            "<p>Run: <code>cd ur/online/frontend && npm install && npm run build</code></p>",
            status_code=404,
        )


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
    move_queue: _queue.Queue[int] = _queue.Queue()
    in_lobby = True
    hosted_game_id: Optional[str] = None
    this_loop = asyncio.get_event_loop()

    with _state_lock:
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
                    player_count = int(data.get("player_count", 2))
                    player_count = max(2, min(3, player_count))

                    with _state_lock:
                        if ws in _lobby_watchers:
                            _lobby_watchers.remove(ws)
                        game_id = _new_game_id()
                        game_name = generate_game_name()
                        _rooms[game_id] = GameRoom(
                            game_id=game_id,
                            game_name=game_name,
                            player_count=player_count,
                            host_name=data.get("name", "Player"),
                            host_color=data.get("color", "#d42020"),
                            host_ws=ws,
                            host_mq=move_queue,
                            host_loop=this_loop,
                            created_at=time.time(),
                        )
                        hosted_game_id = game_id

                    in_lobby = False
                    await ws.send_json({
                        "type": "waiting",
                        "game_id": game_id,
                        "game_name": game_name,
                        "player_count": player_count,
                        "slots_filled": 1,
                    })
                    await _broadcast_games()

                elif msg_type == "join":
                    game_id = data.get("game_id", "")
                    joiner_name = data.get("name", "Player")
                    joiner_color = data.get("color", "#2060d4")
                    run_room: Optional[GameRoom] = None
                    error_msg: Optional[str] = None

                    with _state_lock:
                        room = _rooms.get(game_id)
                        if ws in _lobby_watchers:
                            _lobby_watchers.remove(ws)

                        if room is None:
                            _lobby_watchers.append(ws)
                            error_msg = "Game not found or already started"
                        else:
                            joiner = JoinerSlot(
                                name=joiner_name,
                                color=joiner_color,
                                ws=ws,
                                mq=move_queue,
                                loop=this_loop,
                            )
                            room.joiners.append(joiner)
                            in_lobby = False
                            hosted_game_id = None

                            if room.is_full:
                                del _rooms[game_id]
                                run_room = room

                    if error_msg:
                        await ws.send_json({"type": "error", "msg": error_msg})
                        await _send_games(ws)
                    elif run_room is not None:
                        # Room is full — start the game
                        asyncio.create_task(_run_game(run_room))
                        await _broadcast_games()
                    else:
                        # Still waiting for more players in a 3-player room
                        slots_filled = room.slots_filled
                        update = {
                            "type": "waiting",
                            "game_id": game_id,
                            "game_name": room.game_name,
                            "player_count": room.player_count,
                            "slots_filled": slots_filled,
                        }
                        await ws.send_json(update)
                        # Notify the host too
                        try:
                            await room.host_ws.send_json(update)
                        except Exception:
                            pass
                        await _broadcast_games()

            else:
                # In game — only moves matter
                if msg_type == "move":
                    move_queue.put(data["piece_id"])

    except (WebSocketDisconnect, Exception):
        pass
    finally:
        with _state_lock:
            if ws in _lobby_watchers:
                _lobby_watchers.remove(ws)
            if hosted_game_id and hosted_game_id in _rooms:
                del _rooms[hosted_game_id]
        asyncio.create_task(_broadcast_games())


# ── Game loop ─────────────────────────────────────────────────────────────────

async def _cross_send(ws: WebSocket, msg: dict, target_loop: asyncio.AbstractEventLoop) -> None:
    """Send a message to a WebSocket that may live in a different event loop."""
    current_loop = asyncio.get_event_loop()
    if target_loop is current_loop:
        await ws.send_json(msg)
    else:
        coro = ws.send_json(msg)
        if not target_loop.is_running():
            coro.close()
            return
        future = asyncio.run_coroutine_threadsafe(coro, target_loop)
        await asyncio.get_event_loop().run_in_executor(None, future.result)


async def _run_game(room: GameRoom) -> None:
    """Server-authoritative game loop. Supports 2- and 3-player rooms."""
    n = room.player_count

    # Build ordered lists that match player indices 0..n-1.
    # Host is always player 0; joiners follow in join order.
    names   = [room.host_name,  *(j.name  for j in room.joiners)]
    colors  = [room.host_color, *(j.color for j in room.joiners)]
    sockets = [room.host_ws,    *(j.ws    for j in room.joiners)]
    queues  = [room.host_mq,    *(j.mq    for j in room.joiners)]
    loops   = [room.host_loop,  *(j.loop  for j in room.joiners)]

    if n == 3:
        paths = _3P_PATHS
        rosettas = CROSS_ROSETTAS_3P
        piece_count = CROSS_PIECES_PER_PLAYER
    else:
        paths = _2P_PATHS
        rosettas = None   # Engine uses default ROSETTAS from game.rules
        piece_count = 7

    players = [Player(i, names[i], paths[i], piece_count) for i in range(n)]
    engine = Engine(players, rosettas=rosettas)

    async def send(idx: int, msg: dict) -> None:
        try:
            await _cross_send(sockets[idx], msg, loops[idx])
        except Exception:
            pass

    async def broadcast(msg: dict) -> None:
        for i in range(n):
            await send(i, msg)

    # ── Matched notification ──────────────────────────────────────────────────
    for i in range(n):
        opponents = [
            {"name": names[j], "color": colors[j]}
            for j in range(n) if j != i
        ]
        msg: dict = {
            "type": "matched",
            "player_idx": i,
            "game_name": room.game_name,
            "you": {"name": names[i], "color": colors[i]},
            "opponents": opponents,
        }
        # Backward compat: 2-player clients expect a singular "opponent" key
        if n == 2:
            msg["opponent"] = opponents[0]
        await send(i, msg)

    # ── Main game loop ────────────────────────────────────────────────────────
    while not engine.winner:
        roll = engine.roll_dice()
        valid_moves = engine.get_valid_moves(roll)
        cur = engine.current_idx

        if not valid_moves:
            engine.skip_turn(roll)
            await broadcast({
                "type": "no_moves",
                "current_player_idx": cur,
                "board": engine.snapshot(),
                "last_action": asdict(engine.last_action),
            })
            continue

        await send(cur, {
            "type": "your_turn",
            "roll": roll,
            "current_player_idx": cur,
            "valid_moves": [m.piece.identifier for m in valid_moves],
            "board": engine.snapshot(),
            "last_action": asdict(engine.last_action),
        })

        rolling_msg = {
            "type": "rolling",
            "roll": roll,
            "current_player_idx": cur,
            "player_name": names[cur],
            "board": engine.snapshot(),
            "last_action": asdict(engine.last_action),
        }
        for i in range(n):
            if i != cur:
                await send(i, rolling_msg)

        piece_id = await asyncio.get_event_loop().run_in_executor(
            None, queues[cur].get
        )
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
                "current_player_idx": engine.current_idx,
                "board": engine.snapshot(),
                "last_action": asdict(engine.last_action),
            })


# ── Static assets (Vite build output) ─────────────────────────────────────────
# Mounted last so the /ws WebSocket route takes priority.
if (_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(_DIST / "assets")), name="assets")
