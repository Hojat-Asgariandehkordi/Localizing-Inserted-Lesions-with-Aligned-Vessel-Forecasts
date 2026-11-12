"""Figure 1: problem and idea, on a synthetic axial slice.

The slice is generated here (no patient data): smooth noise background, two
crossing Gaussian tubes that form a compact junction, and a faint compact
lesion 6.4 mm from the proposal centre. The blob score is a simplified version
of the paper's readout (local-mean removal + one compact template, r = 2.7 mm,
searched within 10 mm), so the markers are computed, not drawn by hand.
"""
import numpy as np
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
import style
import matplotlib.patheffects as pe
PE = [pe.withStroke(linewidth=1.6, foreground="#1b2a33")]
from style import C

style.apply()
N, PX = 64, 0.7
yy, xx = np.mgrid[:N, :N].astype(float)
c = (N - 1) / 2
X, Y = (xx - c) * PX, (yy - c) * PX
R = np.hypot(X, Y)
rng = np.random.default_rng(3)
bg = ndi.gaussian_filter(rng.normal(0, 1, (N, N)), 2.0) * 18 + ndi.gaussian_filter(rng.normal(0, 1, (N, N)), 0.8) * 10


def tube(p0, d, w, a):
    d = np.asarray(d, float); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
    dist = (X - p0[0]) * n[0] + (Y - p0[1]) * n[1]
    return a * np.exp(-dist ** 2 / (2 * w ** 2))


v = tube((2.0, -1.0), (1, 0.45), 1.5, 200) + tube((2.0, -1.0), (-0.35, 1), 1.4, 190)
LES = (-6.0, 4.5)
s = 175 * np.exp(-((X - LES[0]) ** 2 + (Y - LES[1]) ** 2) / (2 * 1.7 ** 2))
y1 = bg + v + s
f_al = v                      # exterior forecast (exact here, for illustration)
f_rot = np.rot90(v)           # same field, quarter-turn about the centre


def peak(img):
    r = 2.7 / PX
    k = np.clip(1 - ((xx - c) ** 2 + (yy - c) ** 2) / r ** 2, 0, None) ** 0.8
    k = k[int(c - 6):int(c + 7), int(c - 6):int(c + 7)]; k = k - k.mean()
    sc = ndi.correlate(img - ndi.gaussian_filter(img, 4), k)
    sc = np.where(R <= 10, sc, -np.inf)
    i = np.unravel_index(np.argmax(sc), sc.shape)
    return X[i], Y[i]


ext = [X.min() - PX / 2, X.max() + PX / 2, Y.max() + PX / 2, Y.min() - PX / 2]
KW = dict(cmap="gray", vmin=-60, vmax=235, extent=ext, interpolation="bilinear")

fig = plt.figure(figsize=(style.TXT_W, 2.05))
W = 0.148; gap = 0.012; x0 = 0.0; b = 0.13; h = 0.66
axs = [fig.add_axes([x0 + i * (W + gap) + (0.012 if i else 0), b, W, h]) for i in range(4)]
axt = fig.add_axes([x0 + 4 * (W + gap) + 0.035, b - 0.06, 1 - (x0 + 4 * (W + gap) + 0.035), h + 0.155])

titles = [("a", "Observed crop"), ("b", "Exterior forecast $f$"), ("c", "Subtract aligned $f$"),
          ("d", "Subtract rotated $f$")]
imgs = [y1, np.where(R > 14, y1, np.nan), y1 - f_al, y1 - f_rot]
for ax, (L, t), im in zip(axs, titles, imgs):
    ax.set_facecolor("#cfd6da")
    ax.imshow(im, **KW)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_color(C["axis"])
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_title(f"$\\bf({L})$ {t}", fontsize=7.8, loc="left", pad=3)

# masked region and search region
for ax in axs:
    ax.add_patch(Circle((0, 0), 14, fill=False, ls=(0, (3, 2)), lw=0.7, color="white"))
axs[1].add_patch(Circle((0, 0), 14.6, fill=True, fc="#cfd6da", ec="none", hatch="////", lw=0, alpha=1))
axs[1].add_patch(Circle((0, 0), 14, fill=False, ls=(0, (3, 2)), lw=0.7, color="white"))
axs[1].contour(X, Y, f_al, levels=[60], colors=[C["profile_aligned"]], linewidths=1.0)
axs[1].text(0, 0, "hidden\n($r<14$ mm)", ha="center", va="center", fontsize=7, color=C["ink"],
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.2))
axs[3].contour(X, Y, f_rot, levels=[60], colors=[C["profile_rotated"]], linewidths=0.9)
axs[2].contour(X, Y, f_al, levels=[60], colors=[C["profile_aligned"]], linewidths=0.9)


