"""Result figures (main + supplement), all numbers from scripts/data.py."""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
import style
from style import C, MARK, LABEL
import data as D

style.apply()
FIG = pathlib.Path(__file__).resolve().parents[1] / "figures"
ASSET = pathlib.Path(__file__).with_name("assets")
D.check()


def zero_line(ax, vertical=True):
    (ax.axvline if vertical else ax.axhline)(0, color=C["axis"], lw=0.8, zorder=1)


def ci(ax, y, est, lo, hi, col, marker="o", filled=True, ms=4.2, lw=1.4):
    ax.plot([lo, hi], [y, y], color=col, lw=lw, solid_capstyle="butt", zorder=2)
    ax.plot(est, y, marker=marker, ms=ms, color=col, mfc=col if filled else "white", mew=1.0, ls="none", zorder=3)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(f"/tmp/{name}.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- placement
def fig_placement():
    fig = plt.figure(figsize=(style.TXT_W, 1.95))
    P = D.PLACEMENT_PANELS
    w = 0.13
    for i, key in enumerate(["control", "aligned", "rotated"]):
        ax = fig.add_axes([0.0 + i * (w + 0.01), 0.2, w, w * style.TXT_W / 1.95])
        im = np.asarray(Image.open(ASSET / f"crop_{key}.png").convert("L"))
        ax.imshow(im, cmap="gray", extent=[0, 1, 0, 1], vmin=0, vmax=255)
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(True); sp.set_color(C["axis"])
        r = P[key]["ring"]
        ax.add_patch(plt.Circle((r["cx"], r["cy"]), r["r"], fill=False, ls=(0, (3, 2)), lw=0.7, color="white"))
        col = {"aligned": C["profile_aligned"], "rotated": C["profile_rotated"]}.get(key)
        lab = {"aligned": "#8af0cd", "rotated": "#ffbd82"}.get(key)
        for cpts in P[key]["contours"]:
            a = np.array(cpts); ax.plot(a[:, 0], a[:, 1], color=lab, lw=0.9)
        if P[key]["cross"]:
            ax.plot(*P[key]["cross"], marker="+", ms=7, mew=2.2, color=C["ink"])
            ax.plot(*P[key]["cross"], marker="+", ms=6, mew=1.0, color="white")
        if "scalebar" in P[key]:
            sb = np.array(P[key]["scalebar"]); ax.plot(sb[:, 0], sb[:, 1], color="white", lw=1.3)
            ax.text(sb[:, 0].mean(), sb[0, 1] + 0.03, "5 mm", color="white", fontsize=6.3, ha="center", va="bottom")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        name = {"control": "Control", "aligned": "Lesion + aligned $f$", "rotated": "Lesion + rotated $f$"}[key]
        ax.set_title(name, fontsize=7.6, pad=2.5, color=col or C["ink"])
    fig.text(0.0, 0.965, r"$\bf(a)$ Same exterior, different placement", fontsize=8.2, va="top")
    fig.text(0.0, 0.03, "Dashed: 14-mm mask.  +: centre of inserted lesion.", fontsize=6.6, color=C["muted"])

    ax = fig.add_axes([0.62, 0.2, 0.32, 0.66])
    rows = [(*r[:4], True) for r in D.PLACEMENT_EFFECT[:1]] + \
           [(*D.PLACEMENT_EFFECT[1][:4], True), (*D.PLACEMENT_CROP[0][:4], False),
            (*D.PLACEMENT_EFFECT[2][:4], True), (*D.PLACEMENT_CROP[1][:4], False)]
    ys = [4.6, 3.0, 2.35, 0.75, 0.1]
    labels = ["Focused LUNA16, crop", "Broader LUNA16, localized", "Broader LUNA16, crop",
              "HiPaS native, localized", "HiPaS native, crop"]
    for (lab, est, lo, hi, main), y, txt in zip(rows, ys, labels):
        col = C["profile_aligned"] if main else C["muted"]
        ci(ax, y, est, lo, hi, col, marker="D" if main else "o", filled=main)
        ax.text(-4.6, y, txt, ha="right", va="center", fontsize=7.2, color=C["ink"] if main else C["muted"])
        ax.text(14.1, y, f"{est:+.2f}", ha="left", va="center", fontsize=7.2,
                color=col, fontweight="bold" if main else "normal")
    zero_line(ax)
    ax.set_xlim(-4, 14); ax.set_xticks([-4, 0, 4, 8, 12]); ax.set_ylim(-0.5, 5.2); ax.set_yticks([])
    ax.spines["left"].set_visible(False); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Aligned $-$ rotated sensitivity (pp), 95% CI")
    fig.text(0.445, 0.965, r"$\bf(b)$ Paired effect of alignment at 10% FPR", fontsize=8.2, va="top")
    save(fig, "placement")


# ---------------------------------------------------------------- localization
def fig_localization():
    fig, (a, b) = plt.subplots(1, 2, figsize=(style.TXT_W, 1.75), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=0.55))
    for i, (k, crop, loc) in enumerate(D.BROAD_ACCEPT):
        y = len(D.BROAD_ACCEPT) - 1 - i
        a.barh(y, loc, color=C[k], height=0.62, zorder=2)
        a.barh(y, crop - loc, left=loc, color=C[k], alpha=0.25, height=0.62, zorder=2)
        a.text(loc - 0.5, y, f"{loc + 1e-9:.1f}", color="white", ha="right", va="center", fontsize=7)
        a.text(crop + 0.5, y, f"{crop + 1e-9:.1f}", color=C["ink"], ha="left", va="center", fontsize=7)
    a.set_yticks(range(4)); a.set_yticklabels([LABEL[k] for k, *_ in D.BROAD_ACCEPT][::-1], fontsize=7.4)
    a.tick_params(axis="y", length=0); a.grid(axis="y", visible=False)
    a.set_xlim(0, 46); a.set_xticks([0, 10, 20, 30]); a.set_xlabel("Positive crops accepted (%)")
    a.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=C["ink"]), plt.Rectangle((0, 0), 1, 1, color=C["ink"], alpha=0.25)],
             labels=["peak within 3 mm", "peak elsewhere"], loc="lower right", fontsize=6.6, ncol=1,
             bbox_to_anchor=(1.03, -0.02), handlelength=1.0)
    a.set_title(r"$\bf(a)$ What the accepted crop points to", loc="left", x=-0.62)

    ylab = []
    for i, (cmp, ep, est, lo, hi, _) in enumerate(D.BROAD_PAIRED):
        y = [3.3, 2.7, 1.0, 0.4][i]
        col = C["profile_aligned"] if cmp.startswith("Profile") else C["fixed_aligned"]
        ci(b, y, est, lo, hi, col, marker="D" if ep == "localized" else "o", filled=(ep == "localized"))
        b.text(hi + 0.25, y, f"{est:+.2f}", fontsize=6.8, va="center", color=col)
    b.text(-3.4, 3.75, "Profile: aligned $-$ rotated", fontsize=7.4, fontweight="bold", color=C["profile_aligned"])
    b.text(-3.4, 1.45, "Aligned: fixed $-$ profile", fontsize=7.4, fontweight="bold", color=C["fixed_aligned"])
    zero_line(b); b.set_ylim(0, 4.1); b.set_yticks([]); b.spines["left"].set_visible(False)
    b.grid(axis="y", visible=False); b.set_xlim(-3.5, 14); b.set_xticks([-2, 0, 2, 4, 6, 8])
    b.set_xlabel("Paired difference (pp), 95% CI")
    b.legend(handles=[Line2D([], [], marker="o", mfc="white", color=C["muted"], ls="none", label="crop sensitivity"),
                      Line2D([], [], marker="D", color=C["muted"], ls="none", label="localized sensitivity")],
             loc="lower right", fontsize=6.6, bbox_to_anchor=(1.03, 0.0))
    b.set_title(r"$\bf(b)$ Paired change at the same FPR", loc="left", x=0.0)
    save(fig, "localization")


