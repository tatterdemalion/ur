import os
import sys
import re
import termios
import tty
import select
from typing import Optional

from ur.cli.tui.constants import (
    ANSI_ESCAPE,
    C_BOARD,
    C_BOLD_TEXT,
    C_RESET,
    C_HOVER,
    LOGO,
)
from ur.cli.tui.i18n import t
from ur.cli.tui.output import ansi_len, center, center_in, out


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
        out(f"\n{center(text)}\n")

    @staticmethod
    def clear():
        out("\033[2J\033[H", end="")

_SEPARATOR = object()


class Menu:
    def __init__(self, title: str, subtitle: str = ""):
        self.title = title
        self.subtitle = subtitle
        self.options = []

    def add(self, text: str, value):
        """Adds an option to the menu. 'value' is what gets returned if selected."""
        self.options.append((text, value))

    def add_separator(self, label: str = ""):
        """Adds a non-selectable separator line, optionally with a centered label."""
        self.options.append((label, _SEPARATOR))

    def _selectable_indices(self) -> list:
        return [i for i, (_, v) in enumerate(self.options) if v is not _SEPARATOR]

    def _next_selectable(self, current: int, direction: int) -> int:
        sel = self._selectable_indices()
        if not sel:
            return current
        pos = sel.index(current) if current in sel else 0
        return sel[(pos + direction) % len(sel)]

    def _render(self, selected_idx: int, width: int, height: int):
        Navigation.clear()

        subtitle_lines = 1 if self.subtitle else 0
        total_lines = len(LOGO) + 2 + subtitle_lines + (len(self.options) + 2) + 2
        top_pad = max(0, (height - total_lines) // 2)
        out("\n" * top_pad, end="")

        logo_width = max(len(ANSI_ESCAPE.sub('', line)) for line in LOGO)
        logo_pad = max(0, (width - logo_width) // 2)

        for line in LOGO:
            out(" " * logo_pad + line)

        out("\n")

        out(center(f"{C_BOLD_TEXT}{self.title}{C_RESET}"))
        if self.subtitle:
            out(center(f"{C_BOARD}{self.subtitle}{C_RESET}"))
        out("")

        box_width = logo_width
        inner_width = box_width - 2

        out(center(f"{C_BOARD}╔" + "═" * inner_width + f"╗{C_RESET}"))

        for i, (text, value) in enumerate(self.options):
            if value is _SEPARATOR:
                if text:
                    out(center(f"{C_BOARD}╠{center_in(f' {text} ', inner_width, '═')}╣{C_RESET}"))
                else:
                    out(center(f"{C_BOARD}╠" + "═" * inner_width + f"╣{C_RESET}"))
                continue

            raw_text = ANSI_ESCAPE.sub('', text)
            padding_total = inner_width - len(raw_text)
            pad_left = padding_total // 2
            pad_right = padding_total - pad_left
            opt_padded = " " * pad_left + text + " " * pad_right

            if i == selected_idx:
                out(center(f"{C_BOARD}║{C_HOVER}{opt_padded}{C_RESET}{C_BOARD}║{C_RESET}"))
            else:
                out(center(f"{C_BOARD}║{C_RESET}{opt_padded}{C_BOARD}║{C_RESET}"))

        out(center(f"{C_BOARD}╚" + "═" * inner_width + f"╝{C_RESET}"))
        out("\n")

    def prompt(self):
        """Displays the interactive menu and blocks until a selection is made."""
        sel = self._selectable_indices()
        if not sel:
            return None

        selected_idx = sel[0]
        while True:
            try:
                cols, lines = os.get_terminal_size()
            except OSError:
                cols, lines = 80, 24

            self._render(selected_idx, cols, lines)
            key = get_keystroke()

            # Account for standard ANSI arrows and alternate application cursor keys
            if key in ('\x1b[A', '\x1bOA'): # Up Arrow
                selected_idx = self._next_selectable(selected_idx, -1)
            elif key in ('\x1b[B', '\x1bOB'): # Down Arrow
                selected_idx = self._next_selectable(selected_idx, 1)
            elif key in ('\r', '\n'): # Enter
                return self.options[selected_idx][1]
            elif key.lower() == 'q' or key == '\x1b' or key == '\x03': # Q, ESC, or Ctrl+C
                return None
