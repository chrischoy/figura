# Pre-Submission Checklist

Run through this before declaring a figure done. Most of these are caught by `pubstyle.apply()` and `export.save()` if you used the standard setup, but verify anyway — a missed item here is something a reviewer or reader will notice.

## Format

- [ ] **Vector format** (PDF or SVG) for any figure with text or lines. PNG only for true raster content (photos, dense heatmaps where vector would be huge).
- [ ] **PDF has fonts embedded** (TrueType, fonttype 42). Verify with `pdffonts fig.pdf` — every font's `emb` column should be `yes` and `type` should be `TrueType` or `CID TrueType`. Type 3 fonts will get rejected by many journals.
- [ ] **No JPEG**. Compression artifacts on text and lines look terrible.
- [ ] **Filename is descriptive** (`fig_training_curves.pdf`, not `Figure_1.pdf` or `output.pdf`). LaTeX `\includegraphics` calls will be cleaner and you'll find the right file faster when revising.

Verify font embedding from a shell:
```bash
pdffonts figures/fig_results.pdf
```

For batch / CI verification across a paper's figures, gate on Type 3 absence:
```bash
for f in figures/*.pdf; do
  n=$(pdffonts "$f" | grep -c -i 'Type 3')
  echo "$f: Type3 count=$n"
done
# Empty grep = pass. Any "Type 3" line = fix needed (usually mathtext.fontset).
```

Reading `pdffonts` output:
- `TrueType` / `CID TrueType` / `Type 1C` / `CID Type 0` with `emb yes` — all good.
- `Type 3` — **fail.** Common cause: `mathtext.fontset='cm'` slipping a Computer Modern math glyph into a PDF whose primary fonts are TrueType. Fix by switching to `'stixsans'` or `'dejavusans'` (both Type 42-safe). `pubstyle.apply()` already does this.

`pdffonts` ships with poppler — `brew install poppler` (macOS) or
`apt install poppler-utils` (Debian/Ubuntu) if it's missing.

## Print-size legibility

- [ ] **View the PNG at the actual print size** (the `view` tool renders it at native resolution). Single-column figures: ~3.3 in wide. Double-column: ~6.8 in. If tick labels or legend text are unreadable here, fonts are too small or the figure is too dense.
- [ ] **Tick labels not overlapping.** Rotate (`rotation=30, ha="right"`) or reduce density (`MaxNLocator(nbins=5)`) if they collide.
- [ ] **Lines and markers visible at print size.** Default `pubstyle` widths (1.25pt lines, 4pt markers) work for most cases; bump if needed.

## Color

- [ ] **Colorblind-safe palette.** Used `colors.categorical()` (Okabe-Ito) or `colors.SEQUENTIAL` / `colors.DIVERGING` for cmaps.
- [ ] **No `jet`, `rainbow`, `hsv`, or `nipy_spectral`.** Quick check:
  ```bash
  grep -nE "cmap=['\"]?(jet|rainbow|hsv|gist_rainbow|nipy_spectral)" your_figure_script.py
  ```
- [ ] **Color is not the only encoding.** If the paper might be printed in grayscale, every series should also have a different line style or marker shape so distinctions survive.
- [ ] **Diverging colormaps centered correctly.** When using `RdBu_r` etc., set `vmin = -vmax` (or use `TwoSlopeNorm`) so zero lands on the colorbar's midpoint.

## Labels and units

- [ ] **Both axes labeled.** No anonymous axes.
- [ ] **Units present** when applicable (`Time (s)`, `Memory (GB)`, `Accuracy (%)`).
- [ ] **Math typeset with mathtext** (`$x^2$`, `$\\sigma$`), not Unicode workarounds or rasterized images. SVG keeps this as text; PDF embeds the glyphs.
- [ ] **Legend placed where it doesn't cover data.** If everywhere is bad, pull it out into its own panel or move outside the axes.
- [ ] **Multi-panel figures have panel labels** ((a), (b), (c) in the corner) referenced by the caption.

## Data integrity

- [ ] **Y-axis starts at zero for bar charts** unless you have a clear reason to truncate (and then say so in the caption). Truncated bar axes mislead.
- [ ] **Error bars defined in the caption** (std? SEM? 95% CI? bootstrap?). The same number can mean very different things.
- [ ] **Sample sizes / n stated** somewhere — caption or legend or panel annotation.
- [ ] **No cherry-picked axis ranges.** Show the full range relevant to the comparison.

## Consistency across the paper

- [ ] **Same palette across all figures.** If Method X is blue in Figure 2, it should be blue in Figure 4. Define the config→color map once at the start of the project and pass it explicitly to every plotting call. For configs that share a hue family across panels (e.g. two blues), distinguish via `linestyle` and `linewidth` — three channels survive grayscale print.
- [ ] **'Ours = blue' is fine when each figure has a different "ours" config.** Reader identifies the headline instantly. Different Python codepaths can share `#0072B2` so long as they don't co-appear in a single panel.
- [ ] **Same fonts across all figures.** `pubstyle.apply()` ensures this for matplotlib-produced figures; check hand-SVG and graphviz outputs match.
- [ ] **Comparable axes use the same scale.** If two panels show accuracy, give them the same y-limits.

## Final spot-check

- [ ] **Open the PDF in a real viewer** (not just the matplotlib preview). Render at 100% and at the print size.
- [ ] **Caption is self-contained.** A reader who only looks at the figure (which is most of them) should understand it from caption + figure alone.
- [ ] **No leftover debug content** — `print()`-style annotations, "TODO", placeholder text, sample data left in.

If the answer to any of these is "I'll fix it in revision", fix it now. Figures are the part of the paper that gets the most attention and the part most readers see first.
