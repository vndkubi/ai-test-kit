#!/usr/bin/env bash
# =============================================================================
# 05_state_dimensions.sh — List every "state dimension" of the domain:
#   enums + fields named status|state|type|level|flag|mode|kind
# Each state dimension = a fixture-variant CANDIDATE (only built when evidence exists).
# Usage:   ./05_state_dimensions.sh [SRC_DIR]
# Output:  docs/scan/STATE_DIMENSIONS.md
# =============================================================================
set -euo pipefail

SRC="${1:-src/main}"
OUT_DIR="${OUT_DIR:-docs/scan}"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/STATE_DIMENSIONS.md"

{
  echo "# STATE DIMENSIONS (generated $(date +%F))"
  echo
  echo "> Enum values / state fields = fixture-variant candidates."
  echo "> RULE: an enum value with NO evidence (validation branch / prod data / external contract)"
  echo "> gets NO fixture — see FIXTURE_BACKLOG.md."
  echo
  echo "## Enum declarations"
  echo
  echo '```'
  grep -rn --include='*.java' -E '^\s*(public\s+)?enum\s+[A-Z]\w*' "$SRC" | sed 's/^[[:space:]]*//' || true
  echo '```'
  echo
  echo "## Enum constants (with file, for tracing)"
  echo
  echo '```'
  # Print enum file contents: constants are usually UPPER_CASE lines near the top
  grep -rln --include='*.java' -E '^\s*(public\s+)?enum\s' "$SRC" | while read -r f; do
    echo "--- $f"
    grep -nE '^\s*[A-Z][A-Z0-9_]+\s*[,;(]' "$f" | head -40 || true
  done
  echo '```'
  echo
  echo "## State-like fields (status/state/type/level/flag/mode/kind)"
  echo
  echo '```'
  grep -rn --include='*.java' -E 'private\s+\w+\s+\w*(status|state|type|level|flag|mode|kind)\w*\s*[;=]' -i "$SRC" \
    | sed 's/^[[:space:]]*//' || true
  echo '```'
} > "$OUT"

echo "OK: $OUT"