def mark(ax, p, ok):
    col = C["profile_aligned"] if ok else "#d1495b"
    ax.plot(*p, marker="+", ms=9, mew=2.4, color="white", zorder=5)
    ax.plot(*p, marker="+", ms=8, mew=1.3, color=col, zorder=6)


for ax, im in zip([axs[0], axs[2], axs[3]], [y1, y1 - f_al, y1 - f_rot]):
    p = peak(im)
    ok = np.hypot(p[0] - LES[0], p[1] - LES[1]) <= 3
    mark(ax, p, ok)
    ax.add_patch(Circle(LES, 3.0, fill=False, lw=0.8, color="#f2c14e", zorder=4))

# annotations in (a)
a = axs[0]
a.annotate("strongest blob:\nvessel junction", xy=(2.4, -1.0), xytext=(4.5, -12.5), fontsize=6.6,
           color="white", ha="center", path_effects=PE, arrowprops=dict(arrowstyle="-", color="white", lw=0.6))
a.annotate("lesion", xy=(LES[0] - 2.2, LES[1] + 2.2), xytext=(-13.0, 14.0), fontsize=6.6, color="#f2c14e",
           ha="center", path_effects=PE, arrowprops=dict(arrowstyle="-", color="#f2c14e", lw=0.6))
a.plot([-19.5, -12.5], [19.5, 19.5], color="white", lw=1.2)
a.text(-16, 18.2, "7 mm", color="white", fontsize=6, ha="center", va="bottom")
axs[1].text(0, -20.3, "fit on the two visible legs", color="white", fontsize=6.2, ha="center", va="top",
            path_effects=PE)

# legend under the image row
from matplotlib.lines import Line2D
H = [Line2D([], [], ls="none", marker="+", ms=7, mew=1.4, color=C["profile_aligned"], label="returned peak, on target"),
     Line2D([], [], ls="none", marker="+", ms=7, mew=1.4, color="#d1495b", label="returned peak, on vessel"),
     Line2D([], [], ls="none", marker="o", ms=6, mfc="none", mec="#e0a92e", label="3-mm target zone"),
     Line2D([], [], ls=(0, (3, 2)), lw=0.8, color=C["muted"], label="14-mm mask")]
fig.legend(handles=H, loc="lower left", bbox_to_anchor=(0.0, -0.01), ncol=4, fontsize=6.8,
           handlelength=1.6, columnspacing=1.2, handletextpad=0.4)

# readout panel
axt.axis("off"); axt.set_xlim(0, 1); axt.set_ylim(0, 1)
axt.text(0.0, 0.985, "$\\bf(e)$ One readout, four vessel gains", fontsize=7.8, va="top")
axt.text(0.0, 0.86, "Each 6-mm window, affine background removed:", fontsize=6.8, va="top", color=C["muted"])
axt.text(0.5, 0.67, r"$z \;\approx\; g\,u \;+\; h\,t,\quad h\geq 0$", fontsize=9.5, ha="center", va="center")
axt.text(0.5, 0.565, "observed = gain $\\times$ forecast + lesion template",
         fontsize=6.4, ha="center", va="center", color=C["muted"])
rows = [("CT only", "$u=0$", C["ct_only"]), ("Fixed", "$g=1$", C["fixed_aligned"]),
        ("Plug-in", "$g=g_0$ (null fit)", "#7a4f9a"), ("Joint profile", "fit $g,h$ together", C["profile_aligned"])]
for i, (n, eq, col) in enumerate(rows):
    yv = 0.455 - i * 0.083
    axt.add_patch(FancyBboxPatch((0.02, yv - 0.033), 0.035, 0.066, boxstyle="round,pad=0.003", fc=col, ec="none"))
    axt.text(0.08, yv, n, fontsize=7.4, va="center", fontweight="bold", color=col)
    axt.text(0.5, yv, eq, fontsize=7.4, va="center")
axt.add_patch(FancyBboxPatch((0.0, 0.005), 1.0, 0.1, boxstyle="round,pad=0.01", fc="#eef3f2", ec="none"))
axt.text(0.5, 0.052, "Shared templates, search and classifier\n"
         "$\\rightarrow$ accept crop? (10% FPR) $\\;\\cdot\\;$ where is the peak?",
         fontsize=6.6, ha="center", va="center", color=C["ink"])

fig.savefig(style.__file__.replace("scripts/style.py", "figures/overview.pdf"))
fig.savefig("/tmp/overview.png", dpi=200)
print("peaks", [peak(i) for i in (y1, y1 - f_al, y1 - f_rot)])
