<!-- word count: 1999 words (body, excluding this comment line) -->

# Strategy Report: Determinized Monte-Carlo Search over the Official PTCG Engine

## Summary

Our Simulation-category agent (`ptcg_ai/agent/main.py`) is a single-file,
depth-limited **Perfect Information Monte Carlo (PIMC)** player. It does not
re-implement Pokemon TCG rules; it drives the competition's own game engine
(`libcg.so`, via `kaggle_environments.envs.cabt.cg.sim`) through its internal
`Search*` API to simulate candidate moves and picks whichever candidate
scores best on average. This makes the agent rules-correct by construction
and immediately benefits from any future engine update.

**Current measured strength vs the built-in `random` agent: 87.0% winrate
(1175/1350) aggregated over five 150-400 game batches after the fixes below,
zero invalid/timeout/error statuses, longest observed win streak 38.** This
clears the project's 80% baseline bar comfortably. A precise, per-decision
loss classification (§6) shows that after two targeted fixes -- a
deterministic "never leave the board empty" safety override and a small
deck consistency change (Deck Concept) -- **100% of classified losses
(58/58 across two full diagnostic batches) are provably unpreventable given
the opening hand actually drawn**: no missed bench opportunity, no unplayed
search trainer, ever. The remaining gap to "100 straight wins" is
opening-hand/race variance inherent to a 60-card TCG deck against a
genuinely random opponent, not a bug; §6 shows why sweeping 100 games in a
row isn't realistic below ~99% per-game. We also built a small offline
learning pipeline (§7); none of its three candidate changes cleared our own
promotion bar, and we report those honest negative results too.

## Model Approach (70%)

### 1. Why search, not a hand-written policy

Each `select` in the observation is a low-level engine sub-decision, not a
full turn, and hand-authoring a policy over this space is error-prone. The
engine's `Search*` API lets us replay the current state under a chosen
hidden-information assignment (a determinization) and step it forward with
arbitrary actions, validated by the same rules code as the real match. We
build a standard **PIMC** search: sample determinizations, roll out
candidate root actions to a depth cap or terminal state, average the outcome.

### 2. Reverse-engineered Search API

Five C functions, bound via `ctypes`: `AgentStart()` allocates a reusable
context once per process. `SearchBegin(ctx, search_begin_input, len, myDeck,
myPrize, oppDeck, oppPrize, oppHand, spare, flag=0)` seeds a search rooted at
the current `obs`; the six int arrays must have lengths exactly equal to the
real zone counts or it fails with `error:1`; the root state gets **handle
0**. `SearchStep(ctx, handle, action_indices, n)` applies a selection to the
state at `handle`, returning a new state at the next sequential handle;
**each handle steps exactly once** (re-stepping errors `4/5` — harmless,
just retry with a different action). `SearchEnd(ctx)` frees every state since
the last call and resets the handle counter to zero; we call it **once per
rollout**, so every `SearchBegin` restarts cleanly at handle 0 (calling it
only once per decision instead was an early bug that silently broke the
"root = handle 0" assumption). `SearchRelease(ctx, handle)` is bound but
unused. Measured throughput: ~18,000 `SearchStep`/s, ~195 full random
playouts/s single-threaded.

### 3. Determinization of hidden information

Our own hidden cards are exact: `Counter(DECK)` minus every card visible in
our hand/board/discard/face-up prizes, shuffled and sliced to `deckCount` +
hidden-prize-count. The opponent's deck is genuinely unknown on Kaggle: we
mirror our own deck's distribution, remove any opponent cards we've actually
observed, and sample the remainder to fill their deck/prizes/hand. A fresh
determinization is drawn **per rollout**, averaging over hidden information
and playout randomness together.

### 4. Candidate enumeration, rollout, and leaf evaluation

