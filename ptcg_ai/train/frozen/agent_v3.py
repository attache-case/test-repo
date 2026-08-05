"""Kaggle submission agent for "The Pokemon Company - PTCG AI Battle Challenge"
(Simulation category baseline).

Self-contained: only the Python standard library and the engine's compiled
``lib`` (loaded below) are used (no ``ptcg_ai`` package-relative imports --
this file is dropped flat into /kaggle_simulations/agent/ with no package
around it). No heavy work happens at import time. The one runtime file
access is optional and defensive: on the first call we look for
``deck.csv`` next to this file (the Kaggle submission bundle convention)
and use it if present and valid, else fall back to the embedded ``DECK``
constant -- see the comment above ``DECK`` for why and
``ptcg_ai/submission/`` for the bundle-building tooling.

Engine import -- dual use, see ptcg_ai/submission/build_submission.sh and
README.md "Submission packaging": the OFFICIAL sample submission bundles a
full ``cg/`` folder (compiled binaries + Python wrapper) as a SIBLING of
main.py and imports it as a plain top-level package (``from cg.api import
...``), rather than relying on anything from a pip-installed
``kaggle_environments`` being importable inside the agent's own runtime --
that's deliberate: the harness process that referees the match is not
guaranteed to be the same process/environment your submitted agent code
runs in, so the agent must carry its own copy of the engine. We follow that
same convention below (try the bundled ``cg`` package first) but keep a
fallback to the pip-installed ``kaggle_environments.envs.cabt.cg`` copy so
this exact file also runs unmodified against the local dev venv (pytest,
smoke_test.py, run_eval.py, etc., none of which have a ``cg/`` folder
sitting next to ptcg_ai/agent/main.py). We use the engine's raw ``lib``
ctypes handle either way (not the official ``cg.api`` dataclass wrapper --
see the "Search API bindings" comment below for why: our own thin
raw-dict/ctypes bindings, cross-verified against ``cg/api.py``, are
lighter-weight for a tight rollout loop that calls SearchStep tens of
thousands of times per game).

Strategy in one line: determinized Monte Carlo search (PIMC) that drives the
official game engine's own ``Search*`` API to roll out candidate actions to a
depth cap (or terminal), scores leaves with a small heuristic, and picks the
action with the best mean score across a few random determinizations of the
hidden zones (opponent hand/deck/prizes and our own undrawn deck/prizes).

IMPORTANT: ``agent`` must remain the LAST top-level function defined in this
file -- kaggle-environments treats the last top-level function as the
submission entrypoint.
"""

import ctypes
import json
import os
import random
import time
from collections import Counter

# NOTE: deliberately no ``__file__`` anywhere in this module (see
# _resolve_submission_deck below for the full explanation): kaggle-
# environments' real agent loader (kaggle_environments/agent.py,
# get_last_callable) compiles+execs a submitted file's source text into a
# fresh namespace WITHOUT binding ``__file__`` -- only ``sys.path`` gets the
# file's directory appended for the duration of that exec call. So a plain
# ``from cg.sim import lib`` already resolves correctly against a bundled
# sibling ``cg/`` package with no manual sys.path work needed (and manual
# sys.path work that reads ``__file__`` would crash at import time). This
# was verified directly: python3 -m py_compile fails silently but
# ``kaggle_environments.make("cabt").run([path, path])`` raised
# ``NameError: name '__file__' is not defined`` the first time this file
# had a module-level ``__file__`` reference; removing it fixed the preflight.
try:
    from cg.sim import lib  # Kaggle submission bundle: cg/ is a sibling of this file
except ImportError:
    from kaggle_environments.envs.cabt.cg.sim import lib  # local dev/eval venv fallback

# ---------------------------------------------------------------------------
# Search API bindings (verified signatures -- see ptcg_ai/report/strategy_report.md)
# ---------------------------------------------------------------------------

lib.AgentStart.restype = ctypes.c_void_p
lib.AgentStart.argtypes = []
lib.SearchBegin.restype = ctypes.c_char_p
lib.SearchBegin.argtypes = (
    [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    + [ctypes.POINTER(ctypes.c_int)] * 6
    + [ctypes.c_int]
)
lib.SearchStep.restype = ctypes.c_char_p
lib.SearchStep.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int64,  # search_id -- c_int64 confirmed against the official
                      # cg/sim.py (byte-identical libcg.so exports this
                      # signature); c_long happens to alias c_int64 on
                      # 64-bit Linux so this was not observably wrong on
                      # Kaggle's runtime, but is fixed here for exactness.
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
]
lib.SearchEnd.argtypes = [ctypes.c_void_p]
lib.SearchRelease.argtypes = [ctypes.c_void_p, ctypes.c_int64]

# ---------------------------------------------------------------------------
# Deck constant. CLEARLY MARKED SWAP POINT: replace this list with a tuned
# 60-card deck once further meta / deckbuilding work is done; the search
# logic below is deck-agnostic.
#
# v2 (evidence-driven, see strategy_report.md "Deck Concept"): the original
# kaggle_environments sample deck carries only 6 Basic Pokemon (2 Kyogre +
# 4 Snover) in 60 cards. Diagnostics showed all losses ended with ZERO
# Pokemon in play (the TCG "no Pokemon in play" instant loss), and with only
# 6 basics a 7-card opening hand has ~86% probability of holding at most 1
# Basic Pokemon. We raised Kyogre 2->4 (the real-TCG 4-copy cap), dropping 2
# Basic Energy (33->31) to keep 60 cards: P(<=1 basic in opener) 86.0%->76.8%.
#
# v3 (this revision): added 2x Chien-Pao (209, non-ex, 120 HP, "Icicle Loop"
# 120 dmg for 2 Water + 1 Colorless -- an efficient, low-retreat-cost, non-
# evolving Water attacker) as a 3rd Basic Pokemon line, cutting Mega Signal
# (1145, a narrow "fetch a Mega Evolution ex" search effect made partly
# redundant by the extra basic) to keep energy at 31 rather than diluting it
# (a lesson from testing several rejected candidates -- see the deck
# evaluation table in strategy_report.md). Basics 8->10, P(<=1 basic in
# opener) 76.8%->67.0%. Validated: 50.0% (20/40) head-to-head vs v2 (parity
# -- the goal here is consistency, not raw power) and 89.7% (269/300) vs
# `random`, both at full production search budget, both clearing this
# project's promotion bars.
# ---------------------------------------------------------------------------

