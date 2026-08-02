"""Kaggle submission agent for "The Pokemon Company - PTCG AI Battle Challenge"
(Simulation category baseline).

Self-contained: only the Python standard library and ``kaggle_environments`` are
used. No files are read at runtime and no heavy work happens at import time.

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

from kaggle_environments.envs.cabt.cg.sim import lib

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
    ctypes.c_long,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
]
lib.SearchEnd.argtypes = [ctypes.c_void_p]
lib.SearchRelease.argtypes = [ctypes.c_void_p, ctypes.c_long]

# ---------------------------------------------------------------------------
# Deck constant. CLEARLY MARKED SWAP POINT: replace this list with a tuned
# 60-card deck once further meta / deckbuilding work is done; the search
# logic below is deck-agnostic.
#
# v2 change (evidence-driven, see strategy_report.md "Deck Concept"): the
# original kaggle_environments sample deck carries only 6 Basic Pokemon
# (2 Kyogre + 4 Snover) in 60 cards. Diagnostics on 250 games showed 100% of
# our losses ended with ZERO Pokemon in play on our side (the TCG "no
# Pokemon in play" instant loss) -- and with only 6 basics, a 7-card opening
# hand has ~86% probability of holding at most 1 Basic Pokemon
# (hypergeometric: P(0)=45.9%, P(1)=40.1%), leaving no bench insurance if
# that lone Pokemon is knocked out early. We raise Kyogre (a tanky 150 HP
# basic) from 2 to 4 copies (the real-TCG 4-copy cap), dropping 2 Basic
# Energy (33 -> 31, still >50% of the deck) to keep the list at 60. This
# lowers P(<=1 basic in opener) from 86.0% to 76.8% -- a meaningful,
# low-risk consistency improvement with no change to the deck's identity.
# ---------------------------------------------------------------------------

DECK = [
    721, 721, 721, 721, 722, 722, 722, 722, 723, 723, 723, 723,
    1092, 1121, 1121, 1145, 1145, 1163, 1163,
    1219, 1219, 1219, 1219, 1227, 1227, 1227, 1227, 1262, 1262,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
]
assert len(DECK) == 60

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
W_PRIZE = 0.40
W_HP = 0.20
W_BOARD_DEV = 0.10
W_HAND = 0.05
W_PRESENCE = 0.25
PRESENCE_CAP = 3  # Pokemon count beyond which extra copies stop adding safety value

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
    if len(_STATS["history"]) > _HISTORY_LEN:
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


def determinize(cur):
    """Build one random determinization of both players' hidden zones.

    My hidden zones (deck + face-down prizes): sampled from MY known 60-card
    deck (``DECK``) minus everything currently visible of mine -- exact by
    construction since we always submit ``DECK`` as our real deck.

    Opponent hidden zones (deck + face-down prizes + hand): the true opponent
    deck is unknown on Kaggle, so we fall back to a "mirror of our own deck"
    filler pool with any opponent cards we HAVE seen removed from it first.
    This is a placeholder policy; see report for future work (deck inference).
    """
    me = cur["yourIndex"]
    my = cur["players"][me]
    op = cur["players"][1 - me]

    my_template = Counter(DECK)
    for cid in visible_ids(my):
        if my_template[cid] > 0:
            my_template[cid] -= 1
    my_needed_deck = my["deckCount"]
    my_needed_prize = sum(1 for x in my["prize"] if x is None)
    my_pool = _pool_from_counter(my_template, my_needed_deck + my_needed_prize)
    my_deck_cards = my_pool[:my_needed_deck]
    my_prize_cards = my_pool[my_needed_deck:my_needed_deck + my_needed_prize]

    opp_template = Counter(DECK)
    for cid in visible_ids(op):
        if opp_template[cid] > 0:
            opp_template[cid] -= 1
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


def search_begin(ctx, obs):
    cur = obs["current"]
    my_deck, my_prize, opp_deck, opp_prize, opp_hand = determinize(cur)
    sbi = obs["search_begin_input"]
    if isinstance(sbi, str):
        sbi = sbi.encode("ascii")
    r = lib.SearchBegin(
        ctx,
        sbi,
        len(sbi),
        arr(my_deck),
        arr(my_prize),
        arr(opp_deck),
        arr(opp_prize),
        arr(opp_hand),
        arr([]),
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


def playout_policy(sel):
    """Biased-random legal action for playouts. Tiered preference, each tier
    only used when it's non-empty and the pick size k fits it:
      1. attacks (option type 13) -- push the game toward a decision/win.
      2. "play to board" options (type 8 targeting inPlayArea 4, i.e. bench)
         -- covers both benching a new Pokemon and attaching energy to a
         benched one; both develop the board, which loss diagnosis showed
         is the single highest-leverage thing to reward (every observed
         loss ended with us at zero Pokemon in play).
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
    board_dev = [i for i in non_pass if opts[i].get("type") == 8 and opts[i].get("inPlayArea") == 4]

    pool = None
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
    try:
        j = search_begin(ctx, obs)
        if not j.get("state"):
            if DEBUG and _STATS is not None:
                _STATS["search_begin_fail"] += 1
            return None
        handle = 0
        out = json.loads(
            lib.SearchStep(ctx, handle, arr(first_action), len(first_action)).decode()
        )
        if not out.get("state"):
            if DEBUG and _STATS is not None:
                _STATS["search_step_fail"] += 1
            return None
        handle += 1
        st = out["state"]
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
            success = False
            for _ in range(MAX_STEP_RETRIES):
                act = playout_policy(sel)
                out = json.loads(
                    lib.SearchStep(ctx, handle, arr(act), len(act)).decode()
                )
                if out.get("state"):
                    st = out["state"]
                    handle += 1
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
            return list(DECK)

        sel = obs["select"]
        n = len(sel.get("option") or [])
        cur = obs.get("current") or {}
        if DEBUG and cur:
            me_dbg = cur.get("yourIndex")
            if me_dbg is not None:
                mp = cur["players"][me_dbg]
                _debug_board = {
                    "active_n": len(mp.get("active") or []),
                    "bench_n": len(mp.get("bench") or []),
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
