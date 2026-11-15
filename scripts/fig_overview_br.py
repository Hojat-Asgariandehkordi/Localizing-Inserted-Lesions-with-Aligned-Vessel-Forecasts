"""Figure 1 (method overview) from BioRender art, relabelled in Times.

Input : figures/biorender/method_overview_v3_hi.png (BioRender draft 3,
        https://app.biorender.com/illustrations/bb14dcd7fad0b7abcc6ab85f,
        captured at 1470x820 px).
Output: figures/overview.pdf (vector text over the raster art).

Steps (cvpr-paper-revision skill, Sec. 4):
 1. erase every BioRender text box (fill with the median colour of its border);
 2. rebuild panel 4 scientifically: both tiles use the same lesion crop (taken
    from panel 6 with its crosshair removed by cv2.inpaint); aligned = vessel
    removed under the teal forecast, mark on the lesion; rotated = vessel kept,
    orange forecast rotated by 90 degrees about the crop centre, mark on vessel;
 3. typeset every label in Times from the LAYOUT table.
"""
import pathlib
import numpy as np
import cv2
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import style
from style import C

style.apply()
ROOT = pathlib.Path(__file__).resolve().parents[1]
art = np.asarray(Image.open(ROOT / "figures/biorender/method_overview_v3_hi.png").convert("RGB")).copy()
H, W = art.shape[:2]
TEAL, ORNG, GOLD, RED, GREEN = C["profile_aligned"], C["profile_rotated"], "#e0a92e", "#d1495b", "#2e8b3d"


def erase(x0, y0, x1, y1):
    """Fill a box with the median colour of its 2-px border."""
    b = np.concatenate([art[y0:y0 + 2, x0:x1].reshape(-1, 3), art[y1 - 2:y1, x0:x1].reshape(-1, 3),
                        art[y0:y1, x0:x0 + 2].reshape(-1, 3), art[y0:y1, x1 - 2:x1].reshape(-1, 3)])
    art[y0:y1, x0:x1] = np.median(b, axis=0).astype(np.uint8)


# 1. BioRender lettering (boxes in pixels of the 1470x820 capture) ----------------
TEXT_BOXES = [
    (12, 8, 275, 48), (497, 8, 760, 48), (555, 50, 700, 92), (805, 50, 1015, 92), (670, 322, 865, 362),
    (1118, 8, 1415, 48), (1418, 6, 1462, 48),                       # titles, y-labels, gear
    (12, 425, 215, 472), (497, 425, 735, 472), (1118, 425, 1275, 472),
    (1185, 478, 1440, 522), (500, 728, 1030, 812), (1190, 770, 1385, 815),
    (566, 490, 745, 524),                                           # colour dots row in panel 5
]
for bx in TEXT_BOXES:
    erase(*bx)
# panel 5 tiles: blank their labels but keep the coloured boxes
for (x0, y0, x1, y1) in [(552, 132, 758, 172), (552, 186, 758, 226), (552, 240, 758, 280)]:
    y0 += 400; y1 += 400
    art[y0 + 3:y1 - 3, x0 + 6:x1 - 6] = np.median(art[y0 + 6:y0 + 9, x0 + 10:x1 - 10].reshape(-1, 3), axis=0)

