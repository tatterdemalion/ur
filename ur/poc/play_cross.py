"""
Royal Game of Ur — Cross Board
A self-contained play module for the cross-shaped board (ur/poc/rules_cross.py).

Menu modes
----------
  Human vs StrategicBot       — you play P1 (West arm)
  StrategicBot vs StrategicBot — fully automated, watch the game
  RandomBot vs RandomBot       — fully automated, random play

Run via:
  make cross          # full speed
  make cross-step     # STEP=1 pauses between turns
"""

import os
import sys
import time

from ur.cli.tui.constants import (
    C_BOARD,
    C_BOLD_TEXT,
    C_P1,
    C_P2,
    C_P3,
    C_RESET,
    C_ROSETTA,
    C_SCORE,
    NUM_CIRCLES,
    VICTORY_ART,
    DEFEAT_ART,
)
from ur.cli.tui.i18n import t
from ur.cli.tui.output import center, out, word_wrap
from ur.cli.tui.utils import GameUtils
from ur.cli.tui.widgets import Menu, Navigation
from ur.poc.board_cross import CrossBoard
from ur.poc.bots3 import RandomBot, StrategicBot
from ur.poc.engine3 import ActionType, Engine, Player
from ur.poc.rules_cross import (
    CROSS_ROSETTAS,
    CROSS_ROSETTAS_3P,
    FINISH,
    P1_PATH_CROSS,
    P2_PATH_CROSS,
    P3_PATH_CROSS,
    PIECES_PER_PLAYER,
)

_STEP = os.environ.get("STEP") == "1"
_BOT_PAUSE = 1.2  # seconds between bot turns


_PLAYER_COLORS = [C_P1, C_P2, C_P3]


def _fmt_action(engine: Engine, local_idx: int) -> str:
    """Format the last engine action into a readable status line."""
    a = engine.last_action
    if a.action_type == ActionType.STARTED:
        return t("action.game_started")

    player = engine.players[a.player_idx]
    is_local = a.player_idx == local_idx
    color = _PLAYER_COLORS[a.player_idx] if a.player_idx < len(_PLAYER_COLORS) else C_RESET
    roll_str = f"{color}{'●' * a.roll}{'○' * (4 - a.roll)}{C_RESET}"

    if a.action_type == ActionType.SKIPPED:
        subject = t("action.you") if is_local else player.name
        return t("action.skipped", subject=subject, roll=roll_str)

    subject = t("action.you") if is_local else player.name

    if a.action_type == ActionType.SCORED:
        piece_sym = f"{color}{NUM_CIRCLES.get(a.piece_id, '#')}{C_RESET}"
        if is_local:
            return f"{C_SCORE}{t('action.scored_you', subject=subject, roll=roll_str, piece=piece_sym)}{C_RESET}"
        return f"{color}{t('action.scored_opp', subject=subject, roll=roll_str)}{C_RESET}"

    # MOVED
    rosetta_labels = {4: "move.rosetta_first", 8: "move.rosetta_middle", 14: "move.rosetta_last"}
    tgt = a.target_progress
    if tgt in rosetta_labels:
        tgt_str = f"{t(rosetta_labels[tgt])} {C_ROSETTA}✿{C_RESET}"
    else:
        tgt_str = t("move.square", letter=chr(96 + tgt))

    if is_local:
        piece_sym = f"{color}{NUM_CIRCLES.get(a.piece_id, '#')}{C_RESET}"
        parts = [t("action.moved_you", subject=subject, roll=roll_str, piece=piece_sym, target=tgt_str)]
    else:
        parts = [t("action.moved_opp", subject=subject, roll=roll_str, target=tgt_str)]

    if a.hit:
        parts.append(f"{color}{t('action.hit_you' if is_local else 'action.hit_opp')}{C_RESET}")
    if a.rosetta:
        parts.append(f"{C_ROSETTA}{t('action.rosetta_you' if is_local else 'action.rosetta_opp')}{C_RESET}")

    return " ".join(parts)


