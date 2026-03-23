import dataclasses
import unittest

from ur.game.engine import Action, ActionType, Engine, Move, Player
from ur.game.rules import FINISH, P1_PATH, P2_PATH, ROSETTAS


def make_game():
    p1 = Player(0, "P1", P1_PATH)
    p2 = Player(1, "P2", P2_PATH)
    return Engine(p1, p2), p1, p2


class TestPiece(unittest.TestCase):
    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_initial_progress_is_zero(self):
        for piece in self.p1.pieces:
            self.assertEqual(piece.progress, 0)

    def test_coord_at_progress_zero_is_none(self):
        # Progress 0 maps to None (off-board / waiting area)
        self.assertIsNone(self.p1.pieces[0].coord)

    def test_coord_at_valid_progress(self):
        piece = self.p1.pieces[0]
        piece.progress = 5
        self.assertEqual(piece.coord, P1_PATH[5])

    def test_is_available_in_range(self):
        piece = self.p1.pieces[0]
        piece.progress = 7
        self.assertTrue(piece.is_available)

    def test_is_available_false_when_finished(self):
        piece = self.p1.pieces[0]
        piece.progress = FINISH
        self.assertFalse(piece.is_available)

    def test_move_dataclass_fields(self):
        piece = self.p1.pieces[0]
        piece.progress = 3
        move = Move(piece=piece, target_progress=5, target_coord=P1_PATH[5])
        self.assertEqual(move.target_progress, 5)
        self.assertEqual(move.target_coord, P1_PATH[5])
        self.assertIs(move.piece, piece)


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_player_has_seven_pieces(self):
        self.assertEqual(len(self.p1.pieces), 7)

    def test_has_won_false_initially(self):
        self.assertFalse(self.p1.has_won())

    def test_has_won_true_when_all_pieces_finished(self):
        for piece in self.p1.pieces:
            piece.progress = FINISH
        self.assertTrue(self.p1.has_won())

    def test_has_won_false_when_one_piece_remains(self):
        for piece in self.p1.pieces[:-1]:
            piece.progress = FINISH
        self.assertFalse(self.p1.has_won())


class TestEngineSetup(unittest.TestCase):
    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_initial_turn_is_p1(self):
        self.assertEqual(self.game.current_idx, 0)
        self.assertIs(self.game.current_player, self.p1)

    def test_opponent_is_p2_at_start(self):
        self.assertIs(self.game.opponent, self.p2)

    def test_switch_player(self):
        self.game.switch_player()
        self.assertEqual(self.game.current_idx, 1)
        self.assertIs(self.game.current_player, self.p2)

    def test_switch_player_twice_returns_to_p1(self):
        self.game.switch_player()
        self.game.switch_player()
        self.assertEqual(self.game.current_idx, 0)

    def test_winner_is_none_initially(self):
        self.assertIsNone(self.game.winner)

    def test_winner_detected_when_p1_wins(self):
        for piece in self.p1.pieces:
            piece.progress = FINISH
        self.assertIs(self.game.winner, self.p1)

    def test_winner_detected_when_p2_wins(self):
        for piece in self.p2.pieces:
            piece.progress = FINISH
        self.assertIs(self.game.winner, self.p2)

    def test_roll_dice_range(self):
        for _ in range(200):
            roll = self.game.roll_dice()
            self.assertIn(roll, range(5))


class TestGetStats(unittest.TestCase):
    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_initial_stats(self):
        stats = self.game.get_stats()
        self.assertEqual(stats.p1_score, 0)
        self.assertEqual(stats.p1_waiting, 7)
        self.assertEqual(stats.p2_score, 0)
        self.assertEqual(stats.p2_waiting, 7)

    def test_stats_reflect_scored_and_in_play(self):
        self.p1.pieces[0].progress = FINISH
        self.p1.pieces[1].progress = 5  # in play, not waiting
        stats = self.game.get_stats()
        self.assertEqual(stats.p1_score, 1)
        self.assertEqual(stats.p1_waiting, 5)  # 7 - 1 scored - 1 in play

    def test_stats_p2_scored(self):
        for piece in self.p2.pieces[:3]:
            piece.progress = FINISH
        stats = self.game.get_stats()
        self.assertEqual(stats.p2_score, 3)
        self.assertEqual(stats.p2_waiting, 4)


