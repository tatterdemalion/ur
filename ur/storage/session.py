import os
import json


class Session:
    FILE = os.path.join(os.path.dirname(__file__), "../..", "session.json")

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


