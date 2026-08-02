<!-- word count: 1771 words (body, excluding this comment line) -->

# Strategy Report: Determinized Monte-Carlo Search over the Official PTCG Engine

## Summary

Our Simulation-category agent (`ptcg_ai/agent/main.py`) is a single-file,
depth-limited **Perfect Information Monte Carlo (PIMC)** player. It does not
re-implement Pokemon TCG rules or heuristics about specific cards; instead it
drives the competition's own game engine (`libcg.so`, reached through
`kaggle_environments.envs.cabt.cg.sim`) via its internal `Search*` API to
simulate candidate moves forward, and picks whichever candidate scores best
on average. This makes the agent rules-correct by construction (the engine
enforces legality) and immediately benefits from any future engine update,
at the cost of depending on engine internals that are undocumented and were
reverse-engineered for this project.

Locally, over 40 games alternating first/second seat against the built-in
`random` baseline, the agent won 38 (95.0% winrate, mean reward +0.90), with
zero invalid/timeout/error statuses, at roughly 1.6s of wallclock per game.
A first 20-game run scored 16/20 (80.0%), showing the expected sampling
variance of a stochastic policy against a stochastic opponent; both runs
clear the 80% baseline bar.

## Model Approach (70%)

### 1. Why search, not a hand-written policy

Pokemon TCG has enormous combinatorial depth per turn (attaching energy,
playing trainers, evolving, retreating, attacking, all before "end turn"),
and each individual `select` in the observation is a low-level engine
sub-decision, not a full "turn". Hand-authoring a heuristic policy over this
space is both error-prone and hard to validate against the engine's actual
rules. The competition engine exposes a `Search*` C API purpose-built for
exactly this: it lets an agent replay the current game state under a chosen
hidden-information assignment (a "determinization") and step it forward with
arbitrary chosen actions, entirely inside the engine, so every simulated
action is validated by the same rules code that governs the real match. We
therefore build a standard **PIMC / determinized-UCT-style** search on top of
it: sample plausible determinizations of hidden information, roll out
candidate root actions to a depth cap or terminal state, and average the
outcome.

### 2. Reverse-engineered Search API

The engine exposes five relevant C functions, bound via `ctypes`:

- `AgentStart() -> ctx`: allocate a reusable search context (once per
  process).
- `SearchBegin(ctx, search_begin_input, len, myDeck, myPrize, oppDeck,
  oppPrize, oppHand, spare, flag=0) -> {"state": {...}, "error": 0}`: seed a
  new search rooted at the current real `obs`, with an explicit assignment
  of hidden zones. `search_begin_input` is an opaque blob the engine itself
  returns on every observation (`obs["search_begin_input"]`); the six int
  arrays that follow must have lengths that exactly equal the corresponding
  zone counts (`deckCount`, count of `None` in `prize[]`, opponent
  `handCount`, etc.) or `SearchBegin` fails with `error: 1`. The root state
  it returns is allocated **handle 0**, and its `select` is identical to the
  real, currently-pending `obs["select"]`.
- `SearchStep(ctx, handle, action_indices, n) -> {"state": {...}, "error": 0}`:
  apply a chosen selection (indices into `select["option"]`) to the state at
  `handle`, returning a *new* state. Handles are allocated sequentially
  (`0, 1, 2, ...`) across every successful `SearchBegin`/`SearchStep` call
  since the last `SearchEnd`, and **each handle can be stepped exactly
  once** — re-stepping, or stepping with an illegal action, returns
  `error: 4/5` and no new state. This makes a linear playout a simple loop
  that increments its own handle counter by one after each success and
  retries with a different random action on failure.
- `SearchEnd(ctx)`: free every state allocated since the last `SearchEnd`
  and reset the handle counter to zero. We call this once per rollout
  (inside a `try/finally`), matching the verified reference usage, so every
  `SearchBegin` always starts its own rollout back at handle 0 — this was
  the single most important correctness detail: calling `SearchBegin`
  repeatedly *without* an intervening `SearchEnd` keeps incrementing the
  handle counter across rollouts, silently breaking the "root = handle 0"
  assumption used for the first step of each candidate.
- `SearchRelease(ctx, handle)`: fine-grained single-handle release (bound
  but unused by the baseline, which prefers the simpler per-rollout
  `SearchEnd`).

Measured single-threaded throughput on the eval machine: roughly 18,000
`SearchStep` calls/second and ~195 full random playouts/second, which is
what allows dozens of short rollouts per real decision inside a sub-second
budget.

### 3. Determinization of hidden information

Two hidden zones must be filled in before `SearchBegin`: our own undrawn
deck/prizes, and the opponent's entire deck, hand and prizes.

- **Our own hidden cards**: exact. We always submit the literal `DECK`
  constant as our real deck, so the true multiset of our unseen cards is
  simply `Counter(DECK)` minus every card currently visible in our hand,
  active/bench (including attached energy, tools and pre-evolutions),
  discard, and face-up prizes. This is shuffled and sliced into exactly
  `deckCount` deck cards and (count of `None` in `prize[]`) prize cards.
- **Opponent's hidden cards**: genuinely unknown on Kaggle (opponents may
  run arbitrary decks). The baseline uses a simple, pluggable placeholder:
  mirror our own deck's card distribution, remove any opponent cards we
  have actually observed (their board/discard) from that mirrored template,
  and sample the remainder (padding with basic Energy if the template runs
  short) to fill the opponent's deck, hidden prizes, and hand to their
  exact observed counts. This is intentionally simple and clearly flagged
  in the code as a swap point — see Future Work.

A fresh determinization is drawn per rollout (not per decision), so the
average over `D` rollouts per candidate is simultaneously an average over
hidden-information samples and playout randomness, which is the standard
PIMC recipe for reducing "strategy fusion" bias relative to solving a single
fixed determinization to the end.