DECK = [
    721, 721, 721, 721, 722, 722, 722, 722, 723, 723, 723, 723, 209, 209,
    1092, 1121, 1121, 1163, 1163,
    1219, 1219, 1219, 1219, 1227, 1227, 1227, 1227, 1262, 1262,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
]
assert len(DECK) == 60

# ---------------------------------------------------------------------------
# deck.csv (Kaggle submission bundle convention). VERIFIED (see
# strategy_report.md / README.md "Kaggle submission" section): the official
# "How to Submit" instructions mention a deck.csv alongside main.py in the
# .tar.gz bundle, but the actual game engine (kaggle_environments' cabt
# package -- grepped exhaustively across every .py file in both 1.32.2 and
# 1.32.3, byte-identical, plus the generic agent/core-loading code) has NO
# csv-reading logic anywhere. cabt was only added to kaggle_environments on
# 2025-08-18, so the "kaggle-environments 1.14.10" version named on the
# submission page cannot be the actual pinned runtime (no 1.14.x release
# contains cabt at all) -- that text is stale/boilerplate, not a real
# constraint to satisfy. The engine's ONLY deck-input mechanism is this
# agent's own return value on the first call (obs["select"] is None).
# deck.csv is therefore purely a bundle-directory convention for a human (or
# some Kaggle-side display/validation layer we can't inspect) to read the
# decklist without opening main.py -- not something the simulation consumes
# directly. We read it defensively anyway, in case Kaggle's harness DOES do
# something with it: if present next to this file and it parses to exactly
# 60 positive integers (one per line, or comma-separated -- see
# _resolve_submission_deck), we submit ITS content; otherwise we fall back
# to the embedded DECK above. ptcg_ai/submission/deck.csv is the committed
# source-of-truth copy and must always match DECK exactly (built/checked by
# ptcg_ai/submission/build_submission.sh).
# ---------------------------------------------------------------------------
_ACTIVE_DECK = None  # set on first agent() call to whichever deck we actually submitted


def _resolve_submission_deck():
    """Return the 60-card deck to submit: deck.csv if present and valid,
    else the embedded DECK constant. Never raises.

    Deliberately does NOT use ``__file__`` to locate deck.csv (unlike an
    earlier version of this function): kaggle-environments' real agent
    loader execs a submitted file's source into a fresh namespace without
    ever binding ``__file__`` (see the comment by the ``cg.sim`` import
    above), so any ``__file__`` reference anywhere in this module crashes
    the whole agent at import time -- confirmed directly, see the import
    comment above and the preflight validation notes in README.md. Instead
    this mirrors the OFFICIAL sample_submission's own ``read_deck_csv()``
    lookup order exactly: try ``deck.csv`` relative to the current working
    directory first, then the documented absolute submission path. Unlike
    the official version (which has no error handling and will crash on a
    missing/malformed file), this stays defensive and falls back to the
    embedded DECK constant on any failure.
    """
    for path in ("deck.csv", "/kaggle_simulations/agent/deck.csv"):
        try:
            with open(path, "r") as f:
                text = f.read()
            tokens = [tok.strip() for tok in text.replace(",", "\n").splitlines()]
            ids = [int(tok) for tok in tokens if tok]
            if len(ids) == 60 and all(i > 0 for i in ids):
                return ids
        except Exception:
            continue
    return list(DECK)

# Basic Pokemon card ids in DECK (bench targets) and "search my deck for a
# Pokemon" trainer ids (Ultra Ball) -- used by playout_policy's board-safety
# rescue bias and bench_basic_override below. Kept alongside DECK as a
# matching swap point: update both together if DECK changes.
BASIC_POKEMON_IDS = {721, 722, 209}
SEARCH_TRAINER_IDS = {1121}

# AreaType values for "my own Active or Bench spot" (official cg/api.py:
# AreaType.ACTIVE=4, AreaType.BENCH=5), used wherever we match an option's
# ``inPlayArea`` field to detect "plays into my own board". Fixed here from
# a prior version that checked only ``== 4``: that silently matched *only*
# the empty-Active-spot case and missed the equally common "Active already
# occupied, this Basic goes to the Bench" case (inPlayArea==5) -- e.g. when
# we have exactly one Pokemon in play (in Active) and hand holds a second
# Basic, the only legal spot for it is the Bench, so the old filter would
# never fire for that specific (and common) rescue scenario.
ONBOARD_INPLAY_AREAS = (4, 5)

# ---------------------------------------------------------------------------
# Archetype tournament (ptcg_ai/train/artifacts/archetype_tournament.md):
# v3 above was round-robin-tested (30 games/pairing, agent piloting both
# sides, full search budget) against 5 further decks built from
# ptcg_ai/train/artifacts/card_pool_catalog.md, modeled on recognizable
# real-world archetypes. v3 won every pairing (77-97%, 85.3% overall,
# clear #1 by Elo) and remains champion/active DECK. The other decklists
# are kept here for reproducibility and future tournaments -- NOT used at
# runtime (DECK above is always what's submitted).
# ---------------------------------------------------------------------------
ARCHETYPE_DECKS = {
    "v3_champion": DECK,
    "t1_lightning_aggro": (  # Big-Basic Aggro: Pikachu ex / Zekrom ex / Tapu Koko ex
        [210] * 4 + [515] * 4 + [329] * 2
        + [1224] * 4 + [1182] * 4 + [1121] * 4 + [1158] * 1 + [1174] * 3 + [1213] * 3
        + [4] * 31
    ),
    "t2_grass_stage2": (  # Stage-2 Powerhouse: Mega Venusaur ex + Rare Candy, basics splash
        [650] * 4 + [651] * 2 + [652] * 3 + [27] * 4 + [178] * 2
        + [1079] * 4 + [1224] * 4 + [1182] * 2 + [1121] * 2 + [1158] * 1 + [1174] * 1
        + [1] * 31
    ),
    "t3_tera_box": (  # Tera Box: Water/Fighting/Colorless ex+tera basics
        [108] * 4 + [117] * 4 + [176] * 2
        + [1224] * 4 + [1182] * 4 + [1121] * 4 + [1158] * 1 + [1174] * 3 + [1213] * 3
        + [3] * 16 + [6] * 15
    ),
    "t4_fighting_spread": (  # Fighting Spread/bench-damage: Stonjourner / Ting-Lu / Terrakion
        [682] * 4 + [41] * 4 + [607] * 2
        + [1224] * 4 + [1182] * 4 + [1121] * 4 + [1158] * 1 + [1174] * 3 + [1213] * 3
        + [6] * 31
    ),
    "t5_colorless_stall": (  # Disruption/Stall: Snorlax / Regigigas / Hop's Snorlax
        [1072] * 4 + [251] * 4 + [304] * 2
        + [1224] * 4 + [1186] * 2 + [1197] * 2 + [1121] * 4 + [1159] * 1 + [1117] * 3 + [1182] * 2
        + [6] * 32
    ),
}
ARCHETYPE_BASIC_IDS = {
    "v3_champion": BASIC_POKEMON_IDS,
    "t1_lightning_aggro": {210, 515, 329},
    "t2_grass_stage2": {650, 27, 178},
    "t3_tera_box": {108, 117, 176},
    "t4_fighting_spread": {682, 41, 607},
    "t5_colorless_stall": {1072, 251, 304},
}