# ---------------------------------------------------------------- strata (one column)
def fig_strata():
    fig, ax = plt.subplots(figsize=(style.COL_W, 2.25))
    n = len(D.STRATA)
    for i, (g, nf, ef, lf, hf, nb, eb, lb, hb) in enumerate(D.STRATA):
        y = n - 1 - i
        if i == 0:
            ax.axhspan(y - 0.45, y + 0.45, color="#eef3f2", zorder=0, lw=0)
        ci(ax, y + 0.15, ef, lf, hf, C["focused"], marker="s", filled=lf > 0 or hf < 0, ms=3.8, lw=1.2)
        ci(ax, y - 0.15, eb, lb, hb, C["broad"], marker="D", filled=lb > 0 or hb < 0, ms=3.8, lw=1.2)
    ax.set_yticks(range(n)); ax.set_yticklabels([s[0] for s in D.STRATA][::-1], fontsize=7.4)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
    zero_line(ax); ax.set_xlim(-11, 48)
    ax.set_xlabel("Aligned $-$ rotated crop sensitivity (pp)")
    ax.legend(handles=[Line2D([], [], marker="s", color=C["focused"], label="Focused, fixed subtraction"),
                       Line2D([], [], marker="D", color=C["broad"], label="Broader, joint profile")],
              loc="lower center", fontsize=6.5, handlelength=1.4, ncol=2, bbox_to_anchor=(0.4, 1.0),
              columnspacing=1.0)
    save(fig, "strata")


