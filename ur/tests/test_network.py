import threading
import time
import unittest

from ur.game.engine import Engine, Player
from ur.lan.network import Client, Connection, Server
from ur.lan.protocol import ClientProtocol, HostProtocol
from ur.game.rules import FINISH, P1_PATH, P2_PATH


def get_free_port():
    import socket

    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_connected_pair(port):
    """Return (server, client) both connected, server has accepted."""
    server = Server(port=port)
    server.start()

    client = Client("127.0.0.1", port=port)

    ready = threading.Event()

    def _accept():
        server.wait_for_client()
        ready.set()

    t = threading.Thread(target=_accept, daemon=True)
    t.start()
    client.connect()
    ready.wait(timeout=2)
    return server, client


# ---------------------------------------------------------------------------
# 1. Protocol layer (Connection)
# ---------------------------------------------------------------------------


class TestConnection(unittest.TestCase):
    """Low-level send/recv over a real socket pair."""

    def setUp(self):
        import socket

        self.port = get_free_port()
        # Build a raw socket pair via a temporary listener
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", self.port))
        listener.listen(1)

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(("127.0.0.1", self.port))
        server_sock, _ = listener.accept()
        listener.close()

        self.server_conn = Connection(server_sock)
        self.client_conn = Connection(client_sock)

    def tearDown(self):
        self.server_conn.close()
        self.client_conn.close()

    def test_single_message_roundtrip(self):
        self.client_conn.send({"type": "hello", "value": 42})
        msg = self.server_conn.recv()
        self.assertEqual(msg["type"], "hello")
        self.assertEqual(msg["value"], 42)

    def test_multiple_messages_in_sequence(self):
        for i in range(5):
            self.client_conn.send({"seq": i})
        for i in range(5):
            msg = self.server_conn.recv()
            self.assertEqual(msg["seq"], i)

    def test_large_payload(self):
        payload = {"data": "x" * 8000}
        self.client_conn.send(payload)
        msg = self.server_conn.recv()
        self.assertEqual(len(msg["data"]), 8000)

    def test_bidirectional(self):
        self.client_conn.send({"direction": "client->server"})
        self.server_conn.send({"direction": "server->client"})
        self.assertEqual(self.server_conn.recv()["direction"], "client->server")
        self.assertEqual(self.client_conn.recv()["direction"], "server->client")

    def test_messages_batched_in_single_segment(self):
        """Stress the buffer: send many tiny messages rapidly."""
        N = 50
        for i in range(N):
            self.server_conn.send({"n": i})
        for i in range(N):
            msg = self.client_conn.recv()
            self.assertEqual(msg["n"], i)

    def test_connection_closed_raises(self):
        self.server_conn.close()
        with self.assertRaises((ConnectionError, OSError)):
            # Keep recving until the closed connection is detected
            for _ in range(100):
                self.client_conn.recv()


# ---------------------------------------------------------------------------
# 2. Server / Client API
# ---------------------------------------------------------------------------


class TestServerClient(unittest.TestCase):
    def setUp(self):
        self.port = get_free_port()
        self.server, self.client = make_connected_pair(self.port)

    def tearDown(self):
        self.server.close()
        self.client.close()

    def test_server_send_client_recv(self):
        self.server.send({"type": "ping"})
        self.assertEqual(self.client.recv()["type"], "ping")

    def test_client_send_server_recv(self):
        self.client.send({"type": "pong"})
        self.assertEqual(self.server.recv()["type"], "pong")

    def test_request_response_pattern(self):
        def _server_side():
            msg = self.server.recv()
            self.server.send({"echo": msg["value"]})

        t = threading.Thread(target=_server_side, daemon=True)
        t.start()
        self.client.send({"value": "hello"})
        response = self.client.recv()
        t.join(timeout=2)
        self.assertEqual(response["echo"], "hello")

    def test_multiple_round_trips(self):
        def _server_side():
            for _ in range(10):
                msg = self.server.recv()
                self.server.send({"ack": msg["i"]})

        t = threading.Thread(target=_server_side, daemon=True)
        t.start()
        for i in range(10):
            self.client.send({"i": i})
            ack = self.client.recv()
            self.assertEqual(ack["ack"], i)
        t.join(timeout=2)


