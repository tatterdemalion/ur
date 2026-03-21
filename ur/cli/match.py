import socket
import time
from typing import Optional

from ur.ai.bots import Bot
from ur.cli.board import Board
from ur.cli.constants import C_BOLD_TEXT, C_P1, C_P2, C_RESET, C_TEXT, DEFEAT_ART, VICTORY_ART
from ur.cli.i18n import t
from ur.cli.protocol import ClientProtocol, HostProtocol
from ur.cli.utils import GameUtils
from dataclasses import asdict

from ur.game import Action, Engine, Move, Player
from ur.network import PORT, Client, Server
from ur.rules import P1_PATH, P2_PATH
from ur.saves import (
    SaveFile,
    delete_save,
    generate_game_name,
    list_saves,
    load_save_by_name,
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
        print(f"{C_BOLD_TEXT}=== {title} ==={C_RESET}\n")

    def show_message(self, msg: str, delay: float = 0.0):
        print(msg)
        if delay > 0:
            time.sleep(delay)

    def update_display(self):
        """Redraws the board and displays the last action."""
        if self.ui and self.engine:
            self.ui.draw()
            local_idx = 0 if self.ui._local is self.engine.p1 else 1
            opp_name = self.ui._top.name
            print(f"{t('match.last_action')}{GameUtils.format_action(self.engine.last_action, local_idx, opp_name)}")

    def save_state(self, mode: str):
        """Saves the current engine state to disk."""
        if self.engine and self.game_name:
            self.save_path = save_game(self.engine, mode, self.game_name, self.save_path)

    def handle_disconnect(self):
        self.show_message(f"{t('match.opponent_disconnected')}{C_RESET}", 2.0)

    def end_game(self, is_victory: bool):
        """Cleans up the save file, displays the victory/defeat art, then prompts to return to menu."""
        if self.save_path:
            delete_save(self.save_path)
        self.navigation.clear()
        print(VICTORY_ART if is_victory else DEFEAT_ART)
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
            turn_text = (
                t("match.your_turn")
                if self.engine.current_player == self.p1
                else t("match.opponent_turn", name=self.engine.current_player.name)
            )
            GameUtils.animate_dice(turn_text, player_color, roll)

            if not valid_moves:
                self.show_message(t("match.no_valid_moves"), 0)
                self.engine.skip_turn(roll)
                self.save_state("local")
                time.sleep(2.0)
                continue

            if self.engine.current_player == self.p1:
                chosen_move = GameUtils.get_human_move(valid_moves, self.p2, self.bot.name, self.navigation)  # noqa: E501
                if chosen_move is None:
                    return  # Abort to menu
            else:
                time.sleep(1.2)
                chosen_move = GameUtils.get_bot_move(self.bot, self.engine, valid_moves, roll)
                time.sleep(1.2)

            self.engine.execute_move(chosen_move, roll)
            self.save_state("local")

        self.end_game(self.engine.winner.player_idx == self.p1.player_idx)


class HostMatch(Match):
    def __init__(self, navigation):
        super().__init__(navigation)
        self.server = Server()
        self.save = None

    def _setup_game(self):
        self.print_header(t("host.title"))

        lan_saves = [s for s in list_saves() if s.mode == "lan"]
        if lan_saves:
            print(f"{C_TEXT}{t('host.saved_lan_games')}{C_RESET}")
            for s in lan_saves:
                print(f"  {C_P1}{s.game_name}{C_RESET}  — saved {s.saved_at[:16]}")
            print()

        self.navigation.print_commands()
        name_input = input(t("host.enter_game_name")).strip()
        if self.navigation.check_global_commands(name_input):
            return False

        self.game_name = name_input
        if self.game_name:
            self.save = load_save_by_name(self.game_name)
            if self.save:
                print(f"{C_P1}{t('match.save_found')}{self.save}{C_RESET}")
            else:
                print(t("host.no_save_found", name=self.game_name))
        else:
            self.game_name = generate_game_name()
            print(f"{t('host.game_name_label')}{C_P1}{self.game_name}{C_RESET}")

        return True

    def start(self):
        if not self._setup_game():
            return

        self.server.start()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "127.0.0.1"

        print(f"{t('host.your_ip')}{C_P1}{local_ip}{C_RESET}")
        print(t("host.listening", port=str(PORT)))
        print(t("host.waiting"))

        try:
            client_ip = self.server.wait_for_client()
            self.show_message(t("host.opponent_connected", ip=client_ip), 1.0)

            if self.save:
                self.engine, self.p1, self.p2 = self.save.restore_engine()
                self.save_path = self.save.path
                self.server.send(
                    {
                        "type": "restore",
                        "board": self.engine.snapshot(),
                        "last_action": asdict(self.engine.last_action),
                        "current_idx": self.engine.current_idx,
                        "game_name": self.game_name,
                    }
                )
                self.show_message(f"{C_P1}{t('host.resuming', name=self.game_name)}{C_RESET}", 1.0)
            else:
                self.p1 = Player(0, t("player.you"), P1_PATH)
                self.p2 = Player(1, t("player.opponent"), P2_PATH)
                self.engine = Engine(self.p1, self.p2)
                self.server.send({"type": "new_game", "game_name": self.game_name})

            self.ui = Board(self.engine, self.navigation, game_name=self.game_name)

            def on_my_turn(valid_moves: list, roll: int):
                self.update_display()
                GameUtils.animate_dice(t("match.your_turn"), C_P1, roll)
                return GameUtils.get_human_move(valid_moves, self.p2, t("player.opponent"), self.navigation)

            def on_state(last_action):
                self.save_state("lan")
                self.update_display()

            def on_opponent_thinking():
                print(t("match.waiting_opponent"))

            def on_no_moves(roll: int):
                self.save_state("lan")
                self.update_display()
                time.sleep(2.0)

            def on_game_over(winner_idx: int):
                self.end_game(winner_idx == self.p1.player_idx)

            # Show the board once before the loop begins
            self.update_display()

            protocol = HostProtocol(
                server=self.server,
                engine=self.engine,
                p1=self.p1,
                p2=self.p2,
                on_my_turn=on_my_turn,
                on_state=on_state,
                on_opponent_thinking=on_opponent_thinking,
                on_no_moves=on_no_moves,
                on_game_over=on_game_over,
            )
            protocol.run()

        except (ConnectionError, OSError):
            self.handle_disconnect()

        finally:
            self.server.close()


class ClientMatch(Match):
    def __init__(self, host_ip: str, navigation):
        super().__init__(navigation)
        self.host_ip = host_ip
        self.client = Client(host_ip)
        self.p1 = Player(0, t("player.opponent"), P1_PATH)
        self.p2 = Player(1, t("player.you"), P2_PATH)
        self.engine = Engine(self.p1, self.p2)

    def start(self):
        self.print_header(t("join.title"))
        print(t("match.connecting", host=self.host_ip, port=str(PORT)))
        try:
            self.client.connect()
        except (ConnectionRefusedError, OSError, socket.timeout):
            self.show_message(f"{C_P2}{t('match.failed_connect')}{C_RESET}", 2.0)
            return

        self.show_message(t("match.connected"), 1.0)

        try:
            init = self.client.recv()
            self.game_name = init.get("game_name", "")
            self.ui = Board(
                self.engine, self.navigation, local_player=self.p2, game_name=self.game_name
            )

            if init["type"] == "restore":
                self.engine.restore(init["board"])
                self.engine.last_action = Action(**init["last_action"])
                self.engine.current_idx = init["current_idx"]
                self.update_display()
                self.show_message(f"\n{C_P1}{t('host.resuming', name=self.game_name)}{C_RESET}", 1.0)

            def on_rolling(board: dict, roll: int, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.update_display()
                GameUtils.animate_dice(t("match.opponent_turn_anim"), C_P2, roll)
                print(t("match.waiting_opponent"))

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
                self.engine.current_idx = 1  # client is always p2
                valid_moves = self.engine.get_valid_moves(roll)
                valid_moves = [m for m in valid_moves if m.piece.identifier in set(valid_move_ids)]
                self.update_display()
                GameUtils.animate_dice(t("match.your_turn"), C_P1, roll)
                chosen_move = GameUtils.get_human_move(valid_moves, self.p1, t("player.opponent"), self.navigation)
                if chosen_move is None:
                    return None
                return chosen_move.piece.identifier

            def on_game_over(board: dict, winner_idx: int, last_action: dict):
                self.engine.restore(board)
                self.engine.last_action = Action(**last_action)
                self.end_game(winner_idx == self.p2.player_idx)

            protocol = ClientProtocol(
                client=self.client,
                engine=self.engine,
                on_rolling=on_rolling,
                on_state=on_state,
                on_no_moves=on_no_moves,
                on_your_turn=on_your_turn,
                on_game_over=on_game_over,
            )
            protocol.run()

        except (ConnectionRefusedError, OSError, socket.timeout):
            self.handle_disconnect()

        finally:
            self.client.close()
