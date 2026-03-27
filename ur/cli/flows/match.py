import time
from typing import Optional

from ur.ai.bots import Bot
from ur.cli.tui.board import Board
from ur.cli.tui.constants import C_BOLD_TEXT, C_P1, C_P2, C_RESET, DEFEAT_ART, VICTORY_ART
from ur.cli.tui.i18n import t
from ur.cli.tui.output import out, word_wrap, center
from ur.cli.tui.utils import GameUtils
from dataclasses import asdict

from ur.game.engine import Action, Engine, Player
from ur.online.client import ClientProtocol, OnlineSocket, ONLINE_PORT, DEFAULT_HOST
from ur.game.rules import P1_PATH, P2_PATH
from ur.storage.saves import (
    SaveFile,
    delete_save,
    generate_game_name,
    save_game,
)


class Match:
    """Base class handling common UI, display, and state management for all game modes."""

    def __init__(self, navigation):
        self.navigation = navigation
        self.game_name = ""
        self.save_path = None
        self.engine = None
        self.p1 = None
        self.p2 = None
        self.ui = None

    def print_header(self, title: str):
        self.navigation.clear()
        out(f"{C_BOLD_TEXT}=== {title} ==={C_RESET}\n")

    def show_message(self, msg: str, delay: float = 0.0):
        out(center(msg))
        if delay > 0:
            time.sleep(delay)

    def update_display(self, show_labels: bool = False):
        """Redraws the board and displays the last action."""
        if self.ui and self.engine:
            self.ui.draw(show_labels=show_labels)
            local_idx = 0 if self.ui._local is self.engine.p1 else 1
            opp_name = self.ui._top.name
            action_text = f"{t('match.last_action')}{GameUtils.format_action(self.engine.last_action, local_idx, opp_name)}"
            out(word_wrap(action_text, centered=True))

    def save_state(self, mode: str):
        """Saves the current engine state to disk."""
        if self.engine and self.game_name:
            self.save_path = save_game(self.engine, mode, self.game_name, self.save_path)

    def handle_disconnect(self):
        self.show_message(f"{t('match.disconnected')}{C_RESET}", 2.0)

    def end_game(self, is_victory: bool):
        """Cleans up the save file, displays the victory/defeat art, then prompts to return to menu."""
        if self.save_path:
            delete_save(self.save_path)
        self.navigation.clear()
        out(VICTORY_ART if is_victory else DEFEAT_ART)
        time.sleep(5)
        self.navigation.print_commands()
        self.navigation.check_global_commands(
            input(t("match.press_enter_menu")).strip()
        )


class LocalMatch(Match):
    def __init__(self, bot: Bot, navigation, save: Optional[SaveFile] = None):
        super().__init__(navigation)
        self.bot = bot
        if save:
            self.engine, self.p1, self.p2 = save.restore_engine()
            self.p2.name = self.bot.name
            self.game_name = save.game_name
            self.save_path = save.path
        else:
            self.p1 = Player(0, t("player.you"), P1_PATH)
            self.p2 = Player(1, bot.name, P2_PATH)
            self.engine = Engine(self.p1, self.p2)
            self.game_name = generate_game_name()

        self.ui = Board(self.engine, self.navigation, game_name=self.game_name)

    def start(self):
        while not self.engine.winner:
            roll = self.engine.roll_dice()
            valid_moves = self.engine.get_valid_moves(roll)

            self.update_display()

            player_color = C_P1 if self.engine.current_player == self.p1 else C_P2
            GameUtils.animate_dice(player_color, roll)

            if not valid_moves:
                self.show_message(t("match.no_valid_moves"), 0)
                self.engine.skip_turn(roll)
                self.save_state("local")
                time.sleep(2.0)
                continue

            if self.engine.current_player == self.p1:
                chosen_move = GameUtils.get_human_move(valid_moves, self.ui, roll, player_color)
                if chosen_move is None:
                    return  # Abort to menu
            else:
                time.sleep(1.2)
                chosen_move = GameUtils.get_bot_move(self.bot, self.engine, valid_moves, roll)
                time.sleep(1.2)

            self.engine.execute_move(chosen_move, roll)
            self.save_state("local")

        self.end_game(self.engine.winner.player_idx == self.p1.player_idx)


