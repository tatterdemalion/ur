import time
import socket
from typing import Optional
from ur.game import Player, Engine, P1_PATH, P2_PATH
from ur.ai.bots import Bot
from ur.cli.board import Board
from ur.cli.constants import *
from ur.cli.utils import GameUtils
from ur.network import Server, Client, PORT
from ur.saves import SaveFile, save_game, load_save_by_name, list_saves, delete_save, generate_game_name


class LocalMatch:
    def __init__(self, bot: Bot, navigation, save: Optional[SaveFile] = None):
        self.bot = bot
        self.navigation = navigation
        if save:
            self.engine, self.p1, self.p2 = save.restore_engine()
            self.game_name = save.game_name
            self.save_path = save.path
        else:
            self.p1 = Player("You", P1_PATH, "●")
            self.p2 = Player(bot.name, P2_PATH, "●")
            self.engine = Engine(self.p1, self.p2)
            self.game_name = generate_game_name()
            self.save_path = None

        self.ui = Board(self.engine, self.navigation, game_name=self.game_name)

    def start(self):
        while not self.engine.winner:
            roll = self.engine.roll_dice()
            valid_moves = self.engine.get_valid_moves(roll)

            self.ui.draw()
            print(f"Last action: {self.engine.last_action}")

            player_color = C_P1 if self.engine.current_player == self.p1 else C_P2
            turn_text = "Your" if self.engine.current_player == self.p1 else f"{self.engine.current_player.name}'s"
            GameUtils.animate_dice(turn_text, player_color, roll)

            if not valid_moves:
                print("No valid moves. Turn skipped.")
                self.engine.last_action = f"{self.engine.current_player.name} rolled {roll} but had no moves."
                self.engine.switch_player()
                self.save_path = save_game(self.engine, "local", self.game_name, self.save_path)
                time.sleep(2)
                continue

            if self.engine.current_player == self.p1:
                chosen_piece = GameUtils.get_human_move(valid_moves, roll, self.p2, self.bot.name)
                if chosen_piece is None:
                    return  # Abort to menu
            else:
                time.sleep(1.2)
                chosen_piece = GameUtils.get_bot_move(self.bot, self.engine, valid_moves, roll)
                time.sleep(1.2)

            self.engine.execute_move(chosen_piece, roll)
            self.save_path = save_game(self.engine, "local", self.game_name, self.save_path)

        if self.save_path:
            delete_save(self.save_path)
        self.ui.draw()
        print(f"\nGame Over! {self.engine.winner.name} took the crown!")
        self.navigation.print_commands()
        self.navigation.check_global_commands(input("\nPress Enter to return to the main menu: ").strip())


class HostMatch:
    def __init__(self, navigation):
        self.server = Server()
        self.navigation = navigation
        self.game_name = ""
        self.save = None
        self.save_path = None
        self.engine = None
        self.p1 = None
        self.p2 = None
        self.ui = None

    def _setup_game(self):
        self.navigation.clear()
        print(f"{C_BOLD_TEXT}=== HOST GAME ==={C_RESET}\n")

        lan_saves = [s for s in list_saves() if s.mode == "lan"]
        if lan_saves:
            print(f"{C_TEXT}Saved LAN games:{C_RESET}")
            for s in lan_saves:
                print(f"  {C_P1}{s.game_name}{C_RESET}  — saved {s.saved_at[:16]}")
            print()

        self.navigation.print_commands()
        name_input = input("Enter a game name (or press Enter to start fresh): ").strip()
        if self.navigation.check_global_commands(name_input):
            return False

        self.game_name = name_input
        if self.game_name:
            self.save = load_save_by_name(self.game_name)
            if self.save:
                print(f"{C_P1}Save found: {self.save}{C_RESET}")
            else:
                print(f"No save found for '{self.game_name}'. Starting a new game.")
        else:
            self.game_name = generate_game_name()
            print(f"Game name: {C_P1}{self.game_name}{C_RESET}")

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

        print(f"\nYour IP address : {C_P1}{local_ip}{C_RESET}")
        print(f"Listening on port {PORT}...")
        print("\nWaiting for opponent to connect...\n")

        try:
            client_ip = self.server.wait_for_client()
            print(f"Opponent connected from {client_ip}!\n")
            time.sleep(1)

            if self.save:
                self.engine, self.p1, self.p2 = self.save.restore_engine()
                self.save_path = self.save.path
                self.server.send({"type": "restore", "board": GameUtils.serialize_board(self.engine),
                             "last_action": self.engine.last_action,
                             "current_idx": self.engine.current_idx,
                             "game_name": self.game_name})
                print(f"{C_P1}Resuming '{self.game_name}'...{C_RESET}")
                time.sleep(1)
            else:
                self.p1 = Player("You", P1_PATH, "●")
                self.p2 = Player("Opponent", P2_PATH, "●")
                self.engine = Engine(self.p1, self.p2)
                self.save_path = None
                self.server.send({"type": "new_game", "game_name": self.game_name})

            self.ui = Board(self.engine, self.navigation, game_name=self.game_name)

            while not self.engine.winner:
                roll = self.engine.roll_dice()
                valid_moves = self.engine.get_valid_moves(roll)

                self.ui.draw()
                print(f"Last action: {self.engine.last_action}")

                player_color = C_P1 if self.engine.current_player == self.p1 else C_P2
                turn_text = "Your" if self.engine.current_player == self.p1 else "Opponent's"
                GameUtils.animate_dice(turn_text, player_color, roll)

                if not valid_moves:
                    self.server.send({"type": "rolling", "roll": roll,
                                 "board": GameUtils.serialize_board(self.engine)})
                    self.engine.last_action = f"{self.engine.current_player.name} rolled {roll} but had no moves."
                    self.engine.switch_player()
                    self.save_path = save_game(self.engine, "lan", self.game_name, self.save_path)
                    self.server.send({"type": "no_moves", "last_action": self.engine.last_action,
                                 "board": GameUtils.serialize_board(self.engine)})
                    time.sleep(2)
                    continue

                if self.engine.current_player == self.p1:
                    self.server.send({"type": "rolling", "roll": roll,
                                 "board": GameUtils.serialize_board(self.engine)})
                    chosen_piece = GameUtils.get_human_move(valid_moves, roll, self.p2, "Opponent")
                    if chosen_piece is None:
                        return  # Abort to menu
                else:
                    self.server.send({
                        "type": "your_turn",
                        "roll": roll,
                        "valid_moves": [p.identifier for p in valid_moves],
                        "last_action": self.engine.last_action,
                        "board": GameUtils.serialize_board(self.engine),
                    })
                    print("Waiting for opponent to move...")
                    msg = self.server.recv()
                    piece_id = msg["piece_id"]
                    chosen_piece = next(p for p in valid_moves if p.identifier == piece_id)

                self.engine.execute_move(chosen_piece, roll)
                self.save_path = save_game(self.engine, "lan", self.game_name, self.save_path)

                if self.engine.winner:
                    self.server.send({"type": "game_over", "winner": self.engine.winner.name,
                                 "last_action": self.engine.last_action,
                                 "board": GameUtils.serialize_board(self.engine)})
                else:
                    self.server.send({"type": "state", "last_action": self.engine.last_action,
                                 "board": GameUtils.serialize_board(self.engine)})

            if self.save_path:
                delete_save(self.save_path)
            self.ui.draw()
            print(f"\nGame Over! {self.engine.winner.name} took the crown!")

        except (ConnectionError, OSError):
            print(f"\n{C_P2}Opponent disconnected.{C_RESET}")
            time.sleep(2)

        finally:
            self.server.close()

        self.navigation.print_commands()
        self.navigation.check_global_commands(input("\nPress Enter to return to the main menu: ").strip())


