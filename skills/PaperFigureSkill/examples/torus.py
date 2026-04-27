"""3D torus surface — demonstrates PaperFigureSkill on a 3D plot."""

import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))

import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

import pubstyle, colors, export

pubstyle.apply()

# Parametric torus. R = major radius (center → tube center), r = minor radius (tube).
R, r = 1.0, 0.35
n_u, n_v = 240, 96
u = np.linspace(0, 2 * np.pi, n_u)
v = np.linspace(0, 2 * np.pi, n_v)
U, V = np.meshgrid(u, v)

X = (R + r * np.cos(V)) * np.cos(U)
Y = (R + r * np.cos(V)) * np.sin(U)
Z = r * np.sin(V)

# Single-column square gives a clean 3D plot at print size.
fig = plt.figure(figsize=pubstyle.figsize("square"))
ax = fig.add_subplot(111, projection="3d", computed_zorder=False)

# Color and illuminate by Z (height). Single-channel encoding reads as a
# proper rendered surface — the lobe nearest the camera highlights, the
# inner-ring trough goes dark. Cleaner than coloring by the poloidal
# angle, which produces flat bands.
cmap = plt.get_cmap("viridis")
ls = LightSource(azdeg=315, altdeg=45)
facecolors = ls.shade(Z, cmap=cmap, blend_mode="soft", vert_exag=3.0)

ax.plot_surface(
    X, Y, Z,
    facecolors=facecolors,
    rcount=n_v, ccount=n_u,
    linewidth=0, antialiased=False, shade=False,
)

# Box aspect picks vertical squash. (1, 1, 0.5) reads as a torus seen
# slightly from above without being flattened into a ring.
ax.set_box_aspect((1, 1, 0.5))
ax.view_init(elev=28, azim=-55)

# Strip the 3D axes — the torus is the figure, not the box around it.
ax.set_axis_off()
ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-1.35, 1.35)
ax.set_zlim(-0.5, 0.5)

ax.set_title(fr"Torus ($R={R:g},\ r={r:g}$)", fontsize=10, pad=0)

paths = export.save(fig, "fig_torus", outdir=SKILL / "figures")
for p in paths:
    print("wrote", p)
