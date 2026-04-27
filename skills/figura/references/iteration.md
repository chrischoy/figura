# Iteration Loop: Render → View → Fix → Repeat

The point of iterating is that you write the figure code once and then look at it like a reader would. This catches defects that are invisible while you're writing code: fonts that look fine at design time but become unreadable at print size, legends that grow into the data once labels expand, ticks that collide on log axes, error bars that vanish.

## The Loop

1. **Render.**
   - matplotlib: `export.save(fig, name)` — produces PDF/SVG/PNG together.
   - TikZ: `bash scripts/tikz_build.sh figures/my_fig.tex figures` — compiles the standalone PDF and emits a 300 DPI PNG preview (and SVG if `pdf2svg` is installed). See `references/tikz.md`.
2. **View the PNG** using the `view` tool. The PNG is rendered at 300 DPI from a figure whose dimensions are the actual print size, so the pixels on screen correspond directly to what a reader sees on paper.
3. **List defects** using the inspection prompt below. Be specific — "small fonts" is too vague; "y-axis tick labels (0.0, 0.2, ...) are unreadable; need to be ~2x larger" is actionable.
4. **Apply fixes** from the catalog below (matplotlib defects) or `references/tikz.md` (TikZ-specific defects: arrow-through-text, loop-arrow-crossing-nodes, label-on-wrong-segment).
5. **Re-render and re-view.**
6. **Stop** after at most **2 full fix cycles**, or when only sub-pixel / cosmetic issues remain. Figure work has a long tail of nitpicks that don't matter to readers — don't chase perfection.

The stopping rule matters. Without it, you'll spend more time tweaking margins than the figure deserves. The bar is "a careful reader is not confused or annoyed", not "every pixel is perfect."

## Visual Inspection Prompt

Use this prompt when looking at the rendered PNG (whether inspecting yourself with `view` or delegating to a subagent — subagents have fresh eyes and avoid the confirmation bias of staring at code you just wrote).

```
Inspect this figure for user-visible defects at print size. The image is rendered at 300 DPI matching the figure's physical print dimensions, so what you see is what a reader sees in the printed paper.

Check specifically for:

LEGIBILITY (most common failure mode)
- Are all tick labels readable to a reader who isn't squinting?
- Are axis labels readable? Legend text? Annotations inside the plot?
- Are lines thick enough to follow at this size? Markers large enough to distinguish?
- Are error bars visible (not lost in line thickness)?

COLLISION / OVERLAP
- Do tick labels collide with each other (often happens at high tick density or after rotation)?
- Do x-tick labels collide with the x-axis label (insufficient labelpad)?
- Does the legend cover any data points, lines, or important text?
- In multi-panel figures, do panel titles or tick labels collide with adjacent panels?
- Do annotations overlap the data they're labeling?
- Does the colorbar collide with the main plot?

TRUNCATION / CLIPPING
- Is anything cut off at the figure edges? (Title, legend, tick labels, panel labels (a)/(b)/(c).)
- Is data clipped by axis limits that are too tight?
- Are long category labels truncated or running off the figure?

ENCODING
- Can the series be distinguished from each other?
- If the paper might be printed grayscale, can you still tell series apart? (Color alone fails for ~8% of male readers and for any grayscale print.)

LAYOUT
- Is whitespace evenly distributed, or is one region cramped while another is empty?
- Are subplot panels visually balanced (similar plot areas, aligned axes)?
- For grouped bar charts: are bars within a group close enough to read as a group, with gaps between groups?

DYNAMIC RANGE / AXIS SCALING
- Does any axis have one feature (outlier, dominant regime, plateau) that consumes >80% of the visual area while the comparison-relevant range is compressed into <20%?
- On a linear y-axis, does an outlier or one tall bar squeeze the meaningful spread into a thin strip?
- On a histogram with linear y-density, do bins that differ by orders of magnitude in count make the small bins effectively invisible?
- On a decay-to-zero curve, does most of the x-axis sit on the post-convergence flat region, hiding the timescale where the action happens?
- On linear-spaced histogram bins, does data spanning orders of magnitude in x cluster into one or two bins?

For multi-panel figures, walk panels in reading order (top-left → top-right → bottom-left → bottom-right). Report defects per-panel.

For each defect, describe:
- WHICH element (e.g., "x-axis tick labels in panel (b)")
- WHAT's wrong (e.g., "collide with each other after the rotation")
- SEVERITY: blocking (a reader would be confused or have to squint) vs minor (slightly ugly but readable)

Skip cosmetic nitpicks a reader wouldn't notice — sub-pixel positioning, 0.5pt size differences in non-critical text, slightly different vertical alignment of similar elements.
```

