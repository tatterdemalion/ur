import time

from ur.ai.bots import Bot
from ur.cli.board import Board
from ur.cli.constants import C_BOLD_TEXT, C_ITALIC, C_P1, C_P2, C_RESET, C_ROSETTA, C_TUTORIAL
from ur.cli.i18n import t
from ur.cli.match import Match
from ur.cli.utils import GameUtils
from ur.game import Action, ActionType, Engine, Move, Player
from ur.rules import P1_PATH, P2_PATH


def _make_snapshot(p1_pieces: dict[int, int], p2_pieces: dict[int, int]) -> dict:
    """Build a minimal board snapshot compatible with engine.restore()."""
    return {
        "p1_pieces": {str(i): p1_pieces.get(i, 0) for i in range(1, 8)},
        "p2_pieces": {str(i): p2_pieces.get(i, 0) for i in range(1, 8)},
    }


class TutorialEngine(Engine):
    """Engine that returns a rigged roll when one is set, then falls back to random."""

    def __init__(self, p1: Player, p2: Player):
        super().__init__(p1, p2)
        self.rigged_roll: "int | None" = None

    def roll_dice(self) -> int:
        if self.rigged_roll is not None:
            roll = self.rigged_roll
            self.rigged_roll = None
            return roll
        return super().roll_dice()


class TutorialBot(Bot):
    """Bot that moves a specific piece ID set by the state machine each turn."""

    name = "Ur-Namma"

    def __init__(self):
        self.rigged_move_id: "int | None" = None

    def choose_move(self, state: dict, valid_moves: list[Move], player: Player) -> Move:  # noqa: ARG002
        if self.rigged_move_id is not None:
            move_id = self.rigged_move_id
            self.rigged_move_id = None
            chosen = next((m for m in valid_moves if m.piece.identifier == move_id), None)
            if chosen is None:
                raise RuntimeError("Tutorial script asked for invalid bot move!")
            return chosen
        return valid_moves[0]


