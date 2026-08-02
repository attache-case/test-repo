"""Aggregate self-play JSONL records into a learned action-prior table.

Key: "select_type|select_context|option_type" (the shape of the option that
was CHOSEN, not just present -- looked up via option_types[i] for i in the
recorded action). Value: Laplace-smoothed empirical win-rate, i.e.
(sum(outcome) + 1) / (count + 2), so an unseen key defaults toward 0.5 and a
single observation doesn't swing to 0 or 1.

Keys with fewer than --min-support observations are dropped entirely (main.py
falls back to a neutral 0.5 prior for any missing key, so this is safe) --
this keeps noise out and keeps the embedded table small. The result is
written both as a JSON artifact (ptcg_ai/train/artifacts/action_priors.json,
committed) and as a ready-to-paste Python literal for main.py's
LEARNED_PRIORS constant.

Usage:
    /home/user/venv-ptcg/bin/python ptcg_ai/train/build_priors.py \
        --data "ptcg_ai/train/data/*.jsonl" --min-support 8 --max-entries 200
"""
import argparse
import glob
import json
import os
from collections import defaultdict


def load_records(pattern):
    paths = sorted(glob.glob(pattern))
    for path in paths:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def build(pattern, min_support, max_entries):
    agg = defaultdict(lambda: [0.0, 0])  # key -> [sum_outcome, count]
    n_records = 0
    n_files = len(glob.glob(pattern))
    for rec in load_records(pattern):
        n_records += 1
        option_types = rec.get("option_types")
        action = rec.get("action")
        outcome = rec.get("outcome")
        if not option_types or action is None or outcome is None:
            continue
        sel_type = rec.get("sel_type")
        sel_context = rec.get("sel_context")
        for i in action:
            if not isinstance(i, int) or i < 0 or i >= len(option_types):
                continue
            opt_type = option_types[i]
            key = f"{sel_type}|{sel_context}|{opt_type}"
            agg[key][0] += outcome
            agg[key][1] += 1

    scored = []
    for key, (s, c) in agg.items():
        if c < min_support:
            continue
        winrate = (s + 1.0) / (c + 2.0)
        scored.append((key, round(winrate, 4), c))

    # Keep the entries with the most support (most statistically reliable)
    # if we still have more than max_entries after the min-support filter.
    scored.sort(key=lambda t: t[2], reverse=True)
    scored = scored[:max_entries]

    table = {key: winrate for key, winrate, _ in scored}
    return table, n_records, n_files, len(agg)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "data", "*.jsonl"))
    ap.add_argument("--min-support", type=int, default=8)
    ap.add_argument("--max-entries", type=int, default=200)
    ap.add_argument("--out-json", default=os.path.join(os.path.dirname(__file__), "artifacts", "action_priors.json"))
    args = ap.parse_args()

    table, n_records, n_files, n_keys_seen = build(args.data, args.min_support, args.max_entries)

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(table, f, indent=1, sort_keys=True)

    print(f"read {n_records} records from {n_files} file(s)")
    print(f"{n_keys_seen} distinct (sel_type|context|option_type) keys observed")
    print(f"kept {len(table)} keys (min_support={args.min_support}, max_entries={args.max_entries})")
    print(f"wrote {args.out_json}")
    print()
    print("Paste into ptcg_ai/agent/main.py as LEARNED_PRIORS = <this>:")
    print("LEARNED_PRIORS = " + json.dumps(table, sort_keys=True))


if __name__ == "__main__":
    main()
