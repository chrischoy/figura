---
description: Targeted fix for overlap/collision defects — tick labels, legend covering data, axis labels, multi-panel collisions (matplotlib) or arrow-through-text, loop-arrow-crossing-nodes, label-on-node (TikZ).
argument-hint: <path-to-figure-script.py-or-diagram.tex>
allowed-tools: ["Bash", "Read", "Edit", "Write"]
---

Fix overlap/collision defects in the figure produced by `$ARGUMENTS`. Targeted version of `/PaperFigureSkill:iterate` — only address the collision/overlap class, not legibility or color issues.

Dispatch on file extension:

- `*.py` → **matplotlib branch** below.
- `*.tex` → **TikZ branch** below.

---

## matplotlib branch (`*.py`)

Procedure:

1. Run `$ARGUMENTS` and view the rendered PNG.
2. Walk through this collision checklist (drawn from `skills/PaperFigureSkill/references/iteration.md` § "Tick Labels Colliding", "Legend Issues", "Multi-Panel Issues"):
   - X-tick labels colliding with each other or with the x-axis label.
   - Y-tick labels colliding with the panel to the left (multi-panel).
   - Legend covering data points / lines / annotations.
   - Annotations overlapping the data they label.
   - Colorbar colliding with the main plot.
   - Panel titles or labels colliding with adjacent panels.
   - "(a)/(b)/(c)" panel labels clipped at figure edge.
3. For each collision, apply the standard fix from the catalog. Common ones:
   - Tick collision → `ax.tick_params(axis="x", labelrotation=30)` + `plt.setp(ax.get_xticklabels(), ha="right")`.
   - Legend covering data → try `loc="best"` first; if still bad pick a corner manually, or pull outside with `bbox_to_anchor=(1.02, 0.5)` + `fig.subplots_adjust(right=0.78)`.
   - Multi-panel cramping → `plt.subplots(..., gridspec_kw=dict(wspace=0.35, hspace=0.4))` or `sharey=True`.
   - Panel labels clipped → `ax.text(-0.18, 1.05, "(a)", transform=ax.transAxes, fontweight="bold")`.
   - Long category labels overflowing → rotate, wrap, or switch to `barh`.
4. Re-render and re-view. Confirm all collisions resolved.
5. Stop. Do not bleed into legibility/color/encoding tweaks — those belong in `/PaperFigureSkill:beautify` or `/PaperFigureSkill:iterate`.

---

## TikZ branch (`*.tex`)

Procedure:

1. Build with `bash skills/PaperFigureSkill/scripts/tikz_build.sh $ARGUMENTS figures` and view the rendered PNG.
2. Walk through this TikZ collision checklist (drawn from `skills/PaperFigureSkill/references/tikz.md` § "Defect catalog"):
   - **Arrow line crosses through node text** — most common with `diamond` shapes; the leftmost vertex sits on the text baseline.
   - **Loop-back / feedback arrow crosses unrelated nodes** — typical with `|-` or `-|` path operators between rows.
   - **Annotation label overlapping a node body** — happens when label is positioned at the geometric midpoint of two nodes on different rows; the y-midpoint lands between rows, often on top of an intermediate node.
   - **Arrow tip punching into the box** — usually only with hand-coordinate paths bypassing the anchor system.
   - **Two parallel arrows visually merging** — bidirectional edges drawn as overlapping line segments.
   - **Background panel (`fit=...`) clipping a label** — `inner sep` too small.
3. For each collision, apply the standard fix from the catalog:
   - Arrow through diamond text → route from a corner anchor with a bend:
     ```latex
     \draw[loopflow] (d.north west) to[bend left=15] (e.north east);
     ```
     Or make the diamond taller (`minimum height=14mm`).
   - Loop arrow crossing a row → route through explicit waypoints above the entire row:
     ```latex
     \coordinate (loopAnchor) at ($(top.north)+(0,9mm)$);
     \coordinate (loopL) at (bottom.north |- loopAnchor);
     \coordinate (loopR) at (top.north    |- loopAnchor);
     \draw[loopflow] (bottom.north) -- (loopL) -- (loopR) -- (top.north);
     ```
   - Label on top of a node → place the label at the midpoint of the *path waypoints*, not the source/target nodes:
     ```latex
     \node[lbl, fill=white, inner sep=2pt]
       at ($(loopL)!0.5!(loopR)$) {label};
     ```
     `fill=white` cuts the line cleanly behind the label.
   - Arrow tip punching → use named anchors (`(a.east)`) so TikZ shrinks correctly, or add `shorten >=2pt`.
   - Parallel-arrow merge → offset one with `transform canvas={yshift=1mm}` or use `bend left=10` / `bend right=10` for the pair.
   - Background panel clipping a label → bump `inner sep=4mm` on the `fit` node.
4. Re-build and re-view. Confirm all collisions resolved.
5. Stop. Do not bleed into typography/color/encoding tweaks — those belong in `/PaperFigureSkill:beautify` or `/PaperFigureSkill:iterate`.

---

Report which collisions you found and which catalog fixes you applied.
