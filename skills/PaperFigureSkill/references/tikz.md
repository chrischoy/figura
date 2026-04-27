# TikZ / LaTeX Diagrams

Use TikZ when:

- Paper is already LaTeX and you want one toolchain end-to-end.
- Diagram is a flowchart / state machine / boxes-and-arrows where TikZ's `positioning`, `calc`, and `shapes.geometric` libraries make layout declarative.
- You want crisp typography that exactly matches the paper body (same fonts, math, microtype kerning).
- You want the diagram source to live next to the paper as plain `.tex` (diff-friendly, reviewer-friendly).

Skip TikZ if you need many auto-laid-out nodes (use graphviz) or pixel-perfect curves and shading (use matplotlib or hand SVG).

The skill ships:

- `examples/diagram_flow.tex` — copy-paste standalone template (palette, styles, common patterns).
- `scripts/tikz_build.sh` — compile + rasterize helper for the render-view-fix loop.

---

## Workflow

1. **Copy the template.** `cp examples/diagram_flow.tex figures/my_fig.tex` and edit nodes / arrows.
2. **Build.** `bash scripts/tikz_build.sh figures/my_fig.tex figures` writes `figures/my_fig.{pdf,png}` (and `.svg` if `pdf2svg` is installed).
3. **View the PNG** (300 DPI of the standalone-cropped PDF — reflects exactly what `\includegraphics{my_fig}` will show in the paper).
4. **Inspect** for the defects in the catalog below.
5. **Fix** in the `.tex`, rebuild, re-view.
6. **Stop after ≤ 2 fix cycles**, same rule as data figures (see `references/iteration.md`).
7. **In the paper**: `\includegraphics[width=\columnwidth]{figures/my_fig}` — the `standalone` PDF crops tight, so `width=` controls the rendered size.

The `.pdf` is paper-ready vector. The `.png` is the iteration preview, not a deliverable.

---

## The standalone document class

The template uses `\documentclass[tikz,border=4pt]{standalone}`. Two reasons:

- **Crops to content.** No `\maketitle`, no page margins — output PDF is exactly the diagram bounding box plus the 4pt border. Drops into `\includegraphics{}` cleanly.
- **One file, one figure.** Easy to version, easy to rebuild a single diagram without touching the paper build.

When the paper build runs, the diagrams are already compiled to `.pdf` and just `\includegraphics{}`-ed in. No nested TikZ during the main build → faster, less fragile.

If you want the paper's main build to compile TikZ too (e.g. share macros), use `\documentclass[border=4pt]{standalone}` with `\usepackage[mode=buildmissing]{standalone}` in the parent — but the simple split (compile diagrams separately, include the PDFs) is almost always better.

---

## Engine choice

| Engine | When | Notes |
|--------|------|-------|
| `pdflatex` | Default. Most TikZ examples assume it. | Fast. Helvetica via `helvet` package. |
| `lualatex` | Need system fonts (`fontspec`) or large memory for big graphs. | Slower first run; fontspec gives access to Inter, Source Sans, etc. |
| `tectonic` | Reproducible builds, no system TeX install. | `tectonic diagram.tex` — auto-fetches packages. Not always available. |

Override via `TIKZ_ENGINE=lualatex bash scripts/tikz_build.sh ...`.

---

## Color: matching the rest of the paper

Define Okabe–Ito hex codes once at the top — same values as `scripts/colors.py`, so TikZ diagrams and matplotlib figures match exactly:

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

