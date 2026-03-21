import random
import sys
import time
from typing import Optional

from ur.ai.bots import Bot
from ur.cli.constants import C_P1, C_P2, C_RESET, C_ROSETTA, NUM_CIRCLES
from ur.game import Action, ActionType, Engine, Move, Player
from ur.rules import FINISH, ROSETTAS


class GameUtils:
    @staticmethod
    def animate_dice(turn_text: str, player_color: str, roll: int):
        for _ in range(12):
            random_dots = " ".join(random.choice(["●", "○"]) for _ in range(4))
            sys.stdout.write(
                f"\r{turn_text} turn. Rolling...  [{player_color}{random_dots}{C_RESET}]"
            )
            sys.stdout.flush()
            time.sleep(0.06)

        final_faces = ["●"] * roll + ["○"] * (4 - roll)
        random.shuffle(final_faces)
        final_str = " ".join(final_faces)
        sys.stdout.write(
            f"\r{turn_text} turn. Rolled {roll}! [{player_color}{final_str}{C_RESET}]"
            + " " * 10
            + "\n\n"
        )
        sys.stdout.flush()

    @staticmethod
    def build_move_hints(move: Move, p2: Player, bot_name: str) -> str:
        hints = []

        if move.target_progress == FINISH:
            hints.append(f"{C_ROSETTA}Scores a point!{C_RESET}")
        elif move.target_coord in ROSETTAS:
            hints.append(f"{C_ROSETTA}Lands on Rosetta (Roll again!){C_RESET}")

        if move.target_coord is not None:
            for opp_piece in p2.pieces:
                if opp_piece.is_available and opp_piece.coord == move.target_coord:
                    hints.append(f"{C_P2}Captures {bot_name}'s piece!{C_RESET}")

        return f" — {' '.join(hints)}" if hints else ""

    @classmethod
    def get_human_move(cls, valid_moves: list[Move], p2: Player, bot_name: str, navigation) -> Optional[Move]:
        print("Your options:")
        valid_moves.sort(key=lambda m: m.piece.identifier)

        for move in valid_moves:
            status = "Off-board" if move.piece.progress == 0 else f"Square {move.piece.progress}"
            hint_text = cls.build_move_hints(move, p2, bot_name)
            print(
                f"  {C_P1}{NUM_CIRCLES[move.piece.identifier]}{C_RESET} : {status} -> Square {move.target_progress}{hint_text}"
            )

        navigation.print_commands()
        while True:
            raw_input = input("\nSelect a piece to move (1-7): ").strip()

            if navigation.check_global_commands(raw_input):
                return None

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

        if action.action_type == ActionType.SKIPPED:
            return f"{subject} rolled {action.roll} but had no moves."

        if is_local:
            piece_str = f"{C_P1}{NUM_CIRCLES[action.piece_id]}{C_RESET}"  # type: ignore[index]
        else:
            piece_str = f"{C_P2}●{C_RESET}"

        if action.action_type == ActionType.SCORED:
            return f"{subject} rolled {action.roll}: {piece_str} scored!"

        # MOVED
        parts = [f"{subject} rolled {action.roll}: {piece_str} moved to square {action.target_progress}."]
        if action.hit:
            parts.append("Hit opponent!")
        if action.rosetta:
            parts.append("Rolled again!")
        return " ".join(parts)

    @staticmethod
    def get_bot_move(bot: Bot, engine: Engine, valid_moves: list[Move], roll: int) -> Move:
        state = {
            "my_pieces": sorted([p.progress for p in engine.current_player.pieces]),
            "opp_pieces": sorted([p.progress for p in engine.opponent.pieces]),
            "current_roll": roll,
        }
        return bot.choose_move(state, valid_moves, engine.current_player)