`maxCount==1` selects: one candidate per option (plus empty if `minCount==0`).
Multi-select: the greedy "first k" plus up to 8 random valid combos, capped
at 24 total. A single legal candidate skips search entirely — most selects
are forced single options, which is why per-game wallclock stays far below
`moves x budget`. Each rollout applies the candidate, then plays out with a
**tiered biased-random policy**: attacks (55%) > board-development plays
(bench a Pokemon / attach energy, 55%) > any non-pass (85%) > pass, to a
depth cap of 90 steps or terminal. Terminal leaves score +1/0/-1; non-terminal
leaves use a weighted heuristic (`W_PRIZE=0.40, W_HP=0.20, W_BOARD_DEV=0.10,
W_HAND=0.05, W_PRESENCE=0.25`) over prize differential, HP removed, board
development, hand size, and a **board-presence term** (min(Pokemon in
play, 3)/3, mine minus opponent's) added after loss diagnosis (§6).

### 5. Time control and safety

Per-decision budget: 1.2s soft / 3.0s hard normally, boosted to 2.5s soft /
4.5s hard for turn <=2 "setup" decisions, with a floor of 8 determinizations
(diagnosis showed these are the highest-leverage decisions). Every path,
including any exception, is wrapped so the function always returns a valid
answer, falling back to "first non-pass option" or the first `minCount`
indices. `SearchEnd` runs in a `finally` per rollout so no engine state leaks.

### 6. Loss diagnosis, a deterministic safety override, and the variance floor

`PTCG_DEBUG=1`-gated instrumentation (silent by default) records, per
decision, the select shape, chosen action, board state, full hand contents,
and a map from *every offered option* to the specific hand card it would
play -- letting us tell precisely whether a play was live and skipped, not
just that a card sat in hand. `PTCG_FULL_HISTORY=1` keeps the *entire*
game's decisions, not a ring buffer. Across >1000 diagnosed games, **100% of
losses ended with our side at zero Pokemon in play** (the TCG's instant
loss) — never from a search/engine error.

**Deterministic safety override.** `bench_basic_override()` runs *before*
search on every decision: if our total Pokemon in play is <=1, bench space
exists, and any offered option plays a Basic Pokemon from hand onto the
bench, we take it immediately and unconditionally, at zero search cost.
Matched on *shape* (source/destination zone + the target card's identity),
not a specific option "type" code, since the engine reuses different codes
for this play across contexts (setup vs. a normal turn). The playout-policy
rescue bias was broadened the same way and raised to 95%.

**Precise classification.** For every loss we determine: (a) Basic Pokemon
count in the opening hand; (b) whether *any* decision had presence <=1,
bench room, and an unchosen bench-a-basic option (a real bug, distinct from
what the override now always takes); (c) whether Ultra Ball was a live,
offered, unplayed option right before death. Across two full-history
batches on the shipped config (350 games, 58 losses): **0 missed-bench
chances, 0 unplayed-search-trainer cases — 58/58 (100%) are true variance**:
we provably never had a second Basic Pokemon available when needed.

**Why "100 straight" isn't the right bar.** At the observed ~87% rate, the
expected longest win streak over N games is `log(N(1-p))/log(1/p)`; over
1350 games that predicts ~35 (observed: 38). An *expected* 100-streak at
this rate needs N ~= 3x10^6 games. Only pushing the true rate toward ~99%
makes a 100-streak plausible at a normal sample size, and that is a
deck-power/format target, not something search or a safety override alone
can deliver.

### 7. Learning pipeline (`ptcg_ai/train/`) and its honest results

To improve from experience rather than only hand-tuning, we built four
offline stages baking output back into `main.py` as embedded constants (no
runtime file loads): (1) `selfplay.py`, 250 games / 15,653 decision records;
(2) `build_priors.py`, a `(select_type, context, option_type) -> win-rate`
table (19 keys, Laplace-smoothed, falling back to neutral for unseen keys);
(3) `tune_weights.py`, coordinate descent over the leaf weights against a
small gauntlet; (4) `deck_evolve.py`, a rule-validated evolutionary search.

Every candidate must clear a strict **promotion rule**: `league_check.py`
plays it head-to-head against a frozen predecessor snapshot at full
production time budget, winning >55% over >=50 games. Results: **learned priors** scored 54.0%
(27/50) — parity, not promoted. **Tuned weights** (`W_BOARD_DEV`
0.10->0.18) looked like a big win in a fast, shrunk-time-budget gauntlet
(81.2% vs a 56.2% baseline) but scored only **38.0%** at full budget — a
clear reversal, and the key lesson: a shrunk-time-budget gauntlet is **not**
a reliable proxy for full-budget strength, so every promotion decision must
be re-validated at production settings. **Deck evolution** (1 generation, 3
mutants) found nothing beating the 60% bar (best 43.8%), consistent with the
hand-built candidates below. All three were reverted/unshipped; the
pipeline, data, and these results are kept and documented
(`ptcg_ai/train/README.md`) as a working first pass, not a converged system.

## Deck Concept (20%)

### Empirically-discovered deck rules

We probed `lib.BattleStart` directly (bypassing the Python wrapper) with
crafted decks to discover validation rules from `errorType` codes:

| Rule | Evidence |
|---|---|
| Exactly 60 cards/deck | enforced by the Python/Kaggle wrapper layer (the raw C call has no length parameter, so malformed-length probes are unsafe/undefined — not tested at the raw level) |
| Max 4 copies of any card, by `cardId` | 4x Kyogre OK, 5x/6x/8x -> `error:2` |
| **Basic Energy exempt from the 4-cap** | up to 55x Basic {W} Energy (`3`) accepted |
| Special Energy (`cardType 6`) is NOT exempt | 4x OK, 5x -> `error:2`, same as normal cards |
| Must contain >=1 **Basic** Pokemon | all-evolved-Pokemon or all-trainer decks -> `error:3`; 1 basic + 0 evolutions is legal |
| At most 1 **ACE SPEC** card total | 2 different ACE SPEC cards (not just 2 copies of one) -> `error:4` |
| Any known `cardId` (1-1267) usable at <=4 copies | 5 random Pokemon across the id range all accepted |
| No minimum energy requirement | a 0-energy deck (Pokemon + trainers only) is legal |
| Unknown/invalid `cardId` (0, 999999) | `error:1` |

### Deck evaluation

Starting deck: `kaggle_environments`'s sample (Kyogre / Snover-Mega
Abomasnow ex / 33 energy). We first buffed Kyogre 2->4 (basics 6->8, energy
33->31, v2), then hand-built six further candidates and round-robin-tested
them **with our own agent piloting both sides**, 40 games each (evaluated
for *parity*, not power, since the goal is consistency):

| Candidate | Change from v2 | Winrate vs v2 |
|---|---|---|
| C1: all-basic aggro | Replace evolution line with 3 non-evolving basics (Keldeo ex, Ogerpon ex, Chien-Pao), no energy change | 5.0% |
| C3: hybrid | Add 4x Keldeo ex, energy 31->27 | 20.0% |
| C4: +Glastrier | Add 4x Glastrier (non-ex), energy 31->27 | 27.5% |
| C5: +Glastrier, energy-preserved | Add 4x Glastrier, cut narrow trainers instead of energy (energy stays 31) | 45.0% |
| D1: +4x Chien-Pao | Add 4x Chien-Pao (120 HP, non-ex, "Icicle Loop" 120 dmg/3 energy, retreat 1), energy preserved at 31 | 42.5% |
| **D2: +2x Chien-Pao** | Add only 2x Chien-Pao, cut Mega Signal (narrow-use), energy preserved at 31 | **50.0%** |

C1-C5 all lost outright; **D2 reached exact parity (20/40)** and became
**v3, the shipped deck**: basics 8->10 (P(<=1 basic) 76.8%->67.0%), still
31/60 energy, no regression vs `random` (87.0% post-fix vs 88.4%
override-only — within noise). Reusable lessons: (1) `ex`/`megaEx` Pokemon likely cost 2 prizes
when KO'd (inferred from the pattern) — packing many `ex` attackers (C1, C3)
trades power for a faster prize-race loss, while v2/v3's single, 350 HP
`megaEx` rarely pays that tax; (2) diluting energy density to fit more
Pokemon hurts more than extra basics help (C4 vs C5: 27.5%->45.0%; D1 vs D2:
42.5%->50.0%, same fix both times); (3) a smaller, less disruptive addition
(D2) beat a larger one of the same card (D1), suggesting the deck sits near
a local optimum where only small, targeted nudges clear parity.
`ptcg_ai/train/deck_evolve.py` (Future Work) is designed to search this
space systematically instead of by hand.

## Report Quality (10%) — Limitations and Future Work

1. **Root selection has no UCB** — flat MC averaging, not ISMCTS/PUCT.
2. **Opponent modeling** is a naive mirror-of-our-deck placeholder.
3. **Leaf heuristic weights** were hand-picked (§7 shows a fast tuning loop
   can't be trusted to fix this alone).
4. **The remaining ~13% loss rate is a genuine variance floor, not a bug**
   (§6): closing it needs deck-level search for more consistency headroom
   (`deck_evolve.py`, currently one small pass), not more agent cleverness.
5. **The learning pipeline (§7) needs scale, not redesign**: single-pass
   runs validated the machinery but didn't clear our promotion bar. More
   self-play games, more coordinate-descent rounds (always at full budget),
   and more deck-evolution generations are the concrete next steps
   (`ptcg_ai/train/README.md`, "Scaling up").
