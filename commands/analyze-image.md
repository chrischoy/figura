---
description: Read-only visual audit of a rendered figure (PNG or PDF). Reports defects categorized by legibility, collision, truncation, encoding, layout — does not modify anything.
argument-hint: <path-to-image-or-pdf>
allowed-tools: ["Read"]
---

Audit the figure at `$ARGUMENTS`. Read-only — do not edit any source files, do not re-render, do not propose patches. The output is a defect report the user can act on.

Use the inspection prompt and defect categories from `skills/PaperFigureSkill/references/iteration.md` § "Visual Inspection Prompt". Report every issue you can see at the image's native resolution (the PNG renders at 300 DPI, sized to print dimensions, so on-screen pixels match what a reader sees on paper).

Procedure:

1. Use `Read` on `$ARGUMENTS` to view the image. Both PNG and PDF are supported.
2. Walk through the five defect categories below. For each issue, record:
   - **Element** — which specific thing is wrong (e.g. "x-tick labels in panel (b)", "legend in upper-right", "colorbar tick at 0.5").
   - **Defect** — what is wrong (collision, unreadable, clipped, etc.).
   - **Severity** — `blocking` (a careful reader would be confused or have to squint) or `minor` (slightly ugly but readable).

Categories to scan:

- **Legibility** — tick labels, axis labels, legend text, annotations all readable without squinting? Lines thick enough to follow? Markers large enough to distinguish? Error bars visible (not lost in line thickness)? Math glyphs vector and crisp?
- **Collision / overlap** — tick labels colliding with each other or with axis labels? Legend covering data? Annotations overlapping data? Multi-panel: titles or labels colliding with adjacent panels? Colorbar colliding with main plot?
- **Truncation / clipping** — anything cut off at figure edges (title, legend, tick labels, panel labels (a)/(b)/(c))? Data clipped by axis limits? Long category labels running off?
- **Encoding** — series distinguishable from each other? If grayscale-printed, can you still tell them apart (color + line style or color + marker)? Diverging colormap centered on zero? `jet`/`rainbow` in use (auto-flag)?
- **Layout** — whitespace evenly distributed or one region cramped while another is empty? Subplot panels visually balanced (similar plot areas, aligned axes)? Grouped bars: bars within a group close, gaps between groups?

If the image is a **TikZ / boxes-and-arrows diagram** rather than a data plot, also scan for these defects (catalog: `skills/PaperFigureSkill/references/tikz.md` § "Defect catalog"):

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

If the user wants to apply fixes, point them at `/PaperFigureSkill:iterate`, `/PaperFigureSkill:beautify`, or `/PaperFigureSkill:fix-overlap` depending on which class dominates.