# ---------------------------------------------------------------------------
# Tunables (kept as simple module-level constants per spec)
# ---------------------------------------------------------------------------

TARGET_TIME = 1.2            # seconds, soft per-decision budget
HARD_CAP = 3.0                # seconds, absolute per-decision budget
SETUP_TURN_CUTOFF = 2         # turn <= this: treat as high-leverage "setup" (see below)
SETUP_TARGET_TIME = 2.5       # soft budget for setup-phase decisions (more D, still headroom)
SETUP_HARD_CAP = 4.5          # hard cap for setup-phase decisions
SETUP_MIN_DETERMINIZATIONS = 8  # never go below this many determinizations during setup
DEPTH_CAP = 90                # max SearchStep applications per playout
CANDIDATE_CAP = 24            # max candidate actions considered per decision
MULTI_RANDOM_COMBOS = 8       # extra random combos tried for multi-select options
MAX_STEP_RETRIES = 3          # retries on an invalid SearchStep during playout
FILLER_CARD_ID = 3            # Basic {W} Energy -- padding for determinization pools

# heuristic_eval weights (rebalanced after loss diagnosis -- see report):
# a "board presence" term was added because 100% of observed losses ended
# with zero Pokemon in play on our side; the old weights (prize/hp/board/hand)
# didn't explicitly reward keeping spare Pokemon in reserve.
W_PRIZE = 0.48
W_HP = 0.28
W_BOARD_DEV = 0.18
W_HAND = 0.05
W_PRESENCE = 0.25
PRESENCE_CAP = 3  # Pokemon count beyond which extra copies stop adding safety value

# ---------------------------------------------------------------------------
# Learned action priors (ptcg_ai/train/ pipeline). Keyed by
# "select_type|select_context|option_type" -> empirical win-rate in [0, 1]
# with Laplace smoothing, mined from self-play by
# ptcg_ai/train/build_priors.py (see ptcg_ai/train/README.md to regenerate).
# Embedded as a plain literal so main.py stays self-contained (no runtime
# file loads). Empty/missing keys fall back to PRIOR_DEFAULT (neutral) --
# the tiered heuristics in playout_policy/enumerate_candidates always work
# even with LEARNED_PRIORS = {}, so this is purely an additive refinement.
# ---------------------------------------------------------------------------
PRIOR_DEFAULT = 0.5
PRIOR_BLEND = 0.6  # weight on the learned prior vs. the 0.5 neutral prior
# A 19-key table WAS generated 2026-08-02 by ptcg_ai/train/build_priors.py
# from 250 self-play games (15,653 decisions; see
# ptcg_ai/train/artifacts/action_priors.json and ptcg_ai/train/README.md to
# regenerate/inspect it). Per this project's own promotion rule -- a change
# must beat its immediate predecessor >55% over >=50 games
# (ptcg_ai/train/league_check.py) before shipping -- that table scored only
# 54.0% (27/50) head-to-head against the pre-priors frozen snapshot
# (ptcg_ai/train/frozen/agent_v1.py): statistically indistinguishable from
# parity at this small self-play scale, not a proven improvement. So it is
# NOT activated by default here (LEARNED_PRIORS stays empty); the mined
# table, the pipeline, and this result are kept and documented as a working
# first pass to scale up (more self-play games) rather than a shipped
# behavior change. See strategy_report.md "Model Approach" for the numbers.
LEARNED_PRIORS = {}

_CTX = None  # lazily-created AgentStart() context, reused across decisions

# ---------------------------------------------------------------------------
# Optional debug instrumentation -- OFF by default so the Kaggle submission is
# completely unaffected. Enable by setting the environment variable
# PTCG_DEBUG=1 *before this module is imported* (eval/diagnostic scripts do
# this). When enabled, `get_debug_stats()` exposes counters for fallback
# usage and engine call failures, plus a ring buffer of the last dozen real
# decisions, so a diagnostic harness can dump "why did we lose this game"
# context for lost/drawn games.
# ---------------------------------------------------------------------------

DEBUG = os.environ.get("PTCG_DEBUG") == "1"
# Opt-in, only meaningful with DEBUG on: keep the FULL per-game decision
# history instead of trimming to the last dozen. Used by
# ptcg_ai/train/selfplay.py to collect complete per-decision training
# records; diagnostic tooling (loss dumps) keeps the bounded ring buffer.
FULL_HISTORY = os.environ.get("PTCG_FULL_HISTORY") == "1"
_HISTORY_LEN = 12


def _new_stats():
    return {
        "decisions": 0,
        "fallback_decisions": 0,
        "search_begin_fail": 0,
        "search_step_fail": 0,
        "rollout_ok": 0,
        "rollout_fail": 0,
        "history": [],
    }


_STATS = _new_stats() if DEBUG else None


def reset_debug_stats():
    """Reset the module-level debug counters/history. No-op unless
    PTCG_DEBUG=1 was set before import. Call this before each game when
    looping env.run() in one process, so stats don't bleed across games."""
    global _STATS
    if DEBUG:
        _STATS = _new_stats()


