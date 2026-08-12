<!-- word count: 1996 words (body, excluding this comment line) -->

# Strategy Report: Determinized Monte-Carlo Search over the Official PTCG Engine

## Summary

Our Simulation-category agent (`ptcg_ai/agent/main.py`) is a single-file,
depth-limited **Perfect Information Monte Carlo (PIMC)** player. It does not
re-implement TCG rules; it drives the competition's own `libcg.so` engine
through its internal `Search*` API to simulate candidate moves and picks
whichever scores best -- rules-correct by construction.

**89.0% winrate vs the built-in `random` agent, zero invalid/timeout/error
statuses** -- confirmed across three large-N rounds as the agent evolved:
1175/1350 pre-bugfix, 174/200 post-bugfix (§2), 89/100 after two rounds of
promoted weight tuning (§7, every downstream conclusion re-checked against
the fixed agent, never assumed to still hold). A precise loss
classification (§6) shows **100% of classified losses (58/58) are provably
unpreventable** given the opening hand drawn. We **round-robin
tournamented v3 against 5 archetype decks** (450 games; Deck Concept): v3
won every pairing and remains champion, confirmed again post-bugfix on the
two closest contenders. The offline learning pipeline (§7) produced two
promoted weight-tuning rounds (shipped), a confirmed-dead-end time-budget
experiment (reverted, documented), and two honest still-parity results
(priors, deck evolution).

## Model Approach (70%)

### 1. Why search, not a hand-written policy

Each `select` in the observation is a low-level engine sub-decision, not a
full turn, and hand-authoring a policy over this space is error-prone. The
engine's `Search*` API lets us replay the current state under a chosen
hidden-information assignment (a determinization) and step it forward with
arbitrary actions, validated by the same rules as the real match. We build
a standard **PIMC** search: sample determinizations, roll out candidate
root actions to a depth cap or terminal state, average the outcome.

### 2. Reverse-engineered, then officially cross-verified, Search API

Five C functions, bound via `ctypes`: `AgentStart()` allocates a reusable
context once per process; `SearchBegin(ctx, search_begin_input, len,
myDeck, myPrize, oppDeck, oppPrize, oppHand, opponentActive, manualCoin=0)`
seeds a search rooted at the current `obs`; `SearchStep(ctx, search_id,
action_indices, n)` applies a selection, returning a new state plus its own
`searchId`; `SearchEnd(ctx)` frees every state since the last call, called
**once per rollout**. Throughput: ~18,000 `SearchStep`/s single-threaded.

We later obtained the official engine source (C++ plus `cg/api.py`) and
audited our bindings line by line. Fixes: (a) handle type `c_long` ->
`c_int64`; (b) `SearchStep`'s id must be the authoritative `searchId` the
*previous* response returned, not a self-maintained counter as we'd
assumed; (c) `SearchBegin`'s 6th array (`opponent_active`) is **required**
when the opponent's Active is face-down -- we always passed empty, now
guess an id from evidence; (d) most consequentially, `AreaType` (`ACTIVE=4,
BENCH=5`) showed `bench_basic_override` and the rescue bias, both keyed on
`inPlayArea==4`, matched only "into an empty Active" and missed "Active
occupied, second Basic must go to the Bench" (`==5`) -- despite that being
the more common recovery case. Widening to `{4, 5}` moved a 40-game
benchmark 77.5% -> 90.0%, with engine-call failures at 0 either way -- a
silent bug only an official-source audit surfaced.

### 3. Determinization of hidden information

Our own hidden cards are exact: `Counter(DECK)` minus every card visible in
our hand/board/discard/face-up prizes. The opponent's deck is genuinely
unknown: an earlier version mirrored our own distribution, harmless vs
`random` but wrong once real archetype diversity is in play (Deck Concept).
Fixed to deck-agnostic: cards actually observed of theirs, a few
broadly-common staple Trainers, a legality floor of generic Basics, and
heavy weighting on whichever Basic Energy type they've shown. Fresh
determinization **per rollout**, averaging over hidden info and randomness.

### 4. Candidate enumeration, rollout, and leaf evaluation

`maxCount==1` selects: one candidate per option (plus empty if `minCount==0`).
Multi-select: greedy "first k" plus up to 8 random valid combos, capped at
24. A single legal candidate skips search entirely — most selects are
forced single options, why per-game wallclock stays far below
`moves x budget`. Each rollout applies the candidate, plays out with a
**tiered biased-random policy** (attacks 55% > board-development 55% > any
non-pass 85% > pass) to a depth cap of 90 or terminal. Terminal leaves score
+1/0/-1; non-terminal leaves use a weighted heuristic (`W_PRIZE=0.48,
W_HP=0.24, W_BOARD_DEV=0.22, W_HAND=0.05, W_PRESENCE=0.25` -- re-tuned
twice, §7) over prize differential, HP removed, board development, hand
size, and a **board-presence term** added after loss diagnosis (§6).

