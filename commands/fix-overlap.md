---
description: Targeted fix for overlap/collision defects — tick labels, legend covering data, axis labels, multi-panel collisions.
argument-hint: <path-to-figure-script.py>
allowed-tools: ["Bash", "Read", "Edit", "Write"]
---

Fix overlap/collision defects in the figure produced by `$ARGUMENTS`. Targeted version of `/PaperFigureSkill:iterate` — only address the collision/overlap class, not legibility or color issues.

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

Report which collisions you found and which catalog fixes you applied.
