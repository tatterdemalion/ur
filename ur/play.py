import os
import sys
import time
import random
import socket
import json
from typing import Optional
from ur.game import Player, Piece, Engine, P1_PATH, P2_PATH, ROSETTAS, FINISH
from ur.ai.bots import Bot, RandomBot, GreedyBot, StrategicBot
from ur.network import Server, Client, PORT
from ur.saves import SaveFile, save_game, load_save_by_name, list_saves, delete_save, generate_game_name

# --- ANSI COLOR CODES ---
C_RESET = "\033[0m"        # Resets terminal color back to default
C_BOARD = "\033[90m"       # Dark Gray for drawing the grid lines of the board
C_P1 = "\033[96m"          # Bright Cyan for Player 1 (You) and your pieces
C_P2 = "\033[91m"          # Bright Red for Player 2 (The Bot) and its pieces
C_ROSETTA = "\033[93m"     # Bright Yellow for Rosetta squares (✿) and point alerts
C_BOLD_TEXT = '\033[1;97m' # 1 for Bold, 97 for Bright White
C_TEXT = "\033[97m"        # Bright White for headers, menus, and general UI text

NUM_CIRCLES = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦"}
BOARD_ROWS = 3
BOARD_COLUMNS = 8
MISSING_CELLS = ((0, 4), (0, 5), (2, 4), (2, 5))

TEMPLATE = """\
╔═══╦═══╦═══╦═══╗       ╔═══╦═══╗
║{a}║{b}║{c}║{d}║       ║{e}║{f}║
╠═══╬═══╬═══╬═══╬═══╦═══╬═══╬═══╣
║{g}║{h}║{i}║{j}║{k}║{l}║{m}║{n}║
╠═══╬═══╬═══╬═══╬═══╩═══╬═══╬═══╣
║{o}║{p}║{q}║{r}║       ║{s}║{t}║
╚═══╩═══╩═══╩═══╝       ╚═══╩═══╝\
"""


SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "session.json")


def _load_session() -> dict:
    try:
        with open(SESSION_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_session(data: dict):
    session = _load_session()
    session.update(data)
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)


COMMANDS_HINT = f"{C_TEXT}  (Type 'menu' to return to main menu, 'exit' / 'quit' / ':q' to quit){C_RESET}"


class BackToMenu(Exception):
    pass


def _is_exit(s: str) -> bool:
    return s.lower() in ("exit", "quit", ":q")


def _is_menu(s: str) -> bool:
    return s.lower() == "menu"


def _handle_command(s: str):
    """Call after any input to handle global commands."""
    if _is_exit(s):
        sys.exit()
    if _is_menu(s):
        raise BackToMenu()


def clear():
    os.system("clear")


class BoardVisualizer:
    def __init__(self, engine: Engine, local_player: Optional[Player] = None, game_name: str = ""):
        self.engine = engine
        self.p1, self.p2 = self.engine.players
        # local_player determines who is drawn at the bottom in cyan.
        # Defaults to p1 (host/single-player perspective).
        self._local = local_player if local_player is not None else self.p1
        self.game_name = game_name

    @property
    def _bottom(self) -> Player:
        return self._local

    @property
    def _top(self) -> Player:
        return self.p2 if self._local is self.p1 else self.p1

    def draw(self):
        clear()

        cells = self._get_cells()

        bottom, top = self._bottom, self._top

        bottom_score = sum(1 for p in bottom.pieces if p.progress == FINISH)
        top_score    = sum(1 for p in top.pieces    if p.progress == FINISH)
        top_waiting  = sum(1 for p in top.pieces    if p.progress == 0)

        top_waiting_line    = f"{C_P2}{' ●' * top_waiting}{C_RESET}"
        bottom_waiting_line = " ".join([
            f"{C_P1}{self._numbered_piece(piece)}{C_RESET}"
            for piece in bottom.pieces if piece.progress == 0
        ])

        top_line    = f"{C_P2} {top.name} {top_score * '●'} {C_RESET}"
        bottom_line = f"{C_P1} {bottom.name} {bottom_score * '●'} {C_RESET}"

        board = TEMPLATE.format(**cells)

        name_display = f"  {C_TEXT}{self.game_name}{C_RESET}" if self.game_name else ""
        game_screen = f"""
{C_BOLD_TEXT}=== THE ROYAL GAME OF UR ==={C_RESET}{name_display}

        {top_line}
        {top_waiting_line}
{C_BOARD}{board}{C_RESET}
         {bottom_waiting_line}
        {bottom_line}
        """
        print(game_screen)

    def _get_cells(self) -> dict[str, str]:
        """
        Generates the visual content for each square on the board.

        We use single-character keys ('a', 'b', 'c') for the template variables
        because the string "{a}" is exactly 3 characters wide. This perfectly
        matches the 3-character width of the ASCII grid walls (e.g., "═══").
        This allows the TEMPLATE string in the source code to be a visually
        perfect 1:1 representation of the final printed board.
        """
        bottom, top = self._bottom, self._top
        cells = {}
        letter_code = 97  # ASCII code for 'a'

        # When local player is P2 (row 0), flip rows so their lane appears at bottom
        row_order = range(BOARD_ROWS - 1, -1, -1) if self._local is self.p2 else range(BOARD_ROWS)

        for r in row_order:
            for c in range(BOARD_COLUMNS):
                coord = (r, c)
                if coord in MISSING_CELLS: continue

                # Base content is always exactly 1 visible character
                content = " "

                if coord in ROSETTAS:
                    content = f"{C_ROSETTA}✿{C_BOARD}"

                for piece in top.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = f"{C_P2}●{C_BOARD}"

                for piece in bottom.pieces:
                    if piece.is_available and piece.coord == coord:
                        content = f"{C_P1}{self._numbered_piece(piece)}{C_BOARD}"

                # Uniformly pad the 1-character content to fit the 3-character walls
                cells[chr(letter_code)] = f" {content} "
                letter_code += 1

        return cells

    def _numbered_piece(self, piece: Piece) -> str:
        return NUM_CIRCLES[piece.identifier]


