import json
import os
import sys
import time
from typing import Optional

from ur.ai.bots import Bot, GreedyBot, RandomBot, StrategicBot
from ur.cli.constants import C_BOLD_TEXT, C_RESET, C_ROSETTA, C_TEXT
from ur.cli.match import ClientMatch, HostMatch, LocalMatch
from ur.saves import SaveFile, list_saves


class Session:
    FILE = os.path.join(os.path.dirname(__file__), "..", "session.json")

    @classmethod
    def load(cls) -> dict:
        try:
            with open(cls.FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def save(cls, data: dict):
        session = cls.load()
        session.update(data)
        with open(cls.FILE, "w") as f:
            json.dump(session, f)


class Navigation:
    COMMANDS_HINT = (
        f"{C_TEXT}  (Type 'menu' to return to main menu, 'exit' or 'quit' to quit){C_RESET}"
    )

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
    def print_commands() -> None:
        print(f"\n{Navigation.COMMANDS_HINT}\n")

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

            raw = input("Select an option: ").strip()

            if Navigation.check_global_commands(raw):
                return None

            try:
                idx = int(raw) - 1
                if 0 <= idx < len(self.options):
                    return self.options[idx][1]
            except ValueError:
                pass


def show_tutorial():
    Navigation.clear()
    print(f"{C_BOLD_TEXT}=== HOW TO PLAY THE ROYAL GAME OF UR ==={C_RESET}\n")
    print(
        "1. Objective: Move all 7 of your pieces across the board to the end before your opponent."
    )
    print("2. Movement: You roll 4 binary dice each turn, yielding a move of 0 to 4 spaces.")
    print("3. Stacking: You cannot land on a square occupied by your own piece.")
    print("4. Combat: Landing on an opponent's piece in the shared middle row 'captures' it,")
    print("   sending it back off-board to start over.")
    print(
        f"5. Rosettas: Landing on a Rosetta ({C_ROSETTA}✿{C_RESET}) grants an extra turn immediately."
    )
    print(
        "   Additionally, the central Rosetta is a safe haven where your piece cannot be captured.\n"
    )
    Navigation.print_commands()
    raw = input("\nPress Enter to return to the main menu: ").strip()
    Navigation.check_global_commands(raw)


def _pick_local_save_menu() -> Optional[SaveFile]:
    saves = [s for s in list_saves() if s.mode == "local"]
    if not saves:
        print("No local saves found.")
        time.sleep(1.5)
        return None

    menu = Menu("CONTINUE GAME")
    for s in saves:
        menu.add(str(s), s)

    return menu.prompt()


def _bot_by_name(name: str) -> Optional[Bot]:
    return {"RandomBot": RandomBot, "GreedyBot": GreedyBot, "StrategicBot": StrategicBot}.get(
        name, lambda: None
    )()


def select_bot_menu() -> Optional[Bot]:
    menu = Menu("SELECT OPPONENT")
    menu.add("RandomBot    (Easy - Moves completely randomly)", RandomBot())
    menu.add("GreedyBot    (Medium - Always takes points or hits immediately)", GreedyBot())
    menu.add("StrategicBot (Hard - Calculates probabilities of danger)", StrategicBot())
    return menu.prompt()


def main_menu():
    menu = Menu("THE ROYAL GAME OF UR")
    menu.add("Play vs Bot", "play")
    menu.add("Continue vs Bot", "continue")
    menu.add("Host Multiplayer Game", "host")
    menu.add("Join Multiplayer Game", "join")
    menu.add("How to Play (Tutorial)", "tutorial")

    navigation = Navigation()

    while True:
        choice = menu.prompt()

        if choice == "play":
            bot = select_bot_menu()
            if bot:
                LocalMatch(bot, navigation).start()
        elif choice == "continue":
            save = _pick_local_save_menu()
            if save:
                bot = _bot_by_name(save.p2_name) or select_bot_menu()
                if bot:
                    LocalMatch(bot, navigation, save=save).start()
        elif choice == "host":
            HostMatch(navigation).start()
        elif choice == "join":
            Navigation.clear()
            print(f"{C_BOLD_TEXT}=== JOIN GAME ==={C_RESET}\n")
            last_ip = Session.load().get("last_ip", "")
            prompt = (
                f"Enter host IP address [{last_ip}]: " if last_ip else "Enter host IP address: "
            )
            Navigation.print_commands()
            host_ip = input(prompt).strip()

            if Navigation.check_global_commands(host_ip):
                continue

            host_ip = host_ip or last_ip
            if host_ip:
                Session.save({"last_ip": host_ip})
                ClientMatch(host_ip, navigation).start()
        elif choice == "tutorial":
            show_tutorial()
