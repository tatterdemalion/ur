from ur.cli.tui.i18n import set_language
from ur.cli.flows.menu import main_menu
from ur.cli.tui.splash import animate_loading
from ur.storage.session import Session


def run():
    saved_lang = Session.load().get("language", "en")
    set_language(saved_lang)

    animate_loading()
    main_menu()