## Defect → Fix Catalog

When the inspection turns up an issue, find it in the table below for the standard fix. Apply, re-render, re-view.

### Legibility

| Defect | Fix |
|--------|-----|
| Tick labels unreadable at print size | `ax.tick_params(axis="both", labelsize=9)` *or* enlarge the figure: `figsize=pubstyle.figsize("single_tall")` instead of `"single"` |
| Axis labels unreadable | `ax.set_xlabel("...", fontsize=10)` (above the rcParam default) |
| Legend text unreadable | `ax.legend(fontsize=9)` |
| Lines too thin to follow | `linewidth=1.6` on each plot call, or `mpl.rcParams.update({"lines.linewidth": 1.6})` before plotting |
| Markers too small | `markersize=5` on plot call, or `s=20` on scatter |
| Error bars invisible | `error_kw=dict(elinewidth=1.0, capsize=3)` on `bar`, or `capsize=3, elinewidth=1.0` on `errorbar` |
| Math too small / pixelated | Use mathtext (`r"$x^2$"`) not Unicode — mathtext is vector. Confirm `pubstyle.apply()` was called. |

### Tick Labels Colliding

| Defect | Fix |
|--------|-----|
| X-tick labels collide with each other | `ax.tick_params(axis="x", labelrotation=30)` and `plt.setp(ax.get_xticklabels(), ha="right")` |
| Too many ticks (clutter) | `from matplotlib.ticker import MaxNLocator; ax.xaxis.set_major_locator(MaxNLocator(nbins=5))` |
| Long numeric labels (10000, 100000) | `ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))` or use `EngFormatter` for k/M/G |
| Date labels collide | `fig.autofmt_xdate()` rotates and right-aligns |
| Tick labels overlap axis label | `ax.xaxis.set_label_coords(0.5, -0.18)` to push axis label down, or `ax.xaxis.labelpad = 6.0` |

### Legend Issues

| Defect | Fix |
|--------|-----|
| Legend covers data | Try `loc="best"` first; if still bad, manually pick: `loc="upper right"`, `loc="lower left"`, etc. |
| No good location inside plot | Move outside: `ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)` then add `fig.subplots_adjust(right=0.78)` |
| Legend takes too much vertical space | Lay out horizontally: `ax.legend(ncol=N, loc="upper center", bbox_to_anchor=(0.5, 1.15))` |
| Legend frame distracting | Already off in `pubstyle`; if it sneaked back: `ax.legend(frameon=False)` |
| Legend entries duplicated (seaborn quirk) | `handles, labels = ax.get_legend_handles_labels(); by_label = dict(zip(labels, handles)); ax.legend(by_label.values(), by_label.keys())` |

### Multi-Panel Issues

| Defect | Fix |
|--------|-----|
| Panels too close, labels collide | Increase wspace/hspace in subplots: `plt.subplots(..., gridspec_kw=dict(wspace=0.35, hspace=0.4))` |
| Panel labels (a), (b), (c) clipped | Use axes-relative coords with margin: `ax.text(-0.18, 1.05, "(a)", transform=ax.transAxes, fontweight="bold", fontsize=10)` |
| Y-axis labels of left panels run into right panel's tick labels | Bump wspace, or use shared y-axis: `plt.subplots(..., sharey=True)` |
| Outer figure margins too tight | `fig.tight_layout()` before save (export.save uses `bbox_inches="tight"` already, which usually catches this) |
| Inset axes frame clipped, or colorbar pushed into adjacent panel's tick labels | Replace `tight_layout()` with `plt.subplots(..., constrained_layout=True)`. `tight_layout` doesn't account for inset frames or cbars in 2×2 grids; constrained_layout does, and co-operates with `bbox_inches='tight'` on save. |
| Colorbar in panel (c) of 2×2 still encroaches on panel (d) y-labels after constrained_layout | Move colorbar **inside** panel (c) as an inset: `cax = ax_c.inset_axes([0.85, 0.05, 0.04, 0.5]); fig.colorbar(im, cax=cax)`. Doesn't push panel (d) at all. |

