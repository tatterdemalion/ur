import random
import sys
import time

from ur.cli.constants import C_BOARD, C_P1, C_P2, C_RESET, C_ROSETTA, C_TEXT

LOGO = f"""
{C_BOARD}════════════════════════════════════════════════════════════════{C_RESET}

{C_TEXT}                  T H E   R O Y A L   G A M E   O F{C_RESET}

{C_P1}                        ██╗   ██╗██████╗
                        ██║   ██║██╔══██╗
                        ██║   ██║██████╔╝
                        ██║   ██║██╔══██╗
                        ╚██████╔╝██║  ██║
                         ╚═════╝ ╚═╝  ╚═╝{C_RESET}

{C_BOARD}════════════════════════════════════════════════════════════════{C_RESET}
"""

TASKS = [
    "Sweeping sand off the board...",
    "Carving lapis lazuli...",
    "Consulting the Oracles...",
    "Rolling the tetrahedrons...",
    "Waking the Gods...",
]

def animate_loading():
    # Clear the entire screen and print the static logo
    sys.stdout.write("\033[2J\033[H")
    print(LOGO)

    # Print 2 blank lines so we have space to overwrite our animation
    print("\n\n")

    bar_length = 40

    for i in range(bar_length + 1):
        # ANSI Magic: Move cursor up 2 lines (\033[2A), return to start (\r), clear to bottom (\033[J)
        sys.stdout.write("\033[2A\r\033[J")

        # --- 1. THE CINEMATIC CHASE ANIMATION ---
        track = [" "] * bar_length
        p1_pos = i

        # Scripted Offset Logic for Red Piece
        if i < 8:
            offset = -2               # Starts behind
        elif i < 14:
            offset = min(2, i - 9)    # Accelerates past Cyan
        elif i < 22:
            offset = 2                # Holds the lead
        elif i < 29:
            offset = max(-3, 23 - i)  # Slows down, Cyan catches up
        elif i < 35:
            offset = -3               # Trails behind
        else:
            offset = 0                # Sprints at the end to catch up!

        p2_pos = i + offset

        # Draw the chasing opponent
        if 0 <= p2_pos < bar_length:
            track[p2_pos] = f"{C_P2}●{C_RESET}"

        # Draw the fleeing player (Drawn second so it overlays Red if they clash)
        if 0 <= p1_pos < bar_length:
            track[p1_pos] = f"{C_P1}①{C_RESET}"

        # Draw the safe Rosetta at the very end of the track
        if p1_pos < bar_length:
            # If the spot is empty, draw a flower. If a piece is there, don't overwrite it!
            if track[-1] == " ":
                track[-1] = f"{C_ROSETTA}✿{C_RESET}"
        elif p1_pos >= bar_length:
            # Photo-finish! Cyan hits the Rosetta, Red stops exactly 1 space behind.
            track[-1] = f"{C_P2}●{C_RESET}"
            track[-1] = f"{C_ROSETTA}①{C_RESET}"

        print("".join(track))

        # --- 2. THE PROGRESS BAR ---
        percent = i / bar_length

        # Use Sumerian stars for filled, stone dashes for empty
        filled = f"{C_ROSETTA}" + "𒀭" * i
        empty = f"{C_BOARD}" + "─" * (bar_length - i)
        bar = f"[{filled}{empty}{C_RESET}]"

        # Pick a funny thematic task based on percentage
        task_idx = min(int(percent * len(TASKS)), len(TASKS) - 1)
        task = TASKS[task_idx]

        print(f"{bar} {int(percent * 100)}% {C_TEXT}{task:<30}{C_RESET}")

        # Smooth, slightly randomized sleep timer so it feels natural
        time.sleep(random.uniform(0.02, 0.06))

    time.sleep(0.5)
    print(f"\n        {C_ROSETTA}Press Enter to step into the past...{C_RESET}")
    input()

if __name__ == "__main__":
    animate_loading()
