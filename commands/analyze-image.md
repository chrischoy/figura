---
description: Read-only visual audit of a rendered figure (PNG or PDF). Reports defects categorized by legibility, collision, truncation, encoding, layout — does not modify anything.
argument-hint: <path-to-image-or-pdf>
allowed-tools: ["Read"]
---

Audit the figure at `$ARGUMENTS`. Read-only — do not edit any source files, do not re-render, do not propose patches. The output is a defect report the user can act on.

If `$ARGUMENTS` is empty, ask the user for a path before proceeding. Do not improvise (e.g. globbing `paper/figures/*.png`) — the audit needs an explicit target.

Use the inspection prompt and defect categories from `skills/figura/references/iteration.md` § "Visual Inspection Prompt". Report every issue you can see at the image's native resolution.

**Print-size assumption.** The "on-screen pixels match printed paper" guarantee only holds when the figure was saved at `dpi=300` from a `figsize` matching its target column width (NeurIPS/ICML single ≈ 3.25 in, double ≈ 6.75 in; IEEE single ≈ 3.5 in, double ≈ 7.16 in). If you can read the producing script, sanity-check `figsize`; if not, ask the user what column width the figure targets. A figure built at `figsize=(13, 4.5)` will look fine on screen and tiny in print.

Procedure:

1. Use `Read` on `$ARGUMENTS` to view the image. Both PNG and PDF are supported.
2. Walk through the five defect categories below. For each issue, record:
   - **Element** — which specific thing is wrong (e.g. "x-tick labels in panel (b)", "legend in upper-right", "colorbar tick at 0.5").
   - **Defect** — what is wrong (collision, unreadable, clipped, etc.).
   - **Severity** — `blocking` (a careful reader would be confused or have to squint) or `minor` (slightly ugly but readable).

For multi-panel figures, walk panels in **reading order** (top-left → top-right → bottom-left → bottom-right) and report defects per-panel.

Categories to scan:

- **Legibility** — tick labels, axis labels, legend text, annotations all readable without squinting? Lines thick enough to follow? Markers large enough to distinguish? Error bars visible (not lost in line thickness)? Math glyphs vector and crisp?
- **Collision / overlap** — tick labels colliding with each other or with axis labels? Legend covering data? Annotations overlapping data? Multi-panel: titles or labels colliding with adjacent panels? Colorbar colliding with main plot? Inset axes colliding with legend?
- **Truncation / clipping** — anything cut off at figure edges (title, legend, tick labels, panel labels (a)/(b)/(c))? Data clipped by axis limits? Long category labels running off?
- **Encoding** — series distinguishable from each other? If grayscale-printed, can you still tell them apart (color + line style or color + marker)? Diverging colormap centered on zero? `jet`/`rainbow` in use (auto-flag)? Histogram-specific: linear y-density on multi-order-of-magnitude data, linear-spaced bins on log-distributed x, `density=True` masking unequal sample sizes?
- **Layout** — whitespace evenly distributed or one region cramped while another is empty? Subplot panels visually balanced (similar plot areas, aligned axes)? Grouped bars: bars within a group close, gaps between groups?
- **Dynamic range / axis scaling** — does any axis have one feature (outlier, dominant regime, plateau) consuming >80% of the visual area while the comparison-relevant range is compressed into <20%? Outlier squeezing linear y-axis? Decay-to-zero curve with 90% post-convergence flatline? Multi-modal distribution with modes differing by orders of magnitude in density?

If the image is a **TikZ / boxes-and-arrows diagram** rather than a data plot, also scan for these defects (catalog: `skills/figura/references/tikz.md` § "Defect catalog"):

- **Arrow crosses through node text** — line passing through a label, often appearing to underline it. Common with `diamond` shapes.
- **Loop-back arrow crosses unrelated nodes** — feedback edge from bottom row to top row passing through an unrelated node like an input box.
- **Annotation label sits on top of a node body** — label placed at xy-midpoint of two nodes on different rows.
- **Default Computer Modern serif font** instead of sans-serif — TikZ analog of "default DejaVu Sans"; classifies as **legibility** for the report.
- **Sharp 90° corners on every box, raw `red`/`blue`/`green` colors** — TikZ analog of "default matplotlib"; classifies as **encoding** (palette not colorblind-safe) and **layout** (dated look).

Report format (markdown table):

```
| Severity | Category | Element | Defect |
|----------|----------|---------|--------|
| blocking | legibility | y-tick labels | unreadable at print size, ~5pt |
| minor    | layout     | left margin    | extra whitespace |
```

After the table, write 1–2 sentences of overall verdict: "ship it", "one fix cycle needed", or "two fix cycles needed and which class is biggest". Skip cosmetic nitpicks a reader would never notice.

End with a **next-step recommendation** based on which defect class dominates:

| Dominant class | Suggested command |
|---|---|
| Encoding (jet/rainbow, default DejaVu, four spines, color-only) | `/figura:beautify` |
| Collision (legend covers data, ticks collide, inset hits legend) | `/figura:fix-overlap` |
| Truncation (anything clipped) | `/figura:fix-overlap` |
| Legibility (fonts too small, lines too thin) | `/figura:beautify` (re-applies pubstyle defaults) or `/figura:iterate` if mixed |
| Dynamic-range squeeze | `/figura:iterate` (no targeted skill yet) |
| Mixed across categories | `/figura:iterate` |
| All issues minor / sub-pixel | Ship it |

Phrase the recommendation as one sentence: "Dominant class is X; recommend `/figura:<cmd>`."
