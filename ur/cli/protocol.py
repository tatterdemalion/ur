"""
Pure game-loop message protocol, decoupled from UI.

HostProtocol drives the authoritative engine and sends state updates over the
network. ClientProtocol receives those updates and fires UI callbacks.

Both classes accept callable hooks so the match layer can wire in display logic
without any network/engine logic leaking upward.
"""

from dataclasses import asdict
from typing import Callable, Optional

from ur.game import Action, Engine, Move, Player
from ur.network import Client, Server


class HostProtocol:
    """
    Drives one complete game as the host (server side).

    Parameters
    ----------
    server : Server
        Already-started and connected server instance.
    engine : Engine
        Freshly constructed (or restored) engine.
    p1, p2 : Player
        Must be the same objects held by *engine*.
    on_my_turn : Callable[[list[Move], int], Optional[Move]]
        Called when it is the host player's turn. Receives valid moves and the
        roll. Must return the chosen Move, or None to abort (returns False from
        run()).
    on_state : Callable[[str], None]
        Called after every move with the last_action string, for display.
    on_opponent_thinking : Callable[[], None]
        Called just before blocking on the opponent's reply.
    on_no_moves : Callable[[int], None]
        Called when the current player has no valid moves; receives the roll.
    on_game_over : Callable[[str], None]
        Called with winner name once the game ends.
    """

    def __init__(
        self,
        server: Server,
        engine: Engine,
        p1: Player,
        p2: Player,
        on_my_turn: Callable[[list[Move], int], Optional[Move]],
        on_state: Callable[[str], None],
        on_opponent_thinking: Callable[[], None],
        on_no_moves: Callable[[int], None],
        on_game_over: Callable[[str], None],
    ):
        self.server = server
        self.engine = engine
        self.p1 = p1
        self.p2 = p2
        self.on_my_turn = on_my_turn
        self.on_state = on_state
        self.on_opponent_thinking = on_opponent_thinking
        self.on_no_moves = on_no_moves
        self.on_game_over = on_game_over

    def run(self) -> bool:
        """
        Run the game loop to completion.

        Returns True if the game finished normally, False if the host aborted
        (on_my_turn returned None).
        """
        engine = self.engine

        while not engine.winner:
            roll = engine.roll_dice()
            valid_moves = engine.get_valid_moves(roll)

            if not valid_moves:
                engine.skip_turn(roll)
                self.server.send(
                    {
                        "type": "no_moves",
                        "last_action": asdict(engine.last_action),
                        "board": engine.snapshot(),
                    }
                )
                self.on_no_moves(roll)
                continue

            if engine.current_player == self.p1:
                self.server.send(
                    {
                        "type": "rolling",
                        "roll": roll,
                        "last_action": asdict(engine.last_action),
                        "board": engine.snapshot(),
                    }
                )
                chosen_move = self.on_my_turn(valid_moves, roll)
                if chosen_move is None:
                    return False
            else:
                self.server.send(
                    {
                        "type": "your_turn",
                        "roll": roll,
                        "valid_moves": [m.piece.identifier for m in valid_moves],
                        "last_action": asdict(engine.last_action),
                        "board": engine.snapshot(),
                    }
                )
                self.on_opponent_thinking()
                msg = self.server.recv()
                chosen_move = next(
                    m for m in valid_moves if m.piece.identifier == msg["piece_id"]
                )

            engine.execute_move(chosen_move, roll)

            msg_type = "game_over" if engine.winner else "state"
            self.server.send(
                {
                    "type": msg_type,
                    "winner": engine.winner.name if engine.winner else None,
                    "last_action": asdict(engine.last_action),
                    "board": engine.snapshot(),
                }
            )
            self.on_state(engine.last_action)

        self.on_game_over(engine.winner.name)
        return True


class ClientProtocol:
    """
    Drives one complete game as the client side.

    Parameters
    ----------
    client : Client
        Already-connected client instance.
    engine : Engine
        Freshly constructed (or restored) engine.
    on_rolling : Callable[[dict, int, dict], None]
        Called when the host (opponent) is rolling; receives board snapshot, roll, and last_action dict.
    on_state : Callable[[dict, dict], None]
        Called after a state update; receives board snapshot and last_action dict.
    on_no_moves : Callable[[dict, dict], None]
        Called when any player had no moves; receives board snapshot and last_action dict.
    on_your_turn : Callable[[dict, int, list[int], dict], Optional[int]]
        Called when it is the client's turn. Receives board snapshot, roll,
        list of valid piece IDs, and last_action dict. Must return the chosen
        piece_id, or None to abort (returns False from run()).
    on_game_over : Callable[[dict, str, dict], None]
        Called with board snapshot, winner name, and last_action dict.
    """

    def __init__(
        self,
        client: Client,
        engine: Engine,
        on_rolling: Callable[[dict, int, dict], None],
        on_state: Callable[[dict, dict], None],
        on_no_moves: Callable[[dict, dict], None],
        on_your_turn: Callable[[dict, int, list, dict], Optional[int]],
        on_game_over: Callable[[dict, str, dict], None],
    ):
        self.client = client
        self.engine = engine
        self.on_rolling = on_rolling
        self.on_state = on_state
        self.on_no_moves = on_no_moves
        self.on_your_turn = on_your_turn
        self.on_game_over = on_game_over

    def run(self) -> bool:
        """
        Run the receive loop to completion.

        Returns True if the game ended normally, False if the client aborted
        (on_your_turn returned None).
        """
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
                self.on_game_over(msg["board"], msg["winner"], msg["last_action"])
                return True
