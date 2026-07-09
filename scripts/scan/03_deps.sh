#!/usr/bin/env bash
# =============================================================================
# 03_deps.sh — Class dependency graph via jdeps (bundled with JDK 11)
# Usage:   ./03_deps.sh CLASSES_DIR PKG_PREFIX
# Example: ./03_deps.sh target/classes com.company
# Output:  docs/scan/deps.txt  (input for 06_heatmap.py)
# Multi-module: run once per target/classes; output is appended.
# =============================================================================
set -euo pipefail

CLASSES="${1:?CLASSES_DIR required, e.g. target/classes}"
PKG="${2:?PKG_PREFIX required, e.g. com.company}"
OUT_DIR="${OUT_DIR:-docs/scan}"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/deps.txt"

# -verbose:class : class-level edges
# -e "$PKG.*"    : keep only in-house dependencies (drop JDK/libs)
jdeps -verbose:class -e "${PKG}.*" "$CLASSES" >> "$OUT"

sort -u "$OUT" -o "$OUT"
echo "OK: $OUT ($(grep -c ' -> ' "$OUT" || true) edges)"
