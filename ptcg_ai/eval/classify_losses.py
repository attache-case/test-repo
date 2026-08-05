"""Loss classification using the GROUND-TRUTH LogType.RESULT.reason field
(official cg/api.py: 1=opponent took all 6 prizes, 2=deck-out i.e. started a
turn with 0 deck cards, 3=no Pokemon in Active Spot, 4=a card effect), in
place of the earlier approach of inferring the cause from final board state.

Why this needs a monkeypatch: kaggle_environments' own interpreter
(kaggle_environments/envs/cabt/cabt.py) deliberately does NOT copy the
terminal observation's ``logs`` (which contains the RESULT entry) into the
agent-facing ``state[i].observation`` once ``current.result >= 0`` -- see
its ``interpreter()``, terminal branch. That means the RESULT log is briefly
present in the module-level ``Battle.obs`` dict (set by
``cg.game.battle_select``/``_get_battle_data``) but is never exposed through
the public ``env.run()`` / ``env.state`` / ``env.steps`` API. This script
wraps ``cg.game.battle_select`` (as imported into the ``cabt`` module) to
capture every observation's ``logs`` as the game is played, then scans the
captured stream for the ``type == 23`` (RESULT) entry after each game.

Usage:
    /home/user/venv-ptcg/bin/python ptcg_ai/eval/classify_losses.py --games 40
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from kaggle_environments import make  # noqa: E402
from kaggle_environments.envs.cabt import cabt as _cabt_mod  # noqa: E402

from ptcg_ai.agent.main import agent  # noqa: E402

REASON_NAMES = {
    1: "opponent_took_all_prizes",
    2: "deck_out",
    3: "no_pokemon_in_active",
    4: "card_effect",
}

_captured_logs = []
_orig_battle_select = _cabt_mod.battle_select


def _capturing_battle_select(select_list):
    obs = _orig_battle_select(select_list)
    logs = obs.get("logs") or []
    _captured_logs.extend(logs)
    return obs


_cabt_mod.battle_select = _capturing_battle_select


def run_one_game(our_seat, opponent_name):
    global _captured_logs
    _captured_logs = []
    agents = [agent, opponent_name] if our_seat == 0 else [opponent_name, agent]
    env = make("cabt", debug=True)
    env.run(agents)
    statuses = [s.status for s in env.state]
    rewards = [s.reward for s in env.state]
    result_log = None
    for l in _captured_logs:
        if l.get("type") == 23:
            result_log = l
    return statuses, rewards, result_log


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=40)
    ap.add_argument("--opponent", default="random", choices=["random", "first"])
    args = ap.parse_args()

    loss_reasons = {}
    win_reasons = {}
    draws = 0
    no_result_log = 0
    wins = losses = 0

    for i in range(args.games):
        our_seat = i % 2
        statuses, rewards, result_log = run_one_game(our_seat, args.opponent)
        my_reward = rewards[our_seat]
        if result_log is None:
            no_result_log += 1
            reason = None
        else:
            reason = result_log.get("reason")
        if my_reward == 1:
            wins += 1
            win_reasons[reason] = win_reasons.get(reason, 0) + 1
        elif my_reward == -1:
            losses += 1
            loss_reasons[reason] = loss_reasons.get(reason, 0) + 1
        else:
            draws += 1
        print(f"game {i:3d} seat={our_seat} reward={my_reward} "
              f"result_log={result_log}")

    print("=" * 64)
    print(f"games={args.games} opponent={args.opponent} wins={wins} losses={losses} draws={draws}")
    print(f"games with no captured RESULT log: {no_result_log}")
    print("\nLoss reason breakdown (ground truth, LogType.RESULT.reason):")
    for reason, count in sorted(loss_reasons.items(), key=lambda x: -x[1]):
        name = REASON_NAMES.get(reason, f"unknown({reason})")
        pct = count / losses * 100 if losses else 0
        print(f"  {name:28s} reason={reason!r}  count={count:3d}  ({pct:.1f}% of losses)")
    print("\nWin reason breakdown:")
    for reason, count in sorted(win_reasons.items(), key=lambda x: -x[1]):
        name = REASON_NAMES.get(reason, f"unknown({reason})")
        pct = count / wins * 100 if wins else 0
        print(f"  {name:28s} reason={reason!r}  count={count:3d}  ({pct:.1f}% of wins)")

    deckout_losses = loss_reasons.get(2, 0)
    if deckout_losses:
        print(f"\nNOTE: {deckout_losses} loss(es) specifically from deck-out (reason=2) -- "
              "a distinct failure mode from the dominant no-Pokemon-in-Active-Spot cause.")


if __name__ == "__main__":
    main()
