import os
import sys
from typing import Optional

from ur.cli.constants import C_BOARD, C_BOLD_TEXT, C_RESET
from ur.cli.i18n import t


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
        os.system("clear")


class Menu:
    def __init__(self, title: str):
        self.title = title
        self.options = []

    def add(self, text: str, value):
        """Adds an option to the menu. 'value' is what gets returned if selected."""
        self.options.append((text, value))

    def prompt(self):
        """Displays the menu and loops until a valid choice or command is entered."""
        while True:
            Navigation.clear()
            print(f"{C_BOLD_TEXT}=== {self.title} ==={C_RESET}\n")
            for i, (text, _) in enumerate(self.options, 1):
                print(f"  [{i}] {text}")
            Navigation.print_commands()

            raw = input(t("nav.select_option")).strip()

            if Navigation.check_global_commands(raw):
                return None

            try:
                idx = int(raw) - 1
                if 0 <= idx < len(self.options):
                    return self.options[idx][1]
            except ValueError:
                pass
