# Training / learning pipeline (Phase 3)

Offline scripts that let the shipped, self-contained `ptcg_ai/agent/main.py`
improve from experience without becoming non-self-contained: everything
learned here gets baked back into `main.py` as **literal embedded
constants** (a `LEARNED_PRIORS` dict, `W_*` weight constants, and the `DECK`
list). Nothing under `ptcg_ai/train/` is imported by `main.py` or runs at
Kaggle submission time.

All commands use the project venv: `/home/user/venv-ptcg/bin/python`.

This is a first, deliberately **time-boxed** pass through the whole pipeline
(a few hundred games per stage, not a converged search) -- see "Scaling up"
at the end.

## 1. Self-play data generation (`selfplay.py`)

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/train/selfplay.py --games 250 --self-frac 0.5
```

Runs a mix of agent-vs-agent and agent-vs-built-in (`random`/`first`) games
with a shrunk search-time budget (fast, "reasonable" rather than peak play),
and records one JSONL line per real decision our agent made -- select
type/context, option types, chosen action, board features, and the game's
eventual outcome from that decision-maker's perspective -- to
`ptcg_ai/train/data/*.jsonl` (gitignored; regenerate rather than expecting it
in git).

Executed so far: **250 games, 15,653 decision records**
(`selfplay_1785681708.jsonl`).

## 2. Learned action priors (`build_priors.py`)

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/train/build_priors.py --min-support 8 --max-entries 200
```

Aggregates the JSONL data into `(select_type, select_context, option_type)
-> Laplace-smoothed win-rate`, drops keys with fewer than `--min-support`
observations, and writes `ptcg_ai/train/artifacts/action_priors.json` (small,
committed) plus a ready-to-paste `LEARNED_PRIORS` literal for `main.py`.
`main.py` uses this table two ways, both with a graceful fallback to the
pre-existing hand-tuned tiers when a key is unseen or the table is empty:
(i) weighted sampling within a playout-policy tier instead of uniform choice;
(ii) prior-ranked (instead of random) truncation of the candidate list when
it exceeds `CANDIDATE_CAP`.

Executed so far: **19 keys** kept (out of 19 observed -- the state space of
`(select_type, context, option_type)` triples is much smaller than raw game
states, so even 250 games gives reasonable support for most of them).

## 3. Eval-weight tuning (`tune_weights.py`)

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/train/tune_weights.py --delta 0.08 --games-per-opponent 8
```

One round of coordinate descent over `(W_PRIZE, W_HP, W_BOARD_DEV, W_HAND,
W_PRESENCE)`: try +/-delta on each weight in turn, score every candidate
vector over a small gauntlet (`random` + `first`, alternating seats, shrunk
time budget), keep whichever vector (including the untouched baseline)
scores best. Prints the winning vector; copying it into `main.py`'s `W_*`
constants and re-verifying with `run_eval.py` is a manual step so a human
signs off before shipping a behavior change.

## 4. League check / promotion gate (`league_check.py`)

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/train/league_check.py --frozen ptcg_ai/train/frozen/agent_v1.py --games 50
```

Head-to-head, current `main.py` vs a frozen snapshot, at full search budget.
**Promotion rule** (applies to any change -- priors, weights, or deck):
the candidate must beat its immediate predecessor >55% over >=50 games
*and* keep the vs-`random` winrate intact (re-check with `run_eval.py`)
before it's considered shipped. `ptcg_ai/train/frozen/agent_v1.py` is the
Phase-1/2 snapshot (commit `9e4a962`) frozen as the first league baseline;
never delete frozen snapshots -- add `agent_v2.py`, `agent_v3.py`, etc. as
the baseline advances. Current baseline for new promotion checks:
`agent_v4.py` (post-bugfix, weight-round-2) -- see "Further strengthening
pass" below for the full lineage.

## Re-validation after the official-source bugfix round (commit `004c94e`)

The `inPlayArea` bugfix (bench_basic_override/rescue bias silently missing
the "Active occupied, second Basic goes to Bench" case) meant every
promotion decision made *before* that fix used a weaker version of the
agent on one side of every comparison, including this project's own
promotion history. Re-ran the rejected candidates against a fresh frozen
baseline (`ptcg_ai/train/frozen/agent_v2.py`, the fixed agent, pre-weight-
retuning) rather than assuming the old verdicts still held:

- **Learned priors**: 48.0% over 50 games vs `agent_v2.py` -- still **not
  promoted** (same conclusion as before the bugfix, still parity).
- **Tuned weights**: a fresh `tune_weights.py` pass found a new candidate
  (`W_PRIZE=0.48, W_HP=0.28, W_BOARD_DEV=0.18, W_HAND=0.05,
  W_PRESENCE=0.25`) scoring 81.2% on the shrunk-budget gauntlet. Per the
  standing lesson that shrunk-budget gauntlets are not a reliable proxy,
  re-verified at **full production budget** vs `agent_v2.py`: **58.0% over
  50 games (29-21)** -- clears the >55% bar this time (previously 38.0%,
  rejected). vs-`random` re-checked at 100 games: 82.0%, statistically
  indistinguishable from the fixed-agent baseline's 87.0%/200-game figure
  (z~1.15, not significant) and still comfortably above the 80% bar --
  **promoted and shipped**. `ptcg_ai/train/frozen/agent_v3.py` freezes this
  as the new baseline for future promotion checks.

This is the first candidate from this pipeline to actually clear the
promotion bar -- a direct consequence of testing against a correct baseline
instead of one with a live bug in exactly the mechanism (bench safety under
Active-already-occupied) that board-presence-weighted heuristics most
depend on getting board state right for.

## Further strengthening pass (post-`agent_v3`)

Two more experiments, both against `agent_v3.py` as predecessor:

- **Time budget increase (negative result)**: with the correctness bugs
  fixed, checked whether the agent was leaving compute on the table --
  the `cabt` environment gives each player a 600s-per-game overage-time
  bank (`actTimeout=0`, `remainingOverageTime` starts at 600) and our
  actual usage was only ~4-13s/game, i.e. under 3% of the budget. Doubled
  `TARGET_TIME`/`HARD_CAP`/`SETUP_TARGET_TIME`/`SETUP_HARD_CAP`
  (1.2/3.0/2.5/4.5 -> 3.0/6.0/5.0/8.0s) and re-checked: vs-`random` held
  (86.7%/60 games, zero timeouts, confirming the larger budget is safe),
  but head-to-head vs `agent_v3.py` scored only **52.5%/40 games -- DO NOT
  PROMOTE**, indistinguishable from a coin flip. More rollouts of the same
  biased-random playout policy hit diminishing returns well before the
  600s ceiling; the bottleneck is elsewhere (policy/heuristic quality, not
  rollout count). Reverted to the original budget.
- **Weight round 2 (promoted)**: a second, finer coordinate-descent pass
  (`--delta 0.04`, starting from `agent_v3`'s weights) found
  `W_HP=0.24, W_BOARD_DEV=0.22` (others unchanged) scoring 70.8% on the
  shrunk-budget gauntlet. Verified at full budget vs `agent_v3.py`:
  **58.0%/50 games (29-21) -- promoted**. vs-`random` at 100 games:
  **89.0%** (up from 87.0%, no regression). Frozen as `agent_v4.py`, now
  the shipped config and the new baseline for future rounds.

Net effect of this pass: the "push time budget" lever is confirmed to be a
dead end at the current search/policy design (documented so it isn't
re-tried without a reason to expect a different result), while a second
weight-tuning round found more real gain along the same axis that worked
before -- a coordinate-descent search over 5 weights clearly hadn't
converged after 2 rounds each with a different delta.


## 5. Deck evolution (`deck_evolve.py`)

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/train/deck_evolve.py --generations 2 --population 4 --games-per-matchup 20
```

Evolutionary search over decks, seeded from the current default. Mutation
swaps 1-3 cards and is validated against the **empirically-verified engine
rules** (60 cards; max 4 copies per `cardId` except Basic Energy 1-8, which
is uncapped; >=1 Basic Pokemon required; at most 1 ACE SPEC card total) via
a real `lib.BattleStart` call before a mutant is even considered -- invalid
mutants are rejected outright rather than mis-scored. Selection: round-robin
winrate with our own agent piloting both sides. A mutant is only promoted to
"incumbent" within the run if it beats the current incumbent by the same
60% bar used for the hand-built Phase-2 candidates; the log
(`ptcg_ai/train/artifacts/deck_evolution.md`, committed) records every
mutant tried and its composition, win/loss lineage included, so the search
is auditable even when nothing gets promoted.

## Scaling up

Every stage above ran at a deliberately small scale (250 self-play games, one
coordinate-descent round, 2 generations x 4 mutants for deck evolution) to
keep the initial pipeline fast and auditable end-to-end. If a given stage's
results look like they're moving winrates (check `strategy_report.md` for the
numbers actually observed), the natural next steps are: more self-play games
and a lower `--min-support` for a bigger prior table; more coordinate-descent
rounds or a proper SPSA loop for weights; a wider mutation operator and more
generations/population for deck evolution, evaluated against a full gauntlet
(random + first + several frozen ancestors) rather than a single incumbent.
