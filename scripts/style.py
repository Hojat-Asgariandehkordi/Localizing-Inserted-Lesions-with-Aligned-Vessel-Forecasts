"""Shared figure style: Times-family serif text, STIX math, editable PDF fonts."""
import matplotlib as mpl
from matplotlib import font_manager as fm
import glob

import os
_HERE = os.path.dirname(os.path.abspath(__file__))
for f in glob.glob(os.path.join(_HERE, "fonts", "texgyretermes-*.ttf")):
    fm.fontManager.addfont(f)
# Use the TrueType conversions only (CFF/OTF copies embed with a type mismatch).
fm.fontManager.ttflist = [e for e in fm.fontManager.ttflist
                          if not (e.name == "TeX Gyre Termes" and e.fname.endswith(".otf"))]

# One colour per readout, used in every figure.
C = {
    "fixed_aligned": "#126584",   # blue
    "profile_aligned": "#067a64", # green
    "profile_rotated": "#a74e23", # orange
    "fixed_rotated": "#c98a5b",   # light orange
    "ct_shell": "#8b691f",        # ochre
    "ct_only": "#626b76",         # grey
    "hessian": "#7a4f9a",         # purple
    "focused": "#126584",
    "broad": "#067a64",
    "native": "#067a64",
    "ink": "#1b2a33",
    "muted": "#5b6b74",
    "grid": "#e3e9ec",
    "axis": "#b4c2c9",
}
MARK = {"fixed_aligned": "s", "profile_aligned": "D", "profile_rotated": "v",
        "ct_shell": "^", "ct_only": "o", "fixed_rotated": "<"}
LABEL = {"fixed_aligned": "Fixed subtraction, aligned", "profile_aligned": "Joint profile, aligned",
         "profile_rotated": "Joint profile, rotated", "ct_shell": "CT + shell summaries",
         "ct_only": "Observed CT only"}

COL_W = 3.25   # CVPR single column (in)
TXT_W = 6.875  # CVPR text width (in)


def apply():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "TeX Gyre Termes", "Nimbus Roman", "Times", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
        "axes.edgecolor": C["axis"], "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": C["muted"], "ytick.color": C["muted"],
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.labelcolor": C["ink"], "text.color": C["ink"],
        "axes.grid": True, "grid.color": C["grid"], "grid.linewidth": 0.5,
        "legend.frameon": False, "savefig.dpi": 300,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
        "lines.linewidth": 1.1, "errorbar.capsize": 0,
    })


def panel_label(ax, letter, title=None, x=-0.02, y=1.04):
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontweight="bold",
            ha="right", va="bottom", fontsize=9)
    if title:
        ax.text(x + 0.02, y, title, transform=ax.transAxes, ha="left", va="bottom", fontsize=8.5)
