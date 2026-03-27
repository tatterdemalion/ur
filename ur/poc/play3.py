import os
import random
import time

from ur.poc.engine3 import ActionType, Engine, Player
from ur.poc.rules3 import FINISH, PATHS, PIECES_PER_PLAYER, ROSETTAS

NAMES = ["Anu", "Bel", "Cir"]
SYMBOLS = ["●", "■", "▲"]
# bright blue, bright red, bright green
COLORS = ["\033[94m", "\033[91m", "\033[92m"]
RESET = "\033[0m"
DIM = "\033[2m"
YELLOW_BG = "\033[43m"

# player_idx -> board row
PLAYER_ROW = {0: 2, 1: 0, 2: 3}
# column in private row -> progress value
PRIV_COL_TO_PROGRESS = {0: 4, 1: 3, 2: 2, 3: 1, 6: 14, 7: 13}
GAP_COLS = {4, 5}


def build_coord_map(engine):
    coord_map: dict = {}
    for player in engine.players:
        for piece in player.pieces:
            if piece.is_available and piece.coord is not None:
                coord = piece.coord
                if coord not in coord_map:
                    coord_map[coord] = []
                coord_map[coord].append((player.player_idx, piece))
    return coord_map


def render_cell(coord, progress, occupants):
    is_rosette = coord in ROSETTAS
    bg = YELLOW_BG if is_rosette else ""
    star = "★" if is_rosette else " "

    if occupants:
        p_idx, piece = occupants[0]
        color = COLORS[p_idx]
        symbol = SYMBOLS[p_idx]
        return f"{bg}{color}[{symbol}{piece.identifier}{star}]{RESET}"
    else:
        label = f"{progress:2d}"
        return f"{bg}{DIM}[{label}{star}]{RESET}"


def render_private_row(player_idx, coord_map):
    board_row = PLAYER_ROW[player_idx]
    cells = []
    for col in range(8):
        if col in GAP_COLS:
            cells.append("     ")
        else:
            progress = PRIV_COL_TO_PROGRESS[col]
            coord = (board_row, col)
            occupants = coord_map.get(coord, [])
            cells.append(render_cell(coord, progress, occupants))
    return cells


def render_shared_row(coord_map):
    cells = []
    for col in range(8):
        progress = col + 5  # sq5 through sq12
        coord = (1, col)
        occupants = coord_map.get(coord, [])
        cells.append(render_cell(coord, progress, occupants))
    return cells


def fmt_row(label, cells):
    return f"  {label:3s} " + " ".join(cells)


def render_board(engine):
    coord_map = build_coord_map(engine)
    sep = "      " + "─" * 47

    header = f"  {DIM}     ← entry (sq4→sq1)              shared (sq5→sq12)        exit →{RESET}"
    p2_cells = render_private_row(1, coord_map)
    sh_cells = render_shared_row(coord_map)
    p1_cells = render_private_row(0, coord_map)
    p3_cells = render_private_row(2, coord_map)

    return "\n".join([
        header,
        fmt_row("Bel", p2_cells),
        sep,
        fmt_row("shr", sh_cells),
        sep,
        fmt_row("Anu", p1_cells),
        fmt_row("Cir", p3_cells),
        f"  {DIM}     col0  col1  col2  col3  col4  col5  col6  col7{RESET}",
    ])


def render_status(engine):
    lines = []
    for i, player in enumerate(engine.players):
        marker = "▶" if i == engine.current_idx else " "
        color = COLORS[i]
        symbol = SYMBOLS[i]
        waiting = sum(1 for p in player.pieces if p.progress == 0)
        scored = sum(1 for p in player.pieces if p.progress == FINISH)
        on_board = [p for p in player.pieces if 0 < p.progress < FINISH]
        board_str = "  ".join(
            f"{color}{symbol}{p.identifier}@sq{p.progress}{RESET}" for p in on_board
        )
        lines.append(
            f"  {marker} {color}{player.name}{RESET}  wait:{waiting}  scored:{scored}  {board_str}"
        )
    return "\n".join(lines)


def clear():
    print("\033[2J\033[H", end="", flush=True)


def display(engine):
    print(render_status(engine))
    print()
    print(render_board(engine))
    print()


def main():
    step_mode = os.environ.get("STEP") == "1"
    players = [Player(i, NAMES[i], PATHS[i], PIECES_PER_PLAYER) for i in range(3)]
    engine = Engine(players)
    turn = 0

    clear()
    display(engine)

    while not engine.winner:
        turn += 1
        player = engine.current_player
        p_idx = player.player_idx
        color = COLORS[p_idx]
        symbol = SYMBOLS[p_idx]

        roll = engine.roll_dice()
        moves = engine.get_valid_moves(roll)

        if not moves:
            print(f"  {color}{player.name}{RESET} rolls {roll}  — no moves, skip")
            engine.skip_turn(roll)
        else:
            move = random.choice(moves)
            from_sq = move.piece.progress
            piece_id = move.piece.identifier
            engine.execute_move(move, roll)
            action = engine.last_action
            to_sq = action.target_progress

            suffixes = ""
            if action.hit:
                suffixes += "  💥 capture!"
            if action.rosetta:
                suffixes += "  ★ extra turn!"
            if action.action_type == ActionType.SCORED:
                suffixes += "  ✓ scored!"

            print(
                f"  {color}{player.name}{RESET} rolls {roll}"
                f"  moves {color}{symbol}{piece_id}{RESET}: sq{from_sq} → sq{to_sq}{suffixes}"
            )

        if step_mode:
            input("  [Enter] ")
        else:
            time.sleep(0.8)

        clear()
        display(engine)

    winner = engine.winner
    w_color = COLORS[winner.player_idx]
    print(f"  {w_color}🏆 {winner.name} wins!{RESET} ({turn} turns)\n")


if __name__ == "__main__":
    main()