def get_debug_stats():
    """Return the live debug stats dict, or None if PTCG_DEBUG is not set."""
    return _STATS


def _debug_note(**entry):
    if not DEBUG or _STATS is None:
        return
    _STATS["decisions"] += 1
    _STATS["history"].append(entry)
    if not FULL_HISTORY and len(_STATS["history"]) > _HISTORY_LEN:
        del _STATS["history"][0]


def arr(lst):
    """ctypes int array helper (never zero-length, per verified working pattern)."""
    return (ctypes.c_int * max(len(lst), 1))(*(lst or [0]))


def visible_ids(player):
    """All card ids we can currently see in a player's zones (hand/board/discard/
    face-up prizes). Used to subtract from the 60-card deck multiset when building
    the determinization pool for that player's hidden zones."""
    ids = [c["id"] for c in (player.get("hand") or [])]
    for zone in ("active", "bench"):
        for mon in player.get(zone) or []:
            ids.append(mon["id"])
            ids += [e["id"] for e in (mon.get("energyCards") or [])]
            ids += [(t["id"] if isinstance(t, dict) else t) for t in (mon.get("tools") or [])]
            ids += [
                (q["id"] if isinstance(q, dict) else q)
                for q in (mon.get("preEvolution") or [])
            ]
    ids += [c["id"] for c in (player.get("discard") or [])]
    ids += [c["id"] for c in (player.get("prize") or []) if c]
    return ids


def _pool_from_counter(counter, needed, filler=FILLER_CARD_ID):
    pool = [cid for cid, n in counter.items() for _ in range(n)]
    random.shuffle(pool)
    if len(pool) < needed:
        pool = pool + [filler] * (needed - len(pool))
    return pool[:needed]


BASIC_ENERGY_IDS = set(range(1, 9))  # cardIds 1-8: one Basic Energy per type
# A small set of broadly-common, deck-agnostic staple trainers (Ultra Ball,
# Boss's Orders, Cheren-style draw, Judge-style hand disruption, Switch) used
# ONLY to pad the opponent's unseen-card pool -- see _opp_generic_template.
GENERIC_STAPLE_TRAINER_IDS = [1121, 1182, 1224, 1213, 1123]
# A few generic Basic Pokemon spread across different types, included ONLY
# as a legality floor: the engine requires every deck to contain >=1 Basic
# Pokemon, so before we've observed any of the opponent's board (e.g. turn
# 0) the template needs *some* Pokemon in it or SearchBegin's determinized
# opponent "deck" fails validation. This is not a guess at their actual
# deck -- just enough variety that the simulated opponent can legally have
# something to play.
NEUTRAL_BASIC_MON_IDS = [721, 682, 210, 1072]


def _infer_opp_energy_id(op):
    """Infer a plausible Basic Energy id for the opponent's deck from
    directly-observed evidence (energy actually attached to their Pokemon,
    or in their discard pile) -- never guessed from our own deck. Falls
    back to a neutral default (Basic {W} Energy) when nothing's been
    observed yet (e.g. turn 0)."""
    seen = Counter()
    for zone in ("active", "bench"):
        for mon in op.get(zone) or []:
            for e in mon.get("energyCards") or []:
                cid = e.get("id") if isinstance(e, dict) else e
                if cid in BASIC_ENERGY_IDS:
                    seen[cid] += 1
    for c in op.get("discard") or []:
        cid = c.get("id") if isinstance(c, dict) else c
        if cid in BASIC_ENERGY_IDS:
            seen[cid] += 1
    if seen:
        return seen.most_common(1)[0][0]
    return FILLER_CARD_ID


def _opp_generic_template(op):
    """Deck-agnostic Counter template for the opponent's unseen cards.

    IMPORTANT: this must NEVER assume the opponent is playing our own
    ``DECK`` -- with multiple archetypes in play (see
    ptcg_ai/train/artifacts/archetype_tournament.md) that assumption is
    actively wrong, not just an approximation. Built purely from evidence
    plus generic, deck-agnostic priors: (a) cardIds we've actually observed
    of theirs, assumed to have ~2 more hidden copies (real decks commonly
    run multiples of a card they've already shown); (b) a small set of
    broadly-common staple trainers; (c) a handful of generic Basic Pokemon
    across different types (a legality floor -- an all-trainer/energy
    template would violate the engine's ">=1 Basic Pokemon per deck" rule
    before we've observed any of their board); (d) heavy weighting on Basic
    Energy of whichever type we've directly observed them using (or a
    neutral default if nothing's been observed). ``_pool_from_counter`` pads
    any shortfall with more filler energy, so this template never needs to
    sum to exactly the required count.
    """
    template = Counter()
    for cid in NEUTRAL_BASIC_MON_IDS:
        template[cid] += 3
    for cid in visible_ids(op):
        if cid not in BASIC_ENERGY_IDS:
            template[cid] += 2
    for cid in GENERIC_STAPLE_TRAINER_IDS:
        template[cid] += 4
    template[_infer_opp_energy_id(op)] += 40
    return template


def determinize(cur):
    """Build one random determinization of both players' hidden zones.

    My hidden zones (deck + face-down prizes): sampled from MY known 60-card
    deck (``DECK``) minus everything currently visible of mine -- exact by
    construction since we always submit ``DECK`` as our real deck.

    Opponent hidden zones (deck + face-down prizes + hand): the true
    opponent deck is unknown on Kaggle (and, in local tournaments, may be a
    completely different archetype from ours), so we build a deck-agnostic
    generic template (``_opp_generic_template``) from observed evidence
    instead of assuming they mirror our own deck.
    """
    me = cur["yourIndex"]
    my = cur["players"][me]
    op = cur["players"][1 - me]

    my_template = Counter(_ACTIVE_DECK if _ACTIVE_DECK is not None else DECK)
    for cid in visible_ids(my):
        if my_template[cid] > 0:
            my_template[cid] -= 1
    my_needed_deck = my["deckCount"]
    my_needed_prize = sum(1 for x in my["prize"] if x is None)
    my_pool = _pool_from_counter(my_template, my_needed_deck + my_needed_prize)
    my_deck_cards = my_pool[:my_needed_deck]
    my_prize_cards = my_pool[my_needed_deck:my_needed_deck + my_needed_prize]

    opp_template = _opp_generic_template(op)
    opp_needed_deck = op["deckCount"]
    opp_needed_prize = sum(1 for x in op["prize"] if x is None)
    opp_needed_hand = op["handCount"]
    opp_pool = _pool_from_counter(
        opp_template, opp_needed_deck + opp_needed_prize + opp_needed_hand
    )
    opp_deck_cards = opp_pool[:opp_needed_deck]
    opp_prize_cards = opp_pool[opp_needed_deck:opp_needed_deck + opp_needed_prize]
    opp_hand_cards = opp_pool[
        opp_needed_deck + opp_needed_prize:
        opp_needed_deck + opp_needed_prize + opp_needed_hand
    ]

    return my_deck_cards, my_prize_cards, opp_deck_cards, opp_prize_cards, opp_hand_cards


