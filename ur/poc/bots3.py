import random

from ur.poc.engine3 import Engine, Move, Player
from ur.poc.rules3 import FINISH


class Bot:
    name = "Bot"

    def choose_move(self, engine: Engine, valid_moves: list[Move]) -> Move:
        raise NotImplementedError("Bots must implement their own logic!")


class RandomBot(Bot):
    name = "RandomBot"

    def choose_move(self, engine: Engine, valid_moves: list[Move]) -> Move:
        return random.choice(valid_moves)


class StrategicBot(Bot):
    """
    3-player adaptation of the 2-player StrategicBot.

    Same priority ladder:
      1. Score (+1000)
      2. Hit any opponent in the shared zone (+600)
      3. Land on a rosette (+400)
      4. Enter the board (+50)
      5. Push forward (+target_progress * 2)

    Danger penalty: for every opponent piece that sits behind our landing
    square in the shared zone and is within reach (1–4 steps away), subtract
    500 × P(roll), where P is the binomial probability of that exact roll.
    In a 3-player game each opponent acts once between our turns, so we sum
    the penalty across ALL opponents — a position threatened by two players
    is penalised twice.
    """

    name = "StrategicBot"

    # Binomial probability of each roll total (4 binary dice)
    _ROLL_PROBS = {1: 4 / 16, 2: 6 / 16, 3: 4 / 16, 4: 1 / 16}

    def choose_move(self, engine: Engine, valid_moves: list[Move]) -> Move:
        # Collect all opponent piece progress values (shared-zone pieces only
        # for hit/danger checks; we keep all for completeness)
        opp_pieces: set[int] = set()
        for opp in engine.opponents:
            for p in opp.pieces:
                if p.is_available:
                    opp_pieces.add(p.progress)

        best_move = valid_moves[0]
        best_score = -float("inf")

        for move in valid_moves:
            score = 0.0

            # --- 1. REWARDS ---
            if move.target_progress == FINISH:
                score += 1000  # Always score when possible

            elif 5 <= move.target_progress <= 12 and move.target_progress in opp_pieces:
                score += 600  # Capture an opponent on the shared corridor

            elif move.target_coord in engine.rosettas:
                score += 400  # Safe square + extra turn

            elif move.piece.progress == 0:
                score += 50   # Enter a new piece

            else:
                score += move.target_progress * 2  # Reward forward progress

            # --- 2. DANGER PENALTY ---
            # Only applies to unprotected squares in the shared zone
            if 5 <= move.target_progress <= 12 and move.target_coord not in engine.rosettas:
                for opp_pos in opp_pieces:
                    if 0 < opp_pos < move.target_progress:
                        distance = move.target_progress - opp_pos
                        if 1 <= distance <= 4:
                            # Each threatening opponent piece adds its own
                            # probability-weighted danger cost
                            score -= 500 * self._ROLL_PROBS[distance]

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