def _animate_dice(turn_text: str, player_color: str, roll: int):
    for _ in range(12):
        random_dots = " ".join(random.choice(["●", "○"]) for _ in range(4))
        sys.stdout.write(f"\r{turn_text} turn. Rolling...  [{player_color}{random_dots}{C_RESET}]")
        sys.stdout.flush()
        time.sleep(0.06)

    final_faces = ["●"] * roll + ["○"] * (4 - roll)
    random.shuffle(final_faces)
    final_str = " ".join(final_faces)
    sys.stdout.write(f"\r{turn_text} turn. Rolled {roll}! [{player_color}{final_str}{C_RESET}]" + " " * 10 + "\n\n")
    sys.stdout.flush()


def _build_move_hints(piece: Piece, roll: int, p2: Player, bot_name: str) -> str:
    target = piece.progress + roll
    target_coord = piece.player.path[target]
    hints = []

    if target == 15:
        hints.append(f"{C_ROSETTA}Scores a point!{C_RESET}")
    elif target_coord in ROSETTAS:
        hints.append(f"{C_ROSETTA}Lands on Rosetta (Roll again!){C_RESET}")

    if target_coord is not None:
        for opp_piece in p2.pieces:
            if opp_piece.is_available and opp_piece.coord == target_coord:
                hints.append(f"{C_P2}Captures {bot_name}'s piece!{C_RESET}")

    return f" — {' '.join(hints)}" if hints else ""


def _get_human_move(valid_moves: list[Piece], roll: int, p2: Player, bot_name: str) -> Piece:
    print("Your options:")
    valid_moves.sort(key=lambda p: p.identifier)

    for piece in valid_moves:
        target = piece.progress + roll
        status = "Off-board" if piece.progress == 0 else f"Square {piece.progress}"
        hint_text = _build_move_hints(piece, roll, p2, bot_name)
        print(f"  {C_P1}{NUM_CIRCLES[piece.identifier]}{C_RESET} : {status} -> Square {target}{hint_text}")

    print(COMMANDS_HINT)
    while True:
        raw_input = input("\nSelect a piece to move (1-7): ").strip()
        _handle_command(raw_input)
        try:
            choice = int(raw_input)
            chosen = next((p for p in valid_moves if p.identifier == choice), None)
            if chosen:
                return chosen
            print("Invalid choice. That piece cannot move right now.")
        except ValueError:
            print("Please enter a valid piece number.")


def _get_bot_move(bot: Bot, engine: Engine, valid_moves: list[Piece], roll: int) -> Piece:
    state = {
        "my_pieces": sorted([p.progress for p in engine.current_player.pieces]),
        "opp_pieces": sorted([p.progress for p in engine.opponent.pieces]),
        "current_roll": roll,
    }
    return bot.choose_move(state, valid_moves, engine.current_player)