class ClientMatch:
    def __init__(self, host_ip: str, navigation):
        self.host_ip = host_ip
        self.navigation = navigation
        self.client = Client(host_ip)
        self.p1 = Player("Host", P1_PATH, "●")
        self.p2 = Player("You", P2_PATH, "●")
        self.engine = Engine(self.p1, self.p2)
        self.ui = None

    def start(self):
        self.navigation.clear()
        print(f"{C_BOLD_TEXT}=== JOIN GAME ==={C_RESET}\n")
        print(f"Connecting to {self.host_ip}:{PORT}...")
        try:
            self.client.connect()
        except Exception:
            print(f"{C_P2}Failed to connect to host.{C_RESET}")
            time.sleep(2)
            return

        print("Connected!\n")
        time.sleep(1)

        try:
            init = self.client.recv()
            game_name = init.get("game_name", "")
            self.ui = Board(self.engine, self.navigation, local_player=self.p2, game_name=game_name)

            if init["type"] == "restore":
                GameUtils.apply_board(self.engine, init["board"])
                self.engine.last_action = init["last_action"]
                self.engine.current_idx = init["current_idx"]
                self.ui.draw()
                print(f"Last action: {self.engine.last_action}")
                print(f"\n{C_P1}Resuming '{game_name}'...{C_RESET}")
                time.sleep(1)

            while True:
                msg = self.client.recv()

                if msg["type"] == "rolling":
                    GameUtils.apply_board(self.engine, msg["board"])
                    self.ui.draw()
                    print(f"Last action: {self.engine.last_action}")
                    GameUtils.animate_dice("Opponent's", C_P2, msg["roll"])

                elif msg["type"] in ("state", "no_moves"):
                    GameUtils.apply_board(self.engine, msg["board"])
                    self.engine.last_action = msg["last_action"]
                    self.ui.draw()
                    print(f"Last action: {self.engine.last_action}")
                    time.sleep(1.2)

                elif msg["type"] == "your_turn":
                    GameUtils.apply_board(self.engine, msg["board"])
                    self.engine.last_action = msg["last_action"]
                    roll = msg["roll"]

                    valid_move_ids = set(msg["valid_moves"])
                    valid_moves = [p for p in self.p2.pieces if p.identifier in valid_move_ids]

                    self.ui.draw()
                    print(f"Last action: {self.engine.last_action}")
                    GameUtils.animate_dice("Your", C_P1, roll)

                    chosen_piece = GameUtils.get_human_move(valid_moves, roll, self.p1, "Host")
                    if chosen_piece is None:
                        return  # Abort to menu
                    self.client.send({"type": "move", "piece_id": chosen_piece.identifier})

                elif msg["type"] == "game_over":
                    GameUtils.apply_board(self.engine, msg["board"])
                    self.engine.last_action = msg["last_action"]
                    self.ui.draw()
                    print(f"\nGame Over! {msg['winner']} took the crown!")
                    break

        except (ConnectionError, OSError):
            print(f"\n{C_P2}Host disconnected.{C_RESET}")
            time.sleep(2)

        finally:
            self.client.close()

        self.navigation.print_commands()
        self.navigation.check_global_commands(input("\nPress Enter to return to the main menu: ").strip())


