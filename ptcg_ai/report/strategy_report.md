<!-- word count: 1477 words (body, excluding this comment line) -->

# Strategy Report: Determinized Monte-Carlo Search over the Official PTCG Engine

## Summary

Our Simulation-category agent (`ptcg_ai/agent/main.py`) is a single-file,
depth-limited **Perfect Information Monte Carlo (PIMC)** player. It does not
re-implement Pokemon TCG rules; it drives the competition's own game engine
(`libcg.so`, via `kaggle_environments.envs.cabt.cg.sim`) through its internal
`Search*` API to simulate candidate moves forward, and picks whichever
candidate scores best on average. This makes the agent rules-correct by
construction and immediately benefits from any future engine update.

**Current measured strength vs the built-in `random` agent: 86.9% winrate
(565/650) aggregated over three independent 200-250 game batches, alternating
seats, zero invalid/timeout/error statuses, longest observed win streak 37,
~1.6-3.2s wallclock per game.** This clears the project's 80% baseline bar
comfortably but falls short of a "100 straight wins" aspiration; a structured
loss diagnosis (below) shows why, and what we did and did not fix.

## Model Approach (70%)

### 1. Why search, not a hand-written policy

Each `select` in the observation is a low-level engine sub-decision, not a
full turn, and hand-authoring a policy over this space is error-prone. The
engine's `Search*` API lets us replay the current state under a chosen
hidden-information assignment (a determinization) and step it forward with
arbitrary actions, validated by the same rules code as the real match. We
build a standard **PIMC** search on top: sample determinizations, roll out
candidate root actions to a depth cap or terminal state, average the outcome.

### 2. Reverse-engineered Search API

Five C functions, bound via `ctypes`: `AgentStart()` allocates a reusable
context once per process. `SearchBegin(ctx, search_begin_input, len, myDeck,
myPrize, oppDeck, oppPrize, oppHand, spare, flag=0)` seeds a search rooted at
the current `obs`; the six int arrays must have lengths exactly equal to the
real zone counts or it fails with `error:1`; the root state gets **handle
0**. `SearchStep(ctx, handle, action_indices, n)` applies a selection to the
state at `handle`, returning a new state at the next sequential handle;
**each handle steps exactly once** (re-stepping errors `4/5`, harmless —
just retry with a different action). `SearchEnd(ctx)` frees every state since
the last call and resets the handle counter to zero; we call it **once per
rollout**, so every `SearchBegin` restarts cleanly at handle 0 — calling it
only once per decision instead (across many rollouts) was an early bug that
silently broke the "root = handle 0" assumption. `SearchRelease(ctx, handle)`
is bound but unused. Measured throughput: ~18,000 `SearchStep`/s, ~195 full
random playouts/s single-threaded.

### 3. Determinization of hidden information

Our own hidden cards are exact: `Counter(DECK)` minus every card visible in
our hand/board/discard/face-up prizes, shuffled and sliced to `deckCount` +
hidden-prize-count. The opponent's deck is genuinely unknown on Kaggle: we
mirror our own deck's distribution, remove any opponent cards we've actually
observed, and sample the remainder to fill their deck/prizes/hand. A fresh
determinization is drawn **per rollout**, averaging over both hidden
information and playout randomness.

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
play, 3)/3, mine minus opponent's) added after loss diagnosis (below).

### 5. Time control and safety

Per-decision budget: 1.2s soft / 3.0s hard normally, boosted to 2.5s soft /
4.5s hard for turn <=2 "setup" decisions (initial placement) with a floor of
8 determinizations, since diagnosis showed these are the highest-leverage
decisions in the game. `remainingOverageTime` shrinks the budget when the
match clock is low. Every path — including any exception — is wrapped so the
function always returns a valid answer, falling back to "first non-pass
option" or the first `minCount` indices. `SearchEnd` runs in a `finally` per
rollout (and again per decision) so no engine state leaks.

### 6. Loss diagnosis and what we fixed

