---
description: Upgrade a "looks like default" figure to publication style — fonts embedded, palette colorblind-safe, spines/grid cleaned, vector exports. Works on matplotlib (.py) and TikZ (.tex).
argument-hint: <path-to-figure-script.py-or-diagram.tex>
allowed-tools: ["Bash", "Read", "Edit", "Write"]
---

Beautify the figure produced by `$ARGUMENTS`. The skill at `skills/figura/` documents the policy — apply it, do not improvise.

If `$ARGUMENTS` is empty, ask the user which file to beautify. Do not improvise (no globbing, no guessing). The user usually knows which figure needs the upgrade.

Dispatch on file extension:

- `*.py` → **matplotlib branch** below.
- `*.tex` → **TikZ branch** below.
- Other → ask the user.

---

## matplotlib branch (`*.py`)

Pre-flight read the script and check for these "default matplotlib" tells (full anti-pattern list in `skills/figura/SKILL.md` § "Anti-Patterns"):

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
   sys.path.insert(0, "<absolute-path-to-this-repo>/skills/figura/scripts")
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

Stop when the figure passes the anti-pattern checklist. Do not start the iteration loop unless explicitly asked — that's `/figura:iterate`.

---

## TikZ branch (`*.tex`)

Pre-flight read the source and check for these "default TikZ" tells (full reference: `skills/figura/references/tikz.md`):

- **`\documentclass{article}` / `{report}` instead of `standalone`** → diagram bakes into a paginated A4/letter PDF; can't `\includegraphics{}` cleanly. Convert to `\documentclass[tikz,border=4pt]{standalone}`.
- **Default Computer Modern serif** → math-paper look that clashes with sans-serif body text in most venues. Add `\usepackage{helvet}\renewcommand{\familydefault}{\sfdefault}` (or `fontspec` under LuaLaTeX to match the paper's actual body font).
- **Raw color names** (`red`, `blue`, `green!50`) → not colorblind-safe, doesn't match the rest of the paper. Replace with the Okabe-Ito palette:
  ```latex
  \definecolor{okBlue}{HTML}{0072B2}
  \definecolor{okOrange}{HTML}{E69F00}
  \definecolor{okGreen}{HTML}{009E73}
  \definecolor{okSky}{HTML}{56B4E9}
  \definecolor{okVerm}{HTML}{D55E00}
  \definecolor{okPurple}{HTML}{CC79A7}
  \definecolor{okYellow}{HTML}{F0E442}
  \definecolor{inkBlack}{HTML}{1A1A1A}
  ```
  Use `okBlue!12` for soft fills, `okBlue` for borders.
- **No reusable styles** — every `\node[draw, rectangle, fill=blue!20, ...]` re-spelled inline. Pull into `tikzpicture` options once:
  ```latex
  stage/.style={rectangle, rounded corners=2pt, draw=#1, fill=#1!12,
                minimum width=22mm, minimum height=9mm, align=center},
  ```
- **Default arrowhead `->`** → undersized, inconsistent with sibling figures. Set globally: `>={Stealth[length=2.2mm,width=1.8mm]}`.
- **Hardcoded coordinates** (`\node at (3.2, 1.7) {A};`) → fragile to content edits. Replace with `positioning`-relative placement: `\node[stage=okBlue, right=of a] (b) {B};`.
- **Sharp 90° corners** on every box → dated. Use `rounded corners=2pt`.
- **Heavy lines (`line width=1.5pt+`)** at print size → bold, hand-drawn look. Drop to `0.7pt`–`0.9pt`.
- **No `font=\small` in tikzpicture** → 10pt nodes look fine in source but unreadable when `\includegraphics[width=\columnwidth]` shrinks the diagram. Set `font=\small` (or `\footnotesize` for dense diagrams).
- **No `\usetikzlibrary{positioning,arrows.meta,shapes.geometric,calc}`** → can't use any of the above. Standard preamble in the template.

Plan:

1. Read `$ARGUMENTS`. List which TikZ anti-patterns it hits.
2. If the document class isn't `standalone`, convert it. Strip out unrelated paper preamble, keep only what the diagram needs.
3. Add the standard preamble (helvet, libraries, Okabe-Ito colors, reusable styles). The template at `skills/figura/examples/diagram_flow.tex` is a copy-paste starting point.
4. Replace raw colors with `okBlue` / `okOrange` / etc. Group nodes by role: input/output one color, transforms another, branching/decision a third.
5. Pull inline node options into named styles defined once at the top of `tikzpicture`.
6. Replace hardcoded coordinates with `positioning`-relative placement where feasible.
7. Set `font=\small`, `line width=0.7pt`, uniform `>={Stealth[...]}`.
8. Build with `bash skills/figura/scripts/tikz_build.sh $ARGUMENTS figures` and view the PNG to confirm the upgrade landed cleanly.
9. **Do not change the diagram's logical content** — same nodes, same edges, same routing topology. Only restyle.

Stop when the diagram passes the anti-pattern checklist. Do not start the iteration loop unless explicitly asked — that's `/figura:iterate`.
