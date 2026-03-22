import os
import sys
import re
import termios
import tty
import select
from typing import Optional

from ur.cli.constants import C_BOARD, C_BOLD_TEXT, C_RESET, C_HOVER, LOGO
from ur.cli.i18n import t

# Regex to strip ANSI colors so we can calculate string length for centering
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def get_keystroke() -> str:
    """Reads a raw keystroke from the terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        # Use os.read to bypass Python's sys.stdin buffer
        ch_bytes = os.read(fd, 1)
        ch = ch_bytes.decode('utf-8', 'replace')

        if ch == '\x1b':
            # Wait 50ms to see if this is an arrow key sequence
            if select.select([fd], [], [], 0.05)[0]:
                ch_bytes += os.read(fd, 2)
                ch = ch_bytes.decode('utf-8', 'replace')
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class Navigation:
    @staticmethod
    def commands_hint() -> str:
        return f"{C_BOARD}{t('nav.commands_hint')}{C_RESET}"

    @staticmethod
    def is_exit(s: str) -> bool:
        return s.lower() in ("exit", "quit", ":q")

    @staticmethod
    def is_menu(s: str) -> bool:
        return s.lower() == "menu"

    @classmethod
    def check_global_commands(cls, s: str) -> bool:
        """Returns True if the user wants to abort to the menu."""
        if cls.is_exit(s):
            sys.exit()
        return cls.is_menu(s)

    @staticmethod
    def print_commands(hint: Optional[str] = None) -> None:
        text = hint if hint is not None else Navigation.commands_hint()
        print(f"\n{text}\n")

    @staticmethod
    def clear():
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

class Menu:
    def __init__(self, title: str):
        self.title = title
        self.options = []

    def add(self, text: str, value):
        """Adds an option to the menu. 'value' is what gets returned if selected."""
        self.options.append((text, value))

    def _render(self, selected_idx: int, width: int, height: int):
        Navigation.clear()

        total_lines = len(LOGO) + 2 + (len(self.options) + 2) + 2
        top_pad = max(0, (height - total_lines) // 2)
        print("\n" * top_pad, end="")

        logo_width = max(len(ANSI_ESCAPE.sub('', line)) for line in LOGO)
        logo_pad = max(0, (width - logo_width) // 2)

        for line in LOGO:
            print(" " * logo_pad + line)

        print("\n")

        title_clean = f"=== {self.title} ==="
        title_pad = max(0, (width - len(title_clean)) // 2)
        print(" " * title_pad + f"{C_BOLD_TEXT}{title_clean}{C_RESET}\n")

        box_width = logo_width
        box_pad = max(0, (width - box_width) // 2)
        inner_width = box_width - 2

        print(" " * box_pad + f"{C_BOARD}╔" + "═" * inner_width + f"╗{C_RESET}")

        for i, (text, _) in enumerate(self.options):
            raw_text = ANSI_ESCAPE.sub('', text)

            padding_total = inner_width - len(raw_text)
            pad_left = padding_total // 2
            pad_right = padding_total - pad_left

            opt_padded = " " * pad_left + text + " " * pad_right

            if i == selected_idx:
                print(" " * box_pad + f"{C_BOARD}║{C_HOVER}{opt_padded}{C_RESET}{C_BOARD}║{C_RESET}")
            else:
                print(" " * box_pad + f"{C_BOARD}║{C_RESET}{opt_padded}{C_BOARD}║{C_RESET}")

        print(" " * box_pad + f"{C_BOARD}╚" + "═" * inner_width + f"╝{C_RESET}")

        # Center the footer hint
        footer = t("nav.commands_hint")
        footer_raw = ANSI_ESCAPE.sub('', footer)
        footer_pad = max(0, (width - len(footer_raw)) // 2)
        print("\n" + " " * footer_pad + f"{C_BOARD}{footer}{C_RESET}")

    def prompt(self):
        """Displays the interactive menu and blocks until a selection is made."""
        if not self.options:
            return None

        selected_idx = 0
        while True:
            try:
                cols, lines = os.get_terminal_size()
            except OSError:
                cols, lines = 80, 24

            self._render(selected_idx, cols, lines)
            key = get_keystroke()

            # Account for standard ANSI arrows and alternate application cursor keys
            if key in ('\x1b[A', '\x1bOA'): # Up Arrow
                selected_idx = (selected_idx - 1) % len(self.options)
            elif key in ('\x1b[B', '\x1bOB'): # Down Arrow
                selected_idx = (selected_idx + 1) % len(self.options)
            elif key in ('\r', '\n'): # Enter
                return self.options[selected_idx][1]
            elif key.lower() == 'q' or key == '\x1b' or key == '\x03': # Q, ESC, or Ctrl+C
                return None
