from ur.cli.i18n import set_language
from ur.cli.menu import Session, main_menu
from ur.cli.splash import animate_loading


def run():
    saved_lang = Session.load().get("language", "en")
    set_language(saved_lang)

    animate_loading()

    main_menu()
