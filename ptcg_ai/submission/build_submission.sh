#!/usr/bin/env bash
# Build the actual Kaggle submission.tar.gz for
# "The Pokemon Company - PTCG AI Battle Challenge".
#
# Real bundle layout (confirmed against the OFFICIAL sample_submission,
# read in full -- NOT just the Kaggle "How to Submit" prose, which turned
# out to describe an incomplete picture): the tarball's top level must
# contain
#   main.py       (the agent -- ptcg_ai/agent/main.py, top-level, not nested)
#   deck.csv      (60 card ids, one per line -- ptcg_ai/submission/deck.csv,
#                  regenerated from main.py's DECK constant by
#                  generate_deck_csv.py so it can never drift)
#   cg/           (the engine's compiled binaries + Python wrapper --
#                  api.py, game.py, sim.py, utils.py, __init__.py, and
#                  libcg.so / libcg-arm64.so / libcg.dylib / cg.dll)
#
# LICENSE COMPLIANCE (see README.md "Submission packaging" section and the
# competition's LicenseRef-PTCG-ABC-Competition-Use-Only license): the cg/
# folder's contents are the official engine, restricted to competition use
# and NOT ours to redistribute or commit. This script therefore copies cg/
# at BUILD TIME ONLY, straight from a local path outside the repo, into a
# gitignored staging directory -- cg/ is never `git add`-ed and the staging
# directory + the final submission.tar.gz are both gitignored.
#
# Source path for cg/: set PTCG_OFFICIAL_DATA_DIR to the directory you
# extracted the official Kaggle competition dataset into (the one containing
# a `sample_submission/.../cg/` subtree somewhere below it). Defaults to
# this project's own scratchpad copy from the session that verified this
# script, purely as a convenience default for re-running it in that same
# environment -- on any other machine you MUST set the env var yourself.
#
# Usage:
#   PTCG_OFFICIAL_DATA_DIR=/path/to/official_data ptcg_ai/submission/build_submission.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUB_DIR="$REPO_ROOT/ptcg_ai/submission"
BUILD_DIR="$SUB_DIR/.build"          # gitignored staging dir, wiped each run
OUT_TAR="$SUB_DIR/submission.tar.gz" # gitignored output

DEFAULT_OFFICIAL_DATA_DIR="/tmp/claude-0/-home-user-test-repo/ea6aef24-9add-5356-acc4-f03b87ef00d7/scratchpad/official_data"
PTCG_OFFICIAL_DATA_DIR="${PTCG_OFFICIAL_DATA_DIR:-$DEFAULT_OFFICIAL_DATA_DIR}"

echo "== 1/6 regenerate deck.csv from main.py's DECK constant (drift check) =="
python3 "$SUB_DIR/generate_deck_csv.py"

echo "== 2/6 locate official cg/ under PTCG_OFFICIAL_DATA_DIR =="
if [ ! -d "$PTCG_OFFICIAL_DATA_DIR" ]; then
    echo "ERROR: PTCG_OFFICIAL_DATA_DIR does not exist: $PTCG_OFFICIAL_DATA_DIR" >&2
    echo "Set it to wherever you extracted the official competition dataset." >&2
    exit 1
fi
CG_SRC="$(find "$PTCG_OFFICIAL_DATA_DIR" -type d -name cg -path '*sample_submission*' | head -n1)"
if [ -z "$CG_SRC" ]; then
    echo "ERROR: no sample_submission/.../cg directory found under $PTCG_OFFICIAL_DATA_DIR" >&2
    exit 1
fi
if [ ! -f "$CG_SRC/api.py" ]; then
    echo "ERROR: $CG_SRC does not look like the official cg/ folder (no api.py)" >&2
    exit 1
fi
echo "cg/ source: $CG_SRC"

echo "== 3/6 stage bundle (gitignored $BUILD_DIR) =="
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp "$REPO_ROOT/ptcg_ai/agent/main.py" "$BUILD_DIR/main.py"
cp "$SUB_DIR/deck.csv" "$BUILD_DIR/deck.csv"
cp -r "$CG_SRC" "$BUILD_DIR/cg"

echo "== 4/6 sanity checks on the staged bundle =="
python3 -c "
import ast, sys
with open('$BUILD_DIR/main.py') as f:
    src = f.read()
tree = ast.parse(src)
top_funcs = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
assert top_funcs, 'no top-level functions found'
assert top_funcs[-1] == 'agent', f'last top-level function must be agent, got {top_funcs[-1]!r}'
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('ptcg_ai'):
        sys.exit('main.py has a forbidden ptcg_ai-relative import: ' + node.module)
print('main.py: agent() is last top-level function, no ptcg_ai-relative imports -- OK')
"
DECK_LINES=$(wc -l < "$BUILD_DIR/deck.csv" | tr -d ' ')
if [ "$DECK_LINES" != "60" ]; then
    echo "ERROR: staged deck.csv has $DECK_LINES lines, expected 60" >&2
    exit 1
fi
echo "deck.csv: 60 lines -- OK"

echo "== 5/6 tar.gz (flat top level, matching the official 'tar -czvf submission.tar.gz *' recipe) =="
rm -f "$OUT_TAR"
( cd "$BUILD_DIR" && tar -czvf "$OUT_TAR" * )

echo "-- tar -tzf (verifying flat top-level structure) --"
tar -tzf "$OUT_TAR"
TOP_ENTRIES=$(tar -tzf "$OUT_TAR" | awk -F/ '{print $1}' | sort -u)
echo "top-level entries: $TOP_ENTRIES"
if ! echo "$TOP_ENTRIES" | grep -qx "main.py"; then
    echo "ERROR: main.py is not at the tar's top level" >&2
    exit 1
fi

echo "== 6/6 size check (limit 197.7 MiB) =="
SIZE_BYTES=$(stat -c%s "$OUT_TAR" 2>/dev/null || stat -f%z "$OUT_TAR")
SIZE_MIB=$(python3 -c "print(f'{$SIZE_BYTES/1024/1024:.2f}')")
echo "submission.tar.gz: ${SIZE_MIB} MiB ($SIZE_BYTES bytes)"
python3 -c "
size_mib = $SIZE_BYTES / 1024 / 1024
limit = 197.7
assert size_mib < limit, f'{size_mib:.2f} MiB exceeds the {limit} MiB limit'
print(f'OK: {size_mib:.2f} MiB < {limit} MiB limit')
"

echo
echo "Built: $OUT_TAR"
echo "Next: validate with the self-vs-self preflight, e.g."
echo "  python3 -c \"from kaggle_environments import make; make('cabt', debug=True).run(['$BUILD_DIR/main.py', '$BUILD_DIR/main.py'])\""
