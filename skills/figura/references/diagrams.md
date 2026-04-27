# Diagrams: Architecture, Schematic, Model Illustration

Four approaches, picked by the diagram's character:

| Approach | Best for | Tradeoff |
|----------|----------|----------|
| **matplotlib custom drawing** | Diagrams that should match your data figures (same fonts, palette, export pipeline) | Manual layout — you place every box |
| **TikZ / LaTeX** | LaTeX papers; flowcharts, state machines, boxes-and-arrows where you want crisp typography matching the paper body | Manual layout; LaTeX toolchain required. See `references/tikz.md`. |
| **graphviz** | Many nodes, you want auto-layout (system diagrams, dataflow, dependency graphs) | Less aesthetic control |
| **Hand-authored SVG** | One-off polished illustrations where layout is artistic | Slowest to build |

For ML model architectures (transformer blocks, U-Nets, encoder-decoders), prefer matplotlib or hand-SVG — graphviz fights you on positioning. For pipeline / system / dataflow diagrams with 10+ nodes, graphviz earns its keep. For boxes-and-arrows in a LaTeX paper where you want diagram fonts to exactly match the body text, TikZ is the right tool — see `references/tikz.md` for the full template, build helper, and defect catalog.

---

## matplotlib custom drawing

The big win: same fonts, same colors, same export pipeline as your data figures. The whole paper looks coherent.

Pattern: turn off axes, place boxes (`FancyBboxPatch`) with text, draw arrows (`FancyArrowPatch` or `annotate`).

```python
import sys
sys.path.insert(0, "<absolute-path-to-this-skill>/scripts")
import pubstyle, colors, export
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

pubstyle.apply()
palette = colors.categorical(4)

fig, ax = plt.subplots(figsize=pubstyle.figsize("double"))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.set_aspect("equal")
ax.axis("off")

def box(x, y, w, h, text, color, text_color="white"):
    """Rounded rectangle with centered text."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor=color, edgecolor="none",
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center",
            color=text_color, fontsize=9, fontweight="medium")

def arrow(x1, y1, x2, y2):
    """Arrow with a small head, sized for diagrams."""
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=12,
        linewidth=1.0, color="#444", shrinkA=4, shrinkB=4,
    )
    ax.add_patch(a)

# Layout: input → encoder → bottleneck → decoder → output
boxes = [
    (0.3, 1.5, 1.4, 1.0, "Input",       palette[0]),
    (2.2, 1.5, 1.6, 1.0, "Encoder",     palette[1]),
    (4.3, 1.7, 1.4, 0.6, "Bottleneck",  palette[2]),
    (6.2, 1.5, 1.6, 1.0, "Decoder",     palette[1]),
    (8.3, 1.5, 1.4, 1.0, "Output",      palette[0]),
]
for b in boxes:
    box(*b)

# Draw arrows between consecutive boxes
for (x1, y1, w1, h1, *_), (x2, y2, w2, h2, *_) in zip(boxes, boxes[1:]):
    arrow(x1 + w1, y1 + h1 / 2, x2, y2 + h2 / 2)

# Skip connection (curved arrow over the top)
sa = FancyArrowPatch(
    (3.0, 2.5), (7.0, 2.5),
    connectionstyle="arc3,rad=-0.4",
    arrowstyle="-|>", mutation_scale=10,
    linewidth=0.9, color="#888", linestyle=(0, (3, 2)),
)
ax.add_patch(sa)
ax.text(5.0, 3.2, "skip", ha="center", fontsize=8, color="#666", style="italic")

export.save(fig, "fig_architecture")
```

Tips for matplotlib diagrams:

- **Set `ax.set_aspect("equal")` and turn axes off.** Otherwise rectangles are stretched and arrows angle weirdly.
- **Use a coordinate system that fits your figure size.** Above, the figure is 6.8 × 2.6 in (`double`) and the axes go 0–10 × 0–4. That gives ~0.68 in/unit horizontally and 0.65 in/unit vertically — close to square per unit, which keeps drawing intuitive.
- **`FancyBboxPatch` with `boxstyle="round,..."`** gives modern rounded rectangles. `pad` is internal padding before the corner; `rounding_size` controls corner radius.
- **`shrinkA=4, shrinkB=4`** on arrows pulls the endpoints back from the box edges so the arrowhead doesn't overlap text.
- **Group boxes by role with color** — input/output one color, transforms another, special components a third. Re-use `colors.categorical()` so it matches the data figures.
- **Dashed for "optional" or "skip" or "auxiliary" connections** — `linestyle=(0, (3, 2))` is a clean dash pattern.

For multi-row layouts (e.g. transformer block with parallel attention heads), use a helper function to lay out a grid of boxes and pass coordinates to your `box()` function.

---

## graphviz

When auto-layout matters more than exact positioning. Install: `pip install graphviz`. The `graphviz` Python package writes a DOT file and shells out to the `dot` binary, which must be installed separately (`apt install graphviz` or `brew install graphviz`).

