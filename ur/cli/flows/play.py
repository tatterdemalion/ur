import os

from ur.cli.tui.i18n import set_language
from ur.cli.flows.menu import main_menu
from ur.cli.tui.splash import animate_loading
from ur.cli.flows.tutorial import TutorialMatch
from ur.cli.tui.widgets import Navigation
from ur.storage.session import Session


def run():
    saved_lang = Session.load().get("language", "en")
    set_language(saved_lang)

    step_env = os.environ.get("TUTORIAL_STEP")
    if step_env:
        step = max(1, min(int(step_env), 7))
        TutorialMatch(Navigation()).start(start_step=step)
        return

    animate_loading()
    main_menu()
