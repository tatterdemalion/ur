from ur.game import Engine, Player
from ur.rules import P1_PATH, P2_PATH


class UrEnvironment:
    def __init__(self):
        self.game = None

    def reset(self, p1_name="P1", p2_name="P2"):
        """Starts a fresh game and advances until a player actually has a choice to make."""
        # Clean initialization using standard paths
        p1 = Player(p1_name, P1_PATH, "●")
        p2 = Player(p2_name, P2_PATH, "●")
        self.game = Engine(p1, p2)

        return self._advance_to_next_decision()

    def _get_state(self):
        """
        Translates the board into a simple numerical dictionary so a bot can 'see' it.
        We return the progress of the active player's pieces and the opponent's pieces.
        """
        active_p = self.game.current_player
        opp_p = self.game.opponent

        return {
            "my_pieces": sorted([p.progress for p in active_p.pieces]),
            "opp_pieces": sorted([p.progress for p in opp_p.pieces]),
            "current_roll": self.current_roll,
        }

    def _advance_to_next_decision(self):
        """
        Rolls dice and skips turns automatically if a player has 0 valid moves.
        Pauses and returns the state as soon as a bot actually needs to make a decision.
        """
        while True:
            if self.game.players[0].has_won() or self.game.players[1].has_won():
                return self._get_state(), [], True, self._get_final_reward()

            self.current_roll = self.game.roll_dice()
            valid_moves = self.game.get_valid_moves(self.current_roll)

            if not valid_moves:
                # No moves? The environment handles skipping the turn automatically.
                self.game.switch_player()
                continue

            # We found a valid move! Pause and hand control to the bots.
            return self._get_state(), valid_moves, False, 0

    def step(self, chosen_move):
        """
        Takes the bot's chosen piece, executes it, calculates the reward,
        and fast-forwards to the next decision.
        """
        # Track state before move to calculate rewards
        opp_active_before = sum(1 for p in self.game.opponent.pieces if p.is_available)
        scored_before = sum(1 for p in self.game.current_player.pieces if p.progress == 15)

        # Execute
        self.game.execute_move(chosen_move, self.current_roll)

        # Calculate intermediate rewards (Great for training RL later)
        reward = 0
        opp_active_after = sum(1 for p in self.game.opponent.pieces if p.is_available)
        scored_after = sum(1 for p in self.game.current_player.pieces if p.progress == 15)

        if scored_after > scored_before:
            reward += 10.0  # Big reward for scoring
        if opp_active_after < opp_active_before:
            reward += 5.0  # Medium reward for a hit

        # Fast-forward to the next time someone needs to make a choice
        next_state, next_valid_moves, done, final_reward = self._advance_to_next_decision()

        if done:
            reward += final_reward

        return next_state, next_valid_moves, reward, done

    def _get_final_reward(self):
        """Huge payout for actually winning the game."""
        return 100.0 if self.game.current_player.has_won() else -100.0