def play_game(bot: Bot, save: SaveFile = None):
    if save:
        engine, p1, p2 = save.restore_engine()
        game_name = save.game_name
        save_path = save.path
    else:
        p1 = Player("You", P1_PATH, "●")
        p2 = Player(bot.name, P2_PATH, "●")
        engine = Engine(p1, p2)
        game_name = generate_game_name()
        save_path = None

    ui = BoardVisualizer(engine, game_name=game_name)

    while not engine.winner:
        roll = engine.roll_dice()
        valid_moves = engine.get_valid_moves(roll)

        ui.draw()
        print(f"Last action: {engine.last_action}")

        player_color = C_P1 if engine.current_player == p1 else C_P2
        turn_text = "Your" if engine.current_player == p1 else f"{engine.current_player.name}'s"
        _animate_dice(turn_text, player_color, roll)

        if not valid_moves:
            print("No valid moves. Turn skipped.")
            engine.last_action = f"{engine.current_player.name} rolled {roll} but had no moves."
            engine.switch_player()
            save_path = save_game(engine, "local", game_name, save_path)
            time.sleep(2)
            continue

        if engine.current_player == p1:
            chosen_piece = _get_human_move(valid_moves, roll, p2, bot.name)
        else:
            time.sleep(1.2)
            chosen_piece = _get_bot_move(bot, engine, valid_moves, roll)
            time.sleep(1.2)

        engine.execute_move(chosen_piece, roll)
        save_path = save_game(engine, "local", game_name, save_path)

    delete_save(save_path)
    ui.draw()
    print(f"\nGame Over! {engine.winner.name} took the crown!")
    print(COMMANDS_HINT)
    _handle_command(input("\nPress Enter to return to the main menu: ").strip())


def show_tutorial():
    clear()
    print(f"{C_BOLD_TEXT}=== HOW TO PLAY THE ROYAL GAME OF UR ==={C_RESET}\n")
    print("1. Objective: Move all 7 of your pieces across the board to the end before your opponent.")
    print("2. Movement: You roll 4 binary dice each turn, yielding a move of 0 to 4 spaces.")
    print("3. Stacking: You cannot land on a square occupied by your own piece.")
    print("4. Combat: Landing on an opponent's piece in the shared middle row 'captures' it,")
    print("   sending it back off-board to start over.")
    print(f"5. Rosettas: Landing on a Rosetta ({C_ROSETTA}✿{C_RESET}) grants an extra turn immediately.")
    print("   Additionally, the central Rosetta is a safe haven where your piece cannot be captured.\n")
    print(COMMANDS_HINT)
    raw = input("\nPress Enter to return to the main menu: ").strip()
    _handle_command(raw)


def _serialize_board(engine: Engine) -> dict:
    """Pack just enough state for the client to redraw its board."""
    stats = engine.get_stats()
    return {
        "p1_pieces": {str(p.identifier): p.progress for p in engine.p1.pieces},
        "p2_pieces": {str(p.identifier): p.progress for p in engine.p2.pieces},
        "stats": {
            "p1_score": stats.p1_score, "p1_waiting": stats.p1_waiting,
            "p2_score": stats.p2_score, "p2_waiting": stats.p2_waiting,
        },
    }


def _apply_board(engine: Engine, board: dict):
    """Overwrite piece progress on the client side from a received board snapshot."""
    for piece in engine.p1.pieces:
        piece.progress = board["p1_pieces"][str(piece.identifier)]
    for piece in engine.p2.pieces:
        piece.progress = board["p2_pieces"][str(piece.identifier)]