def _run_game(bots: list, navigation):
    """
    Run one full game on the cross board.

    bots — list of Bot instances or None (None = human player).
    Length 2 for a 2-player game, length 3 for a 3-player game.
    """
    _paths = [P1_PATH_CROSS, P2_PATH_CROSS, P3_PATH_CROSS]
    _bot_names = ["Anu", "Bel", "Ea"]

    all_bots = all(b is not None for b in bots)
    names = []
    for i, bot in enumerate(bots):
        if bot is None:
            names.append(t("player.you"))
        elif all_bots:
            names.append(_bot_names[i])
        else:
            names.append(bot.name)

    players = [Player(i, names[i], _paths[i], PIECES_PER_PLAYER) for i in range(len(bots))]
    rosettas = CROSS_ROSETTAS_3P if len(bots) == 3 else CROSS_ROSETTAS
    engine = Engine(players, rosettas=rosettas)

    local_player = next((p for p, b in zip(players, bots) if b is None), players[0])
    local_idx = local_player.player_idx
    ui = CrossBoard(engine, navigation, local_player=local_player)

    while not engine.winner:
        roll = engine.roll_dice()
        valid_moves = engine.get_valid_moves(roll)
        current_bot = bots[engine.current_idx]
        player_color = _PLAYER_COLORS[engine.current_idx] if engine.current_idx < len(_PLAYER_COLORS) else C_RESET

        ui.draw()
        out(word_wrap(f"{t('match.last_action')}{_fmt_action(engine, local_idx)}"))
        GameUtils.animate_dice(player_color, roll)

        if not valid_moves:
            out(t("match.no_valid_moves"))
            engine.skip_turn(roll)
            time.sleep(2.0)
            continue

        if current_bot is not None:
            time.sleep(_BOT_PAUSE)
            move = current_bot.choose_move(engine, valid_moves)
            time.sleep(0.6)
        else:
            move = GameUtils.get_human_move(valid_moves, ui, roll, player_color)
            if move is None:
                return  # user navigated away

        engine.execute_move(move, roll)

        if _STEP:
            input(center("  [Enter] "))

    # ── End of game ──────────────────────────────────────────────
    ui.draw()
    out(word_wrap(f"{t('match.last_action')}{_fmt_action(engine, local_idx)}"))
    out("")

    winner = engine.winner
    human_player = next((p for p, b in zip(players, bots) if b is None), None)
    if human_player is not None:
        if winner is human_player:
            out(VICTORY_ART)
        else:
            out(DEFEAT_ART)
    else:
        win_color = _PLAYER_COLORS[winner.player_idx] if winner.player_idx < len(_PLAYER_COLORS) else C_RESET
        out(f"\n{C_ROSETTA}✦{C_RESET} {win_color}{winner.name}{C_RESET} {C_ROSETTA}wins!{C_RESET}\n")

    time.sleep(4.0)
    navigation.print_commands()
    navigation.check_global_commands(input(t("match.press_enter_menu")).strip())


def _mode_menu(navigation) -> str | None:
    menu = Menu("✧ ══════ Cross Board ══════ ✧")
    menu.add("Human vs 2 StrategicBots  (3-player)", "human_vs_2bots")
    menu.add("Human vs StrategicBot     (2-player)", "human_vs_bot")
    menu.add("StrategicBot vs StrategicBot vs StrategicBot", "bot_vs_bot_3p")
    menu.add("StrategicBot vs StrategicBot", "bot_vs_bot")
    menu.add("RandomBot vs RandomBot vs RandomBot", "random_3p")
    menu.add_separator()
    menu.add(t("menu.quit"), "quit")
    return menu.prompt()


def run():
    navigation = Navigation()
    while True:
        choice = _mode_menu(navigation)

        if choice == "quit" or choice is None:
            Navigation.clear()
            sys.exit()
        elif choice == "human_vs_2bots":
            _run_game([None, StrategicBot(), StrategicBot()], navigation)
        elif choice == "human_vs_bot":
            _run_game([None, StrategicBot()], navigation)
        elif choice == "bot_vs_bot_3p":
            _run_game([StrategicBot(), StrategicBot(), StrategicBot()], navigation)
        elif choice == "bot_vs_bot":
            _run_game([StrategicBot(), StrategicBot()], navigation)
        elif choice == "random_3p":
            _run_game([RandomBot(), RandomBot(), RandomBot()], navigation)


if __name__ == "__main__":
    run()