def _guess_opponent_active_id(op):
    """Guess a plausible Pokemon card id for SearchBegin's 6th array arg
    (``opponent_active``), which the official cg/api.py confirms is REQUIRED
    -- and raises ValueError without it -- whenever the opponent's Active
    Pokemon is face-down (``players[i].active == [None]`` per the official
    PlayerState/Pokemon dataclasses; our raw JSON uses the same ``None``
    convention). We previously always passed an empty array here, which is
    only valid when the opponent's active is either absent or face-up.

    Prefers a Pokemon id actually observed of theirs (e.g. still visible on
    their bench) since that's evidence of what's in their deck; falls back
    to a generic neutral Basic id otherwise. The exact guess only seeds our
    own simulated opponent for rollouts -- it has no effect on the real
    hidden game state -- so any legal Basic/evolution id is safe, precision
    just improves rollout realism."""
    seen = Counter()
    for mon in op.get("bench") or []:
        cid = mon.get("id") if isinstance(mon, dict) else mon
        if cid:
            seen[cid] += 1
    if seen:
        return seen.most_common(1)[0][0]
    return NEUTRAL_BASIC_MON_IDS[0]


def search_begin(ctx, obs):
    cur = obs["current"]
    me = cur["yourIndex"]
    op = cur["players"][1 - me]
    my_deck, my_prize, opp_deck, opp_prize, opp_hand = determinize(cur)
    sbi = obs["search_begin_input"]
    if isinstance(sbi, str):
        sbi = sbi.encode("ascii")
    opp_active_zone = op.get("active") or []
    if len(opp_active_zone) == 1 and opp_active_zone[0] is None:
        # Face-down opponent Active: opponent_active is required (raises
        # otherwise per the official search_begin contract).
        opponent_active = [_guess_opponent_active_id(op)]
    else:
        opponent_active = []
    r = lib.SearchBegin(
        ctx,
        sbi,
        len(sbi),
        arr(my_deck),
        arr(my_prize),
        arr(opp_deck),
        arr(opp_prize),
        arr(opp_hand),
        arr(opponent_active),
        0,
    )
    return json.loads(r.decode())


def heuristic_eval(obs, me):
    """Cheap non-terminal leaf evaluation in [-1, 1] from MY perspective."""
    cur = obs["current"]
    my = cur["players"][me]
    op = cur["players"][1 - me]

    my_prizes_taken = 6 - len(my["prize"])
    op_prizes_taken = 6 - len(op["prize"])
    prize_diff = (my_prizes_taken - op_prizes_taken) / 6.0

    def hp_removed_fraction(mons):
        total = 0.0
        for m in mons:
            max_hp = m.get("maxHp")
            if max_hp:
                total += (max_hp - m.get("hp", max_hp)) / max_hp
        return total

    my_dmg = hp_removed_fraction(my["active"] + my["bench"])
    op_dmg = hp_removed_fraction(op["active"] + op["bench"])
    hp_diff = (op_dmg - my_dmg) / 6.0

    def board_dev(p):
        energy = sum(len(m.get("energies") or []) for m in p["active"] + p["bench"])
        return energy + len(p["bench"])

    board_diff = (board_dev(my) - board_dev(op)) / 10.0
    hand_diff = (my["handCount"] - op["handCount"]) / 10.0

    # Board presence / "don't get swept" term: reward having Pokemon in play
    # up to a small cap, independent of HP or energy. This exists specifically
    # because the terminal "no Pokemon in play" loss is instant and total --
    # diagnosis showed every observed loss ended with our side at 0 Pokemon
    # in play, so keeping a spare on the bench needs to be valuable even at a
    # shallow, depth-capped leaf where the eventual KO hasn't happened yet.
    def presence(p):
        return min(len(p["active"]) + len(p["bench"]), PRESENCE_CAP) / PRESENCE_CAP

    presence_diff = presence(my) - presence(op)

    score = (
        W_PRIZE * prize_diff
        + W_HP * hp_diff
        + W_BOARD_DEV * board_diff
        + W_HAND * hand_diff
        + W_PRESENCE * presence_diff
    )
    return max(-1.0, min(1.0, score))


def _prior_score(sel_type, sel_context, opt_type):
    """Learned-prior win-rate estimate for picking an option of this shape,
    blended toward neutral (0.5) by PRIOR_BLEND. Returns PRIOR_DEFAULT
    whenever LEARNED_PRIORS is empty or the key is unseen -- a pure no-op
    until ptcg_ai/train/build_priors.py output is embedded."""
    if not LEARNED_PRIORS:
        return PRIOR_DEFAULT
    p = LEARNED_PRIORS.get(f"{sel_type}|{sel_context}|{opt_type}")
    if p is None:
        return PRIOR_DEFAULT
    return PRIOR_BLEND * p + (1 - PRIOR_BLEND) * PRIOR_DEFAULT


