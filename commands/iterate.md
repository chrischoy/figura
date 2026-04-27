---
description: Run the render → view → fix loop on a figure script (matplotlib .py) or TikZ source (.tex) until print-size defects are gone or two cycles pass.
argument-hint: <path-to-figure-script.py-or-diagram.tex>
allowed-tools: ["Bash", "Read", "Edit", "Write"]
---

Run the iteration loop on `$ARGUMENTS`. The skill at `skills/figura/` ships the full procedure in `references/iteration.md` (matplotlib defects) and `references/tikz.md` (TikZ defects) — use them.

Dispatch on file extension:

- `*.py` → **matplotlib branch** (data plot, matplotlib diagram).
- `*.tex` → **TikZ branch** (TikZ standalone diagram).
- Other → ask the user how the figure is rendered.

---

## matplotlib branch (`*.py`)

1. Read the script to understand what it builds and where it writes output. If it does not call `export.save(...)` or write into `figures/`, ask the user where the rendered PNG will land.
2. Run the script: `python $ARGUMENTS`. Capture the output paths.
3. View the resulting PNG with the `Read` tool. The PNG is at native print resolution — what you see is what a reader sees on paper.
4. Inspect for defects using the prompt in `skills/figura/references/iteration.md` § "Visual Inspection Prompt". Be specific: name the element, name the defect, name the severity (blocking vs minor).
5. Apply fixes from the defect catalog in the same file. Edit the script in place. Prefer per-axes fixes (`ax.tick_params`, `ax.set_xlabel(..., fontsize=...)`) over re-applying the whole `pubstyle` block.
6. Re-render and re-view.
7. Stop after at most **2 fix cycles**, or sooner if only sub-pixel / cosmetic issues remain. Do not chase perfection.

## TikZ branch (`*.tex`)

1. Read the `.tex` to understand the diagram (nodes, edges, layout). Confirm it uses `\documentclass[...]{standalone}` — if not, suggest converting (full reference: `skills/figura/references/tikz.md` § "The standalone document class").
2. Build with the bundled helper: `bash skills/figura/scripts/tikz_build.sh $ARGUMENTS figures`. This compiles the standalone PDF and emits a 300 DPI PNG preview at `figures/<name>.png`. If the engine fails, the script prints the last 40 lines of the LaTeX log — read them, fix the source, retry.
3. View the PNG with the `Read` tool. Compile errors show as a missing/stale PNG — confirm timestamps if unsure.
4. Inspect using the same prompt as matplotlib (`references/iteration.md` § "Visual Inspection Prompt"), plus the TikZ-specific defect catalog in `references/tikz.md` § "Defect catalog". The TikZ defects to scan for in particular:
   - Arrow line crosses through node text (especially `diamond` shapes — leftmost vertex aligns with text baseline).
   - Loop-back arrow's horizontal segment crosses unrelated nodes (typical with `|-` / `-|` path operators between rows).
   - Annotation label lands on top of a node body (computed midpoint between two nodes on different rows).
   - Text too small at intended print width — TikZ has no `pubstyle` analog; pick `font=\small` / `\footnotesize` deliberately.
   - Default Computer Modern serif (the LaTeX equivalent of "default DejaVu Sans") — fix with `\usepackage{helvet}\renewcommand{\familydefault}{\sfdefault}`.
5. Apply fixes in the `.tex`. Prefer the patterns from `references/tikz.md`:
   - Route arrows from corner anchors (`.north west`) with `to[bend left=15]` instead of bare `--` when an edge would cross text.
   - Replace `(a) |- (b)` with explicit waypoints (`loopAnchor`, `loopL`, `loopR`) when the loop must clear a row.
   - Place labels at midpoints of *path waypoints* (`($(loopL)!0.5!(loopR)$)`), not at midpoints of source/target nodes.
6. Re-build and re-view.
7. Same stopping rule — **2 fix cycles max**, or sooner if only cosmetic issues remain.

---

Report what defects you found, what you changed, and what (if anything) still bothers you.
