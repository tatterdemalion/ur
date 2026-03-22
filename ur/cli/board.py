import os
from typing import Optional

from ur.cli.constants import (
    BOARD_COLUMNS,
    BOARD_ROWS,
    C_BOARD,
    C_BOLD_TEXT,
    C_P1,
    C_P2,
    C_RESET,
    C_ROSETTA,
    C_TEXT,
    MISSING_CELLS,
    NUM_CIRCLES,
    TEMPLATE,
)
from ur.cli.i18n import t
from ur.game import Engine, Piece, Player
from ur.rules import FINISH, ROSETTAS


class Board:
    def __init__(
        self, engine: Engine, navigation, local_player: Optional[Player] = None, game_name: str = ""
    ):
        self.engine = engine
        self.p1, self.p2 = self.engine.players
        self._local = local_player if local_player is not None else self.p1
        self.game_name = game_name
        self.navigation = navigation

    @property
    def _bottom(self) -> Player:
        return self._local

    @property
    def _top(self) -> Player:
        return self.p2 if self._local is self.p1 else self.p1

    def draw(self, show_labels: bool = False):
        self.navigation.clear()

        # Get terminal size dynamically
        try:
            cols, lines = os.get_terminal_size()
        except OSError:
            cols, lines = 80, 24  # Fallback if standard out is piped or IDE console is weird

        cells = self._get_cells(show_labels=show_labels)
        bottom, top = self._bottom, self._top

        bottom_score = sum(1 for p in bottom.pieces if p.progress == FINISH)
        top_score = sum(1 for p in top.pieces if p.progress == FINISH)

        top_waiting_count = sum(1 for p in top.pieces if p.progress == 0)
        bottom_waiting_count = sum(1 for p in bottom.pieces if p.progress == 0)

        # The physical width of the ASCII board from the TEMPLATE is exactly 33 characters
        board_width = 33

        # Calculate Vertical Padding (leaving room for the action log and input prompts at the bottom)
        v_pad = max(0, (lines - 15) // 2)
        print("\n" * v_pad, end="")

        # 1. Centered Title
        title_text = f"=== {t('board.title')} ==="
        if self.game_name:
            title_text += f"   {self.game_name}"

        title_pad = max(0, (cols - len(title_text)) // 2)
        print(" " * title_pad + f"{C_BOLD_TEXT}{title_text}{C_RESET}\n")

        # Base margin to center the board itself
        board_margin = " " * max(0, (cols - board_width) // 2)

        # 2. Centered Top Player Stats
        top_stat_len = len(top.name) + 2 + top_score
        top_stat_pad = " " * max(0, (board_width - top_stat_len) // 2)
        print(board_margin + top_stat_pad + f"{C_P2}{top.name}  {'●' * top_score}{C_RESET}")

        # Calculate width of waiting circles (e.g. " ● ● ●" is 2 chars per circle)
        top_waiting_len = top_waiting_count * 2
        top_wait_pad = " " * max(0, (board_width - top_waiting_len) // 2)
        print(board_margin + top_wait_pad + f"{C_P2}{' ●' * top_waiting_count}{C_RESET}")

        # 3. The Centered Board
        board_str = TEMPLATE.format(**cells)
        for line in board_str.split("\n"):
            print(board_margin + f"{C_BOARD}{line}{C_RESET}")

        # 4. Centered Bottom Player Stats
        # Width calculation: N circles + (N-1) spaces
        bottom_waiting_len = max(0, bottom_waiting_count * 2 - 1) if bottom_waiting_count > 0 else 0
        bot_wait_pad = " " * max(0, (board_width - bottom_waiting_len) // 2)
        bot_wait_str = " ".join([f"{C_P1}{self._numbered_piece(p)}{C_RESET}" for p in bottom.pieces if p.progress == 0])
        print(board_margin + bot_wait_pad + bot_wait_str)

        bot_stat_len = len(bottom.name) + 2 + bottom_score
        bot_stat_pad = " " * max(0, (board_width - bot_stat_len) // 2)
        print(board_margin + bot_stat_pad + f"{C_P1}{bottom.name}  {'●' * bottom_score}{C_RESET}")

        # Leave a blank line before the action logs begin
        print()

    def _get_cells(self, show_labels: bool = False) -> dict[str, str]:
        bottom, top = self._bottom, self._top
        cells = {}
        letter_code = 97  # ASCII code for 'a'

        bottom_path_letters = {bottom.path[i]: chr(96 + i) for i in range(1, 15)}
        top_path_letters = {top.path[i]: chr(96 + i) for i in range(1, 15)}

        row_order = range(BOARD_ROWS - 1, -1, -1) if self._local is self.p2 else range(BOARD_ROWS)

        for r in row_order:
            for c in range(BOARD_COLUMNS):
                coord = (r, c)
                if coord in MISSING_CELLS:
                    continue

                on_rosetta = coord in ROSETTAS
                bottom_char = bottom_path_letters.get(coord, " ")
                top_char = top_path_letters.get(coord, " ")

                if on_rosetta:
                    content = f"{C_ROSETTA}✿{C_BOARD}"
                elif show_labels and (bottom_char != " " or top_char != " "):
                    content = bottom_char if bottom_char != " " else top_char
                else:
                    content = " "

                for piece in top.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = f"{C_ROSETTA}●{C_BOARD}" if on_rosetta else f"{C_P2}●{C_BOARD}"

                for piece in bottom.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = (
                            f"{C_ROSETTA}{self._numbered_piece(piece)}{C_BOARD}"
                            if on_rosetta
                            else f"{C_P1}{self._numbered_piece(piece)}{C_BOARD}"
                        )

                cells[chr(letter_code)] = f" {content} "
                letter_code += 1

        return cells

    def _numbered_piece(self, piece: Piece) -> str:
        return NUM_CIRCLES[piece.identifier]
