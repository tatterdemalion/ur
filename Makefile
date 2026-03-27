.PHONY: install install-online test lint format simulate play tutorial tuto online-server

PYTHON = .venv/bin/python

install:
	uv venv && uv pip install -e ".[dev]"

install-online:
	uv pip install -e ".[dev,online]"

test:
	$(PYTHON) -m pytest ur/tests/ -v

lint:
	$(PYTHON) -m ruff check ur/
	$(PYTHON) -m ruff format --check ur/

format:
	$(PYTHON) -m ruff format ur/
	$(PYTHON) -m ruff check --fix ur/

simulate:
	$(PYTHON) -m ur.simulate $(BOT1) $(BOT2) --games $(or $(GAMES),1000)

watch:
	$(PYTHON) -m ur.simulate $(BOT1) $(BOT2) --show $(if $(GAMES),--games $(GAMES),)

play:
	$(PYTHON) -m ur.play

# Start the online server: make online-server [PORT=8765]
online-server:
	$(PYTHON) -m uvicorn ur.online.server:app --host 0.0.0.0 --port $(or $(PORT),8765) --reload

# Jump straight to a tutorial step: make tuto STEP=3
tuto:
	$(PYTHON) -c "from ur.storage.session import Session; from ur.cli.tui.i18n import set_language; set_language(Session.load().get('language','en')); from ur.cli.tui.widgets import Navigation; from ur.cli.flows.tutorial import TutorialMatch; TutorialMatch(Navigation()).start($(or $(STEP),1))"