class TutorialMatch(Match):
    """Interactive state-machine tutorial that walks the player through the game rules."""

    def __init__(self, navigation):
        super().__init__(navigation)
        self.p1 = Player(0, t("player.you"), P1_PATH)
        self.p2 = Player(1, TutorialBot.name, P2_PATH)
        self.engine = TutorialEngine(self.p1, self.p2)
        self._bot = TutorialBot()
        self.ui = Board(self.engine, navigation)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _narrate(self, key: str, **kwargs):
        text = t(key, **kwargs)
        print(f"\n{C_TUTORIAL}{text}{C_RESET}\n")

    def _pause(self):
        text = t("tuto.press_enter", bold=C_BOLD_TEXT, reset=C_TUTORIAL)
        input(f"{C_TUTORIAL}{text}{C_RESET}")

    def _get_confirmed_move(self, move: Move) -> bool:
        """Prompt that accepts any input and confirms once Enter is pressed.
        Returns False if the user navigated away (menu/quit), True otherwise."""
        piece_sym = f"{C_P1}{chr(9312 + move.piece.identifier - 1)}{C_RESET}"
        while True:
            raw = input(f"{C_TUTORIAL}[ Enter for {piece_sym}{C_TUTORIAL} ]:{C_RESET} ").strip()
            if not raw:
                return True
            if self.navigation.check_global_commands(raw):
                return False

    def _reset_last_action(self):
        """Reset last_action to the neutral 'game started' state after a teleport."""
        self.engine.last_action = Action(
            player_idx=0, roll=0, piece_id=None,
            action_type=ActionType.STARTED, hit=False, rosetta=False,
        )

    def _show_dice_explainer(self):
        """Teaches the dice mechanic by demoing all five possible outcomes, then continues."""
        self.navigation.clear()
        print(f"\n{C_TUTORIAL}{t('tuto.dice_explainer')}{C_RESET}\n")
        self._pause()

        for demo_roll in range(5):
            GameUtils.animate_dice("", C_P1, demo_roll)
            print(f"{C_TUTORIAL}{t('tuto.dice_demo_result', roll=str(demo_roll))}{C_RESET}\n")
            time.sleep(1.2)

        time.sleep(1)
        self.navigation.clear()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def start(self, start_step: int = 1):
        self.navigation.clear()

        if start_step == 1:
            self._narrate(
                "tuto.intro",
                p1=C_P1, p2=C_P2, p2_name=self.p2.name,
                bold=C_BOLD_TEXT, reset=C_RESET + C_TUTORIAL,
            )
            self._pause()

        tutorial_step = start_step
        allowed_piece_ids: list[int] = []
        color_kwargs = dict(
            p1=C_P1, p2=C_P2, p2_name=self.p2.name,
            rosetta=C_ROSETTA, bold=C_BOLD_TEXT,
            reset=C_RESET + C_TUTORIAL,
        )

        while tutorial_step <= 7:
            # ── A. Step setup ────────────────────────────────────────────
            if tutorial_step == 1:
                # P1 rolls 2, enters the board.
                self.engine.current_idx = 0
                self.engine.rigged_roll = 2
                allowed_piece_ids = [1]

            elif tutorial_step == 2:
                # Bot's turn: P2 rolls 1, moves piece 1.
                self.engine.current_idx = 1
                self.engine.rigged_roll = 1
                self._bot.rigged_move_id = 1

            elif tutorial_step == 3:
                # P1 rolls 2, piece 1 lands on rosetta (progress 4 = coord (2,0)).
                self.engine.current_idx = 0
                self.engine.rigged_roll = 2
                allowed_piece_ids = [1]

            elif tutorial_step == 4:
                # Extra turn from the rosetta — P1 rolls 3, advances piece 1.
                # current_idx stays 0 (engine didn't switch after rosetta).
                self.engine.rigged_roll = 3
                allowed_piece_ids = [1]

            elif tutorial_step == 5:
                # P1① at 6=(1,1), P2① at 9=(1,4). Roll 3: ①→9=(1,4), captures P2①.
                self._narrate("tuto.scene5", **color_kwargs)
                self._pause()
                self.engine.restore(_make_snapshot({1: 6}, {1: 9}))
                self.engine.current_idx = 0
                self._reset_last_action()
                self.engine.rigged_roll = 3
                allowed_piece_ids = [1]

            elif tutorial_step == 6:
                # P1① at 5=(1,0) = square e. P2② at 8=(1,3)✿ central rosetta.
                # Roll 3: ①+3=8 is blocked by the safe rosetta, so only ② (0→3) is valid.
                # The player sees ① sitting right next to the rosetta but unable to capture.
                self._narrate("tuto.scene6", **color_kwargs)
                self._pause()
                self.engine.restore(_make_snapshot({1: 5}, {1: 0, 2: 8}))
                self.engine.current_idx = 0
                self._reset_last_action()
                self.engine.rigged_roll = 3
                allowed_piece_ids = []  # ① is blocked by engine rules, only ② valid

            elif tutorial_step == 7:
                # P1① at 12 (from step 6). Roll 3 → 15=FINISH, scores.
                self._narrate("tuto.scene7", **color_kwargs)
                self._pause()
                self.engine.restore(_make_snapshot({1: 12}, {1: 0, 2: 8}))
                self.engine.current_idx = 0
                self._reset_last_action()
                self.engine.rigged_roll = 3
                allowed_piece_ids = [1]

            # ── B. Turn execution ────────────────────────────────────────
            roll = self.engine.roll_dice()
            valid_moves = self.engine.get_valid_moves(roll)

            if tutorial_step == 1:
                self._show_dice_explainer()

            is_human_turn = self.engine.current_player == self.p1
            player_color = C_P1 if is_human_turn else C_P2
            turn_text = (
                t("match.your_turn")
                if is_human_turn
                else t("match.opponent_turn", name=self.p2.name)
            )

            # Formatted roll string: coloured dots + italic count, e.g. "●● (2)".
            dots = f"{C_P1}{'●' * roll}{'○' * (4 - roll)}{C_RESET + C_TUTORIAL}"
            roll_str = f"{dots} {C_ITALIC}({roll}){C_RESET + C_TUTORIAL}"

            hint_text = t(f"tuto.step{tutorial_step}.hint", roll=roll_str, **color_kwargs)

            def _redraw(show_labels: bool = True):
                self.update_display(show_labels=show_labels)
                print(f"\n{C_TUTORIAL}{hint_text}{C_RESET}\n")

            self.update_display(show_labels=True)
            GameUtils.animate_dice(turn_text, player_color, roll)
            print(f"\n{C_TUTORIAL}{hint_text}{C_RESET}\n")

            if not valid_moves:
                # Should not happen in a well-scripted tutorial, but handle gracefully.
                self.engine.skip_turn(roll)
                tutorial_step += 1
                self._pause()
                continue

            if is_human_turn:
                restricted_moves = [m for m in valid_moves if m.piece.identifier in allowed_piece_ids]
                if not restricted_moves:
                    restricted_moves = valid_moves

                if tutorial_step <= 3:
                    # Steps 1–3: piece is pre-selected, just wait for Enter.
                    chosen_move = restricted_moves[0]
                    if not self._get_confirmed_move(chosen_move):
                        return
                elif tutorial_step == 4:
                    # Step 4: free choice, help hints available.
                    chosen_move = GameUtils.get_human_move(
                        valid_moves, self.p2, self.p2.name, self.navigation,
                        redraw=_redraw,
                    )
                    if chosen_move is None:
                        return
                else:
                    chosen_move = GameUtils.get_human_move(
                        restricted_moves, self.p2, self.p2.name, self.navigation,
                        redraw=_redraw,
                    )
                    if chosen_move is None:
                        return
            else:
                self._pause()
                state = {
                    "my_pieces": sorted([p.progress for p in self.engine.current_player.pieces]),
                    "opp_pieces": sorted([p.progress for p in self.engine.opponent.pieces]),
                    "current_roll": roll,
                }
                chosen_move = self._bot.choose_move(state, valid_moves, self.engine.current_player)
                time.sleep(1.2)

            piece_sym = f"{C_P1}{chr(9312 + chosen_move.piece.identifier - 1)}{C_RESET + C_TUTORIAL}"
            self.engine.execute_move(chosen_move, roll)
            self.update_display(show_labels=True)
            self._narrate(f"tuto.step{tutorial_step}", piece=piece_sym, **color_kwargs)
            tutorial_step += 1
            self._pause()

        # ── Outro ────────────────────────────────────────────────────────
        self._narrate("tuto.outro")
        self._pause()
        self.navigation.clear()
