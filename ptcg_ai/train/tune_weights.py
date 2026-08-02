"""Time-boxed coordinate-descent tuning of the leaf-heuristic weight vector
(W_PRIZE, W_HP, W_BOARD_DEV, W_HAND, W_PRESENCE).

One round: for each weight, try +delta and -delta (holding the others at
their current-best value), score each candidate vector over a small gauntlet
(built-in random + built-in first, alternating seats), and keep whichever
vector scores best (baseline included) after all dimensions are tried. This
is a deliberately modest, fast pass -- see ptcg_ai/train/README.md for how to
run more rounds / a larger gauntlet if it's moving winrates enough to be
worth the wallclock.

Usage:
    /home/user/venv-ptcg/bin/python ptcg_ai/train/tune_weights.py
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402

import ptcg_ai.agent.main as m  # noqa: E402

WEIGHT_KEYS = ["W_PRIZE", "W_HP", "W_BOARD_DEV", "W_HAND", "W_PRESENCE"]


def set_weights(w):
    for k, v in w.items():
        setattr(m, k, v)


def shrink_time_budget(factor=6.0):
    orig = dict(TARGET_TIME=m.TARGET_TIME, HARD_CAP=m.HARD_CAP,
                SETUP_TARGET_TIME=m.SETUP_TARGET_TIME, SETUP_HARD_CAP=m.SETUP_HARD_CAP)
    m.TARGET_TIME = orig["TARGET_TIME"] / factor
    m.HARD_CAP = orig["HARD_CAP"] / factor
    m.SETUP_TARGET_TIME = orig["SETUP_TARGET_TIME"] / factor
    m.SETUP_HARD_CAP = orig["SETUP_HARD_CAP"] / factor

    def restore():
        for k, v in orig.items():
            setattr(m, k, v)
    return restore


def gauntlet_score(w, n_per_opp=8):
    set_weights(w)
    wins = 0
    total = 0
    for opponent in ("random", "first"):
        for i in range(n_per_opp):
            seat = i % 2
            agents = [m.agent, opponent] if seat == 0 else [opponent, m.agent]
            env = make("cabt", debug=True)
            env.run(agents)
            statuses = [s.status for s in env.state]
            rewards = [s.reward for s in env.state]
            if statuses[seat] in ("ERROR", "INVALID", "TIMEOUT"):
                continue
            total += 1
            if rewards[seat] == 1:
                wins += 1
    return wins / total if total else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--delta", type=float, default=0.08)
    ap.add_argument("--games-per-opponent", type=int, default=8)
    ap.add_argument("--speedup", type=float, default=6.0)
    args = ap.parse_args()

    restore = shrink_time_budget(args.speedup)
    t0 = time.time()
    try:
        best = {k: getattr(m, k) for k in WEIGHT_KEYS}
        best_score = gauntlet_score(best, args.games_per_opponent)
        print(f"baseline {best} -> {best_score:.1%}")

        for key in WEIGHT_KEYS:
            for sign in (+1, -1):
                cand = dict(best)
                cand[key] = max(0.0, best[key] + sign * args.delta)
                score = gauntlet_score(cand, args.games_per_opponent)
                print(f"  try {key}{'+' if sign > 0 else '-'}{args.delta} "
                      f"-> {cand[key]:.3f}: {score:.1%}")
                if score > best_score:
                    best_score = score
                    best = cand
                    print(f"    ** new best: {best} -> {best_score:.1%}")
    finally:
        restore()

    elapsed = time.time() - t0
    print("=" * 60)
    print(f"final best weights: {best} -> {best_score:.1%} ({elapsed:.0f}s)")
    print("If clearly better than the shipped weights, copy these into "
          "ptcg_ai/agent/main.py's W_* constants and re-verify with run_eval.py.")


if __name__ == "__main__":
    main()
