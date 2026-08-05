"""Self-play data generation for the learned-priors pipeline (Phase 3).

Runs N games -- a mix of agent-vs-agent (self-play) and agent-vs-built-in
(random/first, for opponent diversity) -- and records one JSONL line per
REAL decision our agent made (using main.py's existing PTCG_DEBUG
instrumentation with PTCG_FULL_HISTORY=1 so no ring-buffer trimming
happens), tagged with that game's final outcome from the mover's
perspective. Raw JSONL under ptcg_ai/train/data/ is gitignored -- only the
small aggregated priors artifact gets committed (see build_priors.py).

To keep generation fast, this script temporarily shrinks the agent's
per-decision time budget (data quality only needs "reasonable" play, not
peak search depth); production main.py budgets are restored on exit.

Usage (always with the project venv):
    /home/user/venv-ptcg/bin/python ptcg_ai/train/selfplay.py --games 200
"""
import argparse
import json
import os
import sys
import time

os.environ["PTCG_DEBUG"] = "1"
os.environ["PTCG_FULL_HISTORY"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402

import ptcg_ai.agent.main as m  # noqa: E402
from ptcg_ai.agent.main import agent, reset_debug_stats, get_debug_stats  # noqa: E402


def shrink_time_budget(factor=6.0):
    """Speed up self-play generation by cutting the search time budget.
    Returns a callable that restores the original module constants."""
    orig = dict(
        TARGET_TIME=m.TARGET_TIME, HARD_CAP=m.HARD_CAP,
        SETUP_TARGET_TIME=m.SETUP_TARGET_TIME, SETUP_HARD_CAP=m.SETUP_HARD_CAP,
    )
    m.TARGET_TIME = orig["TARGET_TIME"] / factor
    m.HARD_CAP = orig["HARD_CAP"] / factor
    m.SETUP_TARGET_TIME = orig["SETUP_TARGET_TIME"] / factor
    m.SETUP_HARD_CAP = orig["SETUP_HARD_CAP"] / factor

    def restore():
        for k, v in orig.items():
            setattr(m, k, v)
    return restore


def run_one_game(opponent):
    """opponent: 'self' (agent vs agent) or a built-in name ('random'/'first')."""
    reset_debug_stats()
    agents = [agent, agent] if opponent == "self" else [agent, opponent]
    env = make("cabt", debug=True)
    env.run(agents)
    statuses = [s.status for s in env.state]
    rewards = [s.reward for s in env.state]
    stats = get_debug_stats()
    history = (stats or {}).get("history", [])
    return statuses, rewards, history


def outcome_for(entry, rewards):
    """1.0 win / 0.5 draw / 0.0 loss, from the perspective of the player who
    made this decision (entry['me'])."""
    me = entry.get("me")
    if me is None or me >= len(rewards) or rewards[me] is None:
        return None
    r = rewards[me]
    if r > 0:
        return 1.0
    if r < 0:
        return 0.0
    return 0.5


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--self-frac", type=float, default=0.5,
                     help="fraction of games that are agent-vs-agent (rest split random/first)")
    ap.add_argument("--speedup", type=float, default=6.0, help="time-budget shrink factor")
    ap.add_argument("--out", default=None, help="output JSONL path (default: timestamped)")
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = args.out or os.path.join(out_dir, f"selfplay_{int(time.time())}.jsonl")

    restore = shrink_time_budget(args.speedup)
    n_records = 0
    n_bad = 0
    t0 = time.time()
    try:
        with open(out_path, "w") as f:
            for i in range(args.games):
                if i < args.games * args.self_frac:
                    opponent = "self"
                else:
                    opponent = "random" if i % 2 == 0 else "first"
                statuses, rewards, history = run_one_game(opponent)
                if any(s in ("ERROR", "INVALID", "TIMEOUT") for s in statuses):
                    n_bad += 1
                    continue
                for entry in history:
                    label = outcome_for(entry, rewards)
                    if label is None:
                        continue
                    rec = dict(entry)
                    rec["outcome"] = label
                    rec["opponent"] = opponent
                    f.write(json.dumps(rec) + "\n")
                    n_records += 1
                if (i + 1) % 20 == 0:
                    print(f"  {i + 1}/{args.games} games, {n_records} records so far "
                          f"({time.time() - t0:.0f}s elapsed)")
    finally:
        restore()

    elapsed = time.time() - t0
    print(f"done: {args.games} games ({n_bad} bad-status games skipped), "
          f"{n_records} decision records -> {out_path}")
    print(f"elapsed {elapsed:.0f}s ({elapsed / args.games:.2f}s/game)")


if __name__ == "__main__":
    main()