Use `okBlue!12` for soft fills (TikZ's `!N` mixes with white). `okBlue` for borders, `inkBlack` for body text. Same palette across plots and diagrams = coherent paper.

---

## Reusable styles

Define styles once in the `tikzpicture` options, reuse on every node. Cuts noise and keeps the diagram consistent.

```latex
\begin{tikzpicture}[
  font=\small,
  >={Stealth[length=2.2mm,width=1.8mm]},   % uniform arrowheads everywhere
  line width=0.7pt,
  node distance=10mm and 9mm,              % vertical and horizontal gaps
  stage/.style={                           % rounded process box, color via #1
    rectangle, rounded corners=2pt,
    draw=#1, fill=#1!12, text=inkBlack,
    minimum width=22mm, minimum height=9mm, align=center,
  },
  decision/.style={                        % diamond
    diamond, aspect=1.6,
    draw=okVerm, fill=okVerm!12, text=inkBlack,
    minimum width=18mm, minimum height=14mm, align=center, inner sep=1pt,
  },
  flow/.style={->, draw=inkBlack},
  loopflow/.style={->, draw=okVerm, dashed, line width=0.8pt},
  pass/.style={->, draw=okGreen, line width=0.9pt},
  lbl/.style={font=\scriptsize\itshape, text=inkBlack!75, inner sep=1.5pt},
]
```

Then nodes are one-liners: `\node[stage=okOrange, right=of a] (b) {Process};`.

---

## Layout: `positioning` + `calc`

`positioning` lets you place nodes relative to others without coordinates: `right=of a`, `below=12mm of b`. Layout becomes self-documenting and survives content changes.

`calc` lets you compute coordinates from existing nodes:

```latex
\coordinate (mid) at ($(a)!0.5!(b)$);              % midpoint of a and b
\coordinate (above) at ($(b.north)+(0,9mm)$);      % 9mm above b
\coordinate (cross) at (a.east |- b.south);        % a's x, b's y
```

The `|-` and `-|` operators are coordinate intersections, *not* path connectors. `(a |- b)` = "(a.x, b.y)". Easy to mix up with the `|-` path operator (vertical-then-horizontal). Keep them straight or you'll waste a fix cycle.

For a U-shaped loop arrow that clears all nodes (e.g. a feedback edge from bottom-row back to top-row), route through explicit waypoints instead of `|-`/`-|` path operators — it's easier to reason about and easier to fix:

```latex
\coordinate (loopAnchor) at ($(top.north)+(0,9mm)$);
\coordinate (loopL) at (bottom.north |- loopAnchor);
\coordinate (loopR) at (top.north    |- loopAnchor);
\draw[loopflow] (bottom.north) -- (loopL) -- (loopR) -- (top.north);
```

---

## Defect catalog (TikZ-specific)

These are the bugs that show up in the first PNG and waste a cycle if you don't know them.

### Arrow crosses through node text

**Symptom:** Arrow line passes visually through a label, often appearing to underline it. Common with `diamond` shapes — the leftmost vertex sits on the text baseline.

**Cause:** Arrow exits the node at the closest border anchor (e.g. `west` for a horizontal arrow), which on a flat-aspect diamond is at text-baseline height.

**Fix:** Route from a corner anchor with a bend, or make the diamond taller.

```latex
% bad: arrow exits at diamond's leftmost vertex, on text baseline
\draw[loopflow] (d) -- (e);

% good: bend from the upper corner, label clearly above
\draw[loopflow] (d.north west) to[bend left=15]
  node[lbl,above,pos=0.5]{retry} (e.north east);
```

### Loop-back arrow crosses unrelated nodes

**Symptom:** A feedback edge from the bottom row to the top row passes through `User request` or some other unrelated node.

**Cause:** `|-` and `-|` path operators take the shortest right-angle path between two points, which often runs *between* rows — straight through the row above the source.

**Fix:** Route through explicit waypoints above (or below) all nodes.

```latex
% bad: horizontal segment lands between rows, crossing nodes
\draw[loopflow] (fix.north) |- (code.north);

% good: explicit waypoint above the entire top row
\coordinate (loopAnchor) at ($(code.north)+(0,9mm)$);
\coordinate (loopL) at (fix.north  |- loopAnchor);
\coordinate (loopR) at (code.north |- loopAnchor);
\draw[loopflow] (fix.north) -- (loopL) -- (loopR) -- (code.north);
```

### Annotation lands on top of a node

**Symptom:** Label like `≤ 2 cycles` appears overlapping a node body.

**Cause:** Position computed as the *xy-midpoint* of two nodes on different rows — the y-midpoint is between rows, often on top of an intermediate node.

**Fix:** Compute the midpoint *along the path you want it on*, not the geometric midpoint of the endpoints. Define explicit waypoints (`loopL`, `loopR` above) and place the label at `($(loopL)!0.5!(loopR)$)`. Add `fill=white` and small `inner sep` so it cleanly cuts the line behind it.

### Arrowhead pokes into the node

**Symptom:** Tip of the arrow overlaps the box border, looks like it's punching through.

**Fix:** TikZ already shrinks to anchor points, but if you used absolute coordinates, add `shorten >=2pt` and `shorten <=2pt` to the path style, or use named anchors (`(a.east)`, `(b.west)`) so TikZ shrinks correctly.

### Text too small at print size

**Symptom:** PNG looks fine but in the actual paper at `\columnwidth` it's unreadable.

**Cause:** TikZ defaults to ambient document size (10pt). When the standalone PDF is shrunk to column width via `\includegraphics[width=\columnwidth]`, the 10pt text shrinks proportionally.

**Fix:** Pick a target physical size and stick to it. For a single-column figure (~3.3 in wide):

```latex
\begin{tikzpicture}[font=\small, ...]   % \small ≈ 9pt at 10pt base
  ...
\end{tikzpicture}
```

If the natural diagram width comes out much larger than 3.3 in, either shrink the diagram (smaller `node distance`, smaller `minimum width`) or design at the larger width and accept that you'll need `font=\footnotesize` so it stays readable when shrunk.

Concrete rule: **the PNG you view is what the reader sees only if you `\includegraphics` it at its natural size.** If you'll scale it in the paper, scale your preview view too: `pdftoppm -r 150` instead of `300`, or open the included version directly.

### Helvetica looks weird / cramped

**Cause:** Default TeX fonts are serif Computer Modern. The template loads `helvet` and sets it as default, which gives Helvetica. If the diagram still looks off, check:

- `\renewcommand{\familydefault}{\sfdefault}` is set (template does this).
- For math, `\usepackage{mathptmx}` or `\usepackage{newtxtext,newtxmath}` matches Helvetica better than CM math.
- For LuaLaTeX with system fonts, swap `helvet` for `\usepackage{fontspec}\setmainfont{Inter}` (or whatever the paper uses).

---

## Common patterns

### Multi-row layout with `matrix of nodes`

For grid-aligned diagrams (e.g. transformer block with parallel attention heads), `matrix` library beats manual `node distance`:

```latex
\usetikzlibrary{matrix}
\matrix[matrix of nodes, row sep=6mm, column sep=8mm,
        nodes={stage=okBlue}] (m) {
  Q & K & V \\
  &  & \\          % gap row
  \multicolumn{3}{Attention} \\
};
```

### Background panel grouping related nodes

```latex
\usetikzlibrary{backgrounds,fit}
\begin{scope}[on background layer]
  \node[fit=(b)(c)(d), draw=okBlue, dashed,
        inner sep=4mm, rounded corners=3pt,
        label={[lbl]above:Encoder}] {};
\end{scope}
```

### Include an external image inside TikZ

For a diagram that mixes a screenshot or photo with TikZ annotations:

```latex
\node[anchor=south west,inner sep=0] (img)
  at (0,0) {\includegraphics[width=6cm]{photo.png}};
\begin{scope}[x={(img.south east)},y={(img.north west)}]
  \draw[red, line width=1pt] (0.4,0.5) circle (0.05);
  \node[okVerm,fill=white] at (0.4,0.6) {detail};
\end{scope}
```

The `scope` rescales coordinates to the unit square of the image — annotations work in 0..1 normalized space and survive image resizing.

---

## Rasterizing for the iteration loop

`scripts/tikz_build.sh` does PDF → PNG via `pdftoppm -r 300`. If `pdf2svg` is installed it also writes `.svg`. For one-off rasterization without the script:

```bash
pdflatex -interaction=nonstopmode my_fig.tex
pdftoppm -r 300 -png my_fig.pdf my_fig
mv my_fig-1.png my_fig.png
```

`pdftoppm` is part of `poppler` (`brew install poppler` / `apt install poppler-utils`). It's faster and crisper than ImageMagick's `convert` for this use case, and doesn't require ghostscript security policy edits.

---

## When TikZ stops being the right answer

Switch to matplotlib or graphviz if:

- The diagram needs >20 auto-positioned nodes — graphviz wins.
- You need shaded surfaces, curves from data, or a 3D look — matplotlib.
- The paper isn't LaTeX (Word, web, slides) — TikZ output is just a PDF, but the source is unusable to a non-LaTeX coauthor. Hand SVG or matplotlib travels better.
- You're still hand-tuning coordinates after 3 fix cycles — the diagram has outgrown TikZ's declarative comfort zone.
