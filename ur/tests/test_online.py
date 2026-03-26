"""
Functional tests for the online (FastAPI + WebSocket) server.

Uses Starlette's TestClient, which runs the ASGI app in-process via anyio.
All WebSocket connections share the same event loop so asyncio primitives
(Lock, Queue, asyncio.create_task) work correctly across connections.

Module-level server state (_rooms, _lobby_watchers, _state_lock) is reset
in setUp() to guarantee test isolation.
"""
import threading
import time
import unittest

import ur.online.server as _srv
from starlette.testclient import TestClient

from ur.game.rules import FINISH


# ── Helpers ────────────────────────────────────────────────────────────────────


def _reset():
    """Wipe module-level server state so each test starts clean."""
    _srv._rooms.clear()
    _srv._lobby_watchers.clear()
    _srv._state_lock = None  # forces re-creation in the current event loop


def _play_to_game_over(ws) -> dict:
    """
    Consume WebSocket messages until 'game_over'.
    Sends the first valid move whenever 'your_turn' is received.
    Returns the 'game_over' message.
    """
    while True:
        msg = ws.receive_json()
        if msg["type"] == "your_turn":
            ws.send_json({"type": "move", "piece_id": msg["valid_moves"][0]})
        elif msg["type"] == "game_over":
            return msg
        # rolling / state / no_moves — consume and continue


class _Base(unittest.TestCase):
    def setUp(self):
        _reset()
        self.tc = TestClient(_srv.app, raise_server_exceptions=True)


# ── 1. HTTP endpoints ──────────────────────────────────────────────────────────


class TestOnlineHTTP(_Base):
    def test_ping_returns_ok(self):
        resp = self.tc.get("/ping")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})

    def test_api_games_initially_empty(self):
        resp = self.tc.get("/api/games")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["type"], "games")
        self.assertEqual(data["games"], [])

    def test_root_serves_html(self):
        resp = self.tc.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["content-type"])
        self.assertIn(b"Royal Game", resp.content)


# ── 2. Lobby protocol ──────────────────────────────────────────────────────────