class TestValidMoves(unittest.TestCase):
    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_zero_roll_gives_no_moves(self):
        self.assertEqual(self.game.get_valid_moves(0), [])

    def test_all_pieces_available_on_roll_from_start(self):
        # All pieces at 0, roll 1 => all 7 pieces can enter the board
        moves = self.game.get_valid_moves(1)
        self.assertEqual(len(moves), 7)

    def test_cannot_land_on_own_piece(self):
        self.p1.pieces[0].progress = 2
        # pieces[1] is at 0; roll 2 would land it on progress 2 — blocked
        moves = self.game.get_valid_moves(2)
        move_pieces = [m.piece for m in moves]
        self.assertNotIn(self.p1.pieces[1], move_pieces)

    def test_cannot_overshoot_finish(self):
        self.p1.pieces[0].progress = 14
        # Roll 2 overshoots FINISH (15) — not valid
        moves = self.game.get_valid_moves(2)
        move_pieces = [m.piece for m in moves]
        self.assertNotIn(self.p1.pieces[0], move_pieces)

    def test_exact_roll_to_finish_is_valid(self):
        self.p1.pieces[0].progress = 14
        moves = self.game.get_valid_moves(1)
        move_pieces = [m.piece for m in moves]
        self.assertIn(self.p1.pieces[0], move_pieces)

    def test_finished_piece_excluded_from_moves(self):
        self.p1.pieces[0].progress = FINISH
        moves = self.game.get_valid_moves(1)
        move_pieces = [m.piece for m in moves]
        self.assertNotIn(self.p1.pieces[0], move_pieces)

    def test_cannot_hit_opponent_on_rosetta(self):
        # Central shared Rosetta is at progress 8 (coord 1,3)
        self.p1.pieces[0].progress = 8
        self.p2.pieces[0].progress = 7
        self.game.current_idx = 1  # P2's turn

        moves = self.game.get_valid_moves(1)
        move_pieces = [m.piece for m in moves]
        self.assertNotIn(self.p2.pieces[0], move_pieces)

    def test_can_hit_opponent_not_on_rosetta(self):
        # P1 is at progress 5 (shared zone, not a rosetta)
        self.p1.pieces[0].progress = 5
        self.p2.pieces[0].progress = 4
        self.game.current_idx = 1  # P2's turn

        moves = self.game.get_valid_moves(1)
        move_pieces = [m.piece for m in moves]
        self.assertIn(self.p2.pieces[0], move_pieces)

    def test_multiple_pieces_can_score_simultaneously(self):
        # Two P1 pieces at 14: both should be valid with roll 1
        self.p1.pieces[0].progress = 14
        self.p1.pieces[1].progress = 14
        moves = self.game.get_valid_moves(1)
        move_pieces = [m.piece for m in moves]
        self.assertIn(self.p1.pieces[0], move_pieces)
        self.assertIn(self.p1.pieces[1], move_pieces)


