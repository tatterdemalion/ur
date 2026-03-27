# Online Server

Central WebSocket server for internet multiplayer. Players connect from the CLI client and meet in a lobby to start matches. The server runs the authoritative game loop — clients only send moves and receive state updates.

## Setup

```bash
make install-online   # installs FastAPI, uvicorn, websockets
```

## Running

```bash
make online-server            # default port 8765
make online-server PORT=9000  # custom port
```

Or directly:

```bash
uvicorn ur.online.server:app --host 0.0.0.0 --port 8765
```

## Endpoints

| Endpoint    | Type      | Purpose                              |
|-------------|-----------|--------------------------------------|
| `/`         | GET       | Serves the browser web client        |
| `/ping`     | GET       | Health check — returns `{"status": "ok"}` |
| `/api/games`| GET       | Lists open game rooms (JSON)         |
| `/ws`       | WebSocket | Lobby + game play                    |

## WebSocket Protocol

### Lobby phase

After connecting, the server sends:
```json
{"type": "lobby"}
{"type": "games", "games": [...]}
```

Client can then:

**Create a game:**
```json
{"type": "create", "name": "Alice", "color": "#d42020"}
```
Server responds with `{"type": "waiting", "game_id": "...", "game_name": "..."}` and broadcasts the updated lobby.

**Join a game:**
```json
{"type": "join", "game_id": "abc123", "name": "Bob", "color": "#1a6dd4"}
```
On success both players receive a `matched` message and the game starts. On failure the server sends `{"type": "error", "msg": "..."}`.

**List games:**
```json
{"type": "list"}
```

### Game phase

Once matched, each player receives:
```json
{
  "type": "matched",
  "player_idx": 0,
  "game_name": "Lapis_Ziggurat",
  "you": {"name": "Alice", "color": "#d42020"},
  "opponent": {"name": "Bob", "color": "#1a6dd4"}
}
```

During the game the server sends these messages to clients:

| Message type | Sent to | Meaning |
|---|---|---|
| `your_turn` | Current player | Roll result + valid moves |
| `rolling` | Waiting player | Opponent rolled, waiting for their move |
| `state` | Both | Board state after a move |
| `no_moves` | Both | Current player had no valid moves, turn skipped |
| `game_over` | Both | Match ended, includes winner index |

The current player responds with:
```json
{"type": "move", "piece_id": 3}
```

## Deployment

The server is stateless between games — no database required. For internet-facing deployment, put it behind a reverse proxy (nginx, Caddy) with TLS. Players connect from the CLI by entering the server's hostname when prompted.