class TestOnlineLobby(_Base):
    def test_first_message_is_lobby(self):
        with self.tc.websocket_connect("/ws") as ws:
            msg = ws.receive_json()
            self.assertEqual(msg["type"], "lobby")

    def test_second_message_is_games(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json()  # lobby
            msg = ws.receive_json()
            self.assertEqual(msg["type"], "games")

    def test_initial_games_list_is_empty(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json()
            msg = ws.receive_json()
            self.assertIsInstance(msg["games"], list)
            self.assertEqual(len(msg["games"]), 0)

    def test_create_returns_waiting(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "create", "name": "Alice", "color": "#d42020"})
            msg = ws.receive_json()
            self.assertEqual(msg["type"], "waiting")

    def test_waiting_message_contains_game_id_and_name(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "create", "name": "Alice", "color": "#d42020"})
            msg = ws.receive_json()
            self.assertIn("game_id", msg)
            self.assertIn("game_name", msg)
            self.assertTrue(len(msg["game_id"]) > 0)
            self.assertTrue(len(msg["game_name"]) > 0)

    def test_created_game_appears_in_api(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "create", "name": "Alice", "color": "#d42020"})
            ws.receive_json()  # waiting

            resp = self.tc.get("/api/games")
            games = resp.json()["games"]
            self.assertEqual(len(games), 1)
            self.assertEqual(games[0]["host_name"], "Alice")
            self.assertEqual(games[0]["host_color"], "#d42020")

    def test_created_game_has_game_id_and_name_in_api(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "create", "name": "Alice", "color": "#d42020"})
            waiting = ws.receive_json()

            games = self.tc.get("/api/games").json()["games"]
            self.assertEqual(games[0]["game_id"], waiting["game_id"])
            self.assertEqual(games[0]["game_name"], waiting["game_name"])

    def test_join_nonexistent_game_returns_error(self):
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "join", "game_id": "doesnotexist",
                          "name": "Bob", "color": "#2060d4"})
            msg = ws.receive_json()
            self.assertEqual(msg["type"], "error")

    def test_after_failed_join_client_receives_fresh_games_list(self):
        """Server re-adds the client to lobby watchers after a bad join."""
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "join", "game_id": "bad",
                          "name": "Bob", "color": "#2060d4"})
            ws.receive_json()  # error
            msg = ws.receive_json()  # fresh games list
            self.assertEqual(msg["type"], "games")

    def test_watcher_receives_games_push_when_host_creates(self):
        """A connected lobby client gets a live update when another player creates a game."""
        results = {}
        errors = []
        host_created = threading.Event()

        def watcher():
            try:
                with self.tc.websocket_connect("/ws") as ws:
                    ws.receive_json()  # lobby
                    ws.receive_json()  # games (empty)
                    host_created.wait(timeout=5)
                    msg = ws.receive_json()  # pushed games update
                    results["push"] = msg
            except Exception as e:
                errors.append(str(e))

        def host():
            try:
                with self.tc.websocket_connect("/ws") as ws:
                    ws.receive_json(); ws.receive_json()
                    ws.send_json({"type": "create", "name": "Alice", "color": "#d42020"})
                    ws.receive_json()  # waiting
                    host_created.set()
                    time.sleep(0.3)  # keep connection open so watcher receives push
            except Exception as e:
                errors.append(str(e))

        wt = threading.Thread(target=watcher)
        ht = threading.Thread(target=host)
        wt.start()
        time.sleep(0.05)  # watcher connects first
        ht.start()
        wt.join(timeout=5)
        ht.join(timeout=5)

        self.assertEqual(errors, [])
        self.assertEqual(results["push"]["type"], "games")
        self.assertEqual(len(results["push"]["games"]), 1)
        self.assertEqual(results["push"]["games"][0]["host_name"], "Alice")

    def test_host_disconnect_removes_game_from_lobby(self):
        """Room is cleaned up when the host disconnects before anyone joins."""
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()
            ws.send_json({"type": "create", "name": "Alice", "color": "#d42020"})
            ws.receive_json()  # waiting
            # context manager exit closes the WebSocket

        games = self.tc.get("/api/games").json()["games"]
        self.assertEqual(games, [])

    def test_list_message_returns_current_games(self):
        """Sending {'type': 'list'} prompts a fresh games response."""
        with self.tc.websocket_connect("/ws") as ws:
            ws.receive_json(); ws.receive_json()  # lobby + initial games
            ws.send_json({"type": "list"})
            msg = ws.receive_json()
            self.assertEqual(msg["type"], "games")


# ── 3. Matchmaking ─────────────────────────────────────────────────────────────


