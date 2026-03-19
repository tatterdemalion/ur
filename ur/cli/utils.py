import sys
import time
import random
from typing import Optional

from ur.game import Player, Piece, Engine, ROSETTAS
from ur.cli.constants import C_P1, C_P2, C_ROSETTA, C_RESET, NUM_CIRCLES
from ur.ai.bots import Bot


class GameUtils:
    @staticmethod
    def serialize_board(engine: Engine) -> dict:
        stats = engine.get_stats()
        return {
            "p1_pieces": {str(p.identifier): p.progress for p in engine.p1.pieces},
            "p2_pieces": {str(p.identifier): p.progress for p in engine.p2.pieces},
            "stats": {
                "p1_score": stats.p1_score, "p1_waiting": stats.p1_waiting,
                "p2_score": stats.p2_score, "p2_waiting": stats.p2_waiting,
            },
        }

    @staticmethod
    def apply_board(engine: Engine, board: dict):
        for piece in engine.p1.pieces:
            piece.progress = board["p1_pieces"][str(piece.identifier)]
        for piece in engine.p2.pieces:
            piece.progress = board["p2_pieces"][str(piece.identifier)]

    @staticmethod
    def animate_dice(turn_text: str, player_color: str, roll: int):
        for _ in range(12):
            random_dots = " ".join(random.choice(["●", "○"]) for _ in range(4))
            sys.stdout.write(f"\r{turn_text} turn. Rolling...  [{player_color}{random_dots}{C_RESET}]")
            sys.stdout.flush()
            time.sleep(0.06)

        final_faces = ["●"] * roll + ["○"] * (4 - roll)
        random.shuffle(final_faces)
        final_str = " ".join(final_faces)
        sys.stdout.write(f"\r{turn_text} turn. Rolled {roll}! [{player_color}{final_str}{C_RESET}]" + " " * 10 + "\n\n")
        sys.stdout.flush()

    @staticmethod
    def build_move_hints(piece: Piece, roll: int, p2: Player, bot_name: str) -> str:
        target = piece.progress + roll
        target_coord = piece.player.path[target]
        hints = []

        if target == 15:
            hints.append(f"{C_ROSETTA}Scores a point!{C_RESET}")
        elif target_coord in ROSETTAS:
            hints.append(f"{C_ROSETTA}Lands on Rosetta (Roll again!){C_RESET}")

        if target_coord is not None:
            for opp_piece in p2.pieces:
                if opp_piece.is_available and opp_piece.coord == target_coord:
                    hints.append(f"{C_P2}Captures {bot_name}'s piece!{C_RESET}")

        return f" — {' '.join(hints)}" if hints else ""

    @classmethod
    def get_human_move(cls, valid_moves: list[Piece], roll: int, p2: Player, bot_name: str) -> Optional[Piece]:
        from ur.cli.menu import Navigation

        print("Your options:")
        valid_moves.sort(key=lambda p: p.identifier)

        for piece in valid_moves:
            target = piece.progress + roll
            status = "Off-board" if piece.progress == 0 else f"Square {piece.progress}"
            hint_text = cls.build_move_hints(piece, roll, p2, bot_name)
            print(f"  {C_P1}{NUM_CIRCLES[piece.identifier]}{C_RESET} : {status} -> Square {target}{hint_text}")

        Navigation.print_commands()
        while True:
            raw_input = input("\nSelect a piece to move (1-7): ").strip()

            if Navigation.check_global_commands(raw_input):
                return None

            try:
                choice = int(raw_input)
                chosen = next((p for p in valid_moves if p.identifier == choice), None)
                if chosen:
                    return chosen
                print("Invalid choice. That piece cannot move right now.")
            except ValueError:
                print("Please enter a valid piece number.")

    @staticmethod
    def get_bot_move(bot: Bot, engine: Engine, valid_moves: list[Piece], roll: int) -> Piece:
        state = {
            "my_pieces": sorted([p.progress for p in engine.current_player.pieces]),
            "opp_pieces": sorted([p.progress for p in engine.opponent.pieces]),
            "current_roll": roll,
        }
        return bot.choose_move(state, valid_moves, engine.current_player)
