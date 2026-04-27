---
description: Upgrade a "looks like default matplotlib" figure to publication style — fonts embedded, palette colorblind-safe, spines/grid cleaned, vector exports.
argument-hint: <path-to-figure-script.py>
allowed-tools: ["Bash", "Read", "Edit", "Write"]
---

Beautify the figure produced by `$ARGUMENTS`. The skill at `skills/PaperFigureSkill/` documents the policy — apply it, do not improvise.

Pre-flight read the script and check for these "default matplotlib" tells (full anti-pattern list in `skills/PaperFigureSkill/SKILL.md` § "Anti-Patterns"):

- No `pubstyle.apply()` → fonts not embedded, defaults at 10pt, all four spines on.
- No `colors.apply_cycle()` → matplotlib's tab10 cycle, not colorblind-safe.
- `cmap="jet"` / `"rainbow"` / `"hsv"` / `"nipy_spectral"` → replace with `"viridis"` (sequential) or `"RdBu_r"` (diverging, with `vmin=-vmax`).
- Saving as JPEG → switch to `export.save(fig, name, formats=("pdf","svg","png"))`.
- Hardcoded `figsize=(12, 8)` → swap for `pubstyle.figsize("single")` / `"double"` / `"square"` so the figure is designed at print size.
- Color-only encoding (multiple solid lines distinguished only by color) → add `linestyle=` or `marker=` so it survives grayscale print.

Plan:

1. Read `$ARGUMENTS`. List which anti-patterns it hits.
2. Add the standard skill setup at the top:
   ```python
   import sys
   sys.path.insert(0, "<absolute-path-to-this-repo>/skills/PaperFigureSkill/scripts")
   import matplotlib
   matplotlib.use("Agg")
   import pubstyle, colors, export
   pubstyle.apply()
   colors.apply_cycle()
   ```
3. Replace anti-patterns with their counterparts. Keep the data and the plot's structure unchanged — only restyle.
4. Replace any `plt.savefig("name.png")` with `export.save(fig, "name")`.
5. Run the script and view the rendered PNG to confirm the upgrade landed cleanly.
6. If a venue is mentioned (NeurIPS, IEEE, Nature), pass it: `pubstyle.apply(venue="ieee")`.

Stop when the figure passes the anti-pattern checklist. Do not start the iteration loop unless explicitly asked — that's `/PaperFigureSkill:iterate`.