class TestOnlineMatchmaking(_Base):
    def _match(self, host_name="Alice", host_color="#d42020",
                guest_name="Bob", guest_color="#2060d4"):
        """
        Open two WebSocket connections simultaneously, create + join,
        and return both 'matched' messages.
        """
        results = {}
        errors = []
        host_ready = threading.Event()
        game_id_ref = [None]

        def host():
            try:
                with self.tc.websocket_connect("/ws") as ws:
                    ws.receive_json(); ws.receive_json()
                    ws.send_json({"type": "create", "name": host_name, "color": host_color})
                    waiting = ws.receive_json()
                    game_id_ref[0] = waiting["game_id"]
                    host_ready.set()
                    results["host"] = ws.receive_json()  # matched
            except Exception as e:
                errors.append(f"host: {e}")
                host_ready.set()

        def guest():
            host_ready.wait(timeout=5)
            if not game_id_ref[0]:
                return
            try:
                with self.tc.websocket_connect("/ws") as ws:
                    ws.receive_json(); ws.receive_json()
                    ws.send_json({"type": "join", "game_id": game_id_ref[0],
                                  "name": guest_name, "color": guest_color})
                    results["guest"] = ws.receive_json()  # matched
            except Exception as e:
                errors.append(f"guest: {e}")

        ht = threading.Thread(target=host)
        gt = threading.Thread(target=guest)
        ht.start(); gt.start()
        ht.join(timeout=5); gt.join(timeout=5)
        self.assertEqual(errors, [], f"Errors during matchmaking: {errors}")
        self.assertIn("host", results)
        self.assertIn("guest", results)
        return results

    def test_both_receive_matched_type(self):
        r = self._match()
        self.assertEqual(r["host"]["type"], "matched")
        self.assertEqual(r["guest"]["type"], "matched")

    def test_host_is_player_0(self):
        self.assertEqual(self._match()["host"]["player_idx"], 0)

    def test_guest_is_player_1(self):
        self.assertEqual(self._match()["guest"]["player_idx"], 1)

    def test_host_you_name(self):
        r = self._match(host_name="Alice")
        self.assertEqual(r["host"]["you"]["name"], "Alice")

    def test_guest_you_name(self):
        r = self._match(guest_name="Bob")
        self.assertEqual(r["guest"]["you"]["name"], "Bob")

    def test_host_sees_guest_as_opponent(self):
        r = self._match(host_name="Alice", guest_name="Bob")
        self.assertEqual(r["host"]["opponent"]["name"], "Bob")

    def test_guest_sees_host_as_opponent(self):
        r = self._match(host_name="Alice", guest_name="Bob")
        self.assertEqual(r["guest"]["opponent"]["name"], "Alice")

    def test_host_you_color(self):
        r = self._match(host_color="#d42020")
        self.assertEqual(r["host"]["you"]["color"], "#d42020")

    def test_guest_you_color(self):
        r = self._match(guest_color="#2060d4")
        self.assertEqual(r["guest"]["you"]["color"], "#2060d4")

    def test_host_sees_guest_color_as_opponent_color(self):
        r = self._match(host_color="#d42020", guest_color="#2060d4")
        self.assertEqual(r["host"]["opponent"]["color"], "#2060d4")

    def test_guest_sees_host_color_as_opponent_color(self):
        r = self._match(host_color="#d42020", guest_color="#2060d4")
        self.assertEqual(r["guest"]["opponent"]["color"], "#d42020")

    def test_game_name_same_on_both_sides(self):
        r = self._match()
        self.assertEqual(r["host"]["game_name"], r["guest"]["game_name"])

    def test_game_removed_from_lobby_after_match(self):
        self._match()
        games = self.tc.get("/api/games").json()["games"]
        self.assertEqual(games, [])


# ── 4. Full game flow ──────────────────────────────────────────────────────────