# ---------------------------------------------------------------------------
# 3. Board serialization helpers
# ---------------------------------------------------------------------------


class TestBoardSerialization(unittest.TestCase):
    def _make_engine(self):
        p1 = Player(0, "P1", P1_PATH)
        p2 = Player(1, "P2", P2_PATH)
        return Engine(p1, p2), p1, p2

    def test_roundtrip_all_at_start(self):
        engine, _, _ = self._make_engine()
        engine2, _, _ = self._make_engine()
        engine2.restore(engine.snapshot())
        for p in engine2.p1.pieces:
            self.assertEqual(p.progress, 0)
        for p in engine2.p2.pieces:
            self.assertEqual(p.progress, 0)

    def test_roundtrip_arbitrary_positions(self):
        engine, p1, p2 = self._make_engine()
        p1.pieces[0].progress = 5
        p1.pieces[3].progress = 12
        p2.pieces[1].progress = 7
        p2.pieces[6].progress = FINISH

        engine2, _, _ = self._make_engine()
        engine2.restore(engine.snapshot())

        self.assertEqual(engine2.p1.pieces[0].progress, 5)
        self.assertEqual(engine2.p1.pieces[3].progress, 12)
        self.assertEqual(engine2.p2.pieces[1].progress, 7)
        self.assertEqual(engine2.p2.pieces[6].progress, FINISH)

    def test_roundtrip_via_json(self):
        """Simulate actual network transit (keys become strings after JSON)."""
        import json

        engine, p1, _ = self._make_engine()
        p1.pieces[2].progress = 9

        serialized = json.loads(json.dumps(engine.snapshot()))

        engine2, _, _ = self._make_engine()
        engine2.restore(serialized)
        self.assertEqual(engine2.p1.pieces[2].progress, 9)


# ---------------------------------------------------------------------------
# 4. Full game integration
# ---------------------------------------------------------------------------


def _run_headless_game(port: int) -> tuple[list, dict, bool]:
    """
    Spin up a full game over real TCP using HostProtocol / ClientProtocol.
    Both sides auto-pick the first valid move.
    Returns (errors, winner_names, timed_out).
    """
    errors: list[str] = []
    winner_names: dict[str, int] = {}

    def run_host():
        server = Server(port=port)
        server.start()
        server.wait_for_client()

        p1 = Player(0, "Host", P1_PATH)
        p2 = Player(1, "Client", P2_PATH)
        engine = Engine(p1, p2)

        try:
            protocol = HostProtocol(
                server=server,
                engine=engine,
                p1=p1,
                p2=p2,
                on_my_turn=lambda moves, roll: moves[0],
                on_state=lambda last_action: None,
                on_opponent_thinking=lambda: None,
                on_no_moves=lambda roll: None,
                on_game_over=lambda winner_idx: winner_names.__setitem__("host_side", winner_idx),
            )
            protocol.run()
        except Exception as e:
            errors.append(f"HOST: {e}")
        finally:
            server.close()

    def run_client():
        time.sleep(0.05)
        p1 = Player(0, "Host", P1_PATH)
        p2 = Player(1, "Client", P2_PATH)
        engine = Engine(p1, p2)

        client = Client("127.0.0.1", port=port)
        client.connect()

        try:
            protocol = ClientProtocol(
                client=client,
                engine=engine,
                on_rolling=lambda board, roll, last_action: None,
                on_state=lambda board, last_action: None,
                on_no_moves=lambda board, last_action: None,
                on_your_turn=lambda board, roll, ids, last_action: ids[0],
                on_game_over=lambda board, winner_idx, action: winner_names.__setitem__(
                    "client_side", winner_idx
                ),
            )
            protocol.run()
        except Exception as e:
            errors.append(f"CLIENT: {e}")
        finally:
            client.close()

    host_t = threading.Thread(target=run_host)
    client_t = threading.Thread(target=run_client)
    host_t.start()
    client_t.start()
    host_t.join(timeout=30)
    client_t.join(timeout=30)

    return errors, winner_names, host_t.is_alive() or client_t.is_alive()