def playout_policy(sel, hand=None, board_thin=False):
    """Biased-random legal action for playouts. Tiered preference, each tier
    only used when it's non-empty and the pick size k fits it:
      0. RESCUE (only when board_thin and hand is our own, i.e. this decision
         is genuinely ours within the rollout): options that play a Basic
         Pokemon from hand (bench it) or a "search my deck for a Pokemon"
         trainer (Ultra Ball) straight from hand. Loss diagnosis showed
         ~93% of losses end with us at zero Pokemon in play after our board
         thinned to <=1 Pokemon; getting a spare into play/hand ASAP is the
         single highest-value action available in that situation.
      1. attacks (option type 13) -- push the game toward a decision/win.
      2. "play to board" options (type 8 targeting my own Active or Bench,
         inPlayArea in {4, 5} per the official AreaType enum) -- covers
         attaching energy/tools to either an active or benched Pokemon,
         which develops the board.
      3. any other non-pass (type != 14) option.
      4. pass (type 14), only if nothing else fits.
    """
    n = len(sel.get("option") or [])
    if n == 0:
        return []
    mn = max(sel.get("minCount", 0), 0)
    mx = sel.get("maxCount", mn)
    mx = min(mx, n)
    mn = min(mn, mx)
    k = random.randint(mn, mx) if mx >= mn else mn
    idxs = list(range(n))
    opts = sel["option"]
    non_pass = [i for i in idxs if opts[i].get("type") != 14]
    attacks = [i for i in non_pass if opts[i].get("type") == 13]
    board_dev = [
        i for i in non_pass
        if opts[i].get("type") == 8 and opts[i].get("inPlayArea") in ONBOARD_INPLAY_AREAS
    ]

    pool = None
    if board_thin and hand:
        rescue = []
        for i in non_pass:
            o = opts[i]
            # shape-based match (area==2 "from hand"), not a specific type
            # code, since the engine uses different type codes for this
            # play in different contexts (e.g. setup vs a normal turn) --
            # see bench_basic_override's docstring for the same reasoning.
            if o.get("area") == 2:
                hidx = o.get("index")
                if hidx is not None and 0 <= hidx < len(hand):
                    cid = hand[hidx].get("id")
                    if cid in BASIC_POKEMON_IDS or cid in SEARCH_TRAINER_IDS:
                        rescue.append(i)
        if rescue and k <= len(rescue) and random.random() < 0.95:
            pool = rescue

    if pool is None:
        if attacks and k <= len(attacks) and random.random() < 0.55:
            pool = attacks
        elif board_dev and k <= len(board_dev) and random.random() < 0.55:
            pool = board_dev
        elif non_pass and k <= len(non_pass) and random.random() < 0.85:
            pool = non_pass
        else:
            pool = idxs

    k = min(k, len(pool))
    if k <= 0:
        return []
    if k == 1 and len(pool) > 1 and LEARNED_PRIORS:
        sel_type, sel_context = sel.get("type"), sel.get("context")
        weights = [max(_prior_score(sel_type, sel_context, opts[i].get("type")), 0.01) for i in pool]
        return [random.choices(pool, weights=weights, k=1)[0]]
    return random.sample(pool, k)


def rollout_score(ctx, obs, first_action, me, deadline):
    """SearchBegin -> apply first_action -> random playout to depth cap or
    terminal -> score. Returns None on any engine failure (caller skips it).
    Always frees the search session via SearchEnd before returning."""
    s = _rollout_score_impl(ctx, obs, first_action, me, deadline)
    if DEBUG and _STATS is not None:
        _STATS["rollout_ok" if s is not None else "rollout_fail"] += 1
    return s


def _rollout_score_impl(ctx, obs, first_action, me, deadline):
    """Note on search_id: the official cg/api.py contract is that SearchStep's
    search_id argument must be the authoritative ``searchId`` field echoed
    back in the prior response's ``state`` (``SearchState.searchId``), not a
    value the caller invents. We read it from ``state["searchId"]`` on every
    step below rather than hand-incrementing a local counter -- on a single
    linear chain of steps within one rollout (which is what happens here:
    begin, then one SearchStep per decision until terminal/depth-cap) a
    same-session incrementing counter starting at 0 might happen to coincide
    with the engine's own ids, but that's an unverified assumption this
    removes entirely by always trusting the response."""
    try:
        j = search_begin(ctx, obs)
        if not j.get("state"):
            if DEBUG and _STATS is not None:
                _STATS["search_begin_fail"] += 1
            return None
        handle = j["state"]["searchId"]
        out = json.loads(
            lib.SearchStep(ctx, handle, arr(first_action), len(first_action)).decode()
        )
        if not out.get("state"):
            if DEBUG and _STATS is not None:
                _STATS["search_step_fail"] += 1
            return None
        st = out["state"]
        handle = st["searchId"]
        steps = 0
        while True:
            o = st["observation"]
            result = o["current"]["result"]
            if result >= 0:
                if result == me:
                    return 1.0
                if result == 2:
                    return 0.0
                return -1.0
            if steps >= DEPTH_CAP or time.time() > deadline:
                return heuristic_eval(o, me)
            sel = o["select"]
            cur_o = o["current"]
            hand = None
            board_thin = False
            if cur_o.get("yourIndex") == me:
                me_p = cur_o["players"][me]
                hand = me_p.get("hand")
                board_thin = (len(me_p.get("active") or []) + len(me_p.get("bench") or [])) <= 1
            success = False
            for _ in range(MAX_STEP_RETRIES):
                act = playout_policy(sel, hand=hand, board_thin=board_thin)
                out = json.loads(
                    lib.SearchStep(ctx, handle, arr(act), len(act)).decode()
                )
                if out.get("state"):
                    st = out["state"]
                    handle = st["searchId"]
                    success = True
                    break
                elif DEBUG and _STATS is not None:
                    _STATS["search_step_fail"] += 1
            if not success:
                return heuristic_eval(o, me)
            steps += 1
    except Exception:
        return None
    finally:
        try:
            lib.SearchEnd(ctx)
        except Exception:
            pass


