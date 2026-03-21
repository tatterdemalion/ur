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

        # --- 1. THE "MINI GAME" ANIMATION (The Chase) ---
        track = [" "] * bar_length
        p1_pos = i
        p2_pos = i - 3  # Opponent is always 3 steps behind!

        # Draw the chasing opponent
        if 0 <= p2_pos < bar_length:
            track[p2_pos] = f"{C_P2}●{C_RESET}"

        # Draw the fleeing player
        if 0 <= p1_pos < bar_length:
            track[p1_pos] = f"{C_P1}①{C_RESET}"

        # Draw the safe Rosetta at the very end of the track
        if p1_pos < bar_length:
            track[-1] = f"{C_ROSETTA}✿{C_RESET}"
        elif p1_pos == bar_length:
            # When the player reaches the end, they land on the Rosetta!
            track[-1] = f"{C_ROSETTA}①{C_RESET}"

        print(f"           {''.join(track)}")

        # --- 2. THE PROGRESS BAR ---
        percent = i / bar_length

        # Use Sumerian stars for filled, stone dashes for empty
        filled = f"{C_ROSETTA}" + "𒀭" * i
        empty = f"{C_BOARD}" + "─" * (bar_length - i)
        bar = f"[{filled}{empty}{C_RESET}]"

        # Pick a funny thematic task based on percentage
        task_idx = min(int(percent * len(TASKS)), len(TASKS) - 1)
        task = TASKS[task_idx]

        print(f"  {C_TEXT}{task:<30}{C_RESET} {bar} {int(percent * 100)}%")

        # Randomize the sleep timer so it feels like it's actually "loading" things
        time.sleep(random.uniform(0.01, 0.08))
    time.sleep(0.5)
    print(f"\n        {C_ROSETTA}Press Enter to step into the past...{C_RESET}")
    input()

if __name__ == "__main__":
    animate_loading()