class TestFullGameIntegration(unittest.TestCase):
    """
    Headless host + client over real TCP using HostProtocol / ClientProtocol.
    Both sides auto-pick the first valid move. Verifies the complete message
    protocol drives a game to completion with a consistent final board state.
    """

    def test_game_completes(self):
        errors, winner_names, timed_out = _run_headless_game(get_free_port())
        self.assertFalse(timed_out, "Game did not finish within 30 seconds")
        self.assertEqual(errors, [])

    def test_winner_consistent_on_both_sides(self):
        errors, winner_names, timed_out = _run_headless_game(get_free_port())
        self.assertFalse(timed_out)
        self.assertEqual(errors, [])
        self.assertEqual(winner_names["host_side"], winner_names["client_side"])

    def test_winner_board_state_is_valid(self):
        """All of the winner's pieces must be at FINISH on the host's engine."""
        port = get_free_port()
        final: dict = {}

        def run_host():
            server = Server(port=port)
            server.start()
            server.wait_for_client()

            p1 = Player(0, "Host", P1_PATH)
            p2 = Player(1, "Client", P2_PATH)
            engine = Engine(p1, p2)

            def _on_game_over(winner_idx: int):
                final["winner_idx"] = winner_idx
                final["p1_done"] = all(p.progress == FINISH for p in p1.pieces)
                final["p2_done"] = all(p.progress == FINISH for p in p2.pieces)

            try:
                protocol = HostProtocol(
                    server=server,
                    engine=engine,
                    p1=p1,
                    p2=p2,
                    on_my_turn=lambda moves, roll: moves[0],
                    on_state=lambda last_action: None,
                    on_opponent_thinking=lambda: None,
                    on_no_moves=lambda roll: None,
                    on_game_over=_on_game_over,
                )
                protocol.run()
            finally:
                server.close()

        host_t = threading.Thread(target=run_host)
        host_t.start()
        time.sleep(0.05)  # let host bind and listen

        p1 = Player(0, "Host", P1_PATH)
        p2 = Player(1, "Client", P2_PATH)
        engine = Engine(p1, p2)
        client = Client("127.0.0.1", port=port)
        client.connect()

        ClientProtocol(
            client=client,
            engine=engine,
            on_rolling=lambda board, roll, last_action: None,
            on_state=lambda board, last_action: None,
            on_no_moves=lambda board, last_action: None,
            on_your_turn=lambda board, roll, ids, last_action: ids[0],
            on_game_over=lambda board, winner_idx, action: None,
        ).run()
        client.close()
        host_t.join(timeout=30)

        if final["winner_idx"] == 0:
            self.assertTrue(final["p1_done"])
        else:
            self.assertTrue(final["p2_done"])

    def test_multiple_games_all_complete(self):
        """Run 5 independent games to confirm no flakiness."""
        for _ in range(5):
            errors, winner_names, timed_out = _run_headless_game(get_free_port())
            self.assertFalse(timed_out)
            self.assertEqual(errors, [])
            self.assertEqual(winner_names["host_side"], winner_names["client_side"])


