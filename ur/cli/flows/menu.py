import sys
from typing import Optional

from ur.ai.bots import Bot, GreedyBot, RandomBot, StrategicBot
from ur.cli.tui.constants import C_BOLD_TEXT, C_RESET, SCREEN_WIDTH
from ur.cli.tui.i18n import set_language, t
from ur.cli.flows.match import ClientMatch, HostMatch, LocalMatch, WebHostMatch, OnlineMatch
from ur.online.client import DEFAULT_HOST, ONLINE_COLORS
from ur.cli.flows.tutorial import TutorialMatch, TUTORIAL_STEPS
from ur.cli.tui.widgets import Menu, Navigation
from ur.cli.tui.output import out
from ur.cli.tui.utils import GameUtils
from ur.storage.session import Session
from ur.storage.saves import SaveFile, list_saves


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
        extra_items=[
            (t("menu.join"), "join_game"),
            (t("menu.web_game"), "web_game"),
        ]
    )


def select_bot_menu() -> Optional[Bot]:
    menu = Menu(t("bot.select_title"))
    menu.add(t("bot.random"), RandomBot())
    menu.add(t("bot.greedy"), GreedyBot())
    menu.add(t("bot.strategic"), StrategicBot())
    menu.add(t("menu.back"), None)
    return menu.prompt()


def tutorial_menu(navigation):
    while True:
        menu = Menu(t("tuto.menu.title"))
        menu.add(t("tuto.menu.start"), "start")
        menu.add(t("menu.back"), None)
        menu.add_separator(t("tuto.menu.steps"))
        for step in TUTORIAL_STEPS:
            menu.add(t(step.title_key), step.step_num)

        choice = menu.prompt()
        if choice is None:
            return
        elif choice == "start":
            TutorialMatch(navigation).start()
        else:
            TutorialMatch(navigation).start(choice, single_step=True)


def language_menu():
    lang_keys = {"en": "lang.english", "tr": "lang.turkish"}
    menu = Menu(t("lang.title"))
    for code, key in lang_keys.items():
        menu.add(t(key), code)
    menu.add(t("menu.back"), None)

    choice = menu.prompt()
    if choice:
        set_language(choice)
        Session.save({"language": choice})


def online_menu(navigation):
    """Prompt for name + color, then connect and enter online lobby."""
    session = Session.load()

    # ── Name ─────────────────────────────────────────────────────────────────
    Navigation.clear()
    out(f"{C_BOLD_TEXT}=== {t('online.title')} ==={C_RESET}\n")
    default_name = session.get("online_name", "")
    prompt = t("online.enter_name_last", name=default_name) if default_name else t("online.enter_name")
    Navigation.print_commands()
    name = input(prompt).strip()
    if Navigation.check_global_commands(name):
        return
    name = name or default_name or "Player"

    # ── Color ─────────────────────────────────────────────────────────────────
    color_menu = Menu(t("online.color_title"))
    for color_name, ansi_code, _ in ONLINE_COLORS:
        color_menu.add(f"{ansi_code}●{C_RESET}  {color_name}", color_name)
    color_menu.add(t("menu.back"), None)

    color_choice = color_menu.prompt()
    if color_choice is None:
        return

    _, ansi_color, hex_color = next(c for c in ONLINE_COLORS if c[0] == color_choice)

    # ── Server ────────────────────────────────────────────────────────────────
    last_host = session.get("last_online_host", DEFAULT_HOST)
    Navigation.clear()
    out(f"{C_BOLD_TEXT}=== {t('online.title')} ==={C_RESET}\n")
    prompt = (
        t("online.enter_host_last", host=last_host) if last_host != DEFAULT_HOST
        else t("online.enter_host")
    )
    Navigation.print_commands()
    host = input(prompt).strip()
    if Navigation.check_global_commands(host):
        return
    host = host or last_host

    # Save preferences
    Session.save({"online_name": name, "last_online_host": host})

    OnlineMatch(host, navigation, name=name, hex_color=hex_color, ansi_color=ansi_color).start()


def main_menu():
    navigation = Navigation()

    while True:
        subtitle = "✧ ══════════════ ✿ ══════════════ ✧"
        menu = Menu(subtitle)
        menu.add(t("menu.single_player"), "single_player")
        menu.add(t("menu.multi_player"), "multi_player")
        menu.add(t("menu.online"), "online")
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
                bot = GameUtils.bot_by_name(save.p2_name)
                if not bot:
                    bot = select_bot_menu()

            if bot:
                LocalMatch(bot, navigation, save=save).start()
            else:
                main_menu()

        elif choice == "multi_player":
            choice = multiplayer_game_menu()
            if choice == "new_game":
                HostMatch(navigation).start()
            elif choice == "web_game":
                WebHostMatch(navigation).start()
            elif choice == "join_game":
                Navigation.clear()
                out(f"{C_BOLD_TEXT}=== {t('join.title')} ==={C_RESET}\n")
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
                HostMatch(navigation).load_game(choice)
            else:
                main_menu()

        elif choice == "online":
            online_menu(navigation)

        elif choice == "tutorial":
            tutorial_menu(navigation)
        elif choice == "language":
            language_menu()
