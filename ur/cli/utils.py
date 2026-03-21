import random
import sys
import time
from typing import TYPE_CHECKING, Optional

from ur.ai.bots import Bot
from ur.cli.constants import C_BOARD, C_ITALIC, C_P1, C_P2, C_RESET, C_ROSETTA, C_SCORE, NUM_CIRCLES
from ur.game import Action, ActionType, Engine, Move, Player
from ur.rules import FINISH, ROSETTAS

if TYPE_CHECKING:
    from ur.cli.menu import Navigation


class GameUtils:
    @staticmethod
    def animate_dice(turn_text: str, player_color: str, roll: int):
        print(f"{turn_text} turn.")
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
    def build_move_hints(move: Move, p2: Player, bot_name: str) -> str:
        hints = []

        if move.target_progress == FINISH:
            hints.append(f"{C_SCORE}Scores a point!{C_SCORE}")
        elif move.target_coord in ROSETTAS:
            hints.append(f"{C_ROSETTA}Lands on Rosetta (Roll again!){C_RESET}")

        if move.target_coord is not None:
            for opp_piece in p2.pieces:
                if opp_piece.is_available and opp_piece.coord == move.target_coord:
                    hints.append(f"{C_P2}Captures {bot_name}'s piece!{C_RESET}")

        return f" — {' '.join(hints)}" if hints else ""

    @classmethod
    def get_human_move(cls, valid_moves: list[Move], p2: Player, bot_name: str, navigation: "Navigation") -> Optional[Move]:
        print("Your options:")

        valid_moves.sort(key=lambda m: m.piece.progress, reverse=True)

        rosetta_names = {4: "first", 8: "middle", 14: "last"}

        # Group moves that have the exact same start, target, and hint
        groups = {}
        for move in valid_moves:
            prog = move.piece.progress
            if prog == 0:
                status = "Off-board"
            elif prog in rosetta_names:
                status = f"{rosetta_names[prog]} {C_ROSETTA}✿{C_RESET}"
            else:
                status = f"Square {chr(96 + prog)}"
            hint_text = cls.build_move_hints(move, p2, bot_name)

            key = (status, move.target_progress, hint_text)

            if key not in groups:
                groups[key] = []
            groups[key].append(move)

        # Print the grouped options
        for (status, target_progress, hint), moves in groups.items():
            moves.sort(key=lambda m: m.piece.identifier)
            piece_symbols = " ".join(f"{C_P1}{NUM_CIRCLES[m.piece.identifier]}{C_RESET}" for m in moves)
            if target_progress == FINISH:
                target_str = "Finish"
            elif target_progress in rosetta_names:
                target_str = f"{rosetta_names[target_progress].capitalize()} {C_ROSETTA}✿{C_RESET}"
            else:
                target_str = f"Square {chr(96 + target_progress)}"
            print(f"  {piece_symbols} : {status} -> {target_str}{hint}")

        navigation.print_commands()

        is_single_choice = len(groups) == 1
        default_move = min(valid_moves, key=lambda m: m.piece.identifier)

        prompt = "\nSelect a piece to move (1-7)"
        if is_single_choice:
            prompt += f" [Enter for {default_move.piece.identifier}]: "
        else:
            prompt += ": "

        while True:
            raw_input = input(prompt).strip()

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
                print("Invalid choice. That piece cannot move right now.")
            except ValueError:
                print("Please enter a valid piece number.")

    @staticmethod
    def format_action(action: Action, local_player_idx: int, opponent_name: str) -> str:
        if action.action_type == ActionType.STARTED:
            return "Game started."

        is_local = action.player_idx == local_player_idx
        subject = "You" if is_local else opponent_name

        roll_faces = "●" * action.roll + "○" * (4 - action.roll)
        roll_color = C_P1 if is_local else C_P2
        roll_str = f"{roll_color}{roll_faces}{C_RESET}"

        if action.action_type == ActionType.SKIPPED:
            return f"{subject} rolled {roll_str} but had no moves."

        rosetta_names = {4: "first", 8: "middle", 14: "last"}

        if action.action_type == ActionType.SCORED:
            if is_local:
                piece_str = f"{C_P1}{NUM_CIRCLES[action.piece_id]}{C_RESET}"  # type: ignore[index]
                return f"{subject} rolled {roll_str} and piece {piece_str} {C_P1}scored!{C_RESET}"
            else:
                return f"{subject} rolled {roll_str} and {C_P2}scored a piece!{C_RESET}"

        # MOVED
        assert action.target_progress is not None
        target = action.target_progress
        if target in rosetta_names:
            rosetta_label = f"{rosetta_names[target]} {C_ROSETTA}✿{C_RESET}"
            target_str = f"the {rosetta_label}"
        else:
            target_str = f"square {chr(96 + target)}"

        if is_local:
            piece_str = f"{C_P1}{NUM_CIRCLES[action.piece_id]}{C_RESET}"  # type: ignore[index]
            parts = [f"{subject} rolled {roll_str} and moved piece {piece_str} to {target_str}."]
        else:
            parts = [f"{subject} rolled {roll_str} and moved a piece to {target_str}."]

        if action.hit:
            if is_local:
                parts.append(f"{C_P1}Took one of their pieces!{C_RESET}")
            else:
                parts.append(f"{C_P2}Took out one of your pieces!{C_RESET}")
        if action.rosetta:
            if is_local:
                parts.append(f"{C_ROSETTA}It is your turn again!{C_RESET}")
            else:
                parts.append(f"{C_ROSETTA}It is their turn again!{C_RESET}")
        return " ".join(parts)

    @staticmethod
    def get_bot_move(bot: Bot, engine: Engine, valid_moves: list[Move], roll: int) -> Move:
        state = {
            "my_pieces": sorted([p.progress for p in engine.current_player.pieces]),
            "opp_pieces": sorted([p.progress for p in engine.opponent.pieces]),
            "current_roll": roll,
        }
        return bot.choose_move(state, valid_moves, engine.current_player)
