import datetime
import random
import sys
import time
from typing import TYPE_CHECKING, Optional

from ur.ai.bots import Bot
from ur.cli.constants import C_BOARD, C_ITALIC, C_P1, C_P2, C_RESET, C_ROSETTA, C_SCORE, NUM_CIRCLES
from ur.cli.i18n import t
from ur.game import Action, ActionType, Engine, Move, Player
from ur.rules import FINISH, ROSETTAS

if TYPE_CHECKING:
    from ur.cli.widgets import Navigation
    from ur.cli.board import Board


class GameUtils:
    @staticmethod
    def animate_dice(turn_text: str, player_color: str, roll: int):
        print(turn_text)
        for _ in range(12):
            random_dots = " ".join(random.choice(["●", "○"]) for _ in range(4))
            sys.stdout.write(
                f"\r[{player_color}{random_dots}{C_RESET}] {C_BOARD}{C_ITALIC}Rolling{C_RESET}" + " " * 4
            )
            sys.stdout.flush()
            time.sleep(0.06)

        final_faces = ["●"] * roll + ["○"] * (4 - roll)
        random.shuffle(final_faces)
        final_str = " ".join(final_faces)
        sys.stdout.write(
            f"\r[{player_color}{final_str}{C_RESET}] {C_BOARD}{C_ITALIC}Rolled{C_RESET} " + " " * 4
        )
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write(f"\r[{player_color}{final_str}{C_RESET}]" + " " * 12 + "\n\n")
        sys.stdout.flush()

    @staticmethod
    def print_static_dice(turn_text: str, player_color: str, roll: int):
        """Instantly prints the dice state for redrawing the screen."""
        print(turn_text)
        final_faces = ["●"] * roll + ["○"] * (4 - roll)
        final_str = " ".join(final_faces)
        print(f"[{player_color}{final_str}{C_RESET}]\n")

    @staticmethod
    def build_move_hints(move: Move, p2: Player, bot_name: str) -> str:
        hints = []

        if move.target_progress == FINISH:
            hints.append(f"{C_SCORE}{t('move.scores_point')}{C_SCORE}")
        elif move.target_coord in ROSETTAS:
            hints.append(f"{C_ROSETTA}{t('move.lands_rosetta')}{C_RESET}")

        if move.target_coord is not None:
            for opp_piece in p2.pieces:
                if opp_piece.is_available and opp_piece.coord == move.target_coord:
                    hints.append(f"{C_P2}{t('move.captures', name=bot_name)}{C_RESET}")

        return f" — {' '.join(hints)}" if hints else ""

    @classmethod
    def _build_move_groups(cls, valid_moves: list[Move], p2: Player, bot_name: str):
        rosetta_keys = {4: "move.rosetta_first", 8: "move.rosetta_middle", 14: "move.rosetta_last"}
        groups = {}
        for move in valid_moves:
            prog = move.piece.progress
            if prog == 0:
                status = t("move.off_board")
            elif prog in rosetta_keys:
                status = f"{t(rosetta_keys[prog])} {C_ROSETTA}✿{C_RESET}"
            else:
                status = t("move.square", letter=chr(96 + prog))
            hint_text = cls.build_move_hints(move, p2, bot_name)
            key = (status, move.target_progress, hint_text)
            if key not in groups:
                groups[key] = []
            groups[key].append(move)
        return groups

    @classmethod
    def _print_move_options(cls, groups: dict):
        rosetta_keys = {4: "move.rosetta_first", 8: "move.rosetta_middle", 14: "move.rosetta_last"}
        print(t("move.your_options"))
        for (status, target_progress, hint), moves in groups.items():
            moves.sort(key=lambda m: m.piece.identifier)
            piece_symbols = " ".join(f"{C_P1}{NUM_CIRCLES[m.piece.identifier]}{C_RESET}" for m in moves)
            if target_progress == FINISH:
                target_str = t("move.finish")
            elif target_progress in rosetta_keys:
                target_str = f"{t(rosetta_keys[target_progress]).capitalize()} {C_ROSETTA}✿{C_RESET}"
            else:
                target_str = t("move.square", letter=chr(96 + target_progress))
            print(f"  {piece_symbols} : {status} -> {target_str}{hint}")

    @classmethod
    def get_human_move(
        cls,
        valid_moves: list[Move],
        ui: "Board",
        roll: int,
        turn_text: str,
        player_color: str
    ) -> Optional[Move]:

        p2 = ui._top
        bot_name = p2.name
        navigation = ui.navigation

        valid_moves.sort(key=lambda m: m.piece.progress, reverse=True)
        groups = cls._build_move_groups(valid_moves, p2, bot_name)

        is_single_choice = len(groups) == 1
        default_move = min(valid_moves, key=lambda m: m.piece.identifier)

        prompt = t("move.select_prompt")
        if is_single_choice:
            prompt += t("move.select_prompt_default", id=str(default_move.piece.identifier))
        else:
            prompt += t("move.select_prompt_end")

        navigation.print_commands(f"{C_BOARD}{t('nav.ingame_commands_hint')}{C_RESET}")

        help_open = False
        error_msg = ""
        while True:
            if error_msg:
                print(f"{C_P2}{error_msg}{C_RESET}")
                error_msg = ""

            raw_input = input(prompt).strip()

            if raw_input.lower() == "help":
                help_open = True
                ui.draw(show_labels=True)
                cls.print_static_dice(turn_text, player_color, roll)
                cls._print_move_options(groups)
                navigation.print_commands(f"{C_BOARD}{t('nav.ingame_help_open_hint')}{C_RESET}")
                continue

            if raw_input.lower() == "back" and help_open:
                help_open = False
                ui.draw(show_labels=False)
                cls.print_static_dice(turn_text, player_color, roll)
                navigation.print_commands(f"{C_BOARD}{t('nav.ingame_commands_hint')}{C_RESET}")
                continue

            if navigation.check_global_commands(raw_input):
                return None

            # Handle the Enter shortcut
            if is_single_choice and not raw_input:
                return default_move

            try:
                choice = int(raw_input)
                chosen = next((m for m in valid_moves if m.piece.identifier == choice), None)
                if chosen:
                    return chosen
                error_msg = t("move.invalid_choice")
            except ValueError:
                error_msg = t("move.invalid_number")

    @staticmethod
    def format_action(action: Action, local_player_idx: int, opponent_name: str) -> str:
        if action.action_type == ActionType.STARTED:
            return t("action.game_started")

        is_local = action.player_idx == local_player_idx
        subject = t("action.you") if is_local else opponent_name

        roll_faces = "●" * action.roll + "○" * (4 - action.roll)
        roll_color = C_P1 if is_local else C_P2
        roll_str = f"{roll_color}{roll_faces}{C_RESET}"

        if action.action_type == ActionType.SKIPPED:
            key = "action.skipped_you" if is_local else "action.skipped"
            return t(key, subject=subject, roll=roll_str)

        rosetta_keys = {4: "move.rosetta_first", 8: "move.rosetta_middle", 14: "move.rosetta_last"}

        if action.action_type == ActionType.SCORED:
            if is_local:
                piece_str = f"{C_P1}{NUM_CIRCLES[action.piece_id]}{C_RESET}"  # type: ignore[index]
                return f"{C_P1}{t('action.scored_you', subject=subject, roll=roll_str, piece=piece_str)}{C_RESET}"
            else:
                return f"{C_P2}{t('action.scored_opp', subject=subject, roll=roll_str)}{C_RESET}"

        # MOVED
        assert action.target_progress is not None
        target = action.target_progress
        if target in rosetta_keys:
            rosetta_label = f"{t(rosetta_keys[target])} {C_ROSETTA}✿{C_RESET}"
            target_str = t("action.rosetta_target", label=rosetta_label)
        else:
            target_str = t("move.square", letter=chr(96 + target))

        if is_local:
            piece_str = f"{C_P1}{NUM_CIRCLES[action.piece_id]}{C_RESET}"  # type: ignore[index]
            parts = [t("action.moved_you", subject=subject, roll=roll_str, piece=piece_str, target=target_str)]
        else:
            parts = [t("action.moved_opp", subject=subject, roll=roll_str, target=target_str)]

        if action.hit:
            if is_local:
                parts.append(f"{C_P1}{t('action.hit_you')}{C_RESET}")
            else:
                parts.append(f"{C_P2}{t('action.hit_opp')}{C_RESET}")
        if action.rosetta:
            if is_local:
                parts.append(f"{C_ROSETTA}{t('action.rosetta_you')}{C_RESET}")
            else:
                parts.append(f"{C_ROSETTA}{t('action.rosetta_opp')}{C_RESET}")
        return " ".join(parts)

    @staticmethod
    def get_bot_move(bot: Bot, engine: Engine, valid_moves: list[Move], roll: int) -> Move:
        state = {
            "my_pieces": sorted([p.progress for p in engine.current_player.pieces]),
            "opp_pieces": sorted([p.progress for p in engine.opponent.pieces]),
            "current_roll": roll,
        }
        return bot.choose_move(state, valid_moves, engine.current_player)

    @staticmethod
    def time_ago(iso_timestamp: str) -> str:
        """Converts an ISO timestamp string into a relative time string (e.g., '5m ago')."""
        try:
            past = datetime.datetime.fromisoformat(iso_timestamp)
        except ValueError:
            # Fail safely
            return "-"

        seconds = int((datetime.datetime.now() - past).total_seconds())

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        elif seconds < 2592000:  # 30 days
            return f"{seconds // 86400}d ago"
        elif seconds < 31536000: # 365 days
            return f"{seconds // 2592000}mo ago"
        else:
            return f"{seconds // 31536000}y ago"