# ---------------------------------------------------------------- native transfer
ORDER = ["fixed_aligned", "profile_aligned", "profile_rotated", "ct_shell", "ct_only"]
SHORT = {"fixed_aligned": "Fixed, aligned", "profile_aligned": "Profile, aligned",
         "profile_rotated": "Profile, rotated", "ct_shell": "CT + shell", "ct_only": "CT only"}


def fig_native():
    fig, (a, b) = plt.subplots(1, 2, figsize=(style.TXT_W, 1.8), gridspec_kw=dict(wspace=0.38))
    for i, k in enumerate(ORDER):
        est, lo, hi = D.NATIVE_LOCALIZED[k]; y = len(ORDER) - 1 - i
        ci(a, y, est, lo, hi, C[k], marker=MARK[k], ms=4.4)
        a.text(hi + 0.15, y, f"{est:.2f}", fontsize=6.8, va="center", color=C[k])
    a.set_yticks(range(5)); a.set_yticklabels([SHORT[k] for k in ORDER][::-1])
    for t, k in zip(a.get_yticklabels(), ORDER[::-1]):
        t.set_color(C[k])
    a.tick_params(axis="y", length=0); a.grid(axis="y", visible=False)
    a.set_xlim(0, 8.2); a.set_xlabel("Localized sensitivity at 10% FPR (%)")
    a.set_title(r"$\bf(a)$ Localization on native vessels", loc="left", x=-0.3)

    for k in ORDER:
        v = D.NATIVE_FROZEN[k]
        b.plot(v["fpr_ci"], [v["sens"]] * 2, color=C[k], lw=1.0)
        b.plot([v["fpr"]] * 2, v["sens_ci"], color=C[k], lw=1.0)
        b.plot(v["fpr"], v["sens"], marker=MARK[k], color=C[k], ms=4.4, ls="none", label=SHORT[k])
    b.axvline(10, color=C["axis"], lw=0.8, ls=(0, (3, 2)))
    b.text(9.8, 14.3, "nominal 10%", ha="right", fontsize=6.6, color=C["muted"])
    b.set_xlim(0, 11.5); b.set_ylim(0, 15)
    b.set_xlabel("Achieved candidate FPR on HiPaS (%)"); b.set_ylabel("Crop sensitivity (%)")
    b.set_title(r"$\bf(b)$ LUNA16 thresholds applied to HiPaS", loc="left", x=-0.12)
    b.legend(loc="upper left", fontsize=6.4, handlelength=1.0, ncol=1, bbox_to_anchor=(0.0, 1.0))
    save(fig, "native_transfer")


