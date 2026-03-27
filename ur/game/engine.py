import random
from dataclasses import dataclass
from typing import Optional

from ur.game.rules import FINISH, ROSETTAS


class ActionType:
    STARTED: str = "started"
    SKIPPED: str = "skipped"
    MOVED: str = "moved"
    SCORED: str = "scored"


@dataclass
class Action:
    player_idx: int
    roll: int
    piece_id: Optional[int]
    action_type: str
    hit: bool
    rosetta: bool
    target_progress: Optional[int] = None


@dataclass
class Stats:
    p1_score: int
    p1_waiting: int
    p2_score: int
    p2_waiting: int


class Piece:
    def __init__(self, identifier: int, player: "Player"):
        self.identifier = identifier
        self.player = player
        self.progress = 0

    @property
    def coord(self):
        return self.player.path[self.progress]

    @property
    def is_available(self):
        return 0 <= self.progress < FINISH


@dataclass
class Move:
    piece: Piece
    target_progress: int
    target_coord: Optional[tuple]


class Player:
    def __init__(self, player_idx: int, name: str, path: dict, piece_count: int = 7):
        self.player_idx = player_idx
        self.name = name
        self.path = path
        self.pieces = [Piece(i, self) for i in range(1, piece_count + 1)]

    def has_won(self) -> bool:
        return all(piece.progress == FINISH for piece in self.pieces)


class Engine:
    def __init__(self, *args, rosettas=None):
        """
        Accepts either:
          Engine(p1, p2)              — 2-player (backward compatible)
          Engine(p1, p2, p3)          — 3-player
          Engine([p1, p2, p3], ...)   — list form
        """
        if len(args) == 1 and isinstance(args[0], list):
            players = args[0]
        else:
            players = list(args)

        self.players = players
        self.rosettas = ROSETTAS if rosettas is None else rosettas
        self.current_idx = 0
        self.last_action = Action(
            player_idx=0,
            roll=0,
            piece_id=None,
            action_type=ActionType.STARTED,
            hit=False,
            rosetta=False,
            target_progress=None,
        )

    # ── Backward-compat 2-player properties ──────────────────────────────────

    @property
    def p1(self) -> Player:
        return self.players[0]

    @property
    def p2(self) -> Player:
        return self.players[1]

    @property
    def opponent_idx(self) -> int:
        """2-player compat: index of the single opponent."""
        return self.current_idx ^ 1

    @property
    def opponent(self) -> Player:
        """2-player compat: the single opponent player."""
        return self.players[self.opponent_idx]

    # ── N-player properties ───────────────────────────────────────────────────

    @property
    def opponents(self) -> list:
        return [p for i, p in enumerate(self.players) if i != self.current_idx]

    @property
    def current_player(self) -> Player:
        return self.players[self.current_idx]

    @property
    def winner(self) -> Optional[Player]:
        for player in self.players:
            if player.has_won():
                return player
        return None

    # ── Serialization ─────────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        """Serialize piece positions to a JSON-safe dict for network/save use."""
        result: dict = {
            "players": [
                {"pieces": {str(p.identifier): p.progress for p in player.pieces}}
                for player in self.players
            ]
        }
        # Backward-compat keys so existing saves/tests keep working
        result["p1_pieces"] = result["players"][0]["pieces"]
        result["p2_pieces"] = result["players"][1]["pieces"]
        stats = self.get_stats()
        result["stats"] = {
            "p1_score": stats.p1_score,
            "p1_waiting": stats.p1_waiting,
            "p2_score": stats.p2_score,
            "p2_waiting": stats.p2_waiting,
        }
        return result

    def restore(self, board: dict):
        """Apply a snapshot dict back onto this engine's piece positions."""
        if "players" in board:
            for i, player_data in enumerate(board["players"]):
                if i < len(self.players):
                    for piece in self.players[i].pieces:
                        piece.progress = player_data["pieces"][str(piece.identifier)]
        else:
            # Legacy 2-player format
            for piece in self.players[0].pieces:
                piece.progress = board["p1_pieces"][str(piece.identifier)]
            for piece in self.players[1].pieces:
                piece.progress = board["p2_pieces"][str(piece.identifier)]

    def get_stats(self) -> Stats:
        return Stats(
            p1_score=sum(1 for p in self.p1.pieces if p.progress == FINISH),
            p1_waiting=sum(1 for p in self.p1.pieces if p.progress == 0),
            p2_score=sum(1 for p in self.p2.pieces if p.progress == FINISH),
            p2_waiting=sum(1 for p in self.p2.pieces if p.progress == 0),
        )

    # ── Turn management ───────────────────────────────────────────────────────

    def skip_turn(self, roll: int):
        self.last_action = Action(
            player_idx=self.current_idx,
            roll=roll,
            piece_id=None,
            action_type=ActionType.SKIPPED,
            hit=False,
            rosetta=False,
        )
        self.switch_player()

    def switch_player(self) -> Player:
        self.current_idx = (self.current_idx + 1) % len(self.players)
        return self.current_player

    def roll_dice(self) -> int:
        return sum(random.getrandbits(1) for _ in range(4))

    # ── Move logic ────────────────────────────────────────────────────────────

    def get_valid_moves(self, roll: int) -> list:
        if roll == 0:
            return []

        current_occupied = {p.progress for p in self.current_player.pieces if p.progress < FINISH}
        opponent_safe = set()
        for opp in self.opponents:
            for p in opp.pieces:
                if p.is_available and p.coord in self.rosettas:
                    opponent_safe.add(p.coord)

        valid_moves = []
        for piece in self.current_player.pieces:
            if not piece.is_available:
                continue

            target_progress = piece.progress + roll

            if target_progress > FINISH:
                continue

            if target_progress in current_occupied:
                continue

            target_coord = self.current_player.path.get(target_progress)

            if target_coord in opponent_safe:
                continue

            valid_moves.append(
                Move(piece=piece, target_progress=target_progress, target_coord=target_coord)
            )

        return valid_moves

    def execute_move(self, move: Move, roll: int):
        hit = False
        roll_again = move.target_coord in self.rosettas and move.target_progress < FINISH

        if move.target_coord is not None:
            for opp in self.opponents:
                for opp_piece in opp.pieces:
                    if opp_piece.coord == move.target_coord and opp_piece.is_available:
                        opp_piece.progress = 0
                        hit = True
                        break
                if hit:
                    break

        move.piece.progress = move.target_progress

        if move.piece.progress == FINISH:
            action_type = ActionType.SCORED
            roll_again = False
        else:
            action_type = ActionType.MOVED

        self.last_action = Action(
            player_idx=self.current_idx,
            roll=roll,
            piece_id=move.piece.identifier,
            action_type=action_type,
            hit=hit,
            rosetta=roll_again,
            target_progress=move.target_progress,
        )

        if self.current_player.has_won():
            pass
        elif roll_again:
            pass
        else:
            self.switch_player()