def _run_rigged_game(port: int, winner_idx: int) -> tuple[int, int, bool]:
    """
    Run a near-finished game over real TCP where the winner is predetermined.

    The winning player has 6 pieces at FINISH and 1 piece at progress 14.
    The losing player has 2 pieces at FINISH and 5 spread across the board.
    It is always the winning player's turn first, so a roll of 1 ends the game
    immediately (piece 14 + 1 = FINISH).

    Returns (host_winner_idx, client_winner_idx, timed_out).
    """
    results: dict[str, int] = {}

    def _make_near_finished_engine(winning_idx: int) -> tuple[Engine, Player, Player]:
        p1 = Player(0, "Host", P1_PATH)
        p2 = Player(1, "Client", P2_PATH)
        engine = Engine(p1, p2)
        winner_player = p1 if winning_idx == 0 else p2
        loser_player = p2 if winning_idx == 0 else p1
        for piece in winner_player.pieces[:-1]:
            piece.progress = FINISH
        winner_player.pieces[-1].progress = 14
        loser_player.pieces[0].progress = FINISH
        loser_player.pieces[1].progress = FINISH
        loser_player.pieces[2].progress = 10
        loser_player.pieces[3].progress = 7
        loser_player.pieces[4].progress = 5
        loser_player.pieces[5].progress = 3
        loser_player.pieces[6].progress = 1
        engine.current_idx = winning_idx
        return engine, p1, p2

    def run_host():
        server = Server(port=port)
        server.start()
        server.wait_for_client()
        engine, p1, p2 = _make_near_finished_engine(winner_idx)
        try:
            HostProtocol(
                server=server,
                engine=engine,
                p1=p1,
                p2=p2,
                on_my_turn=lambda moves, roll: moves[0],
                on_state=lambda last_action: None,
                on_opponent_thinking=lambda: None,
                on_no_moves=lambda roll: None,
                on_game_over=lambda idx: results.__setitem__("host_side", idx),
            ).run()
        finally:
            server.close()

    def run_client():
        time.sleep(0.05)
        engine, p1, p2 = _make_near_finished_engine(winner_idx)
        client = Client("127.0.0.1", port=port)
        client.connect()
        try:
            ClientProtocol(
                client=client,
                engine=engine,
                on_rolling=lambda board, roll, last_action: None,
                on_state=lambda board, last_action: None,
                on_no_moves=lambda board, last_action: None,
                on_your_turn=lambda board, roll, ids, last_action: ids[0],
                on_game_over=lambda board, idx, action: results.__setitem__("client_side", idx),
            ).run()
        finally:
            client.close()

    host_t = threading.Thread(target=run_host)
    client_t = threading.Thread(target=run_client)
    host_t.start()
    client_t.start()
    host_t.join(timeout=10)
    client_t.join(timeout=10)

    timed_out = host_t.is_alive() or client_t.is_alive()
    return results.get("host_side", -1), results.get("client_side", -1), timed_out


