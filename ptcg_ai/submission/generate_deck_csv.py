"""Regenerate ptcg_ai/submission/deck.csv from ptcg_ai/agent/main.py's DECK
constant -- the single source of truth -- so the committed deck.csv can
never silently drift from what main.py actually plays.

Parses main.py with ast (does NOT import/exec it, so this has no dependency
on kaggle_environments being installed) to pull out the literal ``DECK =
[...]`` assignment, asserts it's exactly 60 positive ints, and writes it as
60 newline-separated lines (matching the official sample_submission's
deck.csv format exactly: no header, no commas, one card id per line).

Usage:
    python3 ptcg_ai/submission/generate_deck_csv.py
"""
import ast
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAIN_PY = os.path.join(REPO_ROOT, "ptcg_ai", "agent", "main.py")
OUT_CSV = os.path.join(os.path.dirname(__file__), "deck.csv")


def extract_deck(main_py_path):
    with open(main_py_path, "r") as f:
        tree = ast.parse(f.read(), filename=main_py_path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id == "DECK":
                deck = ast.literal_eval(node.value)
                return deck
    raise RuntimeError(f"No top-level `DECK = [...]` assignment found in {main_py_path}")


def main():
    deck = extract_deck(MAIN_PY)
    if len(deck) != 60:
        raise SystemExit(f"DECK has {len(deck)} cards, expected exactly 60")
    if not all(isinstance(c, int) and c > 0 for c in deck):
        raise SystemExit("DECK contains a non-positive-int card id")
    with open(OUT_CSV, "w") as f:
        f.write("\n".join(str(c) for c in deck) + "\n")
    print(f"wrote {OUT_CSV} ({len(deck)} cards, extracted from {MAIN_PY})")


if __name__ == "__main__":
    main()
