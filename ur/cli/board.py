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

    def draw(self):
        self.navigation.clear()
        cells = self._get_cells()
        bottom, top = self._bottom, self._top

        bottom_score = sum(1 for p in bottom.pieces if p.progress == FINISH)
        top_score = sum(1 for p in top.pieces if p.progress == FINISH)
        top_waiting = sum(1 for p in top.pieces if p.progress == 0)

        top_waiting_line = f"{C_P2}{' ●' * top_waiting}{C_RESET}"
        bottom_waiting_line = " ".join(
            [
                f"{C_P1}{self._numbered_piece(piece)}{C_RESET}"
                for piece in bottom.pieces
                if piece.progress == 0
            ]
        )

        top_line = f"{C_P2} {top.name} {top_score * '●'} {C_RESET}"
        bottom_line = f"{C_P1} {bottom.name} {bottom_score * '●'} {C_RESET}"

        board = TEMPLATE.format(**cells)
        name_display = f"  {C_TEXT}{self.game_name}{C_RESET}" if self.game_name else ""

        game_screen = f"""
{C_BOLD_TEXT}=== {t('board.title')} ==={C_RESET}{name_display}

        {top_line}
        {top_waiting_line}
{C_BOARD}{board}{C_RESET}
         {bottom_waiting_line}
        {bottom_line}
        """
        print(game_screen)

    def _get_cells(self) -> dict[str, str]:
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
                elif bottom_char != " " or top_char != " ":
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