class TestOnlineGameFlow(_Base):
    def _run_game(self, host_name="Alice", host_color="#d42020",
                  guest_name="Bob", guest_color="#2060d4"):
        """
        Run a complete game between two WebSocket clients.
        Both sides always pick the first valid move.
        Returns (results_dict, errors_list, timed_out_bool).
        """
        results = {}
        errors = []
        host_ready = threading.Event()
        game_id_ref = [None]

        def host():
            try:
                with self.tc.websocket_connect("/ws") as ws:
                    ws.receive_json(); ws.receive_json()
                    ws.send_json({"type": "create", "name": host_name, "color": host_color})
                    waiting = ws.receive_json()
                    game_id_ref[0] = waiting["game_id"]
                    host_ready.set()
                    ws.receive_json()  # matched
                    results["host"] = _play_to_game_over(ws)
            except Exception as e:
                errors.append(f"host: {e}")
                host_ready.set()

        def guest():
            host_ready.wait(timeout=5)
            if not game_id_ref[0]:
                return
            try:
                with self.tc.websocket_connect("/ws") as ws:
                    ws.receive_json(); ws.receive_json()
                    ws.send_json({"type": "join", "game_id": game_id_ref[0],
                                  "name": guest_name, "color": guest_color})
                    ws.receive_json()  # matched
                    results["guest"] = _play_to_game_over(ws)
            except Exception as e:
                errors.append(f"guest: {e}")

        ht = threading.Thread(target=host)
        gt = threading.Thread(target=guest)
        ht.start(); gt.start()
        ht.join(timeout=30); gt.join(timeout=30)
        return results, errors, ht.is_alive() or gt.is_alive()

    def test_game_completes_without_timeout(self):
        _, errors, timed_out = self._run_game()
        self.assertFalse(timed_out, "Game did not finish within 30 s")
        self.assertEqual(errors, [])

    def test_both_sides_receive_game_over(self):
        results, errors, timed_out = self._run_game()
        self.assertFalse(timed_out)
        self.assertEqual(errors, [])
        self.assertEqual(results["host"]["type"], "game_over")
        self.assertEqual(results["guest"]["type"], "game_over")

    def test_winner_idx_consistent_on_both_sides(self):
        results, errors, timed_out = self._run_game()
        self.assertFalse(timed_out)
        self.assertEqual(errors, [])
        self.assertEqual(results["host"]["winner_idx"], results["guest"]["winner_idx"])

    def test_winner_idx_is_0_or_1(self):
        results, errors, timed_out = self._run_game()
        self.assertFalse(timed_out)
        self.assertIn(results["host"]["winner_idx"], (0, 1))

    def test_game_over_board_has_winner_pieces_all_at_finish(self):
        """The final board snapshot has every winning piece at FINISH."""
        results, errors, timed_out = self._run_game()
        self.assertFalse(timed_out)
        self.assertEqual(errors, [])

        over = results["host"]
        winner_idx = over["winner_idx"]
        board = over["board"]
        key = "p1_pieces" if winner_idx == 0 else "p2_pieces"
        self.assertTrue(
            all(prog == FINISH for prog in board[key].values()),
            f"Winner (idx={winner_idx}) has unfinished pieces: {board[key]}"
        )

    def test_game_over_board_is_identical_on_both_sides(self):
        """Both players end up with the same board snapshot."""
        results, errors, timed_out = self._run_game()
        self.assertFalse(timed_out)
        self.assertEqual(errors, [])
        self.assertEqual(results["host"]["board"]["p1_pieces"],
                         results["guest"]["board"]["p1_pieces"])
        self.assertEqual(results["host"]["board"]["p2_pieces"],
                         results["guest"]["board"]["p2_pieces"])

    def test_multiple_sequential_games_all_complete(self):
        """Run 3 games back-to-back to confirm no state leaks between games."""
        for i in range(3):
            _, errors, timed_out = self._run_game(
                host_name=f"Host{i}", guest_name=f"Guest{i}"
            )
            self.assertFalse(timed_out, f"Game {i + 1} timed out")
            self.assertEqual(errors, [], f"Game {i + 1} errors: {errors}")

    def test_two_concurrent_games_both_complete(self):
        """Two simultaneous games share the same server without interfering."""
        game_results = [{}, {}]
        game_errors = [[], []]

        def run_game_n(n):
            host_ready = threading.Event()
            game_id_ref = [None]

            def host():
                try:
                    with self.tc.websocket_connect("/ws") as ws:
                        ws.receive_json(); ws.receive_json()
                        ws.send_json({"type": "create", "name": f"Host{n}",
                                      "color": "#d42020"})
                        w = ws.receive_json()
                        game_id_ref[0] = w["game_id"]
                        host_ready.set()
                        ws.receive_json()  # matched
                        game_results[n]["host"] = _play_to_game_over(ws)
                except Exception as e:
                    game_errors[n].append(f"host: {e}")
                    host_ready.set()

            def guest():
                host_ready.wait(timeout=5)
                if not game_id_ref[0]:
                    return
                try:
                    with self.tc.websocket_connect("/ws") as ws:
                        ws.receive_json(); ws.receive_json()
                        ws.send_json({"type": "join", "game_id": game_id_ref[0],
                                      "name": f"Guest{n}", "color": "#2060d4"})
                        ws.receive_json()  # matched
                        game_results[n]["guest"] = _play_to_game_over(ws)
                except Exception as e:
                    game_errors[n].append(f"guest: {e}")

            ht = threading.Thread(target=host)
            gt = threading.Thread(target=guest)
            ht.start(); gt.start()
            return ht, gt

        all_threads = []
        for n in range(2):
            ht, gt = run_game_n(n)
            all_threads.extend([ht, gt])

        for t in all_threads:
            t.join(timeout=30)

        timed_out = any(t.is_alive() for t in all_threads)
        self.assertFalse(timed_out, "One or more concurrent games timed out")

        for n in range(2):
            self.assertEqual(game_errors[n], [], f"Game {n} errors: {game_errors[n]}")
            self.assertIn("host", game_results[n], f"Game {n}: host missing")
            self.assertIn("guest", game_results[n], f"Game {n}: guest missing")
            self.assertEqual(
                game_results[n]["host"]["winner_idx"],
                game_results[n]["guest"]["winner_idx"],
                f"Game {n}: winner_idx mismatch",
            )


if __name__ == "__main__":
    unittest.main()
