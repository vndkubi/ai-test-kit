#!/usr/bin/env bash
# =============================================================================
# 03b_deps_from_imports.sh — FALLBACK dependency graph from import statements,
# for when compiled classes are not available (jdeps needs .class files).
#
# APPROXIMATION: misses same-package references and fully-qualified inline uses.
# Prefer 03_deps.sh (jdeps) whenever a build output exists.
#
# Usage:   ./03b_deps_from_imports.sh SRC_DIR PKG_PREFIX
# Example: ./03b_deps_from_imports.sh backend/src/main com.company
# Output:  docs/scan/deps.txt  (same format 06_heatmap.py consumes)
# =============================================================================
set -euo pipefail

SRC="${1:?SRC_DIR required}"
PKG="${2:?PKG_PREFIX required, e.g. com.company}"
OUT_DIR="${OUT_DIR:-docs/scan}"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/deps.txt"

find "$SRC" -name '*.java' | while read -r f; do
  # FQCN of this file: path after /java/ (or /src/) with dots
  fq=$(echo "$f" | sed -E 's#.*/(java|src)/##; s#\.java$##; s#/#.#g')
  awk -v self="$fq" -v pkg="$PKG" '
    /^import[ \t]/ {
      line=$0; sub(/^import[ \t]+/, "", line); st=0
      if (line ~ /^static[ \t]/) { st=1; sub(/^static[ \t]+/, "", line) }
      sub(/;.*/, "", line)
      if (index(line, pkg ".") != 1) next          # in-house imports only
      if (line ~ /\.\*$/) next                     # skip wildcard imports
      if (st) sub(/\.[A-Za-z0-9_$]+$/, "", line)   # static import: drop the member
      print "   " self " -> " line
    }' "$f"
done | sort -u > "$OUT"

echo "OK: $OUT ($(wc -l < "$OUT") edges) — APPROXIMATION from imports; use jdeps when classes exist"