class TestEndGameWinnerDetection(unittest.TestCase):
    """
    Verifies that winner_idx is reported correctly on both sides for both
    possible outcomes (host wins / client wins) in a LAN game.
    """

    def test_host_wins_reported_correctly_on_host_side(self):
        host_idx, _, timed_out = _run_rigged_game(get_free_port(), winner_idx=0)
        self.assertFalse(timed_out)
        self.assertEqual(host_idx, 0)

    def test_host_wins_reported_correctly_on_client_side(self):
        _, client_idx, timed_out = _run_rigged_game(get_free_port(), winner_idx=0)
        self.assertFalse(timed_out)
        self.assertEqual(client_idx, 0)

    def test_client_wins_reported_correctly_on_host_side(self):
        host_idx, _, timed_out = _run_rigged_game(get_free_port(), winner_idx=1)
        self.assertFalse(timed_out)
        self.assertEqual(host_idx, 1)

    def test_client_wins_reported_correctly_on_client_side(self):
        _, client_idx, timed_out = _run_rigged_game(get_free_port(), winner_idx=1)
        self.assertFalse(timed_out)
        self.assertEqual(client_idx, 1)

    def test_winner_idx_consistent_on_both_sides(self):
        for expected_winner in (0, 1):
            host_idx, client_idx, timed_out = _run_rigged_game(get_free_port(), winner_idx=expected_winner)
            self.assertFalse(timed_out)
            self.assertEqual(host_idx, client_idx)
            self.assertEqual(host_idx, expected_winner)

    def test_host_wins_board_fully_finished(self):
        """When host wins, all of P1's pieces must be at FINISH on both sides."""
        port = get_free_port()
        final: dict = {}

        def run_host():
            server = Server(port=port)
            server.start()
            server.wait_for_client()
            engine, p1, p2 = _make_near_finished_engine_external(winner_idx=0)
            try:
                HostProtocol(
                    server=server,
                    engine=engine,
                    p1=p1,
                    p2=p2,
                    on_my_turn=lambda moves, roll: moves[0],
                    on_state=lambda last_action: None,
                    on_opponent_thinking=lambda: None,
                    on_no_moves=lambda roll: None,
                    on_game_over=lambda idx: final.__setitem__("p1_done", all(p.progress == FINISH for p in p1.pieces)),
                ).run()
            finally:
                server.close()

        host_t = threading.Thread(target=run_host)
        host_t.start()
        time.sleep(0.05)

        engine, p1, p2 = _make_near_finished_engine_external(winner_idx=0)
        client = Client("127.0.0.1", port=port)
        client.connect()
        ClientProtocol(
            client=client,
            engine=engine,
            on_rolling=lambda board, roll, last_action: None,
            on_state=lambda board, last_action: None,
            on_no_moves=lambda board, last_action: None,
            on_your_turn=lambda board, roll, ids, last_action: ids[0],
            on_game_over=lambda board, idx, action: None,
        ).run()
        client.close()
        host_t.join(timeout=10)

        self.assertTrue(final.get("p1_done"), "P1's pieces should all be at FINISH after host wins")

    def test_client_wins_board_fully_finished(self):
        """When client wins, all of P2's pieces must be at FINISH on both sides."""
        port = get_free_port()
        final: dict = {}

        def run_host():
            server = Server(port=port)
            server.start()
            server.wait_for_client()
            engine, p1, p2 = _make_near_finished_engine_external(winner_idx=1)
            try:
                HostProtocol(
                    server=server,
                    engine=engine,
                    p1=p1,
                    p2=p2,
                    on_my_turn=lambda moves, roll: moves[0],
                    on_state=lambda last_action: None,
                    on_opponent_thinking=lambda: None,
                    on_no_moves=lambda roll: None,
                    on_game_over=lambda idx: final.__setitem__("p2_done", all(p.progress == FINISH for p in p2.pieces)),
                ).run()
            finally:
                server.close()

        host_t = threading.Thread(target=run_host)
        host_t.start()
        time.sleep(0.05)

        engine, p1, p2 = _make_near_finished_engine_external(winner_idx=1)
        client = Client("127.0.0.1", port=port)
        client.connect()
        ClientProtocol(
            client=client,
            engine=engine,
            on_rolling=lambda board, roll, last_action: None,
            on_state=lambda board, last_action: None,
            on_no_moves=lambda board, last_action: None,
            on_your_turn=lambda board, roll, ids, last_action: ids[0],
            on_game_over=lambda board, idx, action: None,
        ).run()
        client.close()
        host_t.join(timeout=10)

        self.assertTrue(final.get("p2_done"), "P2's pieces should all be at FINISH after client wins")


def _make_near_finished_engine_external(winner_idx: int) -> tuple[Engine, Player, Player]:
    """Same setup as _run_rigged_game's inner helper, usable from test methods."""
    p1 = Player(0, "Host", P1_PATH)
    p2 = Player(1, "Client", P2_PATH)
    engine = Engine(p1, p2)
    winner_player = p1 if winner_idx == 0 else p2
    loser_player = p2 if winner_idx == 0 else p1
    for piece in winner_player.pieces[:-1]:
        piece.progress = FINISH
    winner_player.pieces[-1].progress = 14
    loser_player.pieces[0].progress = FINISH
    loser_player.pieces[1].progress = FINISH
    loser_player.pieces[2].progress = 10
    loser_player.pieces[3].progress = 7
    loser_player.pieces[4].progress = 5
    loser_player.pieces[5].progress = 3
    loser_player.pieces[6].progress = 1
    engine.current_idx = winner_idx
    return engine, p1, p2


if __name__ == "__main__":
    unittest.main()
