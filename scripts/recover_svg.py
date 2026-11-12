"""Recover plotted numbers from the V6 matplotlib SVGs (figures/v6_original/*.svg).

Used only for values that are not printed in any table or macro of the V6
source (ROC curves/bands, learning curves, HiPaS interval end points, the
qualitative CT crops and forecast contours). Output: scripts/recovered.json and
scripts/assets/. Precision is limited by SVG coordinates (about +-0.02 units).
All recovered values are flagged for author confirmation in REVISION_NOTES.md.
"""
import base64, json, re, sys, pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG = ROOT / "figures" / "v6_original"
OUT = ROOT / "scripts"
NS = {"s": "http://www.w3.org/2000/svg", "x": "http://www.w3.org/1999/xlink"}
S = "{%s}" % NS["s"]


def pts(d):
    v = [float(x) for x in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", d)]
    return list(zip(v[0::2], v[1::2]))


def lin(p0, v0, p1, v1):
    k = (v1 - v0) / (p1 - p0)
    return lambda p: v0 + (p - p0) * k


def axes(svg):
    root = ET.parse(FIG / svg).getroot()
    fig = root.find("s:g", NS)
    return {g.get("id"): g for g in fig.findall("s:g", NS) if g.get("id", "").startswith("axes")}


def items(ax):
    """(group id, kind, colour, points) for every data element in an axes."""
    out = []
    for g in ax.findall("s:g", NS):
        gid = g.get("id", "")
        if gid.startswith("matplotlib.axis") or gid.startswith("legend"):
            continue
        for el in g.iter():
            tag = el.tag.replace(S, "")
            st = el.get("style", "")
            if tag == "path" and el.getparent if False else tag == "path":
                col = re.findall(r"(?:stroke|fill): (#\w+)", st)
                out.append((gid, "path", col[0] if col else None, pts(el.get("d"))))
            elif tag == "use":
                fill = re.search(r"fill: (#\w+)", st)
                strk = re.search(r"stroke: (#\w+)", st)
                out.append((gid, "use", (fill and fill.group(1), strk and strk.group(1)),
                            [(float(el.get("x")), float(el.get("y")))]))
    return out


def xticks(ax):
    res = []
    axg = [a for a in ax.findall("s:g", NS) if a.get("id", "").startswith("matplotlib.axis")]
    for tk in axg[0].findall("s:g", NS):
        p = [pts(q.get("d"))[0] for q in tk.iter(S + "path")]
        lab = [(t.text or "").strip() for t in tk.iter(S + "text")]
        if p and lab:
            res.append((p[0][0], float(lab[0].replace("−", "-"))))
    return res


def yticks(ax):
    res = []
    axg = [a for a in ax.findall("s:g", NS) if a.get("id", "").startswith("matplotlib.axis")]
    for tk in axg[1].findall("s:g", NS):
        p = [pts(q.get("d"))[0] for q in tk.iter(S + "path")]
        lab = [(t.text or "").strip() for t in tk.iter(S + "text")]
        if p and lab:
            res.append((p[0][1], float(lab[0].replace("−", "-"))))
    return res


def fx(ax):
    t = xticks(ax); return lin(t[0][0], t[0][1], t[-1][0], t[-1][1])


def fy(ax):
    t = yticks(ax); return lin(t[0][0], t[0][1], t[-1][0], t[-1][1])


r2 = lambda v: round(v, 2)
rec = {}
COL = {"#126584": "fixed_aligned", "#067a64": "profile_aligned", "#a74e23": "profile_rotated",
       "#8b691f": "ct_shell", "#626b76": "ct_only"}

# ---- native_transfer.svg -------------------------------------------------
A = axes("native_transfer.svg")
a1, a2 = A["axes_1"], A["axes_2"]
X = fx(a1)
nat = {"localized": {}, "frozen": {}}
segs = {}
for gid, kind, col, P in items(a1):
    if kind == "path" and col in COL and len(P) == 2 and P[0][1] == P[1][1]:
        segs[COL[col]] = (r2(X(P[0][0])), r2(X(P[1][0])))
    if kind == "use" and col[0] in COL:
        nat["localized"][COL[col[0]]] = {"est": r2(X(P[0][0])), "ci": segs.get(COL[col[0]])}
X, Y = fx(a2), fy(a2)
cur = {}
for gid, kind, col, P in items(a2):
    if kind == "path" and col in COL and len(P) == 2:
        if abs(P[0][1] - P[1][1]) < 1e-6:
            cur.setdefault(COL[col], {})["fpr_ci"] = (r2(X(P[0][0])), r2(X(P[1][0])))
        elif abs(P[0][0] - P[1][0]) < 1e-6:
            cur.setdefault(COL[col], {})["sens_ci"] = (r2(Y(P[0][1])), r2(Y(P[1][1])))
    if kind == "use" and col[0] in COL:
        cur[COL[col[0]]]["fpr"] = r2(X(P[0][0])); cur[COL[col[0]]]["sens"] = r2(Y(P[0][1]))
nat["frozen"] = cur
rec["native_transfer"] = nat

# ---- roc.svg ---------------------------------------------------------------
A = axes("roc.svg")
roc = {}
for name, ax in [("broad", A["axes_1"]), ("hipas", A["axes_2"])]:
    X, Y = fx(ax), fy(ax)
    d = {"curves": {}, "bands": {}, "cap": {}, "calibrated": {}}
    for gid, kind, col, P in items(ax):
        if kind == "path" and gid.startswith("PolyCollection"):
            byx = {}
            for x, y in P:
                byx.setdefault(round(x, 2), []).append(y)
            xs = sorted(k for k in byx if 0 < X(k) < 99.5)
            d["bands"][COL[col]] = {"fpr": [r2(X(k)) for k in xs],
                                    "lo": [r2(Y(max(byx[k]))) for k in xs],
                                    "hi": [r2(Y(min(byx[k]))) for k in xs]}
        elif (kind == "path" and col in COL and len(P) > 5 and gid.startswith("line2d")
              and P[0][0] > 20):
            # drop the last vertex: it is the clipped extension beyond the axes
            c = [(r2(X(x)), r2(Y(y))) for x, y in P[:-1] if X(x) < 99.5]
            d["curves"][COL[col]] = {"fpr": [p[0] for p in c], "sens": [p[1] for p in c]}
        elif kind == "use":
            fill, strk = col
            key = COL.get(strk)
            if key is None: continue
            tgt = "calibrated" if fill == "#ffffff" else "cap"
            d[tgt][key] = {"fpr": r2(X(P[0][0])), "sens": r2(Y(P[0][1]))}
    roc[name] = d
rec["roc"] = roc

# ---- learning.svg ----------------------------------------------------------
# y tick labels have no tick marks; the label baseline sits 2.76 px below the
# tick. Panel A is anchored on the printed local-ridge value (68.08 % dev AUROC).
s = (FIG / "learning.svg").read_text()
A = axes("learning.svg")
lab = [(float(y), float(v)) for y, v in re.findall(r'<g id="ytick_\d+">.*?y="([\d.]+)"[^>]*>(\d+)<', s, re.S)]
YA = lin(lab[0][0] - 2.76, lab[0][1], lab[3][0] - 2.76, lab[3][1])
YB = lin(lab[4][0] - 2.76, lab[4][1], lab[8][0] - 2.76, lab[8][1])
XA = lin(61.74, 12, 207.4, 46)
XB = fx(A["axes_2"])
L = {"curve": {}, "probe": {}}
for gid, kind, col, P in items(A["axes_1"]):
    if kind == "path" and len(P) == 3 and col in ("#626b76", "#067a64"):
        L["curve"]["train" if col == "#626b76" else "dev"] = {
            "patients": [round(XA(x)) for x, _ in P], "auroc": [r2(YA(y)) for _, y in P]}
    if kind == "path" and len(P) == 2 and col == "#a74e23":
        L["curve"]["ridge_dev"] = r2(YA(P[0][1]))
for gid, kind, col, P in items(A["axes_2"]):
    if kind == "path" and len(P) == 4 and col in ("#626b76", "#067a64") and P[0][0] > 200:
        L["probe"]["all_variants" if col == "#626b76" else "strong_offcenter"] = {
            "epoch": [round(XB(x)) for x, _ in P], "auroc": [r2(YB(y)) for _, y in P]}
rec["learning"] = L

# ---- placement.svg: CT crops and forecast contours --------------------------
s = (FIG / "placement.svg").read_text()
for i, m in enumerate(re.finditer(r'<image xlink:href="data:image/png;base64,([^"]+)"', s)):
    (OUT / "assets" / f"crop_{['control', 'aligned', 'rotated'][i]}.png").write_bytes(
        base64.b64decode(m.group(1).replace("\n", "")))
A = axes("placement.svg")
cont = {}
for name, key in [("axes_1", "control"), ("axes_2", "aligned"), ("axes_3", "rotated")]:
    ax = A[name]
    box = None; c = {"contours": [], "cross": None, "ring": None}
    for gid, kind, col, P in items(ax):
        if gid.startswith("patch") and kind == "path" and len(P) == 4 and box is None:
            xs = [p[0] for p in P]; ys = [p[1] for p in P]
            box = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    nx = lambda x: (x - box[0]) / box[2]
    ny = lambda y: 1 - (y - box[1]) / box[3]
    for gid, kind, col, P in items(ax):
        if gid.startswith("PathCollection"):
            c["contours"].append([(round(nx(x), 4), round(ny(y), 4)) for x, y in P])
        elif gid.startswith("patch") and col == "#ffffff" and len(P) > 10:
            xs = [p[0] for p in P]; ys = [p[1] for p in P]
            c["ring"] = {"cx": round(nx((max(xs) + min(xs)) / 2), 4), "cy": round(ny((max(ys) + min(ys)) / 2), 4),
                         "r": round((max(xs) - min(xs)) / 2 / box[2], 4)}
        elif kind == "use" and col[0] == "#182934":
            c["cross"] = (round(nx(P[0][0]), 4), round(ny(P[0][1]), 4))
        elif gid == "line2d_1" and kind == "path":
            c["scalebar"] = [(round(nx(x), 4), round(ny(y), 4)) for x, y in P]
    cont[key] = c
rec["placement_panels"] = cont

(OUT / "recovered.json").write_text(json.dumps(rec, indent=1))
print(json.dumps({k: v for k, v in rec.items() if k != "placement_panels"}, indent=0)[:3000])
print({k: (len(v["contours"]), v["cross"], v["ring"]) for k, v in cont.items()})
