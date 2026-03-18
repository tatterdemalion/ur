import random
from ur.game import Player, Piece, ROSETTAS

class Bot:
    name = "Bot"

    def choose_move(self, state: dict, valid_moves: list, player: Player) -> Piece:
        raise NotImplementedError("Bots must implement their own logic!")


class RandomBot(Bot):
    name = "RandomBot"

    def choose_move(self, state: dict, valid_moves: list, player: Player):
        return random.choice(valid_moves)


class GreedyBot(Bot):
    name = "GreedyBot"

    def choose_move(self, state: dict, valid_moves: list, player: Player):
        best_move = valid_moves[0]
        best_score = -1

        for piece in valid_moves:
            target_progress = piece.progress + state["current_roll"]
            target_coord = player.path[target_progress]

            score = 0
            # Priority 1: Scoring a point
            if target_progress == 15:
                score = 1000
            # Priority 2: Hitting an opponent (Shared zone is progress 5-12)
            elif 5 <= target_progress <= 12 and target_progress in state["opp_pieces"]:
                score = 500
            # Priority 3: Landing on a Rosetta
            elif target_coord in ROSETTAS:
                score = 300
            # Priority 4: Getting a piece onto the board
            elif piece.progress == 0:
                score = 100

            if score > best_score:
                best_score = score
                best_move = piece

        return best_move


class StrategicBot(Bot):
    name = "StrategicBot"

    def choose_move(self, state: dict, valid_moves: list, player: Player):
        best_move = valid_moves[0]
        best_score = -float('inf')

        # The mathematical probability of each dice roll
        roll_probs = {1: 4/16, 2: 6/16, 3: 4/16, 4: 1/16}

        for piece in valid_moves:
            target_progress = piece.progress + state["current_roll"]
            target_coord = player.path[target_progress]

            score = 0

            # --- 1. REWARDS ---
            if target_progress == 15:
                score += 1000  # Always score if possible
            elif 5 <= target_progress <= 12 and target_progress in state["opp_pieces"]:
                score += 600   # Hit an opponent!
            elif target_coord in ROSETTAS:
                score += 400   # Safe space + extra turn
            elif piece.progress == 0:
                score += 50    # Bring a new piece onto the board
            else:
                score += target_progress * 2 # Slight reward for pushing pieces forward

            # --- 2. PENALTIES (The Smart Part) ---
            # If we land in the shared combat zone (5-12) and NOT on a Rosetta
            if 5 <= target_progress <= 12 and target_coord not in ROSETTAS:
                for opp_pos in state["opp_pieces"]:
                    # Is the opponent behind us on the track?
                    if 0 < opp_pos < target_progress:
                        distance = target_progress - opp_pos
                        # Can they hit us on their next turn?
                        if 1 <= distance <= 4:
                            # We multiply the penalty by the exact probability of them rolling that number
                            danger_penalty = 500 * roll_probs[distance]
                            score -= danger_penalty

            if score > best_score:
                best_score = score
                best_move = piece

        return best_move
