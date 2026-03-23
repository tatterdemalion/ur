import unittest

from ur.cli.tui.board import Board
from ur.cli.tui.widgets import Navigation
from ur.cli.tui.utils import GameUtils
from ur.game.engine import Action, ActionType, Engine, Move, Player
from ur.game.rules import P1_PATH, P2_PATH


def make_game():
    p1 = Player(0, "P1", P1_PATH)
    p2 = Player(1, "P2", P2_PATH)
    return Engine(p1, p2), p1, p2


class TestMoveHints(unittest.TestCase):
    """Tests the UI hint generator to ensure correct text is built."""

    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_hint_score_point_no_phantom_capture(self):
        """
        REGRESSION TEST:
        Moving off the board (target_coord = None) should NOT trigger a capture
        against opponent pieces waiting off the board (coord = None).
        """
        # P1 is about to score
        piece = self.p1.pieces[0]
        piece.progress = 14

        # P2 has a piece waiting in the void
        self.p2.pieces[0].progress = 0

        # P1 rolls a 1, moving from 14 -> 15 (Off the board)
        move = Move(piece=piece, target_progress=15, target_coord=P1_PATH[15])
        hint = GameUtils.build_move_hints(move, self.p2, "Bot")

        self.assertIn("Scores a point!", hint)
        self.assertNotIn("Captures", hint, "Phantom capture detected! None == None bug is back.")

    def test_hint_capture_opponent(self):
        """Moving onto an occupied square should trigger a capture hint."""
        piece = self.p1.pieces[0]
        piece.progress = 4  # Just entering the shared zone

        self.p2.pieces[0].progress = 5  # Opponent is 1 space ahead

        move = Move(piece=piece, target_progress=5, target_coord=P1_PATH[5])
        hint = GameUtils.build_move_hints(move, self.p2, "Bot")

        self.assertIn("Captures Bot's piece!", hint)
        self.assertNotIn("Scores a point!", hint)

    def test_hint_rosetta(self):
        """Landing on a Rosetta should trigger the extra turn hint."""
        piece = self.p1.pieces[0]
        piece.progress = 3  # 1 space away from the first private Rosetta (progress 4)

        move = Move(piece=piece, target_progress=4, target_coord=P1_PATH[4])
        hint = GameUtils.build_move_hints(move, self.p2, "Bot")

        self.assertIn("Lands on Rosetta (Roll again!)", hint)


class TestBoardVisualizer(unittest.TestCase):
    """Tests the UI rendering logic, especially the perspective flipping."""

    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_visualizer_cell_mapping_host(self):
        """Test that pieces map to the correct template variables as the Host (P1)."""
        self.p1.pieces[0].progress = 4  # P1 private path (bottom row, coord 2,0) -> 'o'
        self.p2.pieces[0].progress = 4  # P2 private path (top row, coord 0,0) -> 'a'
        ui = Board(self.game, Navigation())
        cells = ui._get_cells()

        # P1 is local, so their piece is drawn with a circled number ①
        self.assertIn("①", cells["o"])
        # P2 is remote, drawn with a solid dot ●
        self.assertIn("●", cells["a"])

    def test_visualizer_perspective_flip_client(self):
        """
        Test that when the local player is P2, the board rows are inverted so P2
        plays from the bottom of the terminal screen.
        """
        self.p1.pieces[0].progress = 4  # P1 private path (coord 2,0)
        self.p2.pieces[0].progress = 4  # P2 private path (coord 0,0)

        # Initialize the UI pretending we are the Client (P2)
        ui = Board(self.game, Navigation(), local_player=self.p2)
        cells = ui._get_cells()

        # Because the board is flipped, P2's piece at (0,0) should now map to the
        # BOTTOM-left template variable 'o'.
        # Because P2 is local, it should be drawn with a circled number ①.
        self.assertIn("①", cells["o"])

        # P1's piece at (2,0) should now map to the TOP-left template variable 'a'.
        self.assertIn("●", cells["a"])


class TestClientCurrentIdx(unittest.TestCase):
    """
    Regression: client engine's current_idx was never updated, so get_valid_moves
    ran on P1 (the host) instead of P2 (the client), producing wrong move hints.
    """

    def test_get_valid_moves_uses_p2_when_current_idx_is_1(self):
        p1 = Player(0, "Host", P1_PATH)
        p2 = Player(1, "You", P2_PATH)
        engine = Engine(p1, p2)

        # Simulate a restore that doesn't touch current_idx (default 0 = P1's turn)
        p2.pieces[0].progress = 2  # P2 piece ① at Square 2

        # Without the fix, current_idx=0 → get_valid_moves sees P1's pieces
        engine.current_idx = 1  # the fix: set before calling get_valid_moves
        moves = engine.get_valid_moves(1)

        pieces_in_moves = [m.piece for m in moves]
        self.assertIn(p2.pieces[0], pieces_in_moves, "P2's piece must be in valid moves")
        self.assertNotIn(p1.pieces[0], pieces_in_moves, "P1's pieces must not appear")

    def test_move_hint_uses_p2_piece_progress(self):
        """Move hint must show P2's Square 2, not P1's Square 0 (off-board)."""
        p1 = Player(0, "Host", P1_PATH)
        p2 = Player(1, "You", P2_PATH)
        engine = Engine(p1, p2)

        p2.pieces[0].progress = 2
        engine.current_idx = 1
        moves = engine.get_valid_moves(1)
        move = next(m for m in moves if m.piece is p2.pieces[0])

        self.assertEqual(move.piece.progress, 2)
        self.assertEqual(move.target_progress, 3)


class TestFormatActionPerspective(unittest.TestCase):
    def test_format_action_perspective(self):
        action = Action(
            player_idx=1,
            roll=2,
            piece_id=3,
            action_type=ActionType.MOVED,
            hit=False,
            rosetta=False,
            target_progress=5,
        )
        # When local_player_idx matches action.player_idx, subject is "You"
        result_local = GameUtils.format_action(action, local_player_idx=1, opponent_name="Alice")
        self.assertTrue(result_local.startswith("You"), f"Expected 'You...', got: {result_local!r}")

        # When local_player_idx does NOT match, subject is the opponent's name
        result_remote = GameUtils.format_action(action, local_player_idx=0, opponent_name="Alice")
        self.assertTrue(result_remote.startswith("Alice"), f"Expected 'Alice...', got: {result_remote!r}")


if __name__ == "__main__":
    unittest.main()