# ---------------------------------------------------------------- ROC (supplement)
def fig_roc():
    fig, axs = plt.subplots(1, 2, figsize=(style.TXT_W, 2.1), sharey=True, gridspec_kw=dict(wspace=0.12))
    ls = {"fixed_aligned": "-", "profile_aligned": "-", "profile_rotated": (0, (4, 2)), "ct_only": (0, (1, 1.5))}
    for ax, key, title in zip(axs, ["broad", "hipas"], ["(a) Broader LUNA16 holdout", "(b) HiPaS native vessels"]):
        R = D.ROC[key]
        for k, bnd in R["bands"].items():
            ax.fill_between(bnd["fpr"], bnd["lo"], bnd["hi"], color=C[k], alpha=0.14, lw=0)
        for k, cv in R["curves"].items():
            ax.plot(cv["fpr"], cv["sens"], color=C[k], ls=ls[k], lw=1.2, label=LABEL[k])
        for k, p in R["cap"].items():
            ax.plot(p["fpr"], p["sens"], "o", color=C[k], ms=3.5)
        for k, p in R["calibrated"].items():
            ax.plot(p["fpr"], p["sens"], "D", mfc="white", mec=C[k], ms=4.2, mew=1.0)
        ax.axvline(10, color=C["axis"], lw=0.8)
        ax.set_xlim(0, 25); ax.set_ylim(0, 45)
        ax.set_xlabel("Candidate FPR (%)")
        ax.set_title(title.replace(title[:3], f"$\\bf{{{title[:3]}}}$"), loc="left")
    axs[0].set_ylabel("Sensitivity (%)")
    h, l = axs[0].get_legend_handles_labels()
    h += [Line2D([], [], marker="o", color=C["muted"], ls="none"),
          Line2D([], [], marker="D", mfc="white", mec=C["muted"], ls="none")]
    l += ["matched 10% cap", "LUNA16 calibration cutoff"]
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.3), fontsize=6.8)
    save(fig, "roc")


# ---------------------------------------------------------------- learning (supplement)
def fig_learning():
    L = D.LEARNING
    fig, (a, b) = plt.subplots(1, 2, figsize=(style.TXT_W, 1.8), gridspec_kw=dict(wspace=0.3))
    a.plot(L["curve"]["train"]["patients"], L["curve"]["train"]["auroc"], "o--", color=C["ct_only"], ms=3.5, label="training")
    a.plot(L["curve"]["dev"]["patients"], L["curve"]["dev"]["auroc"], "o-", color=C["profile_aligned"], ms=3.5, label="development")
    a.axhline(L["curve"]["ridge_dev"], color=C["profile_rotated"], ls=(0, (1, 1.5)), lw=1.0, label="local ridge, development")
    a.set_xticks([12, 24, 46]); a.set_xlabel("Fit patients"); a.set_ylabel("AUROC (%)"); a.set_ylim(64, 70)
    a.legend(loc="lower right", fontsize=6.6)
    a.set_title(r"$\bf(a)$ Observed-CT CNN learning curve", loc="left")
    b.plot(L["probe"]["strong_offcenter"]["epoch"], L["probe"]["strong_offcenter"]["auroc"], "o-",
           color=C["profile_aligned"], ms=3.5, label="strong off-centre positives")
    b.plot(L["probe"]["all_variants"]["epoch"], L["probe"]["all_variants"]["auroc"], "s-",
           color=C["ct_only"], ms=3.5, label="all insertion variants")
    b.set_xlabel("Training epoch"); b.set_ylabel("Training AUROC (%)"); b.set_ylim(60, 101)
    b.legend(loc="lower right", fontsize=6.6)
    b.set_title(r"$\bf(b)$ Four-patient fitting checks", loc="left")
    save(fig, "learning")


if __name__ == "__main__":
    for f in [fig_placement, fig_localization, fig_strata, fig_native, fig_roc, fig_learning]:
        f(); print("ok", f.__name__)