We added `PTCG_DEBUG=1`-gated instrumentation (silent by default; `os.environ`
check at import) recording, per decision, the select type/context, candidate/
option counts, chosen action, fallback usage, and engine-call failures, plus
a rolling history and board snapshot. Across 250 diagnosed games (pre-fix),
**100% of losses (25/25) ended with our side at zero Pokemon in play** — the
TCG's instant "no Pokemon in play" loss — never from a search/engine error
(fallback and engine-failure counters were consistently 0 in losses). We
applied four fixes: (a) raised Kyogre from 2->4 copies (below) to reduce
single-basic openings; (b) added the board-presence heuristic term above; (c)
biased playouts to try 8-copy Kyogre/Ultra-Ball-style rescue plays first when
our board has <=1 Pokemon; (d) gave setup-phase decisions far more search
budget. Post-fix, over 650 diagnosed/undiagnosed games, **93% of remaining
losses (24/26 sampled) still show the same zero-Pokemon signature**, almost
always by turn 3-15 — i.e. the residual loss rate is now dominated by opening
-hand variance (see Deck Concept) rather than search or engine bugs, and
further gains require deck-level fixes more than agent-level ones.

## Deck Concept (20%)

### Empirically-discovered deck rules

We probed `lib.BattleStart` directly (bypassing the Python wrapper) with
crafted decks to discover validation rules from `errorType` codes (see
`AllCard.json` for card metadata):

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
Abomasnow ex / 33 energy). We first buffed Kyogre 2->4 copies (basics 6->8,
dropping 2 energy 33->31) purely for consistency. We then hand-built four
further candidates from `AllCard`/`AllAttack` and round-robin-tested them
**with our own agent piloting both sides**, 40 games alternating seats:

| Candidate | Change from v2 | Winrate vs v2 |
|---|---|---|
| C1: all-basic aggro | Replace evolution line with 3 non-evolving basics (Keldeo ex, Ogerpon ex, Chien-Pao), no energy change | 5.0% |
| C3: hybrid | Add 4x Keldeo ex, energy 31->27 | 20.0% |
| C4: +Glastrier | Add 4x Glastrier (non-ex), energy 31->27 | 27.5% |
| C5: +Glastrier, energy-preserved | Add 4x Glastrier, cut narrow trainers instead of energy (energy stays 31) | 45.0% |

All four candidates **lost** to the incumbent (v2), none clearing the >60%
promotion bar, so **v2 (Kyogre x4) remains the shipped deck**. Two clear,
reusable lessons emerged: (1) `ex`/`megaEx` Pokemon cost 2 prizes when KO'd
(inferred from the pattern, not directly labeled in `AllCard`) — packing many
`ex` attackers (C1, C3) trades power for a much faster prize-race loss,
whereas v2's single `megaEx` (350 HP, rarely dies) pays that tax rarely; (2)
diluting energy density to make room for more Pokemon hurts more than extra
basics help (C4 vs C5: recovering 4 energy slots nearly doubled the winrate,
27.5%->45.0%). v2's high energy density (31/60) and low-diversity, high-copy
structure is a well-tuned local optimum that naive hand-edits don't beat;
`ptcg_ai/train/deck_evolve.py` (Future Work) is designed to search this space
systematically instead.

## Report Quality (10%) — Limitations and Future Work

1. **Root selection has no UCB** — flat MC averaging, not ISMCTS/PUCT.
2. **Opponent modeling** is a naive mirror-of-our-deck placeholder.
3. **Leaf heuristic weights** were hand-picked, not tuned.
4. **Residual losses are opening-hand-variance-dominated** (93% still hit the
   zero-Pokemon condition, mostly turn 3-15): the fix is more deck redundancy
   found via search, not more agent cleverness, at this point.
5. **Learning pipeline** (`ptcg_ai/train/`): self-play data collection,
   learned action-outcome priors, gauntlet/league eval, and evolutionary deck
   search are designed and implemented at a small, time-boxed scale (see
   `ptcg_ai/train/README.md`) rather than run to convergence — the natural
   next step is scaling each stage up.
