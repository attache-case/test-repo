"""Evolutionary deck search (time-boxed initial pass).

Population starts at [current default deck] + a few random mutants each
generation. Mutation: swap 1-3 cards, respecting the empirically-verified
engine rules (60 cards; max 4 copies per cardId except Basic Energy 1-8,
which are uncapped; >=1 Basic Pokemon required; at most 1 ACE SPEC card
total; only known cardIds 1-1267) -- each mutant is validated against the
real engine (lib.BattleStart) before being kept, so invalid mutants are
rejected outright rather than silently mis-scored.

Selection: round-robin our own agent piloting BOTH sides, mutant vs current
best, alternating seats. A mutant is only promoted to "current best" if it
beats the incumbent by the same >60%-over-N-games bar used for the
hand-built candidates in Phase 2 (see strategy_report.md), and a promoted
deck must also be re-checked against `random` before shipping (this script
only reports the numbers -- promoting into ptcg_ai/agent/main.py is a
manual step so a human reviews the evidence first).

This is a SMALL, time-boxed run by default (population 4, 2 generations,
20 games/matchup at a shrunk search-time budget) -- see
ptcg_ai/train/README.md for how to scale it up.

Usage:
    /home/user/venv-ptcg/bin/python ptcg_ai/train/deck_evolve.py
"""
import argparse
import ctypes
import json
import os
import random
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402
from kaggle_environments.envs.cabt.cg.sim import lib  # noqa: E402

import ptcg_ai.agent.main as m  # noqa: E402

BASIC_ENERGY_IDS = set(range(1, 9))


def load_card_meta():
    lib.AllCard.restype = ctypes.c_char_p
    lib.AllCard.argtypes = []
    cards = json.loads(lib.AllCard().decode())
    return {c["cardId"]: c for c in cards}


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


def engine_validates(deck, other_deck, meta_ids):
    if len(deck) != 60 or len(other_deck) != 60:
        return False
    if any(c not in meta_ids for c in deck):
        return False
    arr = (ctypes.c_int * 120)(*(deck + other_deck))
    sd = lib.BattleStart(arr)
    ok = sd.battlePtr not in (None, 0)
    if ok:
        lib.BattleFinish(sd.battlePtr)
    return ok


def mutate(deck, card_meta, n_swaps=None):
    ids = list(card_meta.keys())
    deck = list(deck)
    n_swaps = n_swaps or random.randint(1, 3)
    for _ in range(n_swaps):
        # remove one random copy of a random card currently in the deck
        remove_idx = random.randrange(len(deck))
        removed = deck.pop(remove_idx)
        # add a random valid card back (bias toward Pokemon so we don't
        # accidentally drift toward an all-trainer deck over many mutations)
        for _try in range(30):
            if random.random() < 0.6:
                candidates = [i for i in ids if card_meta[i]["cardType"] == 0]
            else:
                candidates = ids
            new_id = random.choice(candidates)
            counts = Counter(deck)
            counts[new_id] += 1
            cap_ok = new_id in BASIC_ENERGY_IDS or counts[new_id] <= 4
            ace_ok = (not card_meta[new_id].get("aceSpec")) or sum(
                1 for c in deck if card_meta[c].get("aceSpec")
            ) < 1
            if cap_ok and ace_ok:
                deck.append(new_id)
                break
        else:
            deck.append(removed)  # give up this swap, put the card back
    if not any(card_meta[c]["cardType"] == 0 and card_meta[c]["basic"] for c in deck):
        return None  # invalid: no basic Pokemon left, reject
    return deck


def round_robin_winrate(deck_a, deck_b, n_games):
    def make_agent(deck):
        basics = {cid for cid in set(deck) if True}  # filled by caller via closure below

        def wrapped(obs):
            m.DECK = deck
            return m.agent(obs)
        return wrapped

    agent_a = make_agent(deck_a)
    agent_b = make_agent(deck_b)
    a_wins = 0
    total = 0
    for i in range(n_games):
        seat = i % 2
        agents = [agent_a, agent_b] if seat == 0 else [agent_b, agent_a]
        env = make("cabt", debug=True)
        env.run(agents)
        statuses = [s.status for s in env.state]
        rewards = [s.reward for s in env.state]
        if statuses[seat] in ("ERROR", "INVALID", "TIMEOUT"):
            continue
        total += 1
        if rewards[seat] == 1:
            a_wins += 1
    return (a_wins / total if total else 0.0), total


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--generations", type=int, default=2)
    ap.add_argument("--population", type=int, default=4)
    ap.add_argument("--games-per-matchup", type=int, default=20)
    ap.add_argument("--promote-threshold", type=float, default=0.60)
    ap.add_argument("--speedup", type=float, default=6.0)
    args = ap.parse_args()

    card_meta = load_card_meta()
    incumbent = list(m.DECK)
    log_lines = [
        "# Deck Evolution Log",
        "",
        f"Run parameters: generations={args.generations} population={args.population} "
        f"games_per_matchup={args.games_per_matchup} promote_threshold={args.promote_threshold:.0%}",
        "",
        f"Starting incumbent (v2): {dict(Counter(incumbent))}",
        "",
    ]

    restore = shrink_time_budget(args.speedup)
    t0 = time.time()
    try:
        for gen in range(1, args.generations + 1):
            log_lines.append(f"## Generation {gen}")
            log_lines.append("")
            best_of_gen = None
            best_score = 0.0
            attempts = 0
            mutants_tested = 0
            while mutants_tested < args.population and attempts < args.population * 5:
                attempts += 1
                mutant = mutate(incumbent, card_meta)
                if mutant is None or not engine_validates(mutant, incumbent, set(card_meta.keys())):
                    continue
                mutants_tested += 1
                score, n = round_robin_winrate(mutant, incumbent, args.games_per_matchup)
                counts = dict(Counter(mutant))
                log_lines.append(f"- mutant {mutants_tested}: winrate {score:.1%} over {n} games "
                                  f"vs incumbent; composition={counts}")
                print(f"gen {gen} mutant {mutants_tested}: {score:.1%} over {n} games")
                if score > best_score:
                    best_score = score
                    best_of_gen = mutant
            log_lines.append("")
            if best_of_gen is not None and best_score >= args.promote_threshold:
                log_lines.append(f"**Promoted**: best mutant of generation {gen} "
                                  f"({best_score:.1%}) beat the promotion threshold "
                                  f"({args.promote_threshold:.0%}); becomes incumbent.")
                incumbent = best_of_gen
            else:
                log_lines.append(f"No mutant beat the {args.promote_threshold:.0%} promotion "
                                  f"threshold this generation (best: {best_score:.1%}); "
                                  f"incumbent unchanged.")
            log_lines.append("")
    finally:
        restore()

    elapsed = time.time() - t0
    log_lines.append(f"Total wallclock: {elapsed:.0f}s")
    log_lines.append("")
    log_lines.append(f"Final deck (composition): {dict(Counter(incumbent))}")

    out_path = os.path.join(os.path.dirname(__file__), "artifacts", "deck_evolution.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"wrote {out_path}")
    print(f"final deck: {dict(Counter(incumbent))}")


if __name__ == "__main__":
    main()