class TestExecuteMove(unittest.TestCase):
    def setUp(self):
        self.game, self.p1, self.p2 = make_game()

    def test_move_advances_piece(self):
        piece = self.p1.pieces[0]
        move = Move(piece=piece, target_progress=3, target_coord=P1_PATH[3])
        self.game.execute_move(move, 3)
        self.assertEqual(piece.progress, 3)

    def test_move_passes_turn(self):
        piece = self.p1.pieces[0]
        move = Move(piece=piece, target_progress=1, target_coord=P1_PATH[1])
        self.game.execute_move(move, 1)
        self.assertEqual(self.game.current_idx, 1)

    def test_hit_opponent_resets_their_piece(self):
        # P1 at progress 5, P2 moves there
        self.p1.pieces[0].progress = 5
        self.p2.pieces[0].progress = 4
        self.game.current_idx = 1

        piece = self.p2.pieces[0]
        move = Move(piece=piece, target_progress=5, target_coord=P2_PATH[5])
        self.game.execute_move(move, 1)

        self.assertEqual(self.p2.pieces[0].progress, 5)
        self.assertEqual(self.p1.pieces[0].progress, 0)

    def test_hit_opponent_last_action_message(self):
        self.p1.pieces[0].progress = 5
        self.p2.pieces[0].progress = 4
        self.game.current_idx = 1

        piece = self.p2.pieces[0]
        move = Move(piece=piece, target_progress=5, target_coord=P2_PATH[5])
        self.game.execute_move(move, 1)

        self.assertTrue(self.game.last_action.hit)
        self.assertEqual(self.game.last_action.action_type, ActionType.MOVED)

    def test_rosetta_grants_extra_turn(self):
        # P1 roll 4 lands on private Rosetta at progress 4 (coord 2,0)
        self.assertIn(P1_PATH[4], ROSETTAS)
        piece = self.p1.pieces[0]
        move = Move(piece=piece, target_progress=4, target_coord=P1_PATH[4])
        self.game.execute_move(move, 4)
        self.assertEqual(self.game.current_idx, 0)  # still P1's turn

    def test_shared_rosetta_grants_extra_turn(self):
        # Progress 8 => coord (1,3) which is a rosetta
        self.assertIn(P1_PATH[8], ROSETTAS)
        piece = self.p1.pieces[0]
        piece.progress = 4
        move = Move(piece=piece, target_progress=8, target_coord=P1_PATH[8])
        self.game.execute_move(move, 4)
        self.assertEqual(self.game.current_idx, 0)

    def test_scoring_does_not_grant_extra_turn(self):
        # Landing on FINAL_SQUARE (progress 14, coord (2,6)) which is a rosetta,
        # but scoring (progress 15) should NOT grant extra turn
        piece = self.p1.pieces[0]
        piece.progress = 14
        move = Move(piece=piece, target_progress=FINISH, target_coord=P1_PATH[FINISH])
        self.game.execute_move(move, 1)
        self.assertEqual(piece.progress, FINISH)
        self.assertEqual(self.game.current_idx, 1)  # turn passed

    def test_scoring_sets_last_action(self):
        piece = self.p1.pieces[0]
        piece.progress = 14
        move = Move(piece=piece, target_progress=FINISH, target_coord=P1_PATH[FINISH])
        self.game.execute_move(move, 1)
        self.assertEqual(self.game.last_action.action_type, ActionType.SCORED)

    def test_winning_does_not_switch_player(self):
        # All pieces at 14 except last; last one scores to win
        for piece in self.p1.pieces[:-1]:
            piece.progress = FINISH
        last = self.p1.pieces[-1]
        last.progress = 14
        move = Move(piece=last, target_progress=FINISH, target_coord=P1_PATH[FINISH])
        self.game.execute_move(move, 1)

        self.assertTrue(self.p1.has_won())
        # current_idx stays at 0 — no switch after a win
        self.assertEqual(self.game.current_idx, 0)


class TestActionSerialization(unittest.TestCase):
    def test_action_serialization_roundtrip(self):
        original = Action(
            player_idx=1,
            roll=2,
            piece_id=3,
            action_type=ActionType.MOVED,
            hit=False,
            rosetta=False,
            target_progress=8,
        )
        serialized = dataclasses.asdict(original)
        restored = Action(**serialized)
        self.assertEqual(restored, original)
        self.assertEqual(restored.target_progress, 8)


if __name__ == "__main__":
    unittest.main()