class OnlineMatch(Match):
    """Connect to a central online server, browse the lobby, and play."""

    def __init__(self, host: str, navigation, name: str = "Player", hex_color: str = "#d42020", ansi_color: str = ""):
        super().__init__(navigation)
        url = f"ws://{host}:{ONLINE_PORT}/ws"
        self._socket = OnlineSocket(url)
        self._host = host
        self._name = name
        self._hex_color = hex_color
        self._ansi_color = ansi_color or C_P1

    def _wait_for_matched(self) -> dict:
        """Consume messages until 'matched' arrives (skips lobby updates)."""
        while True:
            msg = self._socket.recv()
            if msg.get("type") == "matched":
                return msg
            # else: games/waiting updates while hosting — ignore

    def start(self):
        from ur.cli.tui.widgets import Menu
        from ur.cli.tui.constants import SCREEN_WIDTH

        self.print_header(t("online.title"))
        out(t("online.connecting", host=self._host, port=str(ONLINE_PORT)))

        try:
            self._socket.connect()
        except Exception:
            self.show_message(f"{C_P2}{t('match.failed_connect')}{C_RESET}", 2.0)
            return

        try:
            # 1 — receive "lobby" confirmation
            msg = self._socket.recv()
            if msg.get("type") != "lobby":
                self.show_message(f"{C_P2}{t('online.match_error')}{C_RESET}", 2.0)
                return

            # 2 — receive current games list
            msg = self._socket.recv()
            games = msg.get("games", []) if msg.get("type") == "games" else []

            # 3 — show lobby menu
            self.print_header(t("online.title"))
            menu = Menu(t("online.choose_game"))
            menu.add(t("online.create_game"), "create")
            for g in games:
                space = " " * max(1, SCREEN_WIDTH - len(g["host_name"]) - len(g["game_name"]) - 2)
                menu.add(f"{g['host_name']}{space}{g['game_name']}", g["game_id"])
            menu.add(t("menu.back"), None)

            choice = menu.prompt()
            if choice is None:
                return

            # 4 — create or join
            if choice == "create":
                self._socket.send({"type": "create", "name": self._name, "color": self._hex_color})
                msg = self._socket.recv()  # "waiting"
                if msg.get("type") == "waiting":
                    self.print_header(t("online.title"))
                    out(center(t("online.waiting")))
                matched = self._wait_for_matched()
            else:
                self._socket.send({"type": "join", "game_id": choice, "name": self._name, "color": self._hex_color})
                matched = self._socket.recv()
                if matched.get("type") == "error":
                    self.show_message(f"{C_P2}{matched.get('msg', t('online.match_error'))}{C_RESET}", 2.0)
                    return
                if matched.get("type") != "matched":
                    self.show_message(f"{C_P2}{t('online.match_error')}{C_RESET}", 2.0)
                    return

            # 5 — set up game from matched message
            player_idx = matched["player_idx"]
            self.game_name = matched.get("game_name", "")
            opp_name = matched.get("opponent", {}).get("name", t("player.opponent"))

            self.show_message(t("online.matched"), 1.0)

            if player_idx == 0:
                self.p1 = Player(0, self._name, P1_PATH)
                self.p2 = Player(1, opp_name, P2_PATH)
            else:
                self.p1 = Player(0, opp_name, P1_PATH)
                self.p2 = Player(1, self._name, P2_PATH)

            self.engine = Engine(self.p1, self.p2)
            local_player = self.p1 if player_idx == 0 else self.p2
            my_color = self._ansi_color

            self.ui = Board(
                self.engine, self.navigation,
                local_player=local_player, game_name=self.game_name,
            )
            self.update_display()

            def on_rolling(board: dict, roll: int, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.update_display()
                GameUtils.animate_dice(C_P2 if player_idx == 0 else C_P1, roll)
                out(center(t("match.waiting_opponent")))

            def on_state(board: dict, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.update_display()
                time.sleep(1.2)

            def on_no_moves(board: dict, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.update_display()
                time.sleep(1.2)

            def on_your_turn(board: dict, roll: int, valid_move_ids: list, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.engine.current_idx = player_idx
                valid_moves = self.engine.get_valid_moves(roll)
                valid_moves = [m for m in valid_moves if m.piece.identifier in set(valid_move_ids)]
                self.update_display()
                GameUtils.animate_dice(my_color, roll)
                chosen = GameUtils.get_human_move(valid_moves, self.ui, roll, my_color)
                if chosen is None:
                    return None
                return chosen.piece.identifier

            def on_game_over(board: dict, winner_idx: int, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.end_game(winner_idx == player_idx)

            protocol = ClientProtocol(
                client=self._socket,
                engine=self.engine,
                on_rolling=on_rolling,
                on_state=on_state,
                on_no_moves=on_no_moves,
                on_your_turn=on_your_turn,
                on_game_over=on_game_over,
            )
            protocol.run()

        except (ConnectionError, OSError, KeyboardInterrupt):
            self.handle_disconnect()
        except Exception:
            self.handle_disconnect()

        finally:
            self._socket.close()
