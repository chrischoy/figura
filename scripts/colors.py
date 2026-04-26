"""
Colorblind-safe color palettes for publication figures.

Three categories of palette, three choices:

CATEGORICAL (different conditions, methods, classes):
    Okabe-Ito (8 colors) — Wong, Nature Methods 2011. Recommended default.
    Designed for colorblind accessibility, distinguishable in grayscale.
    Tol Muted (9 colors) — Paul Tol's qualitative scheme. Lower saturation,
    nice for dense scatter plots where Okabe-Ito feels loud.

SEQUENTIAL (ordered data — depth, density, time, magnitude):
    viridis, cividis, magma, plasma. All perceptually uniform and
    colorblind-safe. cividis is the most colorblind-friendly. Pass as
    cmap="viridis".

DIVERGING (signed data with meaningful zero — residuals, correlations,
log-fold-change):
    RdBu_r, coolwarm, PuOr_r, BrBG_r. Pass as cmap="RdBu_r".

AVOID jet, rainbow, hsv — perceptually nonlinear, mis-rank in grayscale,
unsafe for colorblind readers.
"""

import matplotlib as mpl
from cycler import cycler


# Okabe-Ito palette (Wong, Nature Methods 2011). Yellow is pushed to the
# end because it has low contrast on white — that way default cycles up to
# 7 series stay legible without manual reordering.
OKABE_ITO = [
    "#0072B2",  # blue            — primary
    "#D55E00",  # vermillion      — secondary, contrasts strongly with blue
    "#009E73",  # bluish green
    "#CC79A7",  # reddish purple
    "#56B4E9",  # sky blue
    "#E69F00",  # orange
    "#000000",  # black           — for emphasis or baselines
    "#F0E442",  # yellow          — last; low contrast on white, use sparingly
]


# Tol's "muted" qualitative scheme. Lower saturation, paper-friendly
# for dense scatter plots.
TOL_MUTED = [
    "#332288",  # indigo
    "#88CCEE",  # cyan
    "#44AA99",  # teal
    "#117733",  # green
    "#999933",  # olive
    "#DDCC77",  # sand
    "#CC6677",  # rose
    "#882255",  # wine
    "#AA4499",  # purple
]


_PALETTES = {
    "okabe-ito": OKABE_ITO,
    "tol-muted": TOL_MUTED,
}


def categorical(n: int = 8, palette: str = "okabe-ito") -> list:
    """Return a colorblind-safe categorical palette as hex strings.

    Args:
        n: Number of colors. If > palette length, raises — consider whether
           you really need that many distinct categories in one chart
           (rarely the right call in a paper figure; split into panels).
        palette: 'okabe-ito' (8 colors, default) or 'tol-muted' (9 colors).
    """
    if palette not in _PALETTES:
        raise ValueError(
            f"Unknown palette '{palette}'. Choose from: {sorted(_PALETTES)}"
        )
    src = _PALETTES[palette]
    if n > len(src):
        alt = "tol-muted" if palette != "tol-muted" else "okabe-ito"
        raise ValueError(
            f"Requested {n} colors but '{palette}' has only {len(src)}. "
            f"Try palette='{alt}' for one more, or split categories across "
            "multiple panels."
        )
    return src[:n]


def apply_cycle(palette: str = "okabe-ito") -> None:
    """Set matplotlib's default property cycle to a colorblind-safe palette.

    Call once after pubstyle.apply() and every plot() call inherits the
    palette without passing color= explicitly.
    """
    if palette not in _PALETTES:
        raise ValueError(
            f"Unknown palette '{palette}'. Choose from: {sorted(_PALETTES)}"
        )
    mpl.rcParams["axes.prop_cycle"] = cycler(color=_PALETTES[palette])


# --- Sequential & diverging recommendations.
# These are matplotlib colormap names; pass directly to cmap= arguments.

SEQUENTIAL = ("viridis", "cividis", "magma", "plasma")
"""Single-hue, perceptually uniform. Use for ordered data (heatmaps, density)."""

DIVERGING = ("RdBu_r", "coolwarm", "PuOr_r", "BrBG_r")
"""Two-hue, centered. Use when data has a meaningful zero / midpoint."""

AVOID = ("jet", "rainbow", "hsv", "gist_rainbow", "nipy_spectral")
"""Perceptually nonlinear; misleading in grayscale; bad for colorblind readers."""
