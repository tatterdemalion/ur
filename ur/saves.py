import json
import os
import random
import datetime
from dataclasses import dataclass
from typing import Optional

from ur.game import Player, Engine, P1_PATH, P2_PATH

SAVES_DIR = os.path.join(os.path.dirname(__file__), "..", "saves")

import random

_ADJECTIVES = [
    "Sunbaked", "Cursed", "Divine", "Fallen", "Golden",
    "Brazen", "Exiled", "Sacred", "Forgotten", "Ruthless",
    "Astral", "Ancient", "Royal", "Dusty", "Reckless"
]

_MATERIALS = [
    "Bronze", "Lapis", "Mudbrick", "Clay", "Obsidian",
    "Copper", "Ivory", "Silver", "Reed", "Cedar"
]

_NOUNS = [
    "Ziggurat", "Tablet", "Chariot", "Priestess", "Scribe",
    "King", "Oracle", "Nomad", "Idol", "Relic",
    "River", "Flood", "Dagger", "Tomb", "Crown"
]

_CITIES = [
    "Ur", "Uruk", "Babylon", "Akkad", "Nippur",
    "Eridu", "Lagash", "Sumer", "Kish", "Nineveh"
]

def generate_game_name() -> str:
    """Generates a thematic Mesopotamian save game name."""

    # We define a list of lambda functions, each representing a different naming pattern
    patterns = [
        # Example: Cursed_Ziggurat
        lambda: f"{random.choice(_ADJECTIVES)}_{random.choice(_NOUNS)}",

        # Example: Lapis_Chariot
        lambda: f"{random.choice(_MATERIALS)}_{random.choice(_NOUNS)}",

        # Example: Priestess_of_Uruk
        lambda: f"{random.choice(_NOUNS)}_of_{random.choice(_CITIES)}",

        # Example: Ur_Nomad
        lambda: f"{random.choice(_CITIES)}_{random.choice(_NOUNS)}"
    ]

    return random.choice(patterns)()


def game_name_to_path(name: str) -> str:
    safe = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
    return os.path.join(SAVES_DIR, f"{safe}.json")


@dataclass
class SaveFile:
    path: str
    game_name: str
    mode: str          # "local" | "lan"
    p1_name: str
    p2_name: str
    current_idx: int
    last_action: str
    p1_pieces: dict    # str(identifier) -> progress
    p2_pieces: dict
    started_at: str
    saved_at: str

    def restore_engine(self) -> tuple[Engine, Player, Player]:
        p1 = Player(self.p1_name, P1_PATH, "●")
        p2 = Player(self.p2_name, P2_PATH, "●")
        engine = Engine(p1, p2)
        for piece in p1.pieces:
            piece.progress = self.p1_pieces[str(piece.identifier)]
        for piece in p2.pieces:
            piece.progress = self.p2_pieces[str(piece.identifier)]
        engine.current_idx = self.current_idx
        engine.last_action = self.last_action
        return engine, p1, p2

    def __str__(self) -> str:
        return (
            f"{self.game_name}  [{self.mode}] {self.p1_name} vs {self.p2_name}"
            f"  — saved {self.saved_at[:16]}"
        )


def _ensure_saves_dir():
    os.makedirs(SAVES_DIR, exist_ok=True)


def save_game(engine: Engine, mode: str, game_name: str, path: Optional[str] = None) -> str:
    """Write current engine state to disk. Returns the save file path."""
    _ensure_saves_dir()

    now = datetime.datetime.now().isoformat(timespec="seconds")

    if path is None:
        path = game_name_to_path(game_name)

    started_at = now
    try:
        with open(path) as f:
            started_at = json.load(f).get("started_at", now)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    data = {
        "game_name": game_name,
        "mode": mode,
        "p1_name": engine.p1.name,
        "p2_name": engine.p2.name,
        "current_idx": engine.current_idx,
        "last_action": engine.last_action,
        "p1_pieces": {str(p.identifier): p.progress for p in engine.p1.pieces},
        "p2_pieces": {str(p.identifier): p.progress for p in engine.p2.pieces},
        "started_at": started_at,
        "saved_at": now,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    _prune_saves(keep=10, current_path=path)

    return path


def _prune_saves(keep: int, current_path: str):
    """Delete oldest saves beyond the keep limit, never deleting the current one."""
    all_saves = list_saves()
    if len(all_saves) <= keep:
        return
    for s in all_saves[keep:]:
        if s.path != current_path:
            delete_save(s.path)


def load_save(path: str) -> SaveFile:
    with open(path) as f:
        d = json.load(f)
    return SaveFile(path=path, **d)


def load_save_by_name(name: str) -> Optional[SaveFile]:
    path = game_name_to_path(name)
    try:
        return load_save(path)
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


def list_saves() -> list[SaveFile]:
    """Return all save files sorted by most recently saved."""
    _ensure_saves_dir()
    saves = []
    for filename in os.listdir(SAVES_DIR):
        if filename.endswith(".json"):
            try:
                saves.append(load_save(os.path.join(SAVES_DIR, filename)))
            except (KeyError, json.JSONDecodeError):
                pass
    return sorted(saves, key=lambda s: s.saved_at, reverse=True)


def delete_save(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