def enumerate_candidates(sel):
    """Candidate action list per the spec's enumeration rules, capped and
    deduplicated. Always returns at least one candidate for a non-empty
    option list (or [[]] when maxCount == 0)."""
    n = len(sel.get("option") or [])
    mn = max(sel.get("minCount", 0), 0)
    mx = sel.get("maxCount", mn)
    mx = min(mx, n) if n else 0
    mn = min(mn, mx)

    cands = []
    seen = set()

    def add(c):
        t = tuple(sorted(c))
        if t not in seen:
            seen.add(t)
            cands.append(list(c))

    if n == 0 or mx == 0:
        add([])
        return cands

    if mx == 1:
        if mn == 0:
            add([])
        for i in range(n):
            add([i])
    else:
        add(list(range(min(mx, n))))  # "first k" combo
        tries = 0
        while len(cands) < 1 + MULTI_RANDOM_COMBOS and tries < MULTI_RANDOM_COMBOS * 4:
            tries += 1
            k = random.randint(mn, mx) if mx >= mn else mn
            k = min(k, n)
            combo = random.sample(range(n), k) if k > 0 else []
            add(combo)

    if len(cands) > CANDIDATE_CAP:
        head = cands[0]
        rest = cands[1:]
        if LEARNED_PRIORS:
            sel_type, sel_context = sel.get("type"), sel.get("context")
            opts = sel["option"]

            def _cand_prior(c):
                if len(c) == 1:
                    return _prior_score(sel_type, sel_context, opts[c[0]].get("type"))
                return PRIOR_DEFAULT

            rest.sort(key=_cand_prior, reverse=True)
        else:
            random.shuffle(rest)
        cands = [head] + rest[: CANDIDATE_CAP - 1]

    return cands


def determinizations_for(num_candidates, remaining, min_d=2):
    """Adaptive determinization count based on remaining time budget, with a
    caller-supplied floor (used to force extra rollouts for high-leverage
    low-turn "setup" decisions -- see is_setup_turn())."""
    if remaining <= 0:
        return max(1, min_d)
    per_candidate = remaining / max(num_candidates, 1)
    if per_candidate > 0.15:
        d = 8
    elif per_candidate > 0.08:
        d = 6
    elif per_candidate > 0.04:
        d = 4
    elif per_candidate > 0.015:
        d = 3
    else:
        d = 2
    return max(d, min_d)


def is_setup_turn(cur):
    """Turn 0-SETUP_TURN_CUTOFF decisions (initial active/bench placement and
    the first couple of real turns) are the highest-leverage decisions in the
    game: loss diagnosis showed 100% of observed losses ended with us at
    zero Pokemon in play, and how many Pokemon get benched early is the
    single biggest lever on that outcome. We deliberately spend a
    disproportionate share of the (generous) per-game time budget here."""
    turn = cur.get("turn")
    return isinstance(turn, int) and turn <= SETUP_TURN_CUTOFF


def compute_deadline(obs, start, setup=False):
    budget = SETUP_TARGET_TIME if setup else TARGET_TIME
    hard_cap = SETUP_HARD_CAP if setup else HARD_CAP
    overage = obs.get("remainingOverageTime")
    if isinstance(overage, (int, float)):
        if overage < 3:
            budget = 0.1
        elif overage < 8:
            budget = 0.3 if not setup else 1.0
        elif overage < 20:
            budget = 0.6 if not setup else 1.5
    return start + min(budget, hard_cap)


def fallback_pick(sel):
    """Never-fails heuristic pick used whenever search is skipped or fails:
    first non-pass option (if min/max allow a single pick), else the first
    minCount option indices."""
    if not sel:
        return []
    n = len(sel.get("option") or [])
    if n == 0:
        return []
    mn = max(sel.get("minCount", 0), 0)
    mx = sel.get("maxCount", mn)
    if mn <= 1 <= mx:
        for i in range(n):
            if sel["option"][i].get("type") != 14:
                return [i]
    k = min(max(mn, 0), n)
    return list(range(k))


def _hand_play_option_ids(hand, opts):
    """Map option index -> card id, for every option that plays a specific
    card out of hand (area==2 with a valid hand index). Debug-only; lets
    loss classification tell precisely whether e.g. "play Ultra Ball" was a
    live, offered option that got passed over, rather than just noting the
    card sat somewhere in hand that turn (which doesn't by itself mean it
    was actionable)."""
    if not hand:
        return {}
    out = {}
    for i, o in enumerate(opts):
        if o.get("area") == 2:
            hidx = o.get("index")
            if hidx is not None and 0 <= hidx < len(hand):
                out[i] = hand[hidx].get("id")
    return out


def _benchable_basic_idxs(hand, opts):
    """Option indices that would play a Basic Pokemon from hand into an
    empty Active spot or onto the Bench (same shape-based match as
    bench_basic_override). Used both by the override itself and by debug
    instrumentation, so loss classification can tell whether such an
    opportunity existed on a given decision regardless of whether presence
    was already <=1 at the time."""
    if not hand:
        return []
    idxs = []
    for i, o in enumerate(opts):
        if o.get("area") == 2 and o.get("inPlayArea") in ONBOARD_INPLAY_AREAS:
            hidx = o.get("index")
            if hidx is not None and 0 <= hidx < len(hand):
                cid = hand[hidx].get("id")
                if cid in BASIC_POKEMON_IDS:
                    idxs.append(i)
    return idxs


def bench_basic_override(cur, sel):
    """Deterministic safety override, checked BEFORE search on every real
    decision. Every loss ever observed in diagnosis (100% of an initial
    250-game sample, 93% after Phase 1 fixes) ended with us at zero Pokemon
    in play. If we currently have <=1 Pokemon in play, there is bench room,
    and hand contains a Basic Pokemon playable straight to the bench, taking
    that play is almost never wrong against any opponent and costs zero
    search time -- so we take it unconditionally rather than leaving it to
    a probabilistic search/playout bias. Returns the action (a single-index
    list) or None if the condition doesn't hold (fall through to normal
    search/fallback).

    Matches on shape (area==2 "from hand", inPlayArea in {4, 5} i.e. my own
    Active or Bench per the official AreaType enum, and the underlying hand
    card being a known Basic Pokemon id) rather than a specific option
    "type" code, because the engine uses different type codes for this play
    depending on context (e.g. type 3 during initial setup vs type 8 during
    a normal turn's action menu) -- gating on the card identity instead of
    the type code is robust to both. inPlayArea must cover BOTH zones: an
    empty board offers inPlayArea==4 (into Active), while a lone Pokemon
    already in Active offers inPlayArea==5 for the second Basic (onto
    Bench) -- checking only ==4 (an earlier version's bug, caught by
    cross-referencing the official cg/api.py AreaType enum) silently missed
    that second, equally common case.
    """
    me = cur.get("yourIndex")
    if me is None:
        return None
    players = cur.get("players")
    if not players or me >= len(players):
        return None
    mp = players[me]
    active_n = len(mp.get("active") or [])
    bench_n = len(mp.get("bench") or [])
    bench_max = mp.get("benchMax", 0)
    if active_n + bench_n > 1 or bench_n >= bench_max:
        return None
    hand = mp.get("hand")
    if not hand:
        return None
    mx = sel.get("maxCount", 0)
    mn = sel.get("minCount", 0)
    if mx != 1 or mn > 1:
        return None  # only override plain single-pick selects, never a forced multi-select
    opts = sel.get("option") or []
    for i, o in enumerate(opts):
        if o.get("area") == 2 and o.get("inPlayArea") in ONBOARD_INPLAY_AREAS:
            hidx = o.get("index")
            if hidx is not None and 0 <= hidx < len(hand):
                cid = hand[hidx].get("id")
                if cid in BASIC_POKEMON_IDS:
                    return [i]
    return None