### Truncation / Clipping

| Defect | Fix |
|--------|-----|
| Title/legend/labels cut off at edges | `bbox_inches="tight"` is default in `export.save()` — confirm you're using it. If still clipped, increase `pad_inches=0.1` |
| Data points right at axis edge | Add 5% padding: `ax.margins(x=0.05, y=0.05)` |
| Long category labels run off | Rotate (`rotation=30, ha="right"`) or wrap (`"\n".join(...)`) or switch to horizontal bar (`ax.barh(...)`) |
| Outside-plot legend cut off | After moving legend with `bbox_to_anchor`, call `fig.subplots_adjust(right=0.78)` to make room, or use `bbox_inches="tight"` |

### Color / Encoding

| Defect | Fix |
|--------|-----|
| Series indistinguishable in grayscale | Add second-channel encoding: `linestyle=["-", "--", ":"]` per series, or different `marker=` per series |
| Used `jet` / `rainbow` (auto-flag this) | Replace with `cmap="viridis"` (sequential) or `cmap="RdBu_r"` (diverging, with `vmin=-vmax`) |
| Bars in same color (lost grouping) | Pass an explicit color list: `colors=colors.categorical(n)` |
| Yellow (`#F0E442`) text or thin lines on white | Yellow has low contrast; use it only for filled regions, not lines or text |
| Diverging cmap not centered on zero | Use `from matplotlib.colors import TwoSlopeNorm; norm = TwoSlopeNorm(vcenter=0)` and pass `norm=norm` to `imshow` |
| 3D surface looks flat / banded (no volumetric depth) | `LightSource.shade(coord, cmap)` lit by a parametric coord (U, V, θ) gives angular bands. Switch to `ls.shade(Z, cmap=cmap, blend_mode="soft", vert_exag=2-3)` so the lighting comes from depth |
| 3D surface has Moiré aliasing on the mesh | Replace `rstride=1, cstride=1` with `rcount=n_v, ccount=n_u` (sample counts, not steps) and `antialiased=False` |

### Dynamic Range / Axis Scaling

When one feature of the data dominates the axis and squeezes the comparison band into a strip. Most-hit defect class on real papers.

| Defect | Fix |
|--------|-----|
| Outlier on linear y-axis squeezes the comparison band into <20% of the panel | Cap y-axis at the comparison-relevant max + 10% headroom; mark the off-panel outlier with a broken-axis indicator + arrow annotation (snippet in "Axis Range / Ticks" below) |
| Histogram with linear y-density on data spanning orders of magnitude | `ax.set_yscale('log')` on the density axis. For zero-inclusive distributions use `'symlog'` with `linthresh=` near the smallest non-zero density |
| Linear-spaced bins on data spanning orders of magnitude in x | `bins = np.geomspace(data.min(), data.max(), N)` and `ax.set_xscale('log')`. For zero-inclusive data use `np.concatenate([[0], np.geomspace(eps, max, N)])` |
| `density=True` on histograms when sample counts differ across groups | Density hides effective sample size. Either annotate `n=` in the legend, or use raw counts with separate panels, or normalize by group max instead of integral |
| Bin count too high (jagged histogram) or too low (smoothed-over modes) | Start with `bins=int(np.sqrt(n))` (Rice rule) or `'fd'` (Freedman-Diaconis: `bins='fd'`). Use KDE overlay for visual smoothing without committing to one bin count |
| Decay-to-zero curve where 90% of the x-axis is post-convergence flatline | `ax.set_xscale('log')` to spread early steps; or use an inset axes for the early-step region (`ax.inset_axes([0.4, 0.3, 0.55, 0.6])`) showing the action with main axes preserving the full range |
| Multi-modal distribution where modes differ by orders of magnitude in density | Log y-density (above) **plus** annotate each mode with text (`'early steps'` / `'late steps'`) — the log scale is honest but the modes still need labels for fast skim |

### Axis Range / Ticks

