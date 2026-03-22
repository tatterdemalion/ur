import time
from dataclasses import dataclass
from typing import Callable, Optional

from ur.ai.bots import Bot
from ur.cli.board import Board
from ur.cli.constants import C_BOLD_TEXT, C_ITALIC, C_P1, C_P2, C_RESET, C_ROSETTA, C_TUTORIAL
from ur.cli.i18n import t
from ur.cli.match import Match
from ur.cli.utils import GameUtils
from ur.game import Action, ActionType, Engine, Move, Player
from ur.rules import FINISH, P1_PATH, P2_PATH, ROSETTAS


def _make_snapshot(p1_pieces: dict[int, int], p2_pieces: dict[int, int]) -> dict:
    """Build a minimal board snapshot compatible with engine.restore()."""
    return {
        "p1_pieces": {str(i): p1_pieces.get(i, 0) for i in range(1, 8)},
        "p2_pieces": {str(i): p2_pieces.get(i, 0) for i in range(1, 8)},
    }


@dataclass
class TutorialStep:
    step_num: int
    narrate_key: str
    active_player_idx: int
    rigged_roll: int
    allowed_piece_ids: list[int]
    bot_move_id: Optional[int] = None
    board_setup: Optional[dict] = None
    scene_narrate_key: Optional[str] = None  # narrated + paused before board setup
    pre_turn_hook: Optional[Callable[["TutorialMatch"], None]] = None
    is_free_choice: bool = False


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


# Build the step table after TutorialMatch is defined (forward reference resolved via lambda).
# Steps are defined as a module-level constant after the class definition.