def play_network_host():
    """Host a game: you are P1, the remote player is P2."""
    clear()
    print(f"{C_BOLD_TEXT}=== HOST GAME ==={C_RESET}\n")

    lan_saves = [s for s in list_saves() if s.mode == "lan"]
    if lan_saves:
        print(f"{C_TEXT}Saved LAN games:{C_RESET}")
        for s in lan_saves:
            print(f"  {C_P1}{s.game_name}{C_RESET}  — saved {s.saved_at[:16]}")
        print()

    print(COMMANDS_HINT)
    game_name = input("Enter a game name (or press Enter to start fresh): ").strip()
    _handle_command(game_name)

    save = None
    if game_name:
        save = load_save_by_name(game_name)
        if save:
            print(f"{C_P1}Save found: {save}{C_RESET}")
        else:
            print(f"No save found for '{game_name}'. Starting a new game.")
    else:
        game_name = generate_game_name()
        print(f"Game name: {C_P1}{game_name}{C_RESET}")

    server = Server()
    server.start()

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

    client_ip = server.wait_for_client()
    print(f"Opponent connected from {client_ip}!\n")
    time.sleep(1)

    if save:
        engine, p1, p2 = save.restore_engine()
        save_path = save.path
        server.send({"type": "restore", "board": _serialize_board(engine),
                     "last_action": engine.last_action,
                     "current_idx": engine.current_idx,
                     "game_name": game_name})
        print(f"{C_P1}Resuming '{game_name}'...{C_RESET}")
        time.sleep(1)
    else:
        p1 = Player("You", P1_PATH, "●")
        p2 = Player("Opponent", P2_PATH, "●")
        engine = Engine(p1, p2)
        save_path = None
        server.send({"type": "new_game", "game_name": game_name})

    ui = BoardVisualizer(engine, game_name=game_name)

    try:
        while not engine.winner:
            roll = engine.roll_dice()
            valid_moves = engine.get_valid_moves(roll)

            ui.draw()
            print(f"Last action: {engine.last_action}")

            player_color = C_P1 if engine.current_player == p1 else C_P2
            turn_text = "Your" if engine.current_player == p1 else "Opponent's"
            _animate_dice(turn_text, player_color, roll)

            if not valid_moves:
                server.send({"type": "rolling", "roll": roll,
                             "board": _serialize_board(engine)})
                engine.last_action = f"{engine.current_player.name} rolled {roll} but had no moves."
                engine.switch_player()
                save_path = save_game(engine, "lan", game_name, save_path)
                server.send({"type": "no_moves", "last_action": engine.last_action,
                             "board": _serialize_board(engine)})
                time.sleep(2)
                continue

            if engine.current_player == p1:
                # Notify client of the roll so they can animate before seeing the result
                server.send({"type": "rolling", "roll": roll,
                             "board": _serialize_board(engine)})
                chosen_piece = _get_human_move(valid_moves, roll, p2, "Opponent")
            else:
                # Client's turn — ask client
                server.send({
                    "type": "your_turn",
                    "roll": roll,
                    "valid_moves": [p.identifier for p in valid_moves],
                    "last_action": engine.last_action,
                    "board": _serialize_board(engine),
                })
                print("Waiting for opponent to move...")
                msg = server.recv()
                piece_id = msg["piece_id"]
                chosen_piece = next(p for p in valid_moves if p.identifier == piece_id)

            engine.execute_move(chosen_piece, roll)
            save_path = save_game(engine, "lan", game_name, save_path)

            # Push result to client
            if engine.winner:
                server.send({"type": "game_over", "winner": engine.winner.name,
                             "last_action": engine.last_action,
                             "board": _serialize_board(engine)})
            else:
                server.send({"type": "state", "last_action": engine.last_action,
                             "board": _serialize_board(engine)})

        delete_save(save_path)
        ui.draw()
        print(f"\nGame Over! {engine.winner.name} took the crown!")

    except (ConnectionError, OSError):
        print(f"\n{C_P2}Opponent disconnected.{C_RESET}")

    finally:
        server.close()

    print(COMMANDS_HINT)
    _handle_command(input("\nPress Enter to return to the main menu: ").strip())


