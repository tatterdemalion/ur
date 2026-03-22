import os
import sys
import time
import termios
import tty

# --- ANSI COLOR CODES ---
RESET = "\033[0m"
CYAN = "\033[96m"
GOLD = "\033[93m"
BOARD = "\033[90m"
BOLD = "\033[1m"
HOVER = "\033[46m\033[30m"

# The inner spaces are now mathematically centered relative to the 56-char border
LOGO = [
    f"{BOARD}════════════════════════════════════════════════════════{RESET}",
    f"{GOLD}            T H E   R O Y A L   G A M E   O F{RESET}",
    "",
    f"{CYAN}                   ██╗   ██╗██████╗{RESET}",
    f"{CYAN}                   ██║   ██║██╔══██╗{RESET}",
    f"{CYAN}                   ██║   ██║██████╔╝{RESET}",
    f"{CYAN}                   ██║   ██║██╔══██╗{RESET}",
    f"{CYAN}                   ╚██████╔╝██║  ██║{RESET}",
    f"{CYAN}                    ╚═════╝ ╚═╝  ╚═╝{RESET}",
    f"{BOARD}════════════════════════════════════════════════════════{RESET}"
]

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def get_keystroke():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def render_centered_menu(options, selected_idx, width, height):
    clear_screen()

    total_lines = len(LOGO) + 2 + (len(options) + 2)
    top_pad = max(0, (height - total_lines) // 2)
    print("\n" * top_pad, end="")

    # Calculate Logo padding based on the widest line (56 chars)
    logo_width = max(len(line.replace(CYAN, "").replace(GOLD, "").replace(BOARD, "").replace(RESET, "")) for line in LOGO)
    logo_pad = max(0, (width - logo_width) // 2)

    # Print Logo
    for line in LOGO:
        print(" " * logo_pad + line)

    print("\n")

    # Lock the menu box width to match the logo exactly
    box_width = logo_width
    box_pad = max(0, (width - box_width) // 2)
    inner_width = box_width - 2  # The space available inside the walls

    # Print Top Border
    print(" " * box_pad + f"{BOARD}╔" + "═" * inner_width + f"╗{RESET}")

    # Print Options
    for i, option in enumerate(options):
        # Center the text exactly within the inner width
        opt_padded = option.center(inner_width)

        if i == selected_idx:
            # PERFECT ALIGNMENT: Left Wall (1) + Padded Text (54) + Right Wall (1) = 56
            print(" " * box_pad + f"{BOARD}║{HOVER}{opt_padded}{RESET}{BOARD}║{RESET}")
        else:
            print(" " * box_pad + f"{BOARD}║{RESET}{opt_padded}{BOARD}║{RESET}")

    # Print Bottom Border
    print(" " * box_pad + f"{BOARD}╚" + "═" * inner_width + f"╝{RESET}")

    # Footer hint
    footer = "Use [UP] and [DOWN] arrows. Press [ENTER] to select."
    print("\n" + footer.center(width))

def run_menu():
    options = [
        "Play vs Bot",
        "Continue Saved Game",
        "Host Multiplayer Game",
        "Join Multiplayer Game",
        "How to Play",
        "Quit"
    ]
    selected_idx = 0

    clear_screen()
    cols, lines = os.get_terminal_size()

    logo_width = max(len(l.replace(CYAN, "").replace(GOLD, "").replace(BOARD, "").replace(RESET, "")) for l in LOGO)

    for i in range(len(LOGO)):
        clear_screen()
        for j in range(i + 1):
            print(" " * ((cols - logo_width) // 2) + LOGO[j])
        time.sleep(0.05)
    time.sleep(0.2)

    while True:
        cols, lines = os.get_terminal_size()
        render_centered_menu(options, selected_idx, cols, lines)

        key = get_keystroke()

        if key == '\x1b[A': # Up Arrow
            selected_idx = (selected_idx - 1) % len(options)
        elif key == '\x1b[B': # Down Arrow
            selected_idx = (selected_idx + 1) % len(options)
        elif key in ('\r', '\n'): # Enter Key
            break
        elif key.lower() == 'q' or key == '\x03': # Q or Ctrl+C
            selected_idx = len(options) - 1
            break

    clear_screen()
    selection = options[selected_idx]

    cols, lines = os.get_terminal_size()
    print("\n" * (lines // 2))
    print(f"{CYAN}You selected: {BOLD}{selection}{RESET}".center(cols + 12))
    print("\n" * (lines // 2))

if __name__ == "__main__":
    try:
        run_menu()
    except Exception as e:
        os.system("stty sane")
        print(e)