# 2. panel 4: rebuild from the panel-6 lesion crop ---------------------------------
crop = art[515:765, 1170:1405].copy()                     # 250x235 incl. blue ring
hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
r, g, b = [crop[..., i].astype(int) for i in range(3)]
mask = ((g > r + 25) & (g > b + 10)).astype(np.uint8)                   # green cross
mask |= ((r < 45) & (g < 45) & (b < 45)).astype(np.uint8)               # black crosshair
mask |= ((r > 150) & (g > 110) & (b < 110) & (r - b > 70)).astype(np.uint8)  # gold ring
mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(crop, mask, 4, cv2.INPAINT_TELEA)
ch, cw = clean.shape[:2]
cy, cx = ch / 2 + 2, cw / 2 + 1                                         # crop centre (px)
# vessel axis estimated from the bright pixels inside the CT disc
yy, xx = np.mgrid[:ch, :cw]
disc = (xx - cx) ** 2 + (yy - cy) ** 2 < (0.40 * cw) ** 2
gray = cv2.cvtColor(clean, cv2.COLOR_RGB2GRAY).astype(float)
bright = disc & (gray > np.percentile(gray[disc], 93))
pts = np.column_stack([xx[bright], yy[bright]]).astype(float)
mu = pts.mean(0); _, _, vt = np.linalg.svd(pts - mu); d = vt[0]
n = np.array([-d[1], d[0]])
dist = np.abs((xx - mu[0]) * n[0] + (yy - mu[1]) * n[1])
along = (xx - mu[0]) * d[0] + (yy - mu[1]) * d[1]
vessel = disc & (dist < 9) & (gray > np.percentile(gray[disc], 70))
removed = cv2.inpaint(clean, cv2.dilate(vessel.astype(np.uint8), np.ones((5, 5), np.uint8)), 6, cv2.INPAINT_TELEA)
LES = np.array([cw * 0.50, ch * 0.50]) + np.array([-1.0, -4.0])        # lesion (centre of former gold ring)


def line_through(p, v, half):
    return np.array([p - half * v, p + half * v])


# erase panel-4 interior (keep frame), then place the two tiles
erase(14, 470, 420, 812)

# 2b. the BioRender canvas cuts off the top edge of the upper panels and the bottom
# edge of the lower panels. Pad the canvas, then redraw every panel frame as one
# clean rounded rectangle over the art (old side borders are covered). ----------
from PIL import ImageDraw
PADT, PADB, PADX = 12, 12, 4
FRAME, FILL = (160, 171, 190), (235, 243, 253)
PANELS = [(1, -9, 431, 369), (483, -9, 1048, 369), (1103, -9, 1468, 369),
          (1, 419, 429, H + 9), (482, 419, 1049, H + 9), (1102, 419, 1468, H + 9)]
canvas = Image.new("RGB", (W + 2 * PADX, H + PADT + PADB), "white")
draw = ImageDraw.Draw(canvas)
for x0, y0, x1, y1 in PANELS:                    # fill the padded bands with the panel colour
    draw.rounded_rectangle([x0 + PADX, y0 + PADT, x1 + PADX, y1 + PADT], radius=16, fill=FILL)
art_c = art.copy()
art_c[355:425, :6] = 255                         # stray edge line between the rows (left)
art_c[355:425, W - 6:] = 255
canvas.paste(Image.fromarray(art_c), (PADX, PADT))
draw = ImageDraw.Draw(canvas)
for x0, y0, x1, y1 in PANELS:
    # cover the old border with fill, then draw the new frame
    draw.rounded_rectangle([x0 + PADX, y0 + PADT, x1 + PADX, y1 + PADT], radius=16, outline=FILL, width=9)
    draw.rounded_rectangle([x0 + PADX, y0 + PADT, x1 + PADX, y1 + PADT], radius=16, outline=FRAME, width=2)
art_padded = np.asarray(canvas).copy()

# 3. compose in matplotlib --------------------------------------------------------
HT, WT = H + PADT + PADB, W + 2 * PADX
fig = plt.figure(figsize=(style.TXT_W, style.TXT_W * HT / WT))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-PADX, W + PADX); ax.set_ylim(H + PADB, -PADT); ax.axis("off")
ax.imshow(art_padded, extent=[-PADX, W + PADX, H + PADB, -PADT], interpolation="lanczos")

