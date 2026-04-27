#!/usr/bin/env bash
# tikz_build.sh — compile a TikZ standalone .tex into PDF + SVG + PNG preview.
#
# Output: <outdir>/<name>.{pdf,svg,png} where <name> is the input basename.
# The PDF is the paper-ready vector. The SVG is for web/figures.
# The PNG is a 300 DPI preview for the render-view-fix loop.
#
# Usage:
#   tikz_build.sh path/to/diagram.tex                # writes to ./figures
#   tikz_build.sh diagram.tex out_dir                # custom outdir
#   tikz_build.sh diagram.tex out_dir 600            # custom DPI for PNG
#
# Requires: pdflatex (or lualatex), pdftoppm. Optional: pdf2svg (for SVG).
# Engine override: TIKZ_ENGINE=lualatex tikz_build.sh diagram.tex

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: $(basename "$0") <file.tex> [outdir=figures] [png_dpi=300]" >&2
  exit 2
fi

TEX_PATH="$1"
OUTDIR="${2:-figures}"
DPI="${3:-300}"
ENGINE="${TIKZ_ENGINE:-pdflatex}"

if [ ! -f "$TEX_PATH" ]; then
  echo "error: $TEX_PATH not found" >&2
  exit 1
fi

if ! command -v "$ENGINE" >/dev/null 2>&1; then
  echo "error: $ENGINE not found on PATH (set TIKZ_ENGINE=lualatex or install TeX Live)" >&2
  exit 1
fi
if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "error: pdftoppm not found (install poppler: brew install poppler / apt install poppler-utils)" >&2
  exit 1
fi

NAME="$(basename "${TEX_PATH%.*}")"
SRC_DIR="$(cd "$(dirname "$TEX_PATH")" && pwd)"
mkdir -p "$OUTDIR"
OUTDIR_ABS="$(cd "$OUTDIR" && pwd)"

# Compile in a scratch dir so .aux/.log don't pollute source tree.
BUILD_DIR="$(mktemp -d -t tikzbuild.XXXXXX)"
trap 'rm -rf "$BUILD_DIR"' EXIT

cp "$TEX_PATH" "$BUILD_DIR/$NAME.tex"

# Compile (twice if labels/refs needed; first pass is usually enough for standalone).
(
  cd "$BUILD_DIR"
  "$ENGINE" -interaction=nonstopmode -halt-on-error "$NAME.tex" >/dev/null 2>&1 || {
    echo "error: $ENGINE failed. Last lines of log:" >&2
    tail -40 "$NAME.log" >&2
    exit 1
  }
)

cp "$BUILD_DIR/$NAME.pdf" "$OUTDIR_ABS/$NAME.pdf"

# PNG preview at requested DPI.
pdftoppm -r "$DPI" -png "$OUTDIR_ABS/$NAME.pdf" "$OUTDIR_ABS/$NAME" >/dev/null
# pdftoppm names single-page output as <name>-1.png; rename to <name>.png.
if [ -f "$OUTDIR_ABS/$NAME-1.png" ]; then
  mv -f "$OUTDIR_ABS/$NAME-1.png" "$OUTDIR_ABS/$NAME.png"
fi

# SVG (optional — only if pdf2svg is installed).
if command -v pdf2svg >/dev/null 2>&1; then
  pdf2svg "$OUTDIR_ABS/$NAME.pdf" "$OUTDIR_ABS/$NAME.svg" >/dev/null
fi

echo "wrote: $OUTDIR_ABS/$NAME.pdf"
[ -f "$OUTDIR_ABS/$NAME.svg" ] && echo "wrote: $OUTDIR_ABS/$NAME.svg"
echo "wrote: $OUTDIR_ABS/$NAME.png  (${DPI} DPI preview)"
