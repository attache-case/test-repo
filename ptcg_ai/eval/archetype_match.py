"""Play two named ARCHETYPE_DECKS against each other, our own search/policy
piloting BOTH sides (only the deck differs). Used for the archetype
tournament and its post-bugfix spot-check re-validation.

Each side's deck (and BASIC_POKEMON_IDS, which bench_basic_override/rescue
bias use to recognize "a Basic Pokemon of MY deck" in hand) is forced via
ptcg_ai.agent.main's module globals immediately before every single
decision that side makes -- not just at the initial deck-select call --
because kaggle_environments calls the same underlying `agent` function
object for both seats out of one shared Python process, so the globals
must be re-pinned per call or the two sides' state bleeds into each other.

Usage:
    /home/user/venv-ptcg/bin/python ptcg_ai/eval/archetype_match.py \
        --deck-a v3_champion --deck-b t4_fighting_spread --games 40
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402

import ptcg_ai.agent.main as m  # noqa: E402

BAD_STATUSES = {"ERROR", "INVALID", "TIMEOUT"}


def make_archetype_agent(deck_name):
    deck = m.ARCHETYPE_DECKS[deck_name]
    basics = m.ARCHETYPE_BASIC_IDS[deck_name]

    def wrapped(obs):
        m._ACTIVE_DECK = deck
        m.BASIC_POKEMON_IDS = basics
        if obs.get("select") is None:
            return list(deck)
        return m.agent(obs)

    return wrapped


def run_match(deck_a, deck_b, n):
    agent_a = make_archetype_agent(deck_a)
    agent_b = make_archetype_agent(deck_b)

    a_wins = b_wins = draws = bad = 0
    t0 = time.time()
    for i in range(n):
        a_seat = i % 2
        agents = [agent_a, agent_b] if a_seat == 0 else [agent_b, agent_a]
        env = make("cabt", debug=True)
        env.run(agents)
        statuses = [s.status for s in env.state]
        rewards = [s.reward for s in env.state]
        if statuses[0] in BAD_STATUSES or statuses[1] in BAD_STATUSES:
            bad += 1
            print(f"game {i:3d} a_seat={a_seat} BAD statuses={statuses}")
            continue
        a_reward = rewards[a_seat]
        if a_reward == 1:
            a_wins += 1
        elif a_reward == -1:
            b_wins += 1
        else:
            draws += 1
        print(f"game {i:3d} a_seat={a_seat} statuses={statuses} rewards={rewards}")

    elapsed = time.time() - t0
    decided = a_wins + b_wins + draws
    a_winrate = a_wins / decided if decided else 0.0
    print("=" * 64)
    print(f"{deck_a} vs {deck_b}: games={n} {deck_a}_wins={a_wins} "
          f"{deck_b}_wins={b_wins} draws={draws} bad={bad}")
    print(f"{deck_a} winrate={a_winrate:.1%}  ({elapsed:.0f}s, {elapsed/n:.1f}s/game)")
    return {"deck_a": deck_a, "deck_b": deck_b, "a_wins": a_wins, "b_wins": b_wins,
            "draws": draws, "bad": bad, "a_winrate": a_winrate}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--deck-a", default="v3_champion")
    ap.add_argument("--deck-b", required=True)
    ap.add_argument("--games", type=int, default=40)
    args = ap.parse_args()
    run_match(args.deck_a, args.deck_b, args.games)


if __name__ == "__main__":
    main()