TUTORIAL_STEPS: "list[TutorialStep]" = []  # populated below


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

    def _play_bot_turns(self):
        """Play out any extra bot turns that follow a human rosetta landing."""
        while self.engine.current_player == self.p2:
            roll = self.engine.roll_dice()
            valid_moves = self.engine.get_valid_moves(roll)
            self.update_display(show_labels=True)
            GameUtils.animate_dice(
                t("match.opponent_turn", name=self.p2.name), C_P2, roll
            )
            if not valid_moves:
                self.engine.skip_turn(roll)
                self._pause()
                continue
            state = {
                "my_pieces": sorted([p.progress for p in self.engine.current_player.pieces]),
                "opp_pieces": sorted([p.progress for p in self.engine.opponent.pieces]),
                "current_roll": roll,
            }
            chosen = self._bot.choose_move(state, valid_moves, self.engine.current_player)
            time.sleep(1.2)
            self.engine.execute_move(chosen, roll)
            self.update_display(show_labels=True)
            self._pause()

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

        for step_data in TUTORIAL_STEPS[start_step - 1:]:
            # 1. Scene intro narration (before board teleport)
            if step_data.scene_narrate_key:
                self._narrate(
                    step_data.scene_narrate_key,
                    p1=C_P1, p2=C_P2, p2_name=self.p2.name,
                    rosetta=C_ROSETTA, bold=C_BOLD_TEXT, reset=C_RESET + C_TUTORIAL,
                )
                self._pause()

            # 2. Apply Board Setup & State
            if step_data.board_setup:
                self.engine.restore(step_data.board_setup)
                self._reset_last_action()

            self.engine.current_idx = step_data.active_player_idx
            self.engine.rigged_roll = step_data.rigged_roll
            if step_data.bot_move_id is not None:
                self._bot.rigged_move_id = step_data.bot_move_id

            # 3. Pre-Turn Hook
            if step_data.pre_turn_hook:
                step_data.pre_turn_hook(self)

            # 4. Execute Turn Loop (Roll, Valid Moves, Animate)
            roll = self.engine.roll_dice()
            valid_moves = self.engine.get_valid_moves(roll)

            is_human_turn = self.engine.current_player == self.p1
            player_color = C_P1 if is_human_turn else C_P2
            turn_text = (
                t("match.your_turn")
                if is_human_turn
                else t("match.opponent_turn", name=self.p2.name)
            )

            self.update_display(show_labels=True)
            GameUtils.animate_dice(turn_text, player_color, roll)

            # Print Tutorial Hint
            dots = f"{C_P1}{'●' * roll}{'○' * (4 - roll)}{C_RESET + C_TUTORIAL}"
            roll_str = f"{dots} {C_ITALIC}({roll}){C_RESET + C_TUTORIAL}"
            hint_text = t(
                step_data.narrate_key + ".hint",
                roll=roll_str, p1=C_P1, p2=C_P2, p2_name=self.p2.name,
                rosetta=C_ROSETTA, bold=C_BOLD_TEXT, reset=C_RESET + C_TUTORIAL,
            )
            print(f"\n{C_TUTORIAL}{hint_text}{C_RESET}\n")

            # 5. Get Move & Execute
            if not valid_moves:
                self.engine.skip_turn(roll)
                self._pause()
                continue

            if is_human_turn:
                restricted_moves = (
                    [m for m in valid_moves if m.piece.identifier in step_data.allowed_piece_ids]
                    if step_data.allowed_piece_ids
                    else valid_moves
                )

                if not step_data.is_free_choice:
                    chosen_move = restricted_moves[0]
                    if not self._get_confirmed_move(chosen_move):
                        return
                else:
                    chosen_move = GameUtils.get_human_move(
                        restricted_moves if restricted_moves else valid_moves,
                        self.p2, self.p2.name, self.navigation,
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
            self._narrate(
                step_data.narrate_key,
                piece=piece_sym, p1=C_P1, p2=C_P2, p2_name=self.p2.name,
                rosetta=C_ROSETTA, bold=C_BOLD_TEXT, reset=C_RESET + C_TUTORIAL,
            )
            self._pause()

            # 6. Intercept Bot Extra Turns
            if is_human_turn and chosen_move.target_coord in ROSETTAS and chosen_move.target_progress < FINISH:
                self._play_bot_turns()

        self._narrate("tuto.outro")
        self._pause()
        self.navigation.clear()

# ---------------------------------------------------------------------------
# Step table — defined after TutorialMatch so lambdas can reference it
# ---------------------------------------------------------------------------

TUTORIAL_STEPS = [
    TutorialStep(
        step_num=1,
        narrate_key="tuto.step1",
        active_player_idx=0,
        rigged_roll=2,
        allowed_piece_ids=[1],
        board_setup=_make_snapshot({}, {}),
        pre_turn_hook=lambda m: m._show_dice_explainer(),
    ),
    TutorialStep(
        step_num=2,
        narrate_key="tuto.step2",
        active_player_idx=1,
        rigged_roll=1,
        allowed_piece_ids=[],
        bot_move_id=1,
        board_setup=_make_snapshot({1: 2}, {}),
    ),
    TutorialStep(
        step_num=3,
        narrate_key="tuto.step3",
        active_player_idx=0,
        rigged_roll=2,
        allowed_piece_ids=[1],
        board_setup=_make_snapshot({1: 2}, {1: 1}),
    ),
    TutorialStep(
        step_num=4,
        narrate_key="tuto.step4",
        active_player_idx=0,
        rigged_roll=3,
        allowed_piece_ids=[],
        board_setup=_make_snapshot({1: 4, 2: 2, }, {1: 1}),
        is_free_choice=True,
    ),
    TutorialStep(
        step_num=5,
        narrate_key="tuto.step5",
        active_player_idx=0,
        rigged_roll=3,
        allowed_piece_ids=[1],
        board_setup=_make_snapshot({1: 6}, {1: 9}),
        scene_narrate_key="tuto.scene5",
    ),
    TutorialStep(
        step_num=6,
        narrate_key="tuto.step6",
        active_player_idx=0,
        rigged_roll=3,
        allowed_piece_ids=[],  # ① blocked by engine rules, only ② valid
        board_setup=_make_snapshot({1: 5}, {1: 0, 2: 8}),
        scene_narrate_key="tuto.scene6",
    ),
    TutorialStep(
        step_num=7,
        narrate_key="tuto.step7",
        active_player_idx=0,
        rigged_roll=3,
        allowed_piece_ids=[1],
        board_setup=_make_snapshot({1: 12}, {1: 0, 2: 8}),
        scene_narrate_key="tuto.scene7",
        is_free_choice=True,
    ),
]
