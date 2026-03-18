import random
from dataclasses import dataclass
from typing import Optional

# --- 1. THE BOARD GEOMETRY ---

P1_PATH = {
    0: None, 1: (2, 3), 2: (2, 2), 3: (2, 1), 4: (2, 0),
    5: (1, 0), 6: (1, 1), 7: (1, 2), 8: (1, 3), 9: (1, 4), 10: (1, 5), 11: (1, 6), 12: (1, 7),
    13: (2, 7), 14: (2, 6), 15: None
}

P2_PATH = {
    0: None, 1: (0, 3), 2: (0, 2), 3: (0, 1), 4: (0, 0),
    5: (1, 0), 6: (1, 1), 7: (1, 2), 8: (1, 3), 9: (1, 4), 10: (1, 5), 11: (1, 6), 12: (1, 7),
    13: (0, 7), 14: (0, 6), 15: None
}

ROSETTAS = {(0, 0), (2, 0), (1, 3), (0, 6), (2, 6)}
FINAL_SQUARE = 14
FINISH = 15


@dataclass
class Stats:
    p1_score: int
    p1_waiting: int
    p2_score: int
    p2_waiting: int


# --- 2. ENTITIES ---
class Piece:
    def __init__(self, identifier: int, player: "Player"):
        self.identifier = identifier
        self.player = player
        self.progress = 0
        self.target_progress = 0
        self.target_coord = None

    @property
    def coord(self):
        return self.player.path[self.progress]

    @property
    def is_available(self):
        return 0 <= self.progress < FINISH

    def target(self, roll:int) -> "Piece":
        self.target_progress = self.progress + roll
        self.target_coord = self.player.path.get(self.target_progress)
        return self

    def move(self, target: Optional[int] = None):
        if target is not None:
            self.progress = target
        else:
            self.progress = self.target_progress


class Player:
    def __init__(self, name: str, path: dict, symbol: str):
        self.name = name
        self.path = path
        self.symbol = symbol
        self.pieces = [Piece(i, self) for i in range(1, 8)]

    def has_won(self) -> bool:
        return all(piece.progress == FINISH for piece in self.pieces)


# --- 3. THE ENGINE ---
class Engine:
    def __init__(self, p1: Player, p2: Player):
        self.p1 = p1
        self.p2 = p2
        self.players = [p1, p2]
        self.current_idx = 0
        self.last_action = "Game started."

    @property
    def opponent_idx(self) -> int:
        return 1 - self.current_idx

    @property
    def current_player(self) -> Player:
        return self.players[self.current_idx]

    @property
    def opponent(self) -> Player:
        return self.players[self.opponent_idx]

    @property
    def winner(self) -> Optional[Player]:
        for player in self.players:
            if player.has_won():
                return player
        return None

    def get_stats(self) -> Stats:
        return Stats(
            p1_score=sum(1 for p in self.p1.pieces if p.progress == FINISH),
            p1_waiting=sum(1 for p in self.p1.pieces if p.progress == 0),
            p2_score=sum(1 for p in self.p2.pieces if p.progress == FINISH),
            p2_waiting=sum(1 for p in self.p2.pieces if p.progress == 0),
        )


    def switch_player(self) -> Player:
        self.current_idx = self.opponent_idx
        return self.current_player

    def roll_dice(self) -> int:
        return sum(random.getrandbits(1) for _ in range(4))

    def get_valid_moves(self, roll: int) -> list[Piece]:
        if roll == 0:
            return []

        current_occupied = {p.progress for p in self.current_player.pieces if p.progress < FINISH}
        opponent_safe = {p.coord for p in self.opponent.pieces if p.is_available and p.coord in ROSETTAS}

        valid_moves = []

        for piece in self.current_player.pieces:
            piece.target(roll)

            # Rule A: Piece is already done
            if not piece.is_available:
                continue

            # Rule B: Needs exact roll to score
            if piece.target_progress > FINISH:
                continue

            # Rule C: Cannot land on your own piece
            if piece.target_progress in current_occupied:
                continue

            # Rule D: Cannot hit an opponent on a Rosetta
            if piece.target_coord in opponent_safe:
                continue

            valid_moves.append(piece)

        return valid_moves

    def execute_move(self, piece: Piece, roll: int):
        state = "moved"
        roll_again = piece.target_coord in ROSETTAS and piece.target_progress < FINISH

        # Check for hit
        if piece.target_coord is not None:
            for opp_piece in self.opponent.pieces:
                if opp_piece.coord == piece.target_coord and opp_piece.is_available:
                    opp_piece.move(target=0)
                    state = "hit opponent"
                    break

        piece.move()

        if piece.progress == FINISH:
            state = "scored"
            roll_again = False

        self.last_action = f"{self.current_player.name} rolled {roll}: {piece.identifier} {state}."

        if self.current_player.has_won():
            pass
        elif roll_again:
            self.last_action += " Rolled again!"
        else:
            self.switch_player()
