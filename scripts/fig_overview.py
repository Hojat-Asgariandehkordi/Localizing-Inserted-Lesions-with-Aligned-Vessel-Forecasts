"""Figure 1: problem, paired design, aligned vs rotated forecast.

Panel (a) is BioRender art (figures/biorender/overview_draft2.jpg, problem panel
only, no BioRender text kept). Panels (b)-(d) are generated here on a synthetic
slice with the same vessel layout (long vessel + steep branch, lesion lower-left)
so the markers in (c) and (d) are computed by a simplified readout
(local-mean removal + one compact template, r = 2.7 mm, searched within 10 mm).
All lettering is typeset here in Times.
"""
import pathlib
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import style
from style import C

style.apply()
ROOT = pathlib.Path(__file__).resolve().parents[1]
PE = [pe.withStroke(linewidth=1.8, foreground="#1b2a33")]
GOLD, RED, TEAL, ORNG = "#e0a92e", "#d1495b", C["profile_aligned"], C["profile_rotated"]

# ---------------------------------------------------------------- synthetic slice
N, PX = 64, 0.7
yy, xx = np.mgrid[:N, :N].astype(float)
c = (N - 1) / 2
X, Y = (xx - c) * PX, (yy - c) * PX            # mm, Y points down (image rows)
R = np.hypot(X, Y)
rng = np.random.default_rng(3)
bg = ndi.gaussian_filter(rng.normal(0, 1, (N, N)), 2.0) * 18 + ndi.gaussian_filter(rng.normal(0, 1, (N, N)), 0.8) * 10


def tube(p0, d, w, a, half=False):
    d = np.asarray(d, float); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
    dist = (X - p0[0]) * n[0] + (Y - p0[1]) * n[1]
    along = (X - p0[0]) * d[0] + (Y - p0[1]) * d[1]
    t = a * np.exp(-dist ** 2 / (2 * w ** 2))
    return t / (1 + np.exp(-along / 0.8)) if half else t


JUNC = (2.5, 1.0)
v = tube(JUNC, (1, 0.5), 1.7, 210) + tube(JUNC, (0.3, -1), 1.2, 170, half=True)
LES = (-5.5, 5.0)
s = 180 * np.exp(-((X - LES[0]) ** 2 + (Y - LES[1]) ** 2) / (2 * 1.8 ** 2))
y0, y1 = bg + v, bg + v + s
f, fr = v, np.rot90(v)                         # forecast (exact here) and its quarter-turn


def peak(img):
    r = 2.7 / PX
    k = np.clip(1 - ((xx - c) ** 2 + (yy - c) ** 2) / r ** 2, 0, None) ** 0.8
    k = k[int(c - 6):int(c + 7), int(c - 6):int(c + 7)]; k = k - k.mean()
    sc = ndi.correlate(img - ndi.gaussian_filter(img, 4), k)
    sc = np.where(R <= 10, sc, -np.inf)
    i = np.unravel_index(np.argmax(sc), sc.shape)
    return X[i], Y[i]


EXT = [X.min() - PX / 2, X.max() + PX / 2, Y.max() + PX / 2, Y.min() - PX / 2]
KW = dict(cmap="gray", vmin=-60, vmax=235, extent=EXT, interpolation="bilinear")

# ---------------------------------------------------------------- layout
H = 2.2
fig = plt.figure(figsize=(style.TXT_W, H))
w = 0.148; h = w * style.TXT_W / H; b0 = 0.255
pos = {"a": 0.0, "b1": 0.222, "b2": 0.398, "c": 0.632, "d": 0.818}
ax = {k: fig.add_axes([x, b0, w, h]) for k, x in pos.items()}
for a in ax.values():
    a.set_xticks([]); a.set_yticks([]); a.grid(False)
    for sp in a.spines.values():
        sp.set_visible(True); sp.set_color(C["axis"]); sp.set_linewidth(0.6)


def mark(a, p, ok):
    if ok:
        a.plot(*p, marker="P", ms=8.5, color=TEAL, mec="white", mew=1.0, zorder=6)
    else:
        a.plot(*p, marker="X", ms=8.5, color=RED, mec="white", mew=1.0, zorder=6)


def core(a, lw=0.8):
    a.add_patch(Circle((0, 0), 10, fill=False, ls=(0, (1, 1.6)), lw=lw, color="white", zorder=4))


def label(a, x, y, t, **k):
    a.text(x, y, t, transform=a.transAxes, fontsize=7, color="white", zorder=8,
           bbox=dict(boxstyle="round,pad=0.2", fc="#1b2a33", ec="none", alpha=0.75), **k)


# (a) BioRender problem panel ---------------------------------------------------
im = Image.open(ROOT / "figures/biorender/overview_draft2.jpg").crop((24, 36, 254, 266))
ax["a"].imshow(im, extent=[0, 1, 0, 1])
ax["a"].set_xlim(0, 1); ax["a"].set_ylim(0, 1)
ax["a"].annotate("detector's mark", xy=(0.58, 0.47), xytext=(0.62, 0.9), fontsize=7, color="white",
                 ha="center", path_effects=PE, arrowprops=dict(arrowstyle="-", lw=0.7, color="white"))