def choose_action(ctx, obs, deadline, min_d=2):
    """Returns (best_action, best_mean_score_or_None). best_action is None
    only when enumerate_candidates() itself returns nothing (never happens
    in practice; see enumerate_candidates). ``min_d`` is a floor on
    determinizations per candidate, raised for setup-phase decisions."""
    cur = obs["current"]
    me = cur["yourIndex"]
    sel = obs["select"]
    candidates = enumerate_candidates(sel)
    if not candidates:
        return None, None
    if len(candidates) == 1:
        return candidates[0], None

    num_cand = len(candidates)
    best_action = candidates[0]
    best_score = -2.0
    any_scored = False
    for cand in candidates:
        if time.time() > deadline:
            break
        remaining = deadline - time.time()
        d = determinizations_for(num_cand, remaining, min_d=min_d)
        total = 0.0
        cnt = 0
        for _ in range(d):
            if time.time() > deadline:
                break
            s = rollout_score(ctx, obs, cand, me, deadline)
            if s is not None:
                total += s
                cnt += 1
        if cnt > 0:
            mean = total / cnt
            if mean > best_score:
                best_score = mean
                best_action = cand
                any_scored = True
    return best_action, (best_score if any_scored else None)


def _get_ctx():
    global _CTX
    if _CTX is None:
        _CTX = lib.AgentStart()
    return _CTX


def agent(obs):
    """Kaggle submission entrypoint. Must never raise and must always return
    a valid list[int] answer to the current select (or the deck on the first
    call)."""
    try:
        if obs.get("select") is None:
            global _ACTIVE_DECK
            _ACTIVE_DECK = _resolve_submission_deck()
            return list(_ACTIVE_DECK)

        sel = obs["select"]
        n = len(sel.get("option") or [])
        cur = obs.get("current") or {}
        if DEBUG and cur:
            me_dbg = cur.get("yourIndex")
            if me_dbg is not None:
                mp = cur["players"][me_dbg]
                hand_dbg = mp.get("hand") or []
                _debug_board = {
                    "active_n": len(mp.get("active") or []),
                    "bench_n": len(mp.get("bench") or []),
                    "bench_max": mp.get("benchMax", 0),
                    "hand_ids": [c.get("id") for c in hand_dbg],
                    "benchable_basic_idxs": _benchable_basic_idxs(hand_dbg, sel.get("option") or []),
                    "hand_play_option_ids": _hand_play_option_ids(hand_dbg, sel.get("option") or []),
                }
            else:
                _debug_board = {}
        else:
            _debug_board = {}
        if n == 0:
            if DEBUG:
                _STATS["fallback_decisions"] += 1
                _debug_note(
                    turn=cur.get("turn"), me=cur.get("yourIndex"),
                    sel_type=sel.get("type"), sel_context=sel.get("context"),
                    n_options=0, n_candidates=0,
                    action=[], fallback=True, best_score=None, reason="no_options",
                    **_debug_board,
                )
            return []

        override_action = bench_basic_override(cur, sel)
        if override_action is not None:
            if DEBUG:
                _debug_note(
                    turn=cur.get("turn"), me=cur.get("yourIndex"),
                    sel_type=sel.get("type"), sel_context=sel.get("context"),
                    option_types=[o.get("type") for o in (sel.get("option") or [])],
                    n_options=n, n_candidates=1,
                    action=override_action, fallback=False, best_score=None,
                    reason="bench_override",
                    **_debug_board,
                )
            return override_action

        start = time.time()
        setup = is_setup_turn(cur)
        deadline = compute_deadline(obs, start, setup=setup)
        candidates = enumerate_candidates(sel)
        if len(candidates) <= 1:
            action = candidates[0] if candidates else fallback_pick(sel)
            if DEBUG:
                fb = not candidates
                if fb:
                    _STATS["fallback_decisions"] += 1
                _debug_note(
                    turn=cur.get("turn"), me=cur.get("yourIndex"),
                    sel_type=sel.get("type"), sel_context=sel.get("context"),
                    option_types=[o.get("type") for o in (sel.get("option") or [])],
                    n_options=n, n_candidates=len(candidates),
                    action=action, fallback=fb, best_score=None, reason="single_candidate",
                    **_debug_board,
                )
            return action

        ctx = _get_ctx()
        action, best_score = None, None
        min_d = SETUP_MIN_DETERMINIZATIONS if setup else 2
        try:
            action, best_score = choose_action(ctx, obs, deadline, min_d=min_d)
        finally:
            try:
                lib.SearchEnd(ctx)
            except Exception:
                pass

        used_fallback = action is None
        if action is None:
            action = fallback_pick(sel)

        if DEBUG:
            if used_fallback:
                _STATS["fallback_decisions"] += 1
            _debug_note(
                turn=cur.get("turn"), me=cur.get("yourIndex"),
                sel_type=sel.get("type"), sel_context=sel.get("context"),
                option_types=[o.get("type") for o in (sel.get("option") or [])],
                n_options=n, n_candidates=len(candidates),
                action=action, fallback=used_fallback, best_score=best_score,
                elapsed=round(time.time() - start, 3),
                reason=("fallback" if used_fallback else ("no_rollout" if best_score is None else "search")),
                **_debug_board,
            )
        return action
    except Exception:
        if DEBUG and _STATS is not None:
            _STATS["fallback_decisions"] += 1
        try:
            return fallback_pick(obs.get("select"))
        except Exception:
            return []
