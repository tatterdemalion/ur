from typing import Optional

from ur.cli.tui.constants import (
    C_BOARD,
    C_BOLD_TEXT,
    C_P1,
    C_P1_ROSETTA,
    C_P2,
    C_P2_ROSETTA,
    C_P3,
    C_P3_ROSETTA,
    C_RESET,
    C_ROSETTA,
    NUM_CIRCLES,
)
from ur.cli.tui.i18n import t
from ur.cli.tui.output import center, out
from ur.poc.engine3 import Engine, Player
from ur.poc.rules_cross import CROSS_ROSETTAS_3P, CROSS_TEMPLATE_COORD, FINISH

# Cross-shaped board template.  Each {x} placeholder is a 3-visible-char
# cell formatted by _get_cells().  Border characters are rendered verbatim
# by the C_BOARD colour wrapping applied in draw().
#
# ╬ marks where the vertical centre column intersects a horizontal row.
CROSS_TEMPLATE = """\
                ╔═══╗
                ║{a}║
                ╠═══╣
                ║{b}║
                ╠═══╣
                ║{c}║
                ╠═══╣
                ║{d}║
╔═══╦═══╦═══╦═══╬═══╬═══╦═══╦═══╦═══╗
║{e}║{f}║{g}║{h}║{i}║{j}║{k}║{l}║{m}║
╚═══╩═══╩═══╩═══╬═══╬═══╩═══╩═══╩═══╝
                ║{n}║
                ╠═══╣
                ║{o}║
                ╠═══╣
                ║{p}║
                ╠═══╣
                ║{q}║
                ╠═══╣
                ║{r}║
                ╠═══╣
                ║{s}║
        ╔═══╦═══╬═══╬═══╦═══╗
        ║{t}║{u}║{v}║{w}║{x}║
        ╚═══╩═══╬═══╬═══╩═══╝
                ║{y}║
                ╠═══╣
                ║{z}║
                ╚═══╝"""

# Squares on each player's private path: coord → game letter (a=sq1 … n=sq14)
def _path_letters(path: dict) -> dict:
    return {coord: chr(96 + prog) for prog, coord in path.items() if 1 <= prog <= 14}


_PLAYER_COLORS = [C_P1, C_P2, C_P3]
_PLAYER_ROSETTA_COLORS = [C_P1_ROSETTA, C_P2_ROSETTA, C_P3_ROSETTA]
_PLAYER_SYMBOLS = ["●", "●", "◆"]  # P1 uses NUM_CIRCLES; P2/P3 use these


class CrossBoard:
    """Renders the cross-shaped board for a 2- or 3-player game via engine3.Engine."""

    def __init__(self, engine: Engine, navigation, local_player: Optional[Player] = None):
        self.engine = engine
        self.navigation = navigation
        self._local = local_player if local_player is not None else engine.players[0]

    def draw(self, show_labels: bool = False):
        self.navigation.clear()

        cells = self._get_cells(show_labels=show_labels)

        out(f"{C_BOLD_TEXT}=== {t('board.title')} ==={C_RESET}")
        parts = []
        for i, p in enumerate(self.engine.players):
            color = _PLAYER_COLORS[i] if i < len(_PLAYER_COLORS) else C_RESET
            score = sum(1 for piece in p.pieces if piece.progress == FINISH)
            wait  = sum(1 for piece in p.pieces if piece.progress == 0)
            parts.append(f"{color}{p.name}  {'●' * score}{'○' * wait}{C_RESET}")
        out(f"   {C_BOARD}vs{C_RESET}   ".join(parts))
        out("")

        board_str = CROSS_TEMPLATE.format(**cells)
        for line in board_str.split("\n"):
            out(f"{C_BOARD}{line}{C_RESET}")

        out("")

    def _get_cells(self, show_labels: bool = False) -> dict:
        players = self.engine.players
        all_letters = [_path_letters(p.path) for p in players]

        cells: dict[str, str] = {}
        for key, coord in CROSS_TEMPLATE_COORD.items():
            on_rosetta = coord in CROSS_ROSETTAS_3P
            any_char = next((lm.get(coord) for lm in all_letters if lm.get(coord)), "")
            is_active = bool(any_char)

            # ── Default cell (3 visible chars) ────────────────────────────
            if on_rosetta:
                cell = f" {C_ROSETTA}✿{C_BOARD} "
            elif show_labels and is_active:
                cell = f" {any_char} "
            elif is_active:
                cell = "   "
            else:
                cell = f" \033[2m·\033[0m{C_BOARD} "

            # ── Overlay pieces: render in reverse order so P1 ends on top ─
            # Pieces on a rosette get a ★ suffix so the square type is always
            # visible even when occupied: "①★" vs " ① ".
            for i in range(len(players) - 1, -1, -1):
                p = players[i]
                color = _PLAYER_COLORS[i] if i < len(_PLAYER_COLORS) else C_RESET
                rc = _PLAYER_ROSETTA_COLORS[i] if i < len(_PLAYER_ROSETTA_COLORS) else C_RESET
                for piece in p.pieces:
                    if piece.is_available and piece.coord == coord:
                        if i == 0:
                            sym = NUM_CIRCLES[piece.identifier]
                        else:
                            sym = _PLAYER_SYMBOLS[i] if i < len(_PLAYER_SYMBOLS) else "?"
                        if on_rosetta:
                            cell = f"{rc}{sym}★{C_BOARD} "
                        else:
                            cell = f" {color}{sym}{C_BOARD} "

            cells[key] = cell

        return cells
