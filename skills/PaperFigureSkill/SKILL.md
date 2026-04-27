---
name: PaperFigureSkill
description: Create publication-quality figures, plots, and diagrams for academic papers, with a render-view-fix iteration loop for catching visual defects. Use this skill whenever the user is preparing visuals for a paper, thesis, preprint, technical report, or conference submission — including data plots (line, bar, scatter, heatmap, violin, etc. via matplotlib/seaborn), system or architecture diagrams, schematics, model illustrations, ablation comparisons, or any figure intended for inclusion in a written research deliverable. Trigger on phrases like "figure for my paper," "plot for the manuscript," "architecture diagram," "schematic," "make this look publication-ready," "submission-quality figure," "iterate on this figure," "fix this plot," or any time the user references LaTeX, NeurIPS, ICML, ICLR, IEEE, ACM, Nature, Science, or arXiv. Also use when the user wants to fix or upgrade a figure that "looks like default matplotlib," asks for a colorblind-safe / vector / print-ready version, or wants Claude to visually inspect a rendered figure and fix legibility / overlap / legend / clipping issues. Output files should be vector when possible (PDF/SVG) with PNG only as a high-DPI raster fallback (the PNG also serves as the print-size preview for visual iteration).
---

# Paper Figures

Make figures that look like a careful researcher made them, not the matplotlib defaults.

## Quick Reference

| Task | Where to look |
|------|---------------|
| Data plot (line, bar, scatter, heatmap, violin, error bars, multi-panel) | `references/plots.md` |
| System / architecture diagram | `references/diagrams.md` |
| Schematic, model illustration | `references/diagrams.md` |
| Iterating on a rendered figure (view → fix → repeat) | `references/iteration.md` |
| Pre-submission QA | `references/checklist.md` |
| Color choices | `scripts/colors.py` (palettes) + the "Color" section below |

## Setup (every figure starts with this)

The skill ships three small Python modules in `scripts/`. Import them at the top of every figure script:

```python
import sys
sys.path.insert(0, "<absolute-path-to-this-skill>/scripts")

import matplotlib
matplotlib.use("Agg")                   # headless backend; skip if you want a GUI
import pubstyle, colors, export

pubstyle.apply()                        # vector-safe matplotlib defaults
colors.apply_cycle()                    # colorblind-safe categorical cycle
```

For scripts that live *inside* the skill repo (e.g. `examples/`), use a path relative to the file so the script is portable across machines:

```python
from pathlib import Path
SKILL = Path(__file__).resolve().parent.parent     # adjust depth as needed
sys.path.insert(0, str(SKILL / "scripts"))
```

The `examples/` directory holds runnable end-to-end scripts (e.g. `examples/torus.py` for the 3D surface pattern). Use them as templates when building a new figure.

Build the figure normally with matplotlib/seaborn. At the end:

```python
export.save(fig, "fig_results", formats=("pdf", "svg", "png"))
```

This writes `fig_results.{pdf,svg,png}` into `./figures/` (in the current working directory) with embedded fonts, tight bbox, and 300 DPI for the PNG. Override with `export.save(..., outdir="some/path")` — for the Anthropic analysis-tool sandbox, pass `outdir="/mnt/user-data/outputs"`. The vector formats (PDF/SVG) are what goes into the paper; the PNG is for quick previewing and Slack/Docs.

If the user asked for a specific venue style (NeurIPS, IEEE, Nature), pass it: `pubstyle.apply(venue="ieee")`. Default is generic.

