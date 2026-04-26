# Plot Patterns

Code snippets for the most common plot types in academic papers. Each one assumes the standard setup is already done:

```python
import sys
sys.path.insert(0, "<absolute-path-to-this-skill>/scripts")
import pubstyle, colors, export
import matplotlib.pyplot as plt
import numpy as np

pubstyle.apply()
colors.apply_cycle()
```

Adapt the data, axes labels, and series names — the styling decisions are already made.

## Table of Contents

- [Line plot with shaded error bands](#line-plot-with-shaded-error-bands)
- [Grouped bar chart with error bars](#grouped-bar-chart-with-error-bars)
- [Scatter plot with categories](#scatter-plot-with-categories)
- [Heatmap (e.g. confusion matrix, correlation)](#heatmap)
- [Violin / box plot for distributions](#violin--box-plot)
- [Multi-panel figure (subplots)](#multi-panel-figure)
- [Histogram / KDE for distributions](#histogram--kde)
- [Ablation comparison bar chart](#ablation-comparison-bar-chart)
- [3D surface (parametric or scalar field)](#3d-surface)

---

## Line plot with shaded error bands

The most common plot in ML/CS papers (training curves, scaling laws, ablations over a hyperparameter). Mean line + shaded ±1 std or 95% CI.

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("single"))

x = np.linspace(0, 100, 50)
methods = {
    "Ours":      (np.log1p(x) * 0.4 + 0.3, np.full_like(x, 0.04)),
    "Baseline":  (np.log1p(x) * 0.3 + 0.2, np.full_like(x, 0.05)),
    "Prior SOTA": (np.log1p(x) * 0.35 + 0.25, np.full_like(x, 0.045)),
}
palette = colors.categorical(len(methods))

for (name, (mean, std)), c in zip(methods.items(), palette):
    ax.plot(x, mean, color=c, label=name, linewidth=1.4)
    ax.fill_between(x, mean - std, mean + std, color=c, alpha=0.2, linewidth=0)

ax.set_xlabel("Training steps (×$10^3$)")
ax.set_ylabel("Accuracy")
ax.set_xlim(0, 100)
ax.legend(loc="lower right")

export.save(fig, "fig_training_curves")
```

Notes:
- `linewidth=0` on `fill_between` removes the thin outline that otherwise shows up at the edges.
- Pass `np.std(...) / np.sqrt(n)` instead of std for SEM, or 1.96× SEM for 95% CI.
- For log-scale x-axis (scaling laws, compute studies): `ax.set_xscale("log")`. Use `ax.set_xticks` with explicit values like `[1e6, 1e7, 1e8]` for clean labels.

## Grouped bar chart with error bars

Comparing methods across a few benchmarks. Three or four methods × three or four benchmarks is the sweet spot.

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("single"))

benchmarks = ["MMLU", "GSM8K", "HumanEval", "ARC"]
methods = {
    "Ours":     [73.2, 81.5, 67.4, 85.1],
    "Method A": [69.8, 76.2, 61.0, 82.3],
    "Method B": [71.5, 78.0, 63.8, 83.5],
}
errors = {
    "Ours":     [0.4, 0.6, 0.5, 0.3],
    "Method A": [0.5, 0.7, 0.6, 0.4],
    "Method B": [0.4, 0.5, 0.5, 0.4],
}

x = np.arange(len(benchmarks))
width = 0.26
palette = colors.categorical(len(methods))

for i, ((name, vals), c) in enumerate(zip(methods.items(), palette)):
    offset = (i - (len(methods) - 1) / 2) * width
    ax.bar(x + offset, vals, width, yerr=errors[name], label=name,
           color=c, edgecolor="white", linewidth=0.5,
           error_kw=dict(elinewidth=0.8, capsize=2, ecolor="#333"))

ax.set_xticks(x)
ax.set_xticklabels(benchmarks)
ax.set_ylabel("Accuracy (%)")
ax.set_ylim(50, 90)
ax.legend(loc="upper right", ncol=len(methods))

export.save(fig, "fig_benchmark_comparison")
```

Notes:
- `edgecolor="white"` with thin `linewidth` separates adjacent bars cleanly without adding a hard outline.
- `ax.set_ylim(50, ...)` cuts off uninformative low-accuracy space — use this when all methods are well above zero, but **never** start a bar chart's y-axis at a non-zero value if it makes differences look bigger than they are. State the ylim choice in the caption.
- `ncol=len(methods)` puts the legend in a single horizontal row at top.

## Scatter plot with categories

Two continuous variables, points colored by category. Common for embedding visualizations, parameter sweeps, scaling studies.

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("square"))

rng = np.random.default_rng(0)
n_per = 80
classes = ["Class A", "Class B", "Class C"]
palette = colors.categorical(len(classes))
markers = ["o", "s", "^"]   # second channel for grayscale-readability

for cls, c, m in zip(classes, palette, markers):
    cx, cy = rng.normal(0, 1.2, 2)
    pts = rng.normal([cx, cy], 0.5, (n_per, 2))
    ax.scatter(pts[:, 0], pts[:, 1], c=c, marker=m, s=14,
               alpha=0.7, edgecolors="none", label=cls)

ax.set_xlabel("Component 1")
ax.set_ylabel("Component 2")
ax.set_aspect("equal")
ax.legend(loc="best", markerscale=1.5)

export.save(fig, "fig_scatter_classes")
```

Notes:
- `edgecolors="none"` removes the default black outline that turns dense scatters into mud.
- Different `marker` shapes per class is the second-channel encoding for grayscale-readability — don't skip this.
- `markerscale=1.5` makes legend markers visible without enlarging the data points.

## Heatmap

Confusion matrices, correlation matrices, attention visualizations.

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("square"))

labels = ["cat", "dog", "bird", "fish", "frog"]
mat = np.random.default_rng(0).dirichlet(np.ones(5) * 5, 5)
np.fill_diagonal(mat, mat.diagonal() + 0.6)
mat = mat / mat.sum(axis=1, keepdims=True)

im = ax.imshow(mat, cmap="cividis", vmin=0, vmax=1, aspect="equal")

ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)
ax.set_xlabel("Predicted")
ax.set_ylabel("True")

# Annotate cells. White text on dark cells, dark text on light cells.
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = mat[i, j]
        ax.text(j, i, f"{v:.2f}",
                ha="center", va="center",
                color="white" if v < 0.5 else "black",
                fontsize=7)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.outline.set_linewidth(0.5)

export.save(fig, "fig_confusion")
```

Notes:
- `cividis` is the most colorblind-friendly sequential map. Use `RdBu_r` instead for diverging data (correlations centered on 0): `cmap="RdBu_r", vmin=-1, vmax=1`.
- Cell annotation flips text color at the midpoint so labels stay readable across the whole range.
- `fraction=0.046, pad=0.04` is a known good colorbar size for square heatmaps.

## Violin / box plot

Comparing distributions across conditions. Violin shows shape; box shows quartiles. Combine when you can.

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("single"))

rng = np.random.default_rng(0)
data = [
    rng.normal(0.72, 0.04, 100),
    rng.normal(0.78, 0.03, 100),
    rng.normal(0.81, 0.05, 100),
    rng.normal(0.79, 0.06, 100),
]
labels = ["Baseline", "+ Trick A", "+ Trick B", "+ Both"]
palette = colors.categorical(len(labels))

parts = ax.violinplot(data, showmeans=False, showmedians=False, showextrema=False)
for body, c in zip(parts["bodies"], palette):
    body.set_facecolor(c)
    body.set_edgecolor("none")
    body.set_alpha(0.55)

bp = ax.boxplot(data, widths=0.18, patch_artist=True,
                boxprops=dict(facecolor="white", edgecolor="#222", linewidth=0.8),
                medianprops=dict(color="#222", linewidth=1.0),
                whiskerprops=dict(color="#222", linewidth=0.8),
                capprops=dict(color="#222", linewidth=0.8),
                flierprops=dict(marker="o", markersize=2, markerfacecolor="#222",
                                markeredgecolor="none"))

ax.set_xticks(range(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=15, ha="right")
ax.set_ylabel("Accuracy")

export.save(fig, "fig_violin_box")
```

Notes:
- Violin alone hides quartiles; box-on-violin gives readers both shape and summary statistics.
- `rotation=15, ha="right"` is a good default for slightly long category labels — keeps them readable without going full vertical.

## Multi-panel figure

Two or more related plots side-by-side, with panel labels (a), (b), etc. Standard for results figures.

```python
fig, axes = plt.subplots(1, 3, figsize=pubstyle.figsize("double"),
                         gridspec_kw=dict(wspace=0.32))
palette = colors.categorical(3)
x = np.linspace(0, 10, 100)

# Panel (a): training curves
for i, (name, c) in enumerate(zip(["Ours", "Baseline A", "Baseline B"], palette)):
    axes[0].plot(x, 1 - np.exp(-x * (0.5 + 0.1 * i)), color=c, label=name)
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Accuracy")
axes[0].legend(loc="lower right")

# Panel (b): scaling
for i, c in enumerate(palette):
    axes[1].loglog(x[1:], (x[1:] ** (0.3 + 0.1 * i)) * 0.1, color=c)
axes[1].set_xlabel("Compute (FLOPs)")
axes[1].set_ylabel("Loss")

# Panel (c): bars
methods = ["A", "B", "C"]
axes[2].bar(methods, [62, 71, 78], color=palette, edgecolor="white", linewidth=0.5)
axes[2].set_ylabel("Score")
axes[2].set_ylim(0, 100)

# Panel labels (a), (b), (c) — top-left of each panel.
for ax, label in zip(axes, "abc"):
    ax.text(-0.15, 1.05, f"({label})", transform=ax.transAxes,
            fontsize=10, fontweight="bold", va="bottom", ha="left")

export.save(fig, "fig_multipanel")
```

Notes:
- `gridspec_kw=dict(wspace=0.32)` controls horizontal gap between panels. Tune until y-axis labels of one panel don't crowd the next panel's tick labels.
- Panel labels using `transform=ax.transAxes` place them in axes-relative coordinates so they stay put regardless of data range. `(-0.15, 1.05)` puts them outside the top-left corner.

## Histogram / KDE

For showing the shape of a distribution. KDE looks smoother but can hide multimodality if bandwidth is wrong; histogram is honest about the data but bin choice matters.

```python
import scipy.stats as stats

fig, ax = plt.subplots(figsize=pubstyle.figsize("single"))

rng = np.random.default_rng(0)
samples_a = rng.normal(0, 1, 500)
samples_b = rng.normal(1.5, 0.8, 500)
palette = colors.categorical(2)

bins = np.linspace(-4, 4, 41)
ax.hist(samples_a, bins=bins, density=True, color=palette[0],
        alpha=0.45, label="Condition A", edgecolor="none")
ax.hist(samples_b, bins=bins, density=True, color=palette[1],
        alpha=0.45, label="Condition B", edgecolor="none")

# Overlay KDE for smooth comparison
xs = np.linspace(-4, 4, 200)
ax.plot(xs, stats.gaussian_kde(samples_a)(xs), color=palette[0], linewidth=1.3)
ax.plot(xs, stats.gaussian_kde(samples_b)(xs), color=palette[1], linewidth=1.3)

ax.set_xlabel("Score")
ax.set_ylabel("Density")
ax.legend(loc="upper left")

export.save(fig, "fig_distribution")
```

Notes:
- `density=True` on the histogram puts both distributions on a common scale. Without it, the count axis will mislead anyone comparing groups of different sizes.
- The KDE overlay is optional; for a cleaner look, drop the histogram and keep only the KDE lines (with `fill_between` for shaded areas).

## Ablation comparison bar chart

Single-variable ablation: how does removing/swapping each component affect the metric? Horizontal bars work well when there are 5+ ablations because labels can be long.

```python
fig, ax = plt.subplots(figsize=pubstyle.figsize("single_tall"))

ablations = [
    ("Full method",        81.2),
    ("− Component A",      78.5),
    ("− Component B",      77.1),
    ("− Augmentation",     74.8),
    ("− Pretraining",      69.3),
    ("Random init",        51.0),
]
labels, values = zip(*ablations)
y = np.arange(len(labels))

bars = ax.barh(y, values, color=colors.OKABE_ITO[0], edgecolor="white", linewidth=0.5)
# Highlight the "full method" baseline
bars[0].set_color(colors.OKABE_ITO[1])

ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()                  # full method on top
ax.set_xlabel("Accuracy (%)")
ax.set_xlim(40, 90)

# Numeric annotation at the end of each bar
for yi, v in enumerate(values):
    ax.text(v + 0.5, yi, f"{v:.1f}", va="center", fontsize=7)

export.save(fig, "fig_ablation")
```

Notes:
- `invert_yaxis()` puts the full method at the top, with successive removals below — reads top-to-bottom like a list.
- Highlighting the baseline in a contrasting color makes the comparison obvious without a legend.

## 3D surface

Loss landscapes, manifolds, scalar fields, parametric surfaces (sphere, torus, Möbius strip). The `mpl_toolkits.mplot3d` backend ships with matplotlib — no extra deps.

```python
from matplotlib.colors import LightSource

# Parametric torus. R = major radius, r = minor radius.
R, r = 1.0, 0.35
n_u, n_v = 240, 96
u = np.linspace(0, 2 * np.pi, n_u)
v = np.linspace(0, 2 * np.pi, n_v)
U, V = np.meshgrid(u, v)

X = (R + r * np.cos(V)) * np.cos(U)
Y = (R + r * np.cos(V)) * np.sin(U)
Z = r * np.sin(V)

fig = plt.figure(figsize=pubstyle.figsize("square"))
ax = fig.add_subplot(111, projection="3d")

# Color AND illumination both come from the depth coordinate (Z).
# Shading by a parametric coordinate (U or V) produces flat angular bands;
# shading by Z produces a volumetric, "rendered" read.
cmap = plt.get_cmap("viridis")
ls = LightSource(azdeg=315, altdeg=45)
facecolors = ls.shade(Z, cmap=cmap, blend_mode="soft", vert_exag=3.0)

ax.plot_surface(
    X, Y, Z,
    facecolors=facecolors,
    rcount=n_v, ccount=n_u,
    linewidth=0, antialiased=False, shade=False,
)

# 3D framing: aspect, viewpoint, axes off.
ax.set_box_aspect((1, 1, 0.5))   # squash z so a flat torus reads correctly
ax.view_init(elev=28, azim=-55)  # standard "slightly above, slightly left"
ax.set_axis_off()                # the surface is the figure, not the box
ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35); ax.set_zlim(-0.5, 0.5)

ax.set_title(fr"Torus ($R={R:g},\ r={r:g}$)", fontsize=10, pad=0)
export.save(fig, "fig_torus")
```

Notes:
- **Shade by Z, not by a parametric coord.** `LightSource.shade(data, cmap)` lights from `data`'s gradient. If `data` is a parametric coordinate (U, V, θ, φ), you get banded angular gradients that look flat. If `data` is the surface's depth (Z), you get volumetric illumination — what readers expect from a 3D plot. For non-Z-monotonic surfaces (e.g. a folded manifold) shade by surface curvature or compute lighting from vertex normals via `shade_rgb`.
- **`set_axis_off`** strips the 3D box and tick frame. For most paper figures the box is chartjunk — the surface is the data.
- **`set_box_aspect((1, 1, h))`** controls vertical squash. Equal aspect (1, 1, 1) is rarely right for thin surfaces; tune `h` until the proportions read.
- **`view_init(elev, azim)`** picks the camera. Default `(30, -60)` is fine; (28, -55) used here just nudges the highlight onto the front lobe.
- **Stride control.** Use `rcount`/`ccount` (sample counts) not `rstride`/`cstride` (steps) — strides on a high-res mesh produce Moiré aliasing.
- **For scalar fields** (`Z = f(X, Y)` over a regular grid), drop the parametric U/V and just `np.meshgrid` over the X, Y range.

A runnable version of this lives in `examples/torus.py`.
