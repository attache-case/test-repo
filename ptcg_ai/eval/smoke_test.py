"""Smoke test: one full game, our agent vs the built-in random agent.

Asserts:
  - the environment reaches a clean DONE state for both players (no
    ERROR / INVALID / TIMEOUT statuses anywhere), and
  - our agent's final status is DONE (i.e. it never returned an invalid
    action for the whole game).

Run with the project venv, from the repo root:
    /home/user/venv-ptcg/bin/python ptcg_ai/eval/smoke_test.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402

from ptcg_ai.agent.main import agent  # noqa: E402

BAD_STATUSES = {"ERROR", "INVALID", "TIMEOUT"}


def main():
    t0 = time.time()
    env = make("cabt", debug=True)
    env.run([agent, "random"])
    elapsed = time.time() - t0

    statuses = [s.status for s in env.state]
    rewards = [s.reward for s in env.state]
    print("statuses:", statuses)
    print("rewards:", rewards)
    print(f"elapsed: {elapsed:.2f}s")

    assert statuses[0] not in BAD_STATUSES, f"our agent ended with bad status: {statuses[0]}"
    assert all(s == "DONE" for s in statuses), f"game did not finish cleanly: {statuses}"

    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