def play_network_client(host_ip: str):
    """Join a game: you are P2, the host is P1."""
    client = Client(host_ip)

    clear()
    print(f"{C_BOLD_TEXT}=== JOIN GAME ==={C_RESET}\n")
    print(f"Connecting to {host_ip}:{PORT}...")
    client.connect()
    print("Connected!\n")
    time.sleep(1)

    p1 = Player("Host", P1_PATH, "●")
    p2 = Player("You", P2_PATH, "●")
    engine = Engine(p1, p2)

    # First message carries the game name and optional restore state
    init = client.recv()
    game_name = init.get("game_name", "")
    ui = BoardVisualizer(engine, local_player=p2, game_name=game_name)

    if init["type"] == "restore":
        _apply_board(engine, init["board"])
        engine.last_action = init["last_action"]
        engine.current_idx = init["current_idx"]
        ui.draw()
        print(f"Last action: {engine.last_action}")
        print(f"\n{C_P1}Resuming '{game_name}'...{C_RESET}")
        time.sleep(1)

    try:
        while True:
            msg = client.recv()

            if msg["type"] == "rolling":
                # Show current board + animate the opponent's roll
                _apply_board(engine, msg["board"])
                ui.draw()
                print(f"Last action: {engine.last_action}")
                _animate_dice("Opponent's", C_P2, msg["roll"])

            elif msg["type"] in ("state", "no_moves"):
                # Show the result of the opponent's move
                _apply_board(engine, msg["board"])
                engine.last_action = msg["last_action"]
                ui.draw()
                print(f"Last action: {engine.last_action}")
                time.sleep(1.2)

            elif msg["type"] == "your_turn":
                _apply_board(engine, msg["board"])
                engine.last_action = msg["last_action"]
                roll = msg["roll"]

                # Rebuild valid_moves list from piece IDs
                valid_move_ids = set(msg["valid_moves"])
                valid_moves = [p for p in p2.pieces if p.identifier in valid_move_ids]

                ui.draw()
                print(f"Last action: {engine.last_action}")
                _animate_dice("Your", C_P1, roll)

                chosen_piece = _get_human_move(valid_moves, roll, p1, "Host")
                client.send({"type": "move", "piece_id": chosen_piece.identifier})

            elif msg["type"] == "game_over":
                _apply_board(engine, msg["board"])
                engine.last_action = msg["last_action"]
                ui.draw()
                print(f"\nGame Over! {msg['winner']} took the crown!")
                break

    except (ConnectionError, OSError):
        print(f"\n{C_P2}Host disconnected.{C_RESET}")

    finally:
        client.close()

    print(COMMANDS_HINT)
    _handle_command(input("\nPress Enter to return to the main menu: ").strip())


def _pick_local_save_menu() -> Optional[SaveFile]:
    saves = [s for s in list_saves() if s.mode == "local"]
    if not saves:
        print("No local saves found.")
        time.sleep(1.5)
        return None

    clear()
    print(f"{C_BOLD_TEXT}=== CONTINUE GAME ==={C_RESET}\n")
    for i, s in enumerate(saves, 1):
        print(f"  [{i}] {s}")
    print(f"\n{COMMANDS_HINT}\n")

    while True:
        raw = input("Select a save: ").strip()
        _handle_command(raw)
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(saves):
                return saves[idx]
        except ValueError:
            pass
        print("Invalid choice.")


def _bot_by_name(name: str) -> Optional[Bot]:
    return {"RandomBot": RandomBot, "GreedyBot": GreedyBot, "StrategicBot": StrategicBot}.get(name, lambda: None)()


def main_menu():
    while True:
        clear()
        print(f"{C_TEXT}=== THE ROYAL GAME OF UR ==={C_RESET}\n")
        print("  [1] Play vs Bot")
        print("  [2] Continue vs Bot")
        print("  [3] Host Multiplayer Game")
        print("  [4] Join Multiplayer Game")
        print("  [5] How to Play (Tutorial)")
        print(f"\n{COMMANDS_HINT}\n")

        try:
            choice = input("Select an option: ").strip()
            _handle_command(choice)

            if choice == '1':
                bot = select_bot_menu()
                if bot:
                    play_game(bot)
            elif choice == '2':
                save = _pick_local_save_menu()
                if save:
                    bot = _bot_by_name(save.p2_name) or select_bot_menu()
                    if bot:
                        play_game(bot, save=save)
            elif choice == '3':
                play_network_host()
            elif choice == '4':
                clear()
                print(f"{C_BOLD_TEXT}=== JOIN GAME ==={C_RESET}\n")
                last_ip = _load_session().get("last_ip", "")
                prompt = f"Enter host IP address [{last_ip}]: " if last_ip else "Enter host IP address: "
                print(COMMANDS_HINT + "\n")
                host_ip = input(prompt).strip()
                _handle_command(host_ip)
                host_ip = host_ip or last_ip
                if host_ip:
                    _save_session({"last_ip": host_ip})
                    play_network_client(host_ip)
            elif choice == '5':
                show_tutorial()

        except BackToMenu:
            continue


def select_bot_menu():
    while True:
        clear()
        print(f"{C_BOLD_TEXT}=== SELECT OPPONENT ==={C_RESET}\n")
        print("  [1] RandomBot    (Easy - Moves completely randomly)")
        print("  [2] GreedyBot    (Medium - Always takes points or hits immediately)")
        print("  [3] StrategicBot (Hard - Calculates probabilities of danger)")
        print(f"\n{COMMANDS_HINT}\n")

        choice = input("Select an opponent: ").strip()
        _handle_command(choice)

        if choice == '1':
            return RandomBot()
        elif choice == '2':
            return GreedyBot()
        elif choice == '3':
            return StrategicBot()


if __name__ == "__main__":
    main_menu()
