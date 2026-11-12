"""Result figures (main paper), all numbers from scripts/data.py.

Conventions in every figure (independent figure review, revision 7b):
  colour  = readout  (blue Fixed, green Profile aligned, orange Profile rotated,
                      olive CT + shell, grey CT only)
  marker  = endpoint (circle = crop sensitivity, diamond = localized sensitivity)
  all intervals are 95% paired block-bootstrap CIs, in pp for differences.
Figures are saved at their printed width (6.875 in or 3.25 in), no tight crop,
so font sizes in print equal the sizes set here.
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image
import style
from style import C, LABEL, EP
import data as D

style.apply()
FIG = pathlib.Path(__file__).resolve().parents[1] / "figures"
ASSET = pathlib.Path(__file__).with_name("assets")
D.check()
CI_LAB = "(pp, 95% CI)"


def zero_line(ax, vertical=True):
    (ax.axvline if vertical else ax.axhline)(0, color="#8a9aa3", lw=0.9, zorder=1)


def ci(ax, y, est, lo, hi, col, marker="o", ms=4.6, lw=1.5, mfc=None):
    ax.plot([lo, hi], [y, y], color=col, lw=lw, solid_capstyle="butt", zorder=2)
    for x in (lo, hi):
        ax.plot([x, x], [y - 0.09, y + 0.09], color=col, lw=lw * 0.8, zorder=2)
    ax.plot(est, y, marker=marker, ms=ms, color=col, mfc=mfc or col, mew=1.0, ls="none", zorder=3)


def ep_legend(ax, **kw):
    h = [Line2D([], [], marker=EP["crop"], color=C["muted"], ls="none", ms=5, label="crop sensitivity"),
         Line2D([], [], marker=EP["localized"], color=C["muted"], ls="none", ms=5, label="localized sensitivity")]
    ax.legend(handles=h, **kw)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(f"/tmp/{name}.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- Fig. 2 placement
def fig_placement():
    fig = plt.figure(figsize=(style.TXT_W, 1.8))
    P = D.PLACEMENT_PANELS
    w, h0 = 0.128, 0.2
    hgt = w * style.TXT_W / 1.8
    for i, key in enumerate(["control", "aligned", "rotated"]):
        ax = fig.add_axes([0.0 + i * (w + 0.008), h0, w, hgt])
        im = np.asarray(Image.open(ASSET / f"crop_{key}.png").convert("L"))
        ax.imshow(im, cmap="gray", extent=[0, 1, 0, 1], vmin=0, vmax=255)
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(True); sp.set_color(C["axis"])
        r = P[key]["ring"]
        ax.add_patch(plt.Circle((r["cx"], r["cy"]), r["r"], fill=False, lw=0.6, color="white"))
        col = {"aligned": C["profile_aligned"], "rotated": C["profile_rotated"]}.get(key)
        for cpts in P[key]["contours"]:
            a = np.array(cpts)
            ax.plot(a[:, 0], a[:, 1], color="white", lw=2.0)
            ax.plot(a[:, 0], a[:, 1], color=col, lw=1.1)
        if P[key]["cross"]:
            ax.add_patch(plt.Circle(P[key]["cross"], 0.09, fill=False, lw=1.0, color="#f2c14e"))
        if "scalebar" in P[key]:
            sb = np.array(P[key]["scalebar"]); sb[:, 1] = 0.07
            ax.plot(sb[:, 0], sb[:, 1], color="white", lw=1.4)
            ax.text(sb[:, 0].mean(), 0.1, "5 mm", color="white", fontsize=7, ha="center", va="bottom")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        name = {"control": "Control (no lesion)", "aligned": "Lesion, aligned $f$", "rotated": "Lesion, rotated $f$"}[key]
        ax.set_title(name, fontsize=8, pad=2.5, color=col or C["ink"])
    fig.text(0.0, 0.975, r"$\bf(a)$ Same exterior, forecast aligned vs rotated", fontsize=8.5, va="top")
    fig.text(0.0, 0.035, "thin white circle: 14-mm mask    gold ring: inserted lesion    outline: forecast $f$",
             fontsize=7, color=C["muted"])

    ax = fig.add_axes([0.63, 0.22, 0.3, 0.64])
    rows = [("Low-texture, profile, crop", *D.PLACEMENT_EFFECT[0][1:4], "crop"),
            ("Broader, profile, localized", *D.PLACEMENT_EFFECT[1][1:4], "localized"),
            ("Broader, profile, crop", *D.PLACEMENT_CROP[0][1:4], "crop"),
            ("HiPaS, profile, localized", *D.PLACEMENT_EFFECT[2][1:4], "localized"),
            ("HiPaS, profile, crop", *D.PLACEMENT_CROP[1][1:4], "crop")]
    ys = [4.6, 3.0, 2.35, 0.75, 0.1]
    for (txt, est, lo, hi, ep), y in zip(rows, ys):
        ci(ax, y, est, lo, hi, C["profile_aligned"], marker=EP[ep])
        ax.text(-4.6, y, txt, ha="right", va="center", fontsize=7.5, color=C["ink"])
        ax.text(14.2, y, f"{est:+.2f}", ha="left", va="center", fontsize=7.5, color=C["profile_aligned"],
                fontweight="bold" if lo > 0 else "normal")
    zero_line(ax)
    ax.set_xlim(-4, 14); ax.set_xticks([-4, 0, 4, 8, 12]); ax.set_ylim(-0.5, 5.2); ax.set_yticks([])
    ax.spines["left"].set_visible(False); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Aligned $-$ rotated sensitivity " + CI_LAB)
    fig.text(0.445, 0.975, r"$\bf(b)$ Paired effect of alignment at 10% FPR", fontsize=8.5, va="top")
    save(fig, "placement")


# ---------------------------------------------------------------- Fig. 3 localization
def fig_localization():
    fig, (a, b) = plt.subplots(1, 2, figsize=(style.TXT_W, 1.9), layout="constrained",
                               gridspec_kw=dict(width_ratios=[1.05, 1]))
    for i, (k, crop, loc) in enumerate(D.BROAD_ACCEPT):
        y = len(D.BROAD_ACCEPT) - 1 - i
        a.barh(y, loc, color=C[k], height=0.62, zorder=2)
        a.barh(y, crop - loc, left=loc, color=C[k], alpha=0.28, height=0.62, zorder=2)
        a.text(loc - 0.4, y, f"{loc + 1e-9:.1f}", color="white", ha="right", va="center", fontsize=7.2)
        a.text(crop + 0.4, y, f"{crop + 1e-9:.1f}", color=C["ink"], ha="left", va="center", fontsize=7.2)
    a.set_yticks(range(4)); a.set_yticklabels([LABEL[k] for k, *_ in D.BROAD_ACCEPT][::-1])
    for t, (k, *_) in zip(a.get_yticklabels(), D.BROAD_ACCEPT[::-1]):
        t.set_color(C[k])
    a.tick_params(axis="y", length=0); a.grid(axis="y", visible=False)
    a.set_xlim(0, 30); a.set_xlabel("Lesion crops accepted (%)")
    a.set_ylim(-0.6, 4.3)
    a.legend(handles=[Patch(color=C["muted"]), Patch(color=C["muted"], alpha=0.28)],
             labels=["mark within 3 mm (localized)", "mark elsewhere; bar end = crop sens."],
             loc="upper center", bbox_to_anchor=(0.45, 1.0), ncol=2, fontsize=6.8, handlelength=1.0,
             columnspacing=0.8)
    a.set_title(r"$\bf(a)$ Where accepted lesion crops are marked", loc="left")

    for i, (cmp, ep, est, lo, hi, _) in enumerate(D.BROAD_PAIRED):
        y = [3.3, 2.7, 1.0, 0.4][i]
        col = C["profile_aligned"] if cmp.startswith("Profile") else C["fixed_aligned"]
        ci(b, y, est, lo, hi, col, marker=EP[ep])
        b.text(hi + 0.3, y, f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}]", fontsize=6.8, va="center", color=col)
    b.text(-3.4, 3.62, "Profile, aligned $-$ Profile, rotated", fontsize=7.6, color=C["profile_aligned"])
    b.text(-3.4, 1.42, "Fixed, aligned $-$ Profile, aligned", fontsize=7.6, color=C["fixed_aligned"])
    b.grid(False); zero_line(b); b.set_ylim(-0.4, 4.75); b.set_yticks([]); b.spines["left"].set_visible(False)
    b.grid(axis="y", visible=False); b.set_xlim(-3.5, 15); b.set_xticks([-2, 0, 2, 4, 6, 8])
    b.set_xlabel("Paired difference " + CI_LAB)
    ep_legend(b, loc="upper right", fontsize=6.8, ncol=2, bbox_to_anchor=(1.0, 1.04), handletextpad=0.2, columnspacing=0.8)
    b.set_title(r"$\bf(b)$ Paired change at the same 10% FPR", loc="left")
    save(fig, "localization")


# ---------------------------------------------------------------- Fig. 5 strata (one column)
STRATA_LABEL = {
    "All insertions": "All insertions",
    "Centered": "Centered (0 mm offset)",
    "Displaced": "Displaced from center",
    "Faintest contrast": "Faintest (70 / 84 HU)",
    "Strongest contrast": "Strongest (336 / 364 HU)",
    "Strongest, displaced": "Strongest and displaced",
    "Overlap $\\geq$ 50%": "On vessel (\u2265 50% overlap)",
}


def fig_strata():
    fig, ax = plt.subplots(figsize=(style.COL_W, 2.45), layout="constrained")
    n = len(D.STRATA)
    for i, (g, nf, ef, lf, hf, nb, eb, lb, hb) in enumerate(D.STRATA):
        y = n - 1 - i
        if i == 0:
            ax.axhspan(y - 0.45, y + 0.45, color="#eef3f2", zorder=0, lw=0)
        ci(ax, y + 0.16, ef, lf, hf, C["fixed_aligned"], marker=EP["crop"], ms=4, lw=1.3)
        ci(ax, y - 0.16, eb, lb, hb, C["profile_aligned"], marker=EP["crop"], ms=4, lw=1.3)
        if i == 0:
            ax.text(hf + 1.0, y + 0.16, "low-texture", fontsize=6.8, va="center", color=C["fixed_aligned"])
            ax.text(hb + 1.0, y - 0.16, "broader", fontsize=6.8, va="center", color=C["profile_aligned"])
    ax.set_yticks(range(n)); ax.set_yticklabels([STRATA_LABEL[s[0]] for s in D.STRATA][::-1], fontsize=7.4)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
    zero_line(ax); ax.set_xlim(-11, 48)
    ax.set_xlabel("Aligned $-$ rotated crop sens. " + CI_LAB)
    ax.legend(handles=[Line2D([], [], marker="o", color=C["fixed_aligned"], label="Low-texture: fixed subtraction"),
                       Line2D([], [], marker="o", color=C["profile_aligned"], label="Broader set: profile")],
              loc="lower center", fontsize=6.8, handlelength=1.4, ncol=2, bbox_to_anchor=(0.35, 1.0), markerscale=0.8,
              columnspacing=0.8)
    save(fig, "strata")


# ---------------------------------------------------------------- Fig. 7 native transfer
ORDER = ["fixed_aligned", "profile_aligned", "profile_rotated", "ct_shell", "ct_only"]


def fig_native():
    fig, (a, b) = plt.subplots(1, 2, figsize=(style.TXT_W, 1.95), layout="constrained")
    for i, k in enumerate(ORDER):
        est, lo, hi = D.NATIVE_LOCALIZED[k]; y = len(ORDER) - 1 - i
        ci(a, y, est, lo, hi, C[k], marker=EP["localized"], ms=4.8)
        a.text(hi + 0.15, y, f"{est:.2f}", fontsize=7, va="center", color=C[k])
    a.set_yticks(range(5)); a.set_yticklabels([LABEL[k] for k in ORDER][::-1])
    for t, k in zip(a.get_yticklabels(), ORDER[::-1]):
        t.set_color(C[k])
    a.tick_params(axis="y", length=0); a.grid(axis="y", visible=False)
    a.set_xlim(0, 8.2); a.set_xlabel("Localized sensitivity at 10% FPR (%, 95% CI)")
    a.set_title(r"$\bf(a)$ Localization on native vessels", loc="left")

    for k in ORDER:
        v = D.NATIVE_FROZEN[k]
        b.plot(v["fpr_ci"], [v["sens"]] * 2, color=C[k], lw=1.0)
        b.plot([v["fpr"]] * 2, v["sens_ci"], color=C[k], lw=1.0)
        b.plot(v["fpr"], v["sens"], marker="o", color=C[k], ms=5, ls="none",
               mfc="white", mec=C[k], mew=1.3, label=LABEL[k], zorder=3)
    b.axvline(10, color=C["axis"], lw=0.8, ls=(0, (3, 2)))
    b.text(9.8, 14.2, "intended 10%", ha="right", fontsize=7, color=C["muted"])
    b.annotate("both aligned readouts:\n~2% sens. at <1% FPR", xy=(0.6, 2.1), xytext=(2.6, 0.9),
               fontsize=6.8, color=C["ink"], arrowprops=dict(arrowstyle="-", lw=0.6, color=C["muted"]))
    b.set_xlim(0, 11.5); b.set_ylim(0, 15); b.set_yticks([0, 5, 10, 15])
    b.set_xlabel("Achieved FPR on HiPaS controls (%)"); b.set_ylabel("Crop sensitivity (%)")
    b.set_title(r"$\bf(b)$ Frozen LUNA16 cutoffs applied to HiPaS", loc="left")
    b.legend(loc="upper left", fontsize=6.8, handlelength=1.0, bbox_to_anchor=(0.0, 1.0))
    save(fig, "native_transfer")


# ---------------------------------------------------------------- Fig. 6 ROC
def fig_roc():
    fig, axs = plt.subplots(1, 2, figsize=(style.TXT_W, 2.35), sharey=True, layout="constrained")
    ls = {"fixed_aligned": "-", "profile_aligned": "-", "profile_rotated": (0, (4, 2)), "ct_only": (0, (1, 1.5))}
    for ax, key, title in zip(axs, ["broad", "hipas"], [r"$\bf(a)$ Broader LUNA16 held-out set", r"$\bf(b)$ HiPaS native vessels"]):
        R = D.ROC[key]
        for k, bnd in R["bands"].items():
            ax.fill_between(bnd["fpr"], bnd["lo"], bnd["hi"], color=C[k], alpha=0.14, lw=0)
        for k, cv in R["curves"].items():
            ax.plot(cv["fpr"], cv["sens"], color=C[k], ls=ls[k], lw=1.2, label=LABEL[k])
        for k, p in R["calibrated"].items():
            ax.plot(p["fpr"], p["sens"], marker="o", mfc="white", mec=C[k], ms=4.4, mew=1.2, ls="none", zorder=4)
        ax.axvline(10, color=C["axis"], lw=0.8)
        ax.text(10.4, 43.5, "10% cap", fontsize=7, color=C["muted"], va="top")
        ax.set_xlim(0, 25); ax.set_ylim(0, 45)
        ax.set_xlabel("Candidate FPR (%)")
        ax.set_title(title, loc="left")
    axs[0].set_ylabel("Crop sensitivity (%)")
    axs[1].annotate("frozen LUNA16 cutoffs of the aligned\nreadouts fall below 1% FPR here", xy=(1.0, 2.0), xytext=(12.5, 3.0),
                    fontsize=6.8, arrowprops=dict(arrowstyle="-", lw=0.6, color=C["muted"]))
    h, l = axs[0].get_legend_handles_labels()
    h += [Line2D([], [], marker="o", mfc="white", mec=C["muted"], ls="none", ms=4.5)]
    l += ["frozen LUNA16 cutoff (colour = readout)"]
    fig.legend(h, l, loc="outside lower center", ncol=5, fontsize=7, handlelength=1.8)
    save(fig, "roc")


# ---------------------------------------------------------------- Fig. 4 learning
def fig_learning():
    L = D.LEARNING
    fig, (a, b) = plt.subplots(1, 2, figsize=(style.TXT_W, 1.95), layout="constrained")
    a.plot(L["curve"]["dev"]["patients"], L["curve"]["dev"]["auroc"], "o-", color=C["ct_only"], ms=3.8,
           label="CNN, development (single seed)")
    a.plot(L["curve"]["train"]["patients"], L["curve"]["train"]["auroc"], "o--", color=C["ct_only"], ms=3.8,
           mfc="white", label="CNN, training (single seed)")
    a.axhline(L["curve"]["ridge_dev"], color=C["ink"], ls=(0, (1, 1.5)), lw=1.0, label="ridge classifier, development")
    a.set_xticks([12, 24, 46]); a.set_xlabel("Fit patients"); a.set_ylabel("AUROC (%)"); a.set_ylim(64, 70)
    a.legend(loc="lower right", fontsize=6.8)
    a.set_title(r"$\bf(a)$ Development AUROC rises with fit patients", loc="left")
    b.plot(L["probe"]["strong_offcenter"]["epoch"], L["probe"]["strong_offcenter"]["auroc"], "o-",
           color=C["ct_only"], ms=3.8, label="easy: strong off-center lesions")
    b.plot(L["probe"]["all_variants"]["epoch"], L["probe"]["all_variants"]["auroc"], "s--",
           color=C["ct_only"], ms=3.8, mfc="white", label="hard: all insertion variants")
    b.axhline(50, color=C["axis"], lw=0.9, ls=(0, (3, 2)))
    b.text(178, 51.5, "chance", ha="right", fontsize=7, color=C["muted"])
    b.set_xlabel("Training epoch"); b.set_ylabel("Training AUROC (%)"); b.set_ylim(45, 102)
    b.legend(loc="center right", fontsize=6.8)
    b.set_title(r"$\bf(b)$ Four-patient fitting checks", loc="left")
    save(fig, "learning")


if __name__ == "__main__":
    for f in [fig_placement, fig_localization, fig_strata, fig_native, fig_roc, fig_learning]:
        f(); print("ok", f.__name__)