```python
from graphviz import Digraph

g = Digraph(format="pdf", engine="dot")
g.attr(rankdir="LR", fontname="Helvetica",
       nodesep="0.4", ranksep="0.5", bgcolor="white")
g.attr("node", shape="box", style="rounded,filled",
       fontname="Helvetica", fontsize="10",
       fillcolor="#0072B2", fontcolor="white",
       color="none", margin="0.15,0.08")
g.attr("edge", fontname="Helvetica", fontsize="9",
       color="#444", arrowsize="0.7")

g.node("input",     "Input")
g.node("tokenize",  "Tokenize")
g.node("embed",     "Embedding")
g.node("blocks",    "Transformer\\nBlocks ×N", fillcolor="#D55E00")
g.node("head",      "Output Head")
g.node("logits",    "Logits")

g.edge("input",    "tokenize")
g.edge("tokenize", "embed")
g.edge("embed",    "blocks")
g.edge("blocks",   "head")
g.edge("head",     "logits")

out = "figures/fig_pipeline"
for fmt in ("pdf", "svg", "png"):
    g.format = fmt
    g.render(out, cleanup=True)
```

Tips for graphviz:

- **`rankdir="LR"`** lays out left-to-right (typical for pipelines). `"TB"` is top-to-bottom (default, typical for trees / hierarchies).
- **`nodesep` / `ranksep`** control spacing — bump up for breathing room.
- **Match colors to `colors.OKABE_ITO`** so the diagram matches the data figures. Hex codes work directly.
- **`fontname="Helvetica"`** matches what `pubstyle.apply()` sets for matplotlib. Coherence across figures.
- **For complex graphs**, the `neato`, `fdp`, or `circo` engines may lay out better than `dot`. Pass `engine="neato"` etc.

Graphviz's default look is recognizable and a bit dated — the customizations above (rounded boxes, filled colors, no border) bring it up to a modern paper aesthetic.

---

## Hand-authored SVG

Most control, slowest. Use when the diagram is one-off and important enough to be worth manual placement — a teaser figure, a key conceptual diagram, an illustrative schematic.

Two paths: write SVG directly, or use a Python library like `drawsvg`.

### Direct SVG

Best when you have a clear mental picture and just need to commit it to a file. Group related elements with `<g>`, use CSS-like attributes, keep coordinates round.

```python
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 200"
              font-family="Helvetica, Arial, sans-serif" font-size="11">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#444" />
    </marker>
  </defs>

  <!-- Boxes. dominant-baseline="central" with y at the box midline gives
       renderer-independent vertical centering. -->
  <g text-anchor="middle" dominant-baseline="central" fill="white">
    <rect x="20"  y="80" width="80" height="40" rx="6" fill="#0072B2" />
    <text x="60"  y="100">Input</text>

    <rect x="140" y="80" width="100" height="40" rx="6" fill="#D55E00" />
    <text x="190" y="100">Process</text>

    <rect x="280" y="80" width="80" height="40" rx="6" fill="#009E73" />
    <text x="320" y="100">Output</text>
  </g>

  <!-- Arrows -->
  <g stroke="#444" stroke-width="1.4" fill="none" marker-end="url(#arrow)">
    <line x1="100" y1="100" x2="140" y2="100" />
    <line x1="240" y1="100" x2="280" y2="100" />
  </g>
</svg>"""

from pathlib import Path
out = Path("figures")
out.mkdir(parents=True, exist_ok=True)
(out / "fig_diagram.svg").write_text(svg)
```

For PDF/PNG conversion of hand-SVG, use `cairosvg`:

```python
import cairosvg
cairosvg.svg2pdf(bytestring=svg.encode(), write_to="figures/fig_diagram.pdf")
cairosvg.svg2png(bytestring=svg.encode(), write_to="figures/fig_diagram.png",
                 output_width=1200)  # bumps DPI for the raster
```

### drawsvg

Pythonic API for the same thing. Good when the diagram is generated from data:

```python
import drawsvg as dw

d = dw.Drawing(480, 200, font_family="Helvetica, Arial, sans-serif", font_size=11)

def box(x, y, w, h, fill, label):
    d.append(dw.Rectangle(x, y, w, h, rx=6, fill=fill))
    d.append(dw.Text(label, x=x + w / 2, y=y + h / 2,
                     text_anchor="middle", dominant_baseline="central",
                     fill="white"))

box(20,  80, 80,  40, "#0072B2", "Input")
box(140, 80, 100, 40, "#D55E00", "Process")
box(280, 80, 80,  40, "#009E73", "Output")

# Arrows (with marker)
arrow = dw.Marker(0, 0, 10, 10, refX=9, refY=5, orient="auto", scale=0.7)
arrow.append(dw.Path(d="M0,0 L10,5 L0,10 z", fill="#444"))
d.append(arrow)
for x1, x2 in [(100, 140), (240, 280)]:
    d.append(dw.Line(x1, 100, x2, 100, stroke="#444", stroke_width=1.4,
                     marker_end=arrow))

d.save_svg("figures/fig_diagram.svg")
d.save_png("figures/fig_diagram.png")
```

---

## Choosing the right approach

A quick decision tree:

- **Paper is LaTeX, diagram is boxes-and-arrows / flowchart / state machine?** → TikZ (`references/tikz.md`).
- **Boxes-and-arrows with ≤10 nodes, want exact layout, paper isn't LaTeX?** → matplotlib.
- **15+ nodes, layout would be tedious to do by hand?** → graphviz.
- **Single hero diagram with non-grid layout (curves, branches, custom shapes)?** → SVG.
- **Want it to match the rest of your paper figures stylistically?** → matplotlib (same pipeline) for non-LaTeX papers; TikZ for LaTeX papers (matches body fonts and math).
- **Need to regenerate as data changes?** → matplotlib or graphviz programmatically.

Whichever you pick, run the QA checklist (`references/checklist.md`) before declaring done.
