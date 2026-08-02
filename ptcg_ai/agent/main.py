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
# Deck constant -- copied verbatim from kaggle_environments' cabt sample deck.
# CLEARLY MARKED SWAP POINT: replace this list with a tuned 60-card deck once
# meta / deckbuilding work is done; the search logic below is deck-agnostic.
# ---------------------------------------------------------------------------

DECK = [
    721, 721, 722, 722, 722, 722, 723, 723, 723, 723,
    1092, 1121, 1121, 1145, 1145, 1163, 1163,
    1219, 1219, 1219, 1219, 1227, 1227, 1227, 1227, 1262, 1262,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
]
assert len(DECK) == 60

# ---------------------------------------------------------------------------
# Tunables (kept as simple module-level constants per spec)
# ---------------------------------------------------------------------------

TARGET_TIME = 0.8          # seconds, soft per-decision budget
HARD_CAP = 1.5              # seconds, absolute per-decision budget
DEPTH_CAP = 60               # max SearchStep applications per playout
CANDIDATE_CAP = 24           # max candidate actions considered per decision
MULTI_RANDOM_COMBOS = 8      # extra random combos tried for multi-select options
MAX_STEP_RETRIES = 3         # retries on an invalid SearchStep during playout
FILLER_CARD_ID = 3           # Basic {W} Energy -- padding for determinization pools

_CTX = None  # lazily-created AgentStart() context, reused across decisions


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

    score = 0.5 * prize_diff + 0.25 * hp_diff + 0.15 * board_diff + 0.10 * hand_diff
    return max(-1.0, min(1.0, score))


def playout_policy(sel):
    """Uniform-random legal action, lightly biased away from "pass" (type 14)
    when other options exist, per spec's cheap-improvement suggestion."""
    n = len(sel.get("option") or [])
    if n == 0:
        return []
    mn = max(sel.get("minCount", 0), 0)
    mx = sel.get("maxCount", mn)
    mx = min(mx, n)
    mn = min(mn, mx)
    k = random.randint(mn, mx) if mx >= mn else mn
    idxs = list(range(n))
    non_pass = [i for i in idxs if sel["option"][i].get("type") != 14]
    pool = non_pass if (non_pass and k <= len(non_pass) and random.random() < 0.85) else idxs
    k = min(k, len(pool))
    if k <= 0:
        return []
    return random.sample(pool, k)


def rollout_score(ctx, obs, first_action, me, deadline):
    """SearchBegin -> apply first_action -> random playout to depth cap or
    terminal -> score. Returns None on any engine failure (caller skips it).
    Always frees the search session via SearchEnd before returning."""
    try:
        j = search_begin(ctx, obs)
        if not j.get("state"):
            return None
        handle = 0
        out = json.loads(
            lib.SearchStep(ctx, handle, arr(first_action), len(first_action)).decode()
        )
        if not out.get("state"):
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


def determinizations_for(num_candidates, remaining):
    """Adaptive determinization count (2-8) based on remaining time budget."""
    if remaining <= 0:
        return 1
    per_candidate = remaining / max(num_candidates, 1)
    if per_candidate > 0.15:
        return 8
    if per_candidate > 0.08:
        return 6
    if per_candidate > 0.04:
        return 4
    if per_candidate > 0.015:
        return 3
    return 2


def compute_deadline(obs, start):
    budget = TARGET_TIME
    overage = obs.get("remainingOverageTime")
    if isinstance(overage, (int, float)):
        if overage < 3:
            budget = 0.1
        elif overage < 8:
            budget = 0.3
        elif overage < 20:
            budget = 0.6
    return start + min(budget, HARD_CAP)


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


def choose_action(ctx, obs, deadline):
    cur = obs["current"]
    me = cur["yourIndex"]
    sel = obs["select"]
    candidates = enumerate_candidates(sel)
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    num_cand = len(candidates)
    best_action = candidates[0]
    best_score = -2.0
    for cand in candidates:
        if time.time() > deadline:
            break
        remaining = deadline - time.time()
        d = determinizations_for(num_cand, remaining)
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
    return best_action


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
        if n == 0:
            return []

        start = time.time()
        deadline = compute_deadline(obs, start)
        candidates = enumerate_candidates(sel)
        if len(candidates) <= 1:
            return candidates[0] if candidates else fallback_pick(sel)

        ctx = _get_ctx()
        action = None
        try:
            action = choose_action(ctx, obs, deadline)
        finally:
            try:
                lib.SearchEnd(ctx)
            except Exception:
                pass

        if action is None:
            action = fallback_pick(sel)
        return action
    except Exception:
        try:
            return fallback_pick(obs.get("select"))
        except Exception:
            return []
