import os
from typing import Optional

from ur.cli.tui.constants import (
    BOARD_COLUMNS,
    BOARD_ROWS,
    C_BOARD,
    C_BOLD_TEXT,
    C_P1,
    C_P2,
    C_RESET,
    C_ROSETTA,
    C_P1_ROSETTA,
    C_P2_ROSETTA,
    C_ITALIC,
    MISSING_CELLS,
    NUM_CIRCLES,
    TEMPLATE,
)
from ur.cli.tui.i18n import t
from ur.cli.tui.output import out, center
from ur.game.engine import Engine, Piece, Player
from ur.game.rules import FINISH, ROSETTAS


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

        cells = self._get_cells(show_labels=show_labels)
        bottom, top = self._bottom, self._top

        bottom_score = sum(1 for p in bottom.pieces if p.progress == FINISH)
        top_score = sum(1 for p in top.pieces if p.progress == FINISH)

        top_waiting_count = sum(1 for p in top.pieces if p.progress == 0)

        out(center(f"{C_BOLD_TEXT}=== {t('board.title')} ==={C_RESET}"))
        if self.game_name:
            out(center(f"{C_ITALIC}{self.game_name}{C_RESET}\n"))

        out(center(f"{C_P2}{top.name}  {'●' * top_score}{C_RESET}"))

        out(center(f"{C_P2}{' ●' * top_waiting_count}{C_RESET}"))

        board_str = TEMPLATE.format(**cells)
        for line in board_str.split("\n"):
            out(center(f"{C_BOARD}{line}{C_RESET}"))

        bot_wait_str = " ".join([f"{C_P1}{self._numbered_piece(p)}{C_RESET}" for p in bottom.pieces if p.progress == 0])
        out(center(bot_wait_str))

        out(center(f"{C_P1}{bottom.name}  {'●' * bottom_score}{C_RESET}"))

        out("")

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
                        content = f"{C_P2_ROSETTA}●{C_BOARD}" if on_rosetta else f"{C_P2}●{C_BOARD}"

                for piece in bottom.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = (
                            f"{C_P1_ROSETTA}{self._numbered_piece(piece)}{C_BOARD}"
                            if on_rosetta
                            else f"{C_P1}{self._numbered_piece(piece)}{C_BOARD}"
                        )

                cells[chr(letter_code)] = f" {content} "
                letter_code += 1

        return cells

    def _numbered_piece(self, piece: Piece) -> str:
        return NUM_CIRCLES[piece.identifier]