| Defect | Fix |
|--------|-----|
| Bar chart y-axis doesn't start at 0 (misleading) | `ax.set_ylim(0, ...)`. If you have a legitimate reason to truncate, use a "broken axis" instead and state it in the caption |
| Y-axis range too wide (data squashed) | `ax.set_ylim(actual_min - 0.05*range, actual_max + 0.05*range)` |
| One outlier point lives above the panel (would distort y-range if shown) | Don't mark with a red `×` — reads as "error/excluded data point" in scientific figures. Use a broken-axis indicator + arrow annotation: <br>```python<br>d = .015<br>kw = dict(transform=ax.transAxes, color='k', clip_on=False, lw=0.8)<br>ax.plot((-d, +d), (0.96-d, 0.96+d), **kw)<br>ax.plot((-d, +d), (0.94-d, 0.94+d), **kw)<br>ax.annotate('config X: 73.9° (diverged)',<br>            xy=(x_outlier, ax.get_ylim()[1]*0.97),<br>            xytext=(x_outlier-0.2, ax.get_ylim()[1]*0.85),<br>            arrowprops=dict(arrowstyle='->', lw=0.8), fontsize=7)<br>```|
| Bar chart with one giant bar buries the spread of the others | If the giant bar is rhetorical ("raw beats nothing, obvious") not informational, **drop it** and put the value in the caption ("baseline X: 38.7° off-chart"). The y-range then fits the comparison that actually matters. Alternative: broken-axis at y=N where N just clears the small bars. |
| Inset axes overlap legend (both top-right) | Place inset where data is sparse. For log-y plots descending from upper-left, lines crowd the bottom — put inset at `ax.inset_axes([0.45, 0.10, 0.5, 0.45])` (lower-right). Keep legend top-right. Or move legend below figure: `bbox_to_anchor=(0.5, -0.18), ncol=N`. |
| Inset y-range too tight on the headline line | Headline line touching the inset frame edge looks like clipping. Pad the inset y-range by ~10% beyond the headline's std band: if the headline is at 21.56 ± 0.06, set inset `ylim=[20.8, 26.2]` not `[21, 26]`. |
| Reference line on a viridis scatter is hard to spot | Don't use gray (`#A6A6A6`) for the reference — it sits inside viridis's mid-luminance range and reads as "mid-value data point". Use black (`#1A1A1A`); it falls outside the viridis spectrum and reads as "annotation, not data". |
| Bimodal histogram with empty middle reads as one weird distribution | Add 7pt text annotations near each peak (`'early steps'` / `'late steps'`), or a vertical dashed line at the gap boundary, or hatching (`hatch='//'` vs `hatch='\\\\'`) on top of color+alpha. Annotations are usually cheapest. |
| Log axis with bad ticks | `ax.set_xscale("log"); ax.set_xticks([1e3, 1e4, 1e5, 1e6])` and use `LogFormatterSciNotation` for clean labels |
| Heatmap cell values invisible (low contrast) | Flip annotation color at midpoint: `color="white" if value < 0.5 * vmax else "black"` |

## Worked Example

A typical iteration: bar chart of method comparison, first render reveals two issues.

**Inspection finds:**
- Method names on x-axis are cut off / rotated weirdly
- Legend overlaps the tallest bar in the upper-right

**Fix:**
```python
# Before:
ax.set_xticks(range(len(method_names)))
ax.set_xticklabels(method_names)
ax.legend()

# After:
ax.set_xticks(range(len(method_names)))
ax.set_xticklabels(method_names, rotation=30, ha="right")
ax.legend(loc="upper left", ncol=2)        # move out of the data, lay flat
ax.set_ylim(0, ax.get_ylim()[1] * 1.1)     # extra headroom for the legend
```

(Always `set_xticks` before `set_xticklabels` — matplotlib ≥3.5 warns when labels are set without a fixed tick locator.)

Re-render, re-view. If both issues are gone and nothing new appeared, **stop**. If a new defect appears (e.g., the rotated labels now overflow the bottom edge), do one more cycle, then stop regardless.

## When to Break the Stopping Rule

Two cycles is the default cap, but extend if:
- A truly blocking issue remains (data clipped, text unreadable, legend covering most of the data).
- Each cycle is making clear progress. If you fixed 3 defects on cycle 1 and 1 defect on cycle 2 and there are still 2 left, one more cycle is warranted.

Don't extend if:
- The remaining issues are aesthetic preferences (could the bars be a slightly different shade?).
- You're moving things by 1–2 pixels.
- You're second-guessing layout choices that were fine.

When in doubt, ship it. Reviewers care about the science; figure perfectionism past a certain point is invisible to them.