ax["a"].annotate("lesion", xy=(0.3, 0.27), xytext=(0.2, 0.06), fontsize=7, color=GOLD, ha="center",
                 path_effects=PE, arrowprops=dict(arrowstyle="-", lw=0.7, color=GOLD))

# (b) paired crops with shared exterior -----------------------------------------
for k, img, ttl in [("b1", y0, "control"), ("b2", y1, "control + lesion")]:
    a = ax[k]
    a.imshow(img, **KW)
    a.imshow(np.where(R > 14, 1.0, np.nan), cmap="Blues", vmin=0, vmax=2.4, alpha=0.32, extent=EXT)
    a.add_patch(Circle((0, 0), 14, fc="#d9dee1", ec="white", lw=1.0, alpha=0.18, hatch="////", zorder=3))
    a.contour(X, Y, f, levels=[60], colors=[TEAL], linewidths=0.9, zorder=5)
    core(a)
    if k == "b2":
        a.add_patch(Circle(LES, 3.0, fill=False, lw=1.0, color=GOLD, zorder=6))
    a.set_xlim(EXT[0], EXT[1]); a.set_ylim(EXT[2], EXT[3])
    a.set_title(ttl, fontsize=7.6, pad=2)
# bracket under both crops: same exterior
yb = b0 - 0.025
fig.add_artist(matplotlib.lines.Line2D([pos["b1"] + 0.01, pos["b1"] + 0.01, pos["b2"] + w - 0.01, pos["b2"] + w - 0.01],
                                       [yb + 0.02, yb, yb, yb + 0.02], transform=fig.transFigure, lw=0.8, color=C["ink"]))
fig.text((pos["b1"] + pos["b2"] + w) / 2, yb - 0.012,
         "same exterior (blue, outside the hatched 14-mm ball)  $\\Rightarrow$  one forecast $f$ (teal) for both",
         fontsize=7, ha="center", va="top", color=C["ink"])

# (c) aligned, (d) rotated ------------------------------------------------------
for k, img, fld, col, ttl in [("c", y1 - f, f, TEAL, "subtract aligned $f$"),
                              ("d", y1 - fr, fr, ORNG, "subtract rotated $f$ (sham)")]:
    a = ax[k]
    a.imshow(img, **KW)
    a.contour(X, Y, fld, levels=[60], colors=[col], linewidths=0.8, zorder=4)
    core(a)
    a.add_patch(Circle(LES, 3.0, fill=False, lw=1.0, color=GOLD, zorder=5))
    p = peak(y1 - fld)
    ok = np.hypot(p[0] - LES[0], p[1] - LES[1]) <= 3
    mark(a, p, ok)
    a.set_xlim(EXT[0], EXT[1]); a.set_ylim(EXT[2], EXT[3])
    a.set_title(ttl, fontsize=7.6, pad=2, color=col)
    label(a, 0.04, 0.04, "mark on lesion" if ok else "mark stays\non vessel", ha="left", va="bottom")

# panel letters and group titles
T = 0.875
for x, t in [(0.0, r"$\bf(a)$ Problem"),
             (pos["b1"], r"$\bf(b)$ Paired crops, shared exterior"),
             (pos["c"], r"$\bf(c)$ Same $f$, aligned vs rotated")]:
    fig.text(x, T, t, fontsize=8.4, va="top")


def arrow(x0, y0, x1, y1, rad=0.0):
    fig.add_artist(FancyArrowPatch((x0, y0), (x1, y1), transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=8, lw=0.9, color=C["muted"], connectionstyle=f"arc3,rad={rad}"))


ym = b0 + h / 2
arrow(pos["a"] + w + 0.008, ym, pos["b1"] - 0.008, ym)
arrow(pos["b2"] + w + 0.008, ym, pos["c"] - 0.01, ym)

# footer: outputs and endpoints
fig.add_artist(FancyBboxPatch((0.0, 0.012), 0.995, 0.125, transform=fig.transFigure, boxstyle="round,pad=0.004",
                              fc="#eef3f2", ec="none"))
fig.text(0.5, 0.075,
         "Each readout returns two outputs:  accept the crop?  (threshold set for 10% false positives on controls)   and   one mark.\n"
         "Crop sensitivity = accepted lesion crops.   Localized sensitivity = accepted and mark within 3 mm of the lesion (gold ring).   White dashed or dotted circle: 10-mm search core.",
         fontsize=7.1, ha="center", va="center", color=C["ink"], linespacing=1.35)

fig.savefig(ROOT / "figures/overview.pdf")
fig.savefig("/tmp/overview.png", dpi=200)
print("peaks", peak(y1), peak(y1 - f), peak(y1 - fr))
