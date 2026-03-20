import random

from ur.game import Move, Player
from ur.rules import FINISH, ROSETTAS


class Bot:
    name = "Bot"

    def choose_move(self, state: dict, valid_moves: list[Move], player: Player) -> Move:
        raise NotImplementedError("Bots must implement their own logic!")


class RandomBot(Bot):
    name = "RandomBot"

    def choose_move(self, state: dict, valid_moves: list[Move], player: Player) -> Move:
        return random.choice(valid_moves)


class GreedyBot(Bot):
    name = "GreedyBot"

    def choose_move(self, state: dict, valid_moves: list[Move], player: Player) -> Move:
        best_move = valid_moves[0]
        best_score = -1

        for move in valid_moves:
            score = 0
            # Priority 1: Scoring a point
            if move.target_progress == FINISH:
                score = 1000
            # Priority 2: Hitting an opponent (Shared zone is progress 5-12)
            elif 5 <= move.target_progress <= 12 and move.target_progress in state["opp_pieces"]:
                score = 500
            # Priority 3: Landing on a Rosetta
            elif move.target_coord in ROSETTAS:
                score = 300
            # Priority 4: Getting a piece onto the board
            elif move.piece.progress == 0:
                score = 100

            if score > best_score:
                best_score = score
                best_move = move

        return best_move


class StrategicBot(Bot):
    name = "StrategicBot"

    def choose_move(self, state: dict, valid_moves: list[Move], player: Player) -> Move:
        best_move = valid_moves[0]
        best_score = -float("inf")

        # The mathematical probability of each dice roll
        roll_probs = {1: 4 / 16, 2: 6 / 16, 3: 4 / 16, 4: 1 / 16}

        for move in valid_moves:
            score = 0

            # --- 1. REWARDS ---
            if move.target_progress == FINISH:
                score += 1000  # Always score if possible
            elif 5 <= move.target_progress <= 12 and move.target_progress in state["opp_pieces"]:
                score += 600  # Hit an opponent!
            elif move.target_coord in ROSETTAS:
                score += 400  # Safe space + extra turn
            elif move.piece.progress == 0:
                score += 50  # Bring a new piece onto the board
            else:
                score += move.target_progress * 2  # Slight reward for pushing pieces forward

            # --- 2. PENALTIES (The Smart Part) ---
            # If we land in the shared combat zone (5-12) and NOT on a Rosetta
            if 5 <= move.target_progress <= 12 and move.target_coord not in ROSETTAS:
                for opp_pos in state["opp_pieces"]:
                    # Is the opponent behind us on the track?
                    if 0 < opp_pos < move.target_progress:
                        distance = move.target_progress - opp_pos
                        # Can they hit us on their next turn?
                        if 1 <= distance <= 4:
                            danger_penalty = 500 * roll_probs[distance]
                            score -= danger_penalty

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
