.PHONY: install test lint format simulate play tutorial

PYTHON = .venv/bin/python

install:
	uv venv && uv pip install -e ".[dev]"

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
