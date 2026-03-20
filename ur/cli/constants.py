# --- ANSI COLOR CODES ---
C_RESET = "\033[0m"  # Resets terminal color back to default
C_BOARD = "\033[90m"  # Dark Gray for drawing the grid lines of the board
C_P1 = "\033[96m"  # Bright Cyan for Player 1 (You) and your pieces
C_P2 = "\033[91m"  # Bright Red for Player 2 (The Bot) and its pieces
C_ROSETTA = "\033[93m"  # Bright Yellow for Rosetta squares (✿) and point alerts
C_BOLD_TEXT = "\033[1;97m"  # 1 for Bold, 97 for Bright White
C_TEXT = "\033[97m"  # Bright White for headers, menus, and general UI text

NUM_CIRCLES = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦"}
BOARD_ROWS = 3
BOARD_COLUMNS = 8
MISSING_CELLS = ((0, 4), (0, 5), (2, 4), (2, 5))

TEMPLATE = """\
╔═══╦═══╦═══╦═══╗       ╔═══╦═══╗
║{a}║{b}║{c}║{d}║       ║{e}║{f}║
╠═══╬═══╬═══╬═══╬═══╦═══╬═══╬═══╣
║{g}║{h}║{i}║{j}║{k}║{l}║{m}║{n}║
╠═══╬═══╬═══╬═══╬═══╩═══╬═══╬═══╣
║{o}║{p}║{q}║{r}║       ║{s}║{t}║
╚═══╩═══╩═══╩═══╝       ╚═══╩═══╝\
"""