S = 0.62                                                   # tile scale (crop px -> canvas px)
TILES = {"aligned": (40, 478), "rotated": (40, 646)}
for key, (x0, y0) in TILES.items():
    img = removed if key == "aligned" else clean
    ext = [x0, x0 + cw * S, y0 + ch * S, y0]
    ax.imshow(img, extent=ext, interpolation="lanczos", zorder=2)
    T = lambda q: np.array([x0 + q[0] * S, y0 + q[1] * S])
    if key == "aligned":
        seg = line_through(mu, d, 0.40 * cw)
        col, lab, mark, mcol = TEAL, r"aligned $f$: vessel removed", LES, GREEN
    else:
        c0 = np.array([cx, cy]); rot = lambda q: c0 + np.array([-(q[1] - c0[1]), q[0] - c0[0]])
        seg = np.array([rot(q) for q in line_through(mu, d, 0.40 * cw)])
        col, lab, mark, mcol = ORNG, r"rotated $Qf$: vessel kept", mu + d * 22, RED
    a, bb = T(seg[0]), T(seg[1])
    ax.plot([a[0], bb[0]], [a[1], bb[1]], color="white", lw=2.6, alpha=0.8, zorder=3, solid_capstyle="round")
    ax.plot([a[0], bb[0]], [a[1], bb[1]], color=col, lw=1.6, ls=(0, (4, 2.5)), zorder=4)
    lc = T(LES)
    ax.add_patch(Circle(lc, 9, fill=False, lw=1.1, color=GOLD, zorder=5))
    m = T(mark)
    ax.plot(*m, marker="P" if key == "aligned" else "X", ms=8, color=mcol, mec="white", mew=0.9, zorder=6)
    ax.text(x0 + cw * S + 14, y0 + ch * S * 0.42, lab, fontsize=7.4, va="center", color=col)
    ax.text(x0 + cw * S + 14, y0 + ch * S * 0.62,
            "mark on lesion" if key == "aligned" else "mark on vessel", fontsize=7.4, va="center",
            color=C["ink"])
ax.add_patch(FancyArrowPatch((112, 628), (112, 652), arrowstyle="-|>", mutation_scale=9, lw=1.1,
                             color=C["muted"], connectionstyle="arc3,rad=0.0", zorder=3))
ax.text(124, 640, r"same $f$, rotated $90^{\circ}$", fontsize=7, color=C["muted"], va="center")

# LAYOUT table: (x, y, text, size, kwargs) in canvas pixels -----------------------
TITLE = dict(fontsize=8.6, va="center", ha="left")
LAYOUT = [
    (20, 28, r"$\bf 1$  Candidate crop $y$", TITLE),
    (505, 28, r"$\bf 2$  Paired insertion", TITLE),
    (1126, 28, r"$\bf 3$  Exterior forecast $f=F(y|_E)$", TITLE),
    (20, 448, r"$\bf 4$  Placement sham", TITLE),
    (505, 448, r"$\bf 5$  Local readout", TITLE),
    (1126, 448, r"$\bf 6$  Two outputs", TITLE),
    (627, 72, r"control $y_0$", dict(fontsize=7.8, ha="center", va="center")),
    (912, 72, r"$y_1=y_0+s$", dict(fontsize=7.8, ha="center", va="center")),
    (767, 343, r"identical exterior $E$ (outside 14 mm)", dict(fontsize=7.4, ha="center", va="center")),
    (1287, 352, r"fitted on the exterior only", dict(fontsize=7.0, ha="center", va="center",
                                                                     color=C["muted"])),
    (655, 552, r"observed $z$", dict(fontsize=7.8, ha="center", va="center")),
    (655, 606, r"forecast $u$", dict(fontsize=7.8, ha="center", va="center", color="white")),
    (655, 660, r"template $t$", dict(fontsize=7.8, ha="center", va="center", color="white")),
    (655, 507, r"in each window $W_x$", dict(fontsize=7.2, ha="center", va="center", color=C["muted"])),
    (510, 752, r"fit  $z\approx g\,u+h\,t$, $h\geq0$;  score $m_r(x)$", dict(fontsize=7.8, va="center")),
    (510, 790, r"gain $g$: CT-only, fixed, plug-in, profile", dict(fontsize=7.8, va="center")),
    (1190, 500, r"accept crop: $A(y)$ at 10% FPR", dict(fontsize=7.6, va="center")),
    (1288, 793, r"returned location $L(y)$", dict(fontsize=7.6, ha="center", va="center")),
]
for x, y, t, kw in LAYOUT:
    kw = dict(kw); kw.setdefault("color", C["ink"])
    ax.text(x, y, t, zorder=8, **kw)

fig.savefig(ROOT / "figures/overview.pdf", dpi=300)
fig.savefig("/tmp/overview_br.png", dpi=250)
print("vessel dir", d, "centre", mu)
