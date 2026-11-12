"""Every number plotted in the revised figures, with its source.

Sources
  T:decisive    tables/decisive.tex (main Table 1)
  T:transfer    tables/transfer.tex (HiPaS table)
  T:strata      tables/strata.tex
  M:<macro>     tables/macros.tex (text macros of the V6 submission)
  S:<section>   supplement.tex prose
  R:<key>       scripts/recovered.json, recovered from the V6 vector SVGs by
                scripts/recover_svg.py. These are NOT printed anywhere in the V6
                text; authors should confirm them against the score arrays.
Units: percent, or percentage points (pp) for differences.
"""
import json, pathlib

_REC = json.loads((pathlib.Path(__file__).with_name("recovered.json")).read_text())

# ---- Fig. 2(b): paired effect of alignment -----------------------------------
# (label, estimate, lo, hi, source)
PLACEMENT_EFFECT = [
    ("Focused LUNA16\ncrop sensitivity", 9.37, 4.56, 12.29, "M:FocusedResults / M:PaperAbstract"),
    ("Broader LUNA16\nlocalized sensitivity", 6.09, 4.38, 7.78, "M:BroadResults"),
    ("HiPaS native vessels\nlocalized sensitivity", 2.76, 1.77, 3.76, "M:TransferResults"),
]
# Supporting context for the same panel (crop-level effects, broad + HiPaS)
PLACEMENT_CROP = [
    ("Broader LUNA16\ncrop sensitivity", 2.08, -0.27, 4.40, "M:BroadResults"),
    ("HiPaS\ncrop sensitivity", 1.36, -0.26, 3.69, "M:TransferResults"),
]

# ---- Fig. localization(a): broader holdout at matched 10% FPR -----------------
# (key, matched crop sensitivity, localized sensitivity)   source: T:decisive
BROAD_ACCEPT = [
    ("fixed_aligned", 24.05, 15.38),
    ("profile_aligned", 23.32, 13.45),
    ("profile_rotated", 21.23, 7.35),
    ("ct_only", 21.39, 13.37),
]
# ---- Fig. localization(b): paired differences (pp, 95% CI) --------------------
# (comparison, endpoint, est, lo, hi, source)
BROAD_PAIRED = [
    ("Profile: aligned $-$ rotated", "crop", 2.08, -0.27, 4.40, "M:BroadResults"),
    ("Profile: aligned $-$ rotated", "localized", 6.09, 4.38, 7.78, "M:BroadResults"),
    # sign flipped from 'profile - fixed' = -0.74 [-3.04, +0.54] (M:ReadoutResults)
    ("Aligned: fixed $-$ profile", "crop", 0.74, -0.54, 3.04, "M:ReadoutResults (negated)"),
    ("Aligned: fixed $-$ profile", "localized", 1.93, 1.05, 3.27, "M:ReadoutResults"),
]

# ---- Fig. strata: aligned minus rotated crop sensitivity, pp ------------------
# (group, n_focused, est, lo, hi, n_broad, est, lo, hi)   source: T:strata,
# 'All insertions' from M:FocusedResults (+14.72) and M:BroadResults (+2.08)
STRATA = [
    ("All insertions", 9882, 14.72, 11.11, 17.05, 12240, 2.08, -0.27, 4.40),
    ("Centered", 3294, -0.94, -5.98, 2.07, 4080, -5.34, -9.49, -1.25),
    ("Displaced", 6588, 22.56, 19.22, 24.83, 8160, 5.80, 4.02, 7.65),
    ("Faintest contrast", 3294, 0.70, -2.00, 2.34, 4080, -1.47, -2.60, -0.24),
    ("Strongest contrast", 3294, 27.32, 24.29, 30.15, 4080, 7.92, 4.26, 11.72),
    ("Strongest, displaced", 2196, 42.53, 38.39, 46.18, 2720, 15.40, 11.84, 19.08),
    ("Overlap $\\geq$ 50%", 6900, 9.52, 5.29, 12.20, 5991, -0.12, -3.59, 3.23),
]

# ---- Fig. native transfer ------------------------------------------------------
# point estimates: T:transfer; interval end points: R:native_transfer
NATIVE_LOCALIZED = {k: (v["est"], *v["ci"]) for k, v in _REC["native_transfer"]["localized"].items()}
NATIVE_FROZEN = {k: dict(sens=v["sens"], sens_ci=tuple(v["sens_ci"]), fpr=v["fpr"], fpr_ci=tuple(v["fpr_ci"]))
                 for k, v in _REC["native_transfer"]["frozen"].items()}
# cross-check against T:transfer (localized; frozen sens, FPR)
_T_TRANSFER = {"fixed_aligned": (5.66, 1.93, 0.46), "profile_aligned": (5.47, 2.15, 0.69),
               "profile_rotated": (2.70, 6.62, 4.63), "ct_shell": (4.21, 4.69, 2.55),
               "ct_only": (3.38, 10.83, 7.87)}

# ---- Supplement ROC and learning figures: R:roc, R:learning ----------------------
ROC = _REC["roc"]
LEARNING = _REC["learning"]
PLACEMENT_PANELS = _REC["placement_panels"]


def check():
    for k, (loc, s, f) in _T_TRANSFER.items():
        assert abs(NATIVE_LOCALIZED[k][0] - loc) < 0.03, k
        assert abs(NATIVE_FROZEN[k]["sens"] - s) < 0.03 and abs(NATIVE_FROZEN[k]["fpr"] - f) < 0.03, k
    t = {"fixed_aligned": 24.05, "profile_aligned": 23.32, "profile_rotated": 21.23, "ct_only": 21.39}
    for k, v in t.items():
        assert abs(ROC["broad"]["cap"][k]["sens"] - v) < 0.03, k
    return "recovered values agree with printed tables"


if __name__ == "__main__":
    print(check())
