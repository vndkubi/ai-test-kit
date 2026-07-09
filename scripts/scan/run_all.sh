#!/usr/bin/env bash
# =============================================================================
# run_all.sh — Run the full Phase 0 scan. Idempotent — run monthly in CI, diff output.
#
# Usage:
#   ./scripts/scan/run_all.sh SRC_DIR PKG_PREFIX [CLASSES_DIR...]
#   ./scripts/scan/run_all.sh src/main com.company target/classes module-b/target/classes
#
# Without CLASSES_DIR: jdeps is skipped and the heatmap runs in degraded mode.
# Output: docs/scan/{ENTRYPOINTS,CHURN,STATE_DIMENSIONS,SQL_INVENTORY,HEATMAP}.md
# =============================================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

SRC="${1:?Usage: run_all.sh SRC_DIR PKG_PREFIX [CLASSES_DIR...]}"
PKG="${2:?PKG_PREFIX required, e.g. com.company}"
shift 2 || true
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export OUT_DIR="${OUT_DIR:-docs/scan}"
mkdir -p "$OUT_DIR"

echo "=== Phase 0: mechanical scan (NO AI involved) ==="
bash "$HERE/01_entrypoints.sh" "$SRC"
bash "$HERE/02_churn.sh" || echo "WARN: churn needs a git repo — skipped"
rm -f "$OUT_DIR/deps.txt"
for classes in "$@"; do
  bash "$HERE/03_deps.sh" "$classes" "$PKG"
done
if [ ! -s "$OUT_DIR/deps.txt" ]; then
  echo "No compiled classes provided — falling back to import-based graph (03b, approximation)"
  bash "$HERE/03b_deps_from_imports.sh" "$SRC" "$PKG"
fi
python3 "$HERE/04_sql_inventory.py" "$SRC"
bash "$HERE/05_state_dimensions.sh" "$SRC"
python3 "$HERE/06_heatmap.py"

echo
echo "=== DONE — output in $OUT_DIR/ ==="
echo "Next steps (AI joins the pipeline from here):"
echo "  1. Give HEATMAP.md + ENTRYPOINTS.md to the 'scanner' agent to group & name flows in plain language"
echo "  2. Fill docs/FLOW_BACKLOG.md by priority: money-touching(x3) > churn > incidents > core entities"
echo "  3. Run prompt 01-investigate-flow for the first flow"
