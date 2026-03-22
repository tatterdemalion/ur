import json
import os
import sys
import time
from typing import Optional

from ur.ai.bots import Bot, GreedyBot, RandomBot, StrategicBot
from ur.cli.constants import C_BOLD_TEXT, C_RESET, SCREEN_WIDTH
from ur.cli.i18n import set_language, t
from ur.cli.match import ClientMatch, HostMatch, LocalMatch
from ur.cli.tutorial import TutorialMatch
from ur.cli.widgets import Menu, Navigation
from ur.cli.utils import GameUtils
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


def _game_selection_menu(title: str, saves: list, extra_items: Optional[list] = None) -> Optional[SaveFile]:
    if not extra_items:
        extra_items = []

    menu = Menu(title)
    menu.add(t("new_game"), "new_game")
    for title, choice in extra_items:
        menu.add(title, choice)

    for save in saves:
        time_ago = GameUtils.time_ago(save.saved_at)
        space = " " * (SCREEN_WIDTH - len(save.game_name) - len(time_ago))
        text = f"{save.game_name}{space}{time_ago}"
        menu.add(text, save)

    menu.add(t("menu.back"), None)
    return menu.prompt()


def local_game_menu() -> Optional[SaveFile]:
    saves = [s for s in list_saves() if s.mode == "local"]
    return _game_selection_menu(title=t("menu.single_player"), saves=saves)


def multiplayer_game_menu() -> Optional[SaveFile]:
    saves = [s for s in list_saves() if s.mode == "lan"]
    return _game_selection_menu(
        title=t("menu.multi_player"),
        saves=saves,
        extra_items=[(t("menu.join"), "join_game")]
    )


def _bot_by_name(name: str) -> Optional[Bot]:
    return {"RandomBot": RandomBot, "GreedyBot": GreedyBot, "StrategicBot": StrategicBot}.get(
        name, lambda: None
    )()


def select_bot_menu() -> Optional[Bot]:
    menu = Menu(t("bot.select_title"))
    menu.add(t("bot.random"), RandomBot())
    menu.add(t("bot.greedy"), GreedyBot())
    menu.add(t("bot.strategic"), StrategicBot())
    menu.add(t("menu.back"), None)
    return menu.prompt()


def _language_menu():
    lang_keys = {"en": "lang.english", "tr": "lang.turkish"}
    menu = Menu(t("lang.title"))
    for code, key in lang_keys.items():
        menu.add(t(key), code)
    menu.add(t("menu.back"), None)

    choice = menu.prompt()
    if choice:
        set_language(choice)
        Session.save({"language": choice})


def main_menu():
    navigation = Navigation()

    while True:
        menu = Menu(t("menu.title"))
        menu.add(t("menu.single_player"), "single_player")
        menu.add(t("menu.multi_player"), "multi_player")
        menu.add(t("menu.tutorial"), "tutorial")
        menu.add(t("menu.language"), "language")
        menu.add(t("menu.quit"), "quit")

        choice = menu.prompt()

        if choice == "quit":
            Navigation.clear()
            sys.exit()

        elif choice == "single_player":
            choice = local_game_menu()
            bot = None
            save = None

            if choice == "new_game":
                bot = select_bot_menu()
            elif isinstance(choice, SaveFile):
                save = choice
                bot = _bot_by_name(save.p2_name) or select_bot_menu()

            if bot:
                LocalMatch(bot, navigation, save=save).start()
            else:
                main_menu()

        elif choice == "multi_player":
            match = HostMatch(navigation)
            choice = multiplayer_game_menu()
            if choice == "new_game":
                match.start()
            elif choice == "join_game":
                Navigation.clear()
                print(f"{C_BOLD_TEXT}=== {t('join.title')} ==={C_RESET}\n")
                last_ip = Session.load().get("last_ip", "")
                prompt = (
                    t("join.enter_ip_last", last_ip=last_ip) if last_ip else t("join.enter_ip")
                )
                Navigation.print_commands()
                host_ip = input(prompt).strip()

                if Navigation.check_global_commands(host_ip):
                    continue

                host_ip = host_ip or last_ip
                if host_ip:
                    Session.save({"last_ip": host_ip})
                    ClientMatch(host_ip, navigation).start()
            elif isinstance(choice, SaveFile):
                save = choice
                match.load_game(save)
            else:
                main_menu()

        elif choice == "tutorial":
            TutorialMatch(navigation).start()
        elif choice == "language":
            _language_menu()
