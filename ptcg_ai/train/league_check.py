"""Head-to-head league check: current ptcg_ai/agent/main.py vs a frozen
snapshot in ptcg_ai/train/frozen/. Required before promoting any change
(new weights, new priors, new deck) per the project's promotion rule: beat
the predecessor >55% over >=50 games, in addition to keeping the vs-random
winrate intact.

Usage:
    /home/user/venv-ptcg/bin/python ptcg_ai/train/league_check.py \
        --frozen ptcg_ai/train/frozen/agent_v1.py --games 50
"""
import argparse
import importlib.util
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402

from ptcg_ai.agent.main import agent as current_agent  # noqa: E402


def load_frozen(path):
    spec = importlib.util.spec_from_file_location("frozen_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen", default=os.path.join(os.path.dirname(__file__), "frozen", "agent_v1.py"))
    ap.add_argument("--games", type=int, default=50)
    args = ap.parse_args()

    frozen_agent = load_frozen(args.frozen)

    cur_wins = frozen_wins = draws = bad = 0
    t0 = time.time()
    for i in range(args.games):
        cur_seat = i % 2
        agents = [current_agent, frozen_agent] if cur_seat == 0 else [frozen_agent, current_agent]
        env = make("cabt", debug=True)
        env.run(agents)
        statuses = [s.status for s in env.state]
        rewards = [s.reward for s in env.state]
        if statuses[cur_seat] in ("ERROR", "INVALID", "TIMEOUT") or statuses[1 - cur_seat] in ("ERROR", "INVALID", "TIMEOUT"):
            bad += 1
            continue
        r = rewards[cur_seat]
        if r == 1:
            cur_wins += 1
        elif r == -1:
            frozen_wins += 1
        else:
            draws += 1
        print(f"game {i:3d} current_seat={cur_seat} reward={r}")

    elapsed = time.time() - t0
    decided = cur_wins + frozen_wins + draws
    winrate = cur_wins / decided if decided else 0.0
    print("=" * 60)
    print(f"current_wins={cur_wins} frozen_wins={frozen_wins} draws={draws} bad={bad}")
    print(f"current-vs-frozen winrate={winrate:.1%}  ({elapsed:.0f}s, {elapsed/args.games:.1f}s/game)")
    status = "PROMOTE (>55%)" if winrate > 0.55 else "DO NOT PROMOTE"
    print(f"verdict: {status}")


if __name__ == "__main__":
    main()