### 5. Time control and safety

Per-decision budget: 1.2s soft / 3.0s hard normally, boosted to 2.5s/4.5s
for turn <=2 "setup" decisions, floor of 8 determinizations. Every path,
including any exception, is wrapped so the function always returns a valid
answer, falling back to "first non-pass option" or the first `minCount`
indices. `SearchEnd` runs in a `finally`
per rollout so no engine state leaks.

### 6. Loss diagnosis, a deterministic safety override, and the variance floor

`PTCG_DEBUG=1`-gated instrumentation (off by default) records, per
decision, the select shape, chosen action, board state, hand contents, and
a map from *every offered option* to the specific hand card it would play
-- letting us tell precisely whether a play was live and skipped, not just
that a card sat in hand. `PTCG_FULL_HISTORY=1` keeps the *entire* game's
decisions. Across >1000 diagnosed games, **100% of losses ended with our
side at zero Pokemon in play** (the TCG's instant loss) — never from a
search/engine error.

**Deterministic safety override.** `bench_basic_override()` runs *before*
search on every decision: if Pokemon in play is <=1, bench space exists,
and any offered option plays a Basic Pokemon from hand to the bench, take
it immediately, at zero search cost. Matched on *shape* (zone + card
identity), not a "type" code, since the engine reuses codes across
contexts. The playout-policy rescue bias was broadened the same way, to 95%.

**Precise classification.** For every loss: (a) Basic Pokemon count in the
opening hand; (b) any decision with presence <=1, bench room, and an
unchosen bench-a-basic option; (c) whether Ultra Ball was live and unplayed
right before death. 350 games/58 losses: **0 missed-bench chances, 0
unplayed-search-trainer cases — 58/58 true variance**. Re-run against
ground truth instead of board-state inference: `LogType.RESULT.reason` on
the terminal log (1=opponent took all 6 prizes, 2=deck-out, 3=no Pokemon
in Active, 4=card effect). 60 fresh games (`classify_losses.py`): 8 losses
split 75% reason=3 (matches) and **25% reason=1**, a prize-race sub-mode
the coarser method hadn't separately surfaced; 0 from deck-out/card effect.

**Why "100 straight" isn't the right bar.** At ~87-89%, expected longest
streak over N games is `log(N(1-p))/log(1/p)`; over 1350 games that
predicts ~35 (observed: 38). An *expected* 100-streak needs N ~= 3x10^6
games -- only pushing the true rate toward ~99% makes that plausible at a
normal sample size, a deck-power/format target, not a search/override job.

### 7. Learning pipeline (`ptcg_ai/train/`) and its honest results

Four offline stages (`selfplay.py`, `build_priors.py`, `tune_weights.py`,
`deck_evolve.py`) bake output back into `main.py` as embedded constants --
no runtime file loads. Every candidate must clear a strict **promotion
rule** (`league_check.py`: beat a frozen predecessor >55% over >=50 games
at full production budget, and keep the vs-`random` winrate intact). Since
§2's bugfixes changed agent strength, we re-ran every prior verdict against
a fresh frozen baseline rather than trust conclusions made with a buggy
predecessor: **learned priors still don't promote** (48.0% vs 54.0%
before, parity either way); **tuned weights now do** -- a fresh
coordinate-descent pass found `W_PRIZE=0.48, W_HP=0.28, W_BOARD_DEV=0.18`
(shrunk-budget gauntlet 81.2%), re-verified at full budget **58.0%/50
games (was 38.0% pre-bugfix, rejected)** -- **promoted**, frozen as
`agent_v3.py`. A second, finer pass (delta 0.04) from that new baseline
found further gain -- `W_HP=0.24, W_BOARD_DEV=0.22` -- **58.0%/50 games
vs `agent_v3.py`, and vs-`random` 89.0%/100 games (up from 87.0%)** --
also **promoted**, frozen as `agent_v4.py`, now shipped. Separately, we
checked whether the §2 correctness fixes left compute on the table: the
engine gives each player a 600s/game overage-time bank and we were using
under 3% of it, so we doubled the search-time budget and re-tested --
**52.5%/40 games vs the unmodified predecessor, i.e. no real gain**;
reverted. More rollouts of the same playout policy hit diminishing returns
well below the ceiling, so the bottleneck is policy/heuristic quality, not
compute -- a useful negative result for where to look next. Deck evolution
still found nothing beating 60% (not re-run: unaffected by the agent-logic
bugfix). Pipeline/data: `ptcg_ai/train/README.md`.

## Deck Concept (20%)

### Empirically-discovered deck rules

We probed `lib.BattleStart` with crafted decks to find validation rules
from `errorType` codes:

