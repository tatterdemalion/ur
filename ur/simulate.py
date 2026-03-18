import time
import argparse
from dataclasses import dataclass
from ur.ai.environment import UrEnvironment
from ur.ai import bots
from ur.play import BoardVisualizer


@dataclass
class BotStats:
    name: str
    games_played: int = 0
    wins: int = 0
    total_turns: int = 0

    @property
    def win_rate(self) -> float:
        return (self.wins / self.games_played * 100) if self.games_played > 0 else 0.0

    @property
    def avg_turns(self) -> float:
        return (self.total_turns / self.wins) if self.wins > 0 else 0.0

    def __str__(self) -> str:
        return (
            f"{self.name}: {self.wins}/{self.games_played} wins "
            f"({self.win_rate:.1f}%) | "
            f"Avg turns when winning: {self.avg_turns:.0f}"
        )


def run_simulation(bot_class_1, bot_class_2, num_games=1000, show=False):
    env = UrEnvironment()

    bot_a = bot_class_1()
    bot_b = bot_class_2()

    # Handle naming, especially if pitting the same bot classes against each other
    name_a = bot_class_1.__name__
    name_b = bot_class_2.__name__
    if name_a == name_b:
        name_a, name_b = f"{name_a}_1", f"{name_b}_2"

    results = {
        name_a: BotStats(name=name_a),
        name_b: BotStats(name=name_b),
    }

    start_time = time.time()

    if not show:
        print(f"Starting simulation of {num_games} games between {name_a} and {name_b}...")

    for i in range(num_games):
        # Fair play tournament swap: who gets to go first as P1?
        if i < num_games // 2:
            p1_name, p1_bot = name_a, bot_a
            p2_name, p2_bot = name_b, bot_b
        else:
            p1_name, p1_bot = name_b, bot_b
            p2_name, p2_bot = name_a, bot_a

        state, valid_moves, done, _ = env.reset(p1_name, p2_name)

        players = {0: p1_bot, 1: p2_bot}

        ui = BoardVisualizer(env.game) if show else None
        turns = 0

        if show:
            ui.draw()
            time.sleep(0.5)

        while not done:
            turns += 1
            active_player_idx = env.game.current_idx
            active_bot = players[active_player_idx]
            active_player = env.game.current_player

            chosen_piece = active_bot.choose_move(state, valid_moves, active_player)
            state, valid_moves, reward, done = env.step(chosen_piece)

            if show:
                ui.draw()
                time.sleep(0.1)

        winner_idx = 0 if env.game.players[0].has_won() else 1
        winner_name = env.game.players[winner_idx].name

        results[name_a].games_played += 1
        results[name_b].games_played += 1
        results[winner_name].wins += 1
        results[winner_name].total_turns += turns

    # Print Report only if we aren't using the visualizer
    if not show:
        elapsed = time.time() - start_time
        print("\n=== SIMULATION RESULTS ===")
        print(f"Games Played: {num_games} (in {elapsed:.2f} seconds)")
        for stats in results.values():
            print(stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Ur AI Simulations")
    parser.add_argument("bot1", type=str, help="Name of the first bot class (e.g., RandomBot)")
    parser.add_argument("bot2", type=str, help="Name of the second bot class (e.g., GreedyBot)")
    parser.add_argument("--games", type=int, default=1000, help="Number of games to simulate")
    parser.add_argument("--show", action="store_true", help="Watch the bots play in the terminal")

    args = parser.parse_args()

    # Dynamically grab the bot classes from the bots.py file
    bot1_cls = getattr(bots, args.bot1, None)
    bot2_cls = getattr(bots, args.bot2, None)

    if not bot1_cls or not bot2_cls:
        print("Error: Could not find one or both bots. Available bots in game/ai/bots.py:")
        for attr_name in dir(bots):
            if attr_name.endswith("Bot") and attr_name != "Bot":
                print(f" - {attr_name}")
        exit(1)

    # If --show is passed, default to 1 game unless explicitly told otherwise
    games_to_play = 1 if args.show and args.games == 1000 else args.games

    run_simulation(bot1_cls, bot2_cls, games_to_play, show=args.show)
