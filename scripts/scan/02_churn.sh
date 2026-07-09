#!/usr/bin/env bash
# =============================================================================
# 02_churn.sh — 2-year code churn: most-changed files = tests that pay off fastest
# Usage:   ./02_churn.sh [SRC_GLOB] [SINCE]     (default: 'src/main/**/*.java', '2 years ago')
# Output:  docs/scan/CHURN.md
# Run from the repo root (requires .git).
# =============================================================================
set -euo pipefail

GLOB="${1:-src/main/**/*.java}"
SINCE="${2:-2 years ago}"
TOP="${TOP:-50}"
OUT_DIR="${OUT_DIR:-docs/scan}"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/CHURN.md"

{
  echo "# CHURN — top $TOP most-changed files (since: $SINCE, generated $(date +%F))"
  echo
  echo "> High churn + money-touching = highest priority in FLOW_BACKLOG.md"
  echo
  echo "| Commits | File |"
  echo "|---|---|"
  # `|| true` guards against SIGPIPE under pipefail when the repo has more than TOP files
  { git log --since="$SINCE" --format= --name-only -- "$GLOB" 2>/dev/null \
    | grep -v '^$' | sort | uniq -c | sort -rg | head -"$TOP" \
    | awk '{printf "| %s | %s |\n", $1, $2}'; } || true
} > "$OUT"

echo "OK: $OUT"
