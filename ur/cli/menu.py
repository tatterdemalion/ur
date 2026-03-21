import json
import os
import time
from typing import Optional

from ur.ai.bots import Bot, GreedyBot, RandomBot, StrategicBot
from ur.cli.constants import C_BOLD_TEXT, C_RESET, C_ROSETTA
from ur.cli.i18n import set_language, t
from ur.cli.match import ClientMatch, HostMatch, LocalMatch
from ur.cli.widgets import Menu, Navigation
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


def show_tutorial():
    Navigation.clear()
    print(f"{C_BOLD_TEXT}=== {t('tutorial.title')} ==={C_RESET}\n")
    print(t("tutorial.line1"))
    print(t("tutorial.line2"))
    print(t("tutorial.line3"))
    print(t("tutorial.line4"))
    print(t("tutorial.line4b"))
    print(t("tutorial.line5", rosetta=f"{C_ROSETTA}✿{C_RESET}"))
    print(f"{t('tutorial.line5b')}\n")
    Navigation.print_commands()
    raw = input(t("nav.press_enter_menu")).strip()
    Navigation.check_global_commands(raw)


def _pick_local_save_menu() -> Optional[SaveFile]:
    saves = [s for s in list_saves() if s.mode == "local"]
    if not saves:
        print(t("continue.no_saves"))
        time.sleep(1.5)
        return None

    menu = Menu(t("continue.title"))
    for s in saves:
        menu.add(str(s), s)

    return menu.prompt()


def _bot_by_name(name: str) -> Optional[Bot]:
    return {"RandomBot": RandomBot, "GreedyBot": GreedyBot, "StrategicBot": StrategicBot}.get(
        name, lambda: None
    )()


def select_bot_menu() -> Optional[Bot]:
    menu = Menu(t("bot.select_title"))
    menu.add(t("bot.random"), RandomBot())
    menu.add(t("bot.greedy"), GreedyBot())
    menu.add(t("bot.strategic"), StrategicBot())
    return menu.prompt()


def _language_menu():
    lang_keys = {"en": "lang.english", "de": "lang.german", "nl": "lang.dutch", "es": "lang.spanish", "tr": "lang.turkish"}
    menu = Menu(t("lang.title"))
    for code, key in lang_keys.items():
        menu.add(t(key), code)
    choice = menu.prompt()
    if choice:
        set_language(choice)
        Session.save({"language": choice})


def main_menu():
    navigation = Navigation()

    while True:
        menu = Menu(t("menu.title"))
        menu.add(t("menu.play_vs_bot"), "play")
        menu.add(t("menu.continue_vs_bot"), "continue")
        menu.add(t("menu.host"), "host")
        menu.add(t("menu.join"), "join")
        menu.add(t("menu.tutorial"), "tutorial")
        menu.add(t("menu.language"), "language")

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
        elif choice == "tutorial":
            show_tutorial()
        elif choice == "language":
            _language_menu()
