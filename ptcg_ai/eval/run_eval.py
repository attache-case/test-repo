"""Local evaluation harness: run N games of our agent vs a built-in opponent,
alternating seats, and report win/loss/draw counts, winrate, mean reward, and
wallclock time.

Usage (always with the project venv):
    /home/user/venv-ptcg/bin/python ptcg_ai/eval/run_eval.py --games 20 --opponent random

Baseline success criterion (see IMPLEMENTATION_SPEC.md): >= 80% winrate vs the
built-in "random" agent over >= 20 games.
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402

from ptcg_ai.agent.main import agent  # noqa: E402

BAD_STATUSES = {"ERROR", "INVALID", "TIMEOUT"}


def run_games(n, opponent_name):
    wins = losses = draws = bad = 0
    my_rewards = []
    per_game = []
    streak = 0
    best_streak = 0
    t0 = time.time()

    for i in range(n):
        our_seat = i % 2  # alternate seats so we play both first and second
        agents = [agent, opponent_name] if our_seat == 0 else [opponent_name, agent]

        env = make("cabt", debug=True)
        env.run(agents)

        statuses = [s.status for s in env.state]
        rewards = [s.reward for s in env.state]
        my_status = statuses[our_seat]
        my_reward = rewards[our_seat]
        my_rewards.append(my_reward if my_reward is not None else 0)

        outcome = "?"
        if my_status in BAD_STATUSES:
            bad += 1
            outcome = f"BAD:{my_status}"
            streak = 0
        elif my_reward == 1:
            wins += 1
            outcome = "WIN"
            streak += 1
            best_streak = max(best_streak, streak)
        elif my_reward == -1:
            losses += 1
            outcome = "LOSS"
            streak = 0
        else:
            draws += 1
            outcome = "DRAW"
            streak = 0

        per_game.append((i, our_seat, statuses, rewards, outcome))
        print(f"game {i:3d} seat={our_seat} statuses={statuses} rewards={rewards} "
              f"-> {outcome}  (streak={streak})")

    elapsed = time.time() - t0
    decided = wins + losses + draws
    winrate = wins / decided if decided else 0.0
    mean_reward = sum(my_rewards) / len(my_rewards) if my_rewards else 0.0

    print("=" * 64)
    print(f"opponent={opponent_name} games={n} wins={wins} losses={losses} "
          f"draws={draws} bad_status={bad}")
    print(f"winrate={winrate:.1%}  mean_reward={mean_reward:.3f}  best_streak={best_streak}")
    print(f"wallclock={elapsed:.1f}s total, {elapsed / n:.2f}s/game")

    return {
        "opponent": opponent_name,
        "games": n,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "bad_status": bad,
        "winrate": winrate,
        "mean_reward": mean_reward,
        "best_streak": best_streak,
        "elapsed_s": elapsed,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20, help="number of games to play")
    ap.add_argument(
        "--opponent",
        choices=["random", "first"],
        default="random",
        help="built-in opponent agent",
    )
    args = ap.parse_args()

    result = run_games(args.games, args.opponent)

    if result["opponent"] == "random":
        threshold = 0.8
        status = "PASS" if result["winrate"] >= threshold else "FAIL"
        print(f"baseline check ({threshold:.0%} vs random): {status}")


if __name__ == "__main__":
    main()
