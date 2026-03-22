import random
import sys
import time
import os

from ur.cli.constants import C_BOARD, C_P1, C_P2, C_RESET, C_ROSETTA, C_TEXT, LOGO
from ur.cli.i18n import t
from ur.cli.widgets import get_keystroke, ANSI_ESCAPE

_TASK_KEYS = [
    "splash.task.0",
    "splash.task.1",
    "splash.task.2",
    "splash.task.3",
    "splash.task.4",
]

def animate_loading():
    sys.stdout.write("\033[2J\033[H")

    try:
        cols, lines = os.get_terminal_size()
    except OSError:
        cols, lines = 80, 24

    logo_width = max(len(ANSI_ESCAPE.sub('', line)) for line in LOGO)

    total_lines = len(LOGO) + 4
    top_pad = max(0, (lines - total_lines) // 2)
    print("\n" * top_pad, end="")

    for line in LOGO:
        print(" " * max(0, (cols - logo_width) // 2) + line)

    print("\n\n")

    bar_length = 40
    # Calculate left padding for the progress bar
    bar_pad = max(0, (cols - bar_length - 2) // 2)

    for i in range(bar_length + 1):
        sys.stdout.write("\033[2A\r\033[J")

        track = [" "] * bar_length
        p1_pos = i

        if i < 8: offset = -2
        elif i < 14: offset = min(2, i - 9)
        elif i < 22: offset = 2
        elif i < 29: offset = max(-3, 23 - i)
        elif i < 35: offset = -3
        else: offset = 0

        p2_pos = i + offset

        if 0 <= p2_pos < bar_length:
            track[p2_pos] = f"{C_P2}●{C_RESET}"
        if 0 <= p1_pos < bar_length:
            track[p1_pos] = f"{C_P1}①{C_RESET}"

        if p1_pos < bar_length:
            if track[-1] == " ":
                track[-1] = f"{C_ROSETTA}✿{C_RESET}"
        elif p1_pos >= bar_length:
            track[-1] = f"{C_P2}●{C_RESET}"
            track[-1] = f"{C_ROSETTA}①{C_RESET}"

        print(" " * bar_pad + "".join(track))

        percent = i / bar_length
        filled = f"{C_ROSETTA}" + "𒀭" * i
        empty = f"{C_BOARD}" + "─" * (bar_length - i)
        bar = f"[{filled}{empty}{C_RESET}]"

        task_idx = min(int(percent * len(_TASK_KEYS)), len(_TASK_KEYS) - 1)
        task = t(_TASK_KEYS[task_idx])

        # Centered task line
        task_line = f"{bar} {int(percent * 100)}% {C_TEXT}{task:<30}{C_RESET}"
        print(" " * bar_pad + task_line)

        time.sleep(random.uniform(0.02, 0.06))

    time.sleep(0.5)
    prompt = f"{C_ROSETTA}{t('splash.press_enter')}{C_RESET}"
    prompt_raw = ANSI_ESCAPE.sub('', prompt)
    print("\n" + " " * max(0, (cols - len(prompt_raw)) // 2) + prompt)

    get_keystroke()

if __name__ == "__main__":
    animate_loading()
