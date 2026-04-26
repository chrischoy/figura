"""
Matplotlib rcParams for publication-quality figures.

The defaults matplotlib ships with are designed for screen exploration, not
for print. This module sets a small, deliberate set of rcParams that fix the
most common "this looks like default matplotlib" tells:

- Embed TrueType fonts in PDFs (so journals and arXiv don't choke)
- Tight, readable font sizes at typical column widths
- Top/right spines off, subtle ticks, gridlines off by default
- Vector-friendly line widths and marker sizes

Usage:
    import pubstyle
    pubstyle.apply()                    # generic / multi-venue defaults
    pubstyle.apply(venue="neurips")     # tweaks for specific venues
    pubstyle.apply(extra={"font.size": 11})  # one-off override
"""

from typing import Optional

import matplotlib as mpl


# Sensible defaults for a single-column figure (~3.3 in wide) at print size.
_BASE = {
    # --- Fonts: embed properly so PDFs survive journal pipelines.
    "pdf.fonttype": 42,             # TrueType in PDF (not Type 3 — journals reject Type 3)
    "ps.fonttype": 42,              # same for PostScript
    "svg.fonttype": "none",         # keep text as text in SVG (editable, smaller files)
    "font.family": "sans-serif",
    "font.sans-serif": [
        # Deliberate fallback chain. DejaVu Sans is matplotlib's default;
        # we keep it last so it's a true fallback, not the first choice.
        "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans",
    ],

    # Sizes tuned for ~3.3 in single-column at print size.
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,

    # --- Axes: clean, no top/right spines by default.
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "axes.labelpad": 3.0,
    "axes.titlepad": 6.0,

    # --- Ticks: short, outward, just enough to read.
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "xtick.minor.size": 1.5,
    "ytick.minor.size": 1.5,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.direction": "out",
    "ytick.direction": "out",

    # --- Lines & markers: visible at print size, not chunky.
    "lines.linewidth": 1.25,
    "lines.markersize": 4.0,
    "patch.linewidth": 0.8,

    # --- Grid: off by default. Turn on per-figure when it actually helps.
    "axes.grid": False,
    "grid.linewidth": 0.5,
    "grid.alpha": 0.3,
    "grid.color": "#b0b0b0",

    # --- Legend: thin frame, tight padding.
    "legend.frameon": False,
    "legend.handlelength": 1.5,
    "legend.handletextpad": 0.5,
    "legend.borderaxespad": 0.5,

    # --- Figure: white background, sensible DPI.
    # bbox/pad live in export.save() so they apply to every save call there
    # without forcing them on raw plt.savefig() use.
    "figure.facecolor": "white",
    "figure.dpi": 150,              # screen preview
    "savefig.dpi": 300,             # raster export DPI (handled in export.py too)

    # --- Math: mathtext (no LaTeX dependency) by default.
    # Sans math glyphs that match the Helvetica/Arial body text. DejaVu
    # math next to Helvetica labels is a visible mismatch in $x^2$ etc.
    "mathtext.fontset": "stixsans",
    "mathtext.default": "regular",
}


# Per-venue overrides. Generic by default; tweak only where venues differ
# meaningfully.
_VENUES = {
    "generic": {},
    "neurips": {
        "font.size": 8,
        "axes.labelsize": 8,
    },
    "icml": {
        "font.size": 8,
        "axes.labelsize": 8,
    },
    "iclr": {
        "font.size": 8,
        "axes.labelsize": 8,
    },
    "ieee": {
        # IEEE columns are narrower; smaller fonts for legibility at scale.
        "font.size": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
    },
    "acm": {
        "font.size": 8,
        "axes.labelsize": 8,
    },
    "nature": {
        # Nature mandates Helvetica / Arial sans-serif (we already use it)
        # and runs small.
        "font.size": 7,
        "axes.labelsize": 7,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "legend.fontsize": 6,
    },
}


def apply(venue: str = "generic", extra: Optional[dict] = None) -> None:
    """Apply publication-quality rcParams.

    Resets matplotlib to its built-in defaults first, then layers on the
    base style, the per-venue overrides, and the user's `extra` dict. This
    means switching venues mid-session does not leak settings from a prior
    apply() call.

    Args:
        venue: One of 'generic', 'neurips', 'icml', 'iclr', 'ieee', 'acm', 'nature'.
        extra: Optional dict of additional rcParams to override on top.
    """
    if venue not in _VENUES:
        raise ValueError(
            f"Unknown venue '{venue}'. Choose from: {sorted(_VENUES)}"
        )
    mpl.rcdefaults()
    params = dict(_BASE)
    params.update(_VENUES[venue])
    if extra:
        params.update(extra)
    mpl.rcParams.update(params)


# Standard column widths in inches. Pass to plt.subplots(figsize=...).
_SIZES = {
    "single":      (3.3, 2.2),    # single-column, ~3:2 — most common
    "single_tall": (3.3, 3.0),    # single-column, taller (square-ish)
    "double":      (6.8, 2.6),    # double-column, wide and short
    "double_tall": (6.8, 4.0),    # double-column, multi-panel
    "square":      (3.3, 3.3),    # single-column square (correlation, confusion)
}


def figsize(kind: str = "single") -> tuple:
    """Return a sensible figure size in inches.

    Args:
        kind: One of 'single', 'single_tall', 'double', 'double_tall', 'square'.
    """
    if kind not in _SIZES:
        raise ValueError(f"Unknown size '{kind}'. Choose from: {sorted(_SIZES)}")
    return _SIZES[kind]
