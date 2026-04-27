#!/usr/bin/env bash
# Export every PDF in a directory to PNG at 300 DPI.
#
# Usage:
#   export_png_bundle.sh <input-dir> [output-dir]
#
# Defaults output-dir to <input-dir>. Skips PDFs whose PNG is newer than
# the source. Uses pdftoppm (poppler) — `brew install poppler` or
# `apt install poppler-utils` if missing.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <input-dir> [output-dir]" >&2
  exit 1
fi

IN="$1"
OUT="${2:-$IN}"

if [[ ! -d "$IN" ]]; then
  echo "Input directory not found: $IN" >&2
  exit 1
fi

if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "pdftoppm not found. Install with:" >&2
  echo "  macOS:  brew install poppler" >&2
  echo "  Linux:  apt install poppler-utils" >&2
  exit 1
fi

mkdir -p "$OUT"

count=0
skipped=0
shopt -s nullglob
for pdf in "$IN"/*.pdf; do
  base="$(basename "$pdf" .pdf)"
  png="$OUT/$base.png"

  if [[ -f "$png" && "$png" -nt "$pdf" ]]; then
    skipped=$((skipped + 1))
    continue
  fi

  # pdftoppm writes <prefix>-1.png for single-page PDFs; rename to <prefix>.png.
  tmp_prefix="$OUT/.figura_tmp_$base"
  pdftoppm -r 300 -png "$pdf" "$tmp_prefix"
  if [[ -f "${tmp_prefix}-1.png" ]]; then
    mv "${tmp_prefix}-1.png" "$png"
  elif [[ -f "${tmp_prefix}.png" ]]; then
    mv "${tmp_prefix}.png" "$png"
  else
    echo "warn: no PNG emitted for $pdf" >&2
    continue
  fi
  count=$((count + 1))
  echo "  rendered  $base.png"
done

echo "done: $count rendered, $skipped up-to-date in $OUT"