### 4. Candidate enumeration

For each real `select`, we do **not** search every combination:

- `maxCount == 1` (the overwhelming majority of selects): one candidate per
  option index, plus the empty selection when `minCount == 0`.
- multi-select: the greedy "first `k`" combination plus up to 8 random valid
  combinations.
- capped at 24 total candidates (uniform random subsample beyond that,
  always keeping one deterministic candidate).
- if enumeration collapses to a single legal candidate, it is returned
  immediately with **no search at all** — most engine selects (e.g. a
  forced single "OK" prompt) fall into this fast path, which is why mean
  wallclock per game (≈1.6s across dozens of selects) is far below
  `moves × 0.8s`.

### 5. Rollout, leaf evaluation, and playout policy

Each rollout: `SearchBegin` → `SearchStep(candidate)` at the root → a random
playout using a **pass-averse uniform policy** (85% of the time restrict
sampling to options whose `type != 14`, i.e. avoid trivially passing when a
substantive option exists) → stop at a depth cap of 60 `SearchStep`s or at a
terminal state, whichever comes first. Terminal leaves score
`+1 / 0 / -1` for win/draw/loss from our seat's perspective
(`result == yourIndex`). Non-terminal leaves (depth cap reached, time
exhausted, or the engine returning a step error we gave up retrying) are
scored by a compact heuristic in `[-1, 1]`:

```
0.50 * prize_differential   (prizes I've taken − prizes opponent has taken, /6)
+ 0.25 * hp_differential    (fraction of opponent board HP removed − mine, /6)
+ 0.15 * board_development  ((my energy-in-play + bench size) − opponent's, /10)
+ 0.10 * hand_advantage     ((my hand size − opponent's) / 10)
```

These weights are simple, hand-picked constants (no tuning pass was run);
prize differential dominates because taking the sixth prize is the actual
win condition.

### 6. Action selection, time control, and safety

For each candidate we run an adaptive number of determinizations (2–8,
scaled by remaining time budget divided by remaining candidate count) and
take its mean score; the candidate with the highest mean wins ties by
enumeration order. A module-level soft budget of 0.8s and hard cap of 1.5s
per decision governs the whole loop, both checked repeatedly inside the
candidate/determinization loops so we bail out early rather than overrun;
`obs.get("remainingOverageTime")` is consulted to shrink the budget
aggressively (down to 0.1s) when the match clock is running low. Every code
path — deck submission, the "single legal candidate" fast path, full search,
and any unexpected exception anywhere in the pipeline — is wrapped so the
function *always* returns a structurally valid answer: on any failure the
agent falls back to "first non-pass option" or, failing that, the first
`minCount` option indices. `SearchEnd` is always called in a `finally` block
per rollout and again around the whole decision, so no engine state ever
leaks across decisions even when search is interrupted by an exception.

## Deck Concept (20%)

The baseline ships the sample 60-card deck taken as-is from
`kaggle_environments.envs.cabt.cabt.deck`, built around **Kyogre** (`721`,
×2, 150 HP Water attacker) backed by a **Snover → Mega Abomasnow ex**
evolution line (`722` ×4 / `723` ×4, 350 HP, a high-HP mid/late-game
finisher), a small trainer/tool suite (`Secret Box`, `Ultra Ball`, `Mega
Signal`, `Powerglass`, `Team Rocket's Petrel`, `Lillie's Determination`,
`Surfing Beach`) for consistency and search/draw power, and 33 copies of
Basic {W} Energy (`3`) — over half the deck — to guarantee attackers are
almost always fuelled on curve. This is deliberately a **consistency-first
baseline**, not a meta deck: a single, reliable Water-type gameplan with a
heavy energy count minimizes variance so that evaluation results mostly
reflect the search/decision quality rather than deck-building luck. The
`DECK` constant in `main.py` is clearly marked as the swap point for future
meta-informed deckbuilding; the search logic itself is fully deck-agnostic.

## Report Quality (10%) — Limitations and Future Work

Known limitations of this baseline, roughly in order of expected impact:

1. **Root selection has no exploration/exploitation weighting.** We use flat
   Monte Carlo averaging at the root rather than UCB1/PUCT, so search effort
   is spread evenly instead of concentrating on promising lines. Upgrading
   to root-parallel **ISMCTS with UCB** (per determinization or pooled) is
   the highest-value next step.
2. **Opponent modeling is a naive mirror-of-our-deck placeholder.** A real
   improvement would infer plausible opponent decks from observed
   archetypes/cards (e.g. weighting popular meta decks compatible with
   revealed cards) rather than assuming symmetry.
3. **Playout policy is uniform random (pass-averse only).** A cheap learned
   or hand-crafted playout policy (e.g. prefer attacking, prefer energy
   attachment before end-of-turn) would sharpen leaf estimates without
   materially increasing per-step cost.
4. **Leaf heuristic is a fixed linear blend with untuned weights.** These
   could be tuned via self-play, or replaced entirely by a learned value
   network trained on engine self-play data (light RL / supervised value
   function), decoupling strength from search depth.
5. **Candidate enumeration for large multi-select spaces is sampled, not
   exhaustive**, so rare wide selects (e.g. big deck-search effects) may
   miss the truly optimal combination; this only matters for a minority of
   select types.

Overall, the baseline demonstrates that the reverse-engineered `Search*` API
is sufficient to build a legality-safe, competitively strong PIMC agent with
a modest, well-understood implementation, and it establishes clear,
incrementally addressable next steps (ISMCTS, opponent modeling, learned
playout/value functions) for improving strength beyond this baseline.
