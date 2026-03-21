import threading
import time
import unittest

from ur.cli.protocol import ClientProtocol, HostProtocol
from ur.game import Engine, Player
from ur.network import Client, Connection, Server
from ur.rules import FINISH, P1_PATH, P2_PATH


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
        p1 = Player("P1", P1_PATH, "●")
        p2 = Player("P2", P2_PATH, "●")
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
    winner_names: dict[str, str] = {}

    def run_host():
        server = Server(port=port)
        server.start()
        server.wait_for_client()

        p1 = Player("Host", P1_PATH, "●")
        p2 = Player("Client", P2_PATH, "●")
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
                on_game_over=lambda name: winner_names.__setitem__("host_side", name),
            )
            protocol.run()
        except Exception as e:
            errors.append(f"HOST: {e}")
        finally:
            server.close()

    def run_client():
        time.sleep(0.05)
        p1 = Player("Host", P1_PATH, "●")
        p2 = Player("Client", P2_PATH, "●")
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
                on_game_over=lambda board, name, action: winner_names.__setitem__(
                    "client_side", name
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

            p1 = Player("Host", P1_PATH, "●")
            p2 = Player("Client", P2_PATH, "●")
            engine = Engine(p1, p2)

            def _on_game_over(name):
                final["winner"] = name
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

        p1 = Player("Host", P1_PATH, "●")
        p2 = Player("Client", P2_PATH, "●")
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
            on_game_over=lambda board, name, action: None,
        ).run()
        client.close()
        host_t.join(timeout=30)

        winner = final["winner"]
        if winner == "Host":
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


if __name__ == "__main__":
    unittest.main()
