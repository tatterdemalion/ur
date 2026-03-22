import re

# --- ANSI COLOR CODES ---
C_RESET = "\033[0m"  # Resets terminal color back to default
C_BOARD = "\033[90m"  # Dark Gray for drawing the grid lines of the board
C_P1 = "\033[96m"  # Bright Cyan for Player 1 (You) and your pieces
C_P2 = "\033[91m"  # Bright Red for Player 2 (The Bot) and its pieces
C_ROSETTA = "\033[93m"  # Bright Yellow for Rosetta squares (✿) and point alerts
C_SCORE = "\033[92m"  # Green for success
C_ITALIC = "\033[3m"        # Italic text
C_BOLD_TEXT = "\033[1;97m"  # 1 for Bold, 97 for Bright White
C_TEXT = "\033[97m"  # Bright White for headers, menus, and general UI text
C_TUTORIAL = "\033[95m"  # Bright Magenta for tutorial narration
C_HOVER = "\033[46m\033[30m"  # Cyan background, Black text for Hover State

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

NUM_CIRCLES = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦"}
BOARD_ROWS = 3
BOARD_COLUMNS = 8
MISSING_CELLS = ((0, 4), (0, 5), (2, 4), (2, 5))

LOGO = [
    f"{C_BOARD}════════════════════════════════════════════════════════{C_RESET}",
    f"{C_ROSETTA}            T H E   R O Y A L   G A M E   O F{C_RESET}",
    "",
    f"{C_P1}                   ██╗   ██╗██████╗{C_RESET}",
    f"{C_P1}                   ██║   ██║██╔══██╗{C_RESET}",
    f"{C_P1}                   ██║   ██║██████╔╝{C_RESET}",
    f"{C_P1}                   ██║   ██║██╔══██╗{C_RESET}",
    f"{C_P1}                   ╚██████╔╝██║  ██║{C_RESET}",
    f"{C_P1}                    ╚═════╝ ╚═╝  ╚═╝{C_RESET}",
    f"{C_BOARD}════════════════════════════════════════════════════════{C_RESET}"
]

TEMPLATE = """\
╔═══╦═══╦═══╦═══╗       ╔═══╦═══╗
║{a}║{b}║{c}║{d}║       ║{e}║{f}║
╠═══╬═══╬═══╬═══╬═══╦═══╬═══╬═══╣
║{g}║{h}║{i}║{j}║{k}║{l}║{m}║{n}║
╠═══╬═══╬═══╬═══╬═══╩═══╬═══╬═══╣
║{o}║{p}║{q}║{r}║       ║{s}║{t}║
╚═══╩═══╩═══╩═══╝       ╚═══╩═══╝\
"""


VICTORY_ART = f"""
{C_BOARD}       _________________________________________
      /                                         \\
     |    {C_ROSETTA}𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭{C_BOARD}    |
     |  ═══════════════════════════════════════  |
     |                                         |
     |       {C_P1}V I C T O R Y   A T   U R !{C_BOARD}         |
     |                                         |
     |  ───────────────────────────────────────  |
     |        {C_TEXT}T H E   G O D S   S M I L E{C_BOARD}        |
     |            {C_TEXT}U P O N   Y O U{C_BOARD}                |
     |                                         |
     |    {C_ROSETTA}𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭 ☼ 𒀭{C_BOARD}    |
      \\_________________________________________/ {C_RESET}
"""

DEFEAT_ART = f"""
{C_BOARD}       ___________________       _______________
      /                   \\     /               \\
     |    {C_ROSETTA}𒀭 ☼ 𒀭 ☼ 𒀭 ☼{C_BOARD}    \\   /    {C_ROSETTA}𒀭 ☼ 𒀭 ☼{C_BOARD}   |
     |  ═══════════════════|   |══════════════  |
     |                     \\_  |                |
     |       {C_P2}D E F E A T{C_BOARD}     \\ |   {C_P2}A T   U R{C_BOARD}    |
     |                       / |                |
     |  ────────────────────/  |──────────────  |
     |        {C_TEXT}T H E   G O D{C_BOARD} /  | {C_TEXT}S   W E E P{C_BOARD}    |
     |           {C_TEXT}F O R{C_BOARD}     |   / {C_TEXT}Y O U{C_BOARD}          |
     |                     \\  /                 |
     |    {C_ROSETTA}𒀭 ☼ 𒀭 ☼ 𒀭 ☼{C_BOARD}   | |  {C_ROSETTA}𒀭 ☼ 𒀭 ☼{C_BOARD}    |
      \\____________________/   \\_______________/ {C_RESET}
"""