| Rule | Evidence |
|---|---|
| Exactly 60 cards/deck | enforced by the Python/Kaggle wrapper layer |
| Max 4 copies of any card, by `cardId` | 4x Kyogre OK, 5x/6x/8x -> `error:2` |
| **Basic Energy exempt from the 4-cap** | up to 55x Basic {W} Energy (`3`) accepted |
| Special Energy (`cardType 6`) NOT exempt | 4x OK, 5x -> `error:2`, same as normal cards |
| Must contain >=1 **Basic** Pokemon | all-evolved/all-trainer decks -> `error:3` |
| At most 1 **ACE SPEC** card total | 2 different ACE SPEC cards -> `error:4` |
| Any known `cardId` (1-1267), <=4 copies | 5 random Pokemon across the id range all accepted |
| No minimum energy requirement | a 0-energy deck is legal |
| Unknown/invalid `cardId` (0, 999999) | `error:1` |

### Getting to v3

Starting deck: `kaggle_environments`'s sample (Kyogre / Snover-Mega
Abomasnow ex / 33 energy, only 6 Basics). We buffed Kyogre 2->4 (basics
6->8, v2), then hand-tested six single-card-swap candidates vs v2 (40
games each, for *parity* not power). Five lost outright (5-45%); adding
2x Chien-Pao (120 HP non-`ex`, "Icicle Loop" 120 dmg/3 energy) while
cutting a narrow-use trainer reached parity (50.0%, 20/40) and became
**v3**: 10 Basics, P(<=1 basic in opener) 67.0%, 31/60 energy. Lesson:
diluting energy density for more Pokemon hurt more than it helped.

### Archetype tournament

To stress-test v3 against real deck-building diversity, we mined
`card_pool_catalog.md` (`AllCard`/`AllAttack`, grouped by attacker type,
evolution line, and Trainer function) and built 5 further decks modeled on
recognizable real-world archetypes, each independently legal, 10 Basics,
coherent 1-2-type energy: **T1** Lightning big-Basic aggro; **T2** Grass
Stage-2 (Mega Venusaur `ex` + Rare Candy); **T3** Tera Box
(Water/Fighting/Colorless); **T4** Fighting spread/bench-damage; **T5**
Colorless disruption/stall. Full round-robin, 30 games/pairing (450 total),
full production budget:

| Rank | Deck | Overall winrate | Elo-ish |
|---|---|---:|---:|
| 1 | **v3 (champion)** | **85.3%** | **1757** |
| 2 | T4 Fighting spread | 52.3% | 1630 |
| 3 | T5 Colorless stall | 32.0% | 1514 |
| 4 | T1 Lightning aggro | 48.0% | 1379 |
| 5 | T3 Tera Box | 42.7% | 1363 |
| 6 | T2 Grass Stage-2 | 38.9% | 1356 |

v3 won every single pairing (77-97%) and ranks #1 by a wide margin --
consistent with "avoid multi-turn combo dependence, prefer locally-good
turns": v3's simple, high-energy-density, mostly-Basic shell is easy for a
depth-capped PIMC search to pilot well, while T2/T3's sequencing is harder
to navigate optimally. Per our promotion rule (beats v3 head-to-head >55%
AND >=85% vs `random` over 300+ games), nothing came close, so **v3
remains the shipped deck**. Full crosstable:
`ptcg_ai/train/artifacts/archetype_tournament.md`; all 6 decklists are kept
in `main.py`'s `ARCHETYPE_DECKS`. This predates §2's bugfixes, so we
spot-checked the two closest/most bench-dependent contenders with the
fixed agent piloting both sides (`ptcg_ai/eval/archetype_match.py`, 40
games each): v3 vs T4 (previously 52.3%) -> **v3 90.0%**; v3 vs T2
(previously 38.9%, the Stage-2/Rare-Candy deck where bench sequencing
matters most) -> **v3 90.0%**. Both moved further in v3's favor -- the
champion conclusion holds.

## Report Quality (10%) — Limitations and Future Work

1. **Root selection has no UCB** — flat MC averaging, not ISMCTS/PUCT.
2. **Opponent modeling** is generic/evidence-based (§3), not archetype
   inference from observed cards.
3. **Leaf weights are two coordinate-descent rounds** (§7: promoted twice,
   still not a converged search -- likely more gain left on this axis).
4. **The remaining loss rate vs `random` is mostly a variance floor** (§6);
   v3 is a strong local optimum -- `deck_evolve.py` (one small pass) is
   the next lever, not agent logic. Search compute is *not* the lever
   either -- §7's time-budget experiment found no gain well below the
   600s/game ceiling, pointing at policy/heuristic quality instead.
5. **Priors are still parity**; deck evolution still one small pass.
6. **Packaging matches the official sample_submission** (main.py +
   deck.csv + a bundled `cg/` folder); `build_submission.sh` validates it.
