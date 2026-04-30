#!/usr/bin/env bash
# Export every PDF and SVG in a directory to PNG at 300 DPI.
#
# Usage:
#   export_png_bundle.sh <input-dir> [output-dir]
#
# Defaults output-dir to <input-dir>. Skips inputs whose PNG is newer than
# the source. Uses pdftoppm (poppler) for PDFs and svg_to_png.sh (which
# tries rsvg-convert / cairosvg / inkscape / magick) for SVGs.
#
# Install: poppler (`brew install poppler` / `apt install poppler-utils`)
#          for SVG: see svg_to_png.sh for the converter chain.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <input-dir> [output-dir]" >&2
  exit 1
fi

IN="$1"
OUT="${2:-$IN}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -d "$IN" ]]; then
  echo "Input directory not found: $IN" >&2
  exit 1
fi

mkdir -p "$OUT"

count=0
skipped=0
shopt -s nullglob

# --- PDFs via pdftoppm ---
if compgen -G "$IN/*.pdf" > /dev/null; then
  if ! command -v pdftoppm >/dev/null 2>&1; then
    echo "pdftoppm not found, skipping PDFs. Install with:" >&2
    echo "  macOS:  brew install poppler" >&2
    echo "  Linux:  apt install poppler-utils" >&2
  else
    for pdf in "$IN"/*.pdf; do
      base="$(basename "$pdf" .pdf)"
      png="$OUT/$base.png"
      if [[ -f "$png" && "$png" -nt "$pdf" ]]; then
        skipped=$((skipped + 1))
        continue
      fi
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
      echo "  rendered  $base.png  (pdf)"
    done
  fi
fi

# --- SVGs via svg_to_png.sh ---
if compgen -G "$IN/*.svg" > /dev/null; then
  for svg in "$IN"/*.svg; do
    base="$(basename "$svg" .svg)"
    png="$OUT/$base.png"
    if [[ -f "$png" && "$png" -nt "$svg" ]]; then
      skipped=$((skipped + 1))
      continue
    fi
    if bash "$SCRIPT_DIR/svg_to_png.sh" "$svg" "$png" >/dev/null 2>&1; then
      count=$((count + 1))
      echo "  rendered  $base.png  (svg)"
    else
      echo "warn: SVG conversion failed for $svg (run svg_to_png.sh directly to see install hints)" >&2
    fi
  done
fi

echo "done: $count rendered, $skipped up-to-date in $OUT"
