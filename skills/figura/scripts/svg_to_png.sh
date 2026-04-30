#!/usr/bin/env bash
# Render an SVG to PNG at 300 DPI. Tries available converters in order:
#   rsvg-convert (librsvg)   — best quality, fastest
#   cairosvg     (Python)    — pip install cairosvg (in requirements-extras.txt)
#   inkscape                  — heaviest, but already installed for figure work
#   magick / convert          — ImageMagick fallback (worst quality on text/strokes)
#
# Usage:
#   svg_to_png.sh <input.svg> [output.png]
#
# If output path omitted, writes <input>.png next to the source.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <input.svg> [output.png]" >&2
  exit 1
fi

IN="$1"
OUT="${2:-${IN%.svg}.png}"
DPI="${FIGURA_SVG_DPI:-300}"

if [[ ! -f "$IN" ]]; then
  echo "Input file not found: $IN" >&2
  exit 1
fi

if command -v rsvg-convert >/dev/null 2>&1; then
  # rsvg-convert -d/-p only sets DPI metadata; need -z to scale bitmap.
  # SVG default is 96 DPI, so zoom = target / 96.
  zoom=$(awk -v d="$DPI" 'BEGIN { printf "%.4f", d / 96.0 }')
  rsvg-convert -z "$zoom" -f png -o "$OUT" "$IN"
  echo "rendered via rsvg-convert (zoom=$zoom): $OUT"
  exit 0
fi

if python3 -c "import cairosvg" 2>/dev/null; then
  python3 -c "
import sys, cairosvg
cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], dpi=int(sys.argv[3]))
" "$IN" "$OUT" "$DPI"
  echo "rendered via cairosvg: $OUT"
  exit 0
fi

if command -v inkscape >/dev/null 2>&1; then
  inkscape "$IN" --export-type=png --export-dpi="$DPI" --export-filename="$OUT" >/dev/null
  echo "rendered via inkscape: $OUT"
  exit 0
fi

if command -v magick >/dev/null 2>&1; then
  magick -density "$DPI" "$IN" "$OUT"
  echo "rendered via magick (lower quality on vector text): $OUT"
  exit 0
fi

if command -v convert >/dev/null 2>&1; then
  convert -density "$DPI" "$IN" "$OUT"
  echo "rendered via convert (lower quality on vector text): $OUT"
  exit 0
fi

echo "No SVG → PNG converter found. Install one of:" >&2
echo "  rsvg-convert:  brew install librsvg / apt install librsvg2-bin" >&2
echo "  cairosvg:      pip install cairosvg  (also in requirements-extras.txt)" >&2
echo "  inkscape:      brew install --cask inkscape / apt install inkscape" >&2
echo "  imagemagick:   brew install imagemagick / apt install imagemagick" >&2
exit 1