For figure size, prefer the helpers — they match standard column widths in inches:

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("single"))   # 3.3 × 2.2 in, single-column
fig, ax = plt.subplots(figsize=pubstyle.figsize("double"))   # 6.8 × 2.6 in, double-column
# Also: "single_tall", "double_tall", "square"
```

## What "Publication-Quality" Means Here

The bar isn't "looks fancy." The bar is **a careful reader at print size will not be confused or annoyed**. That cashes out as:

- **Designed at print size.** A single-column figure is ~3.3 inches wide on the printed page. If the figure is built at 12 inches wide and shrunk down later, the 8pt fonts become 2.2pt and nobody can read the axis labels. Always start from a realistic figure size and judge legibility there.
- **Vector format** (PDF or SVG) for anything with text, lines, or shapes. PNG only for genuinely raster content — photos, microscopy, dense heatmaps where vector files would balloon to tens of MB.
- **Embedded fonts** in PDFs (`pdf.fonttype = 42`, handled by `pubstyle.apply()`). Without this, journals reject the PDF and arXiv silently substitutes fonts.
- **Colorblind-safe palette.** ~8% of men and ~0.5% of women have red-green colorblindness — that's a non-trivial fraction of any paper's audience. Use `colors.categorical()` (Okabe–Ito) for series, `colors.SEQUENTIAL` for ordered data, `colors.DIVERGING` for signed data.
- **Math typeset properly** with mathtext (`$x^2$`) — readable as text in the SVG, embedded vector in the PDF. Not a screenshot.

## Aesthetic Direction

Academic figures have their own distinct failure modes — the default matplotlib look is the giveaway that the author didn't think about it. Aim for the visual register of a careful Nature, NeurIPS, or IEEE figure: clean, minimal, information-dense, no chartjunk.

What that looks like in practice (most of these are handled by `pubstyle.apply()`, but understand the *why*):

- **Top and right spines off** for line/scatter/bar plots. Eye stays on the data, not the frame.
- **Subtle gridlines** (`alpha=0.3`, behind the data) only when they help reading values. Default off.
- **Tick labels short.** "1k, 10k, 100k" beats "1000, 10000, 100000". Use `ax.ticklabel_format` or formatters.
- **Legend inside the plot** when space allows, with no frame. Outside-right is fine but eats space — only do it when overlap is unavoidable.
- **One color per series, not gradients on bars.** Categorical = distinct hues. Sequential = single-hue gradient.
- **Lines 1.0–1.5pt, markers ~4pt** at print size. Visible without dominating.
- **Sans-serif fonts** at 8–10pt for labels, 7–8pt for tick labels. Helvetica/Arial preferred (Nature requires it; others accept it).

## Color

Three categories, three answers:

- **Categorical** (different conditions, methods, classes): `colors.categorical()` — returns Okabe–Ito hex codes. Or just call `colors.apply_cycle()` once and use `plot()` normally.
- **Sequential** (ordered data, e.g. depth, density, time): `cmap="viridis"` or `"cividis"` (cividis is the most colorblind-friendly). Available constants in `colors.SEQUENTIAL`.
- **Diverging** (signed data with meaningful zero, e.g. residuals, correlations, log-fold-change): `cmap="RdBu_r"` or `"coolwarm"`. Available in `colors.DIVERGING`.

Never use `jet`, `rainbow`, `hsv`, or `nipy_spectral`. They're perceptually nonlinear, mis-rank values in grayscale, and look unprofessional in a 2025 paper. (Listed in `colors.AVOID` for reference.)

If the paper might be printed in grayscale, **encode each series in two channels**: color *and* line style, or color *and* marker shape. Color alone is fragile.

## Anti-Patterns (the "default matplotlib" tells)

These scream "no thought given":

- **`jet` / `rainbow` colormaps.** Already covered. The single most common giveaway.
- **3D bar charts, 3D pies, exploded pies.** No paper has ever been improved by these.
- **Default DejaVu Sans at 10pt with all four spines on.** Literally the matplotlib default. `pubstyle.apply()` fixes this.
- **Saving as JPEG.** Compression artifacts on every line and letter. PNG for raster, PDF/SVG for vector. (`export.save()` warns on JPEG.)
- **Drop shadows, gradient fills, beveled bars, 3D effects.** Tufte-defined chartjunk. Information density goes down, ink-to-data ratio goes up.
- **Rasterized text in a vector file.** Defeats the entire point. `pubstyle.apply()` sets `pdf.fonttype = 42` to keep text as text.
- **Tiny fonts only readable at design size.** Designing at 12 inches and shipping at 3.3 inches makes 8pt → 2.2pt. Design at print size from the start.
- **Legend covering data.** Move it, shrink it, or pull it out into its own panel.
- **Color-only encoding for grayscale-printable content.** Add a second channel (line style, marker shape, hatching).
- **`plt.tight_layout()` without `bbox_inches='tight'` on save.** Things get clipped at the edges. `export.save()` handles bbox.
- **Identical-looking lines** when you have 2 conditions ("blue solid" vs "orange solid"). Make them maximally distinct: different line styles too.
- **3D surface shaded by a parametric coordinate.** `LightSource.shade(V, cmap)` on a torus or similar lights from V's gradient — produces flat angular bands that look 2D. Shade by depth (Z) instead, so the lit region matches what a viewer expects from a 3D object. See `references/plots.md` § 3D surface.

## Diagrams (Architecture / Schematic / Model Illustration)

Three reasonable paths, depending on the diagram's character. Read `references/diagrams.md` for code patterns and tradeoffs.

- **matplotlib custom drawing** — best when the diagram should match the visual style of your data figures (same fonts, same palette, same export pipeline). Layout is manual, but you get total control and one consistent look.
- **graphviz** (via the `graphviz` Python package) — best when there are many nodes and auto-layout matters more than exact positioning. Less control over aesthetics but very fast for complex graphs.
- **Hand-authored SVG** — best for one-off polished illustrations where layout is artistic and a layout engine would fight you. Slowest to build, most control.

For ML papers specifically, model architecture diagrams (transformer blocks, U-Nets, etc.) are usually matplotlib + custom drawing or hand-SVG. Graphviz is better for dataflow / pipeline / system diagrams with many components.

## QA Workflow (Render → View → Fix → Repeat)

**Every figure goes through this loop before declaring done.** Don't skip — first renders almost always have at least one user-visible defect (small fonts, legend overlap, tick collision) that's invisible while writing the code.

1. **Render** with `export.save()`. PDF/SVG/PNG come out together.
2. **View the PNG** with the `view` tool. The PNG is rendered at 300 DPI from a figure whose dimensions are the actual print size, so what you see on screen is what a reader sees on paper.
3. **Inspect for defects** using the inspection prompt and defect catalog in `references/iteration.md`. Be specific about which element is wrong and why.
4. **Apply fixes** from the catalog (most common issues — small fonts, legend covering data, ticks colliding, panels too close — have standard fixes that drop straight in).
5. **Re-render and re-view.**
6. **Stop after at most 2 fix cycles**, or sooner if only sub-pixel / cosmetic issues remain.

The stopping rule matters. Figure work has a long tail of nitpicks that don't matter to readers — the bar is "a careful reader is not confused or annoyed", not "every pixel is perfect."

For full inspection prompt, defect catalog, and worked examples → `references/iteration.md`.

For the final pre-submission audit (font embedding, format, etc., separate from visual defects) → `references/checklist.md`.

## When to Reach for a Reference File

- Iterating on a rendered figure (the Render → View → Fix loop) → `references/iteration.md`
- Building a specific plot type → `references/plots.md` (ready-to-adapt patterns)
- Building a system / architecture diagram or schematic → `references/diagrams.md`
- Final pre-submission check → `references/checklist.md`

Each reference file's code snippets already use `pubstyle`, `colors`, and `export` so they drop in directly.
