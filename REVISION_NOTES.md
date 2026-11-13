# Paper 5 — revision notes (V6 → V7)

*Beyond the Blob: Localizing Inserted Lesions with Aligned Vessel Forecasts* (CVPR 2027, OpenReview BAKLvYCOa2)

Build: `latexmk -pdf main.tex` and `latexmk -pdf supplement.tex` (each compiles on its own).
Figures: `python3 scripts/fig_overview.py && python3 scripts/figs_results.py` (needs matplotlib, scipy, Pillow).

## What changed (supervisor checklist)

| # | Item | Change |
|---|------|--------|
| 0 | **Length vs. CVPR 8-page limit** | At the group's request the main paper now runs to about 9.3 pages of content (10 with references). CVPR 2027 allows 8 pages for the main paper, so it must be trimmed before submission. An 8-page version is commit `0776309`. |
| 1 | Abstract | Rewritten in plain words, with no undefined terms ("arm", "head", "smooth rotation", "joint profiling", "affine background"). Keeps all headline numbers and now states that the broader crop-level gain's CI includes zero. |
| 2 | Schematic Figure 1 | New `figures/overview.pdf`. Panels: (a) problem, (b) exterior forecast, (c) aligned vs (d) rotated subtraction, (e) the four gain rules. It uses a generated phantom, and the markers are computed by a simplified readout. It replaces the old box-diagram workflow figure. |
| 3 | Math step by step + algorithm | Sec. 3 defines core / hidden ball / exterior, then Eq. 1 (pairs). Sec. 4 builds z,u,t → model (Eq. 3) → null fit (Eq. 4) → the four gain rules as an itemised list with their own a and d → score (Eq. 6). **Algorithm 1** added. Localized sensitivity is now Eq. 7, moved into Protocol. |
| 4 | Tables | Table 1 is now one column (`tables/decisive_onecol.tex`). The HiPaS and calibration tables were moved from the supplement as one-column tables. The originals in `tables/` are untouched. |
| 5 | Plots | All plots redrawn with 95% CIs on every estimate, and one colour + marker per readout across figures. Strata is now a one-column figure with both studies on one axis; a filled marker means the CI excludes 0. Fonts are TeX Gyre Termes / STIX only; the figures no longer contain DejaVu (`pdffonts`). |
| 6 | Related work / Conclusion | Both already existed; tightened. Discussion renamed "Discussion and limitations". |
| 7 | Length | About 9.3 pages of content (see item 0). |
| 8 | Two mains | `main.tex` and `supplement.tex` compile separately. The supplement now numbers S1…, Table S1…, Fig. S1…, and main cites it as "Supp. S3" (hard-coded, so no `xr` needed on Overleaf). |
| 9 | Supplement → main | Moved into the main paper: the cohort table (Table 1), the CNN table and learning curves (Table 3, Fig. 4), the HiPaS table (Table 4), the calibration table (Table 5), the original frozen operating points (Table 6) and the ROC figure (Fig. 6). Also moved into the text: forecaster details and sanity checks, the hyperparameter settings, sampling and lesion-bank details, the power calculation, dominance-band rates, localization cross-checks, the LNDb FROC check, and the transition counts. The supplement keeps the readout algebra, the inference details, the strata table and the transition table. |

Other changes:
- Jargon removed throughout ("sealed", "locked", "viewed", "head" → classifier).
- The contributions are now a bulleted list.
- The primary crop criterion failing is stated in bold in Results.
- The LLM statement now also mentions Claude for this revision.
- Every number in the new `main.tex` was checked by script against the V6 sources (main, macros, tables, supplement). All numbers trace back to them.

## Open questions for the group

1. **Localization endpoint status.** The V6 Fig. 1 caption said "prespecified localization endpoint", but Supp. S4 says the localization and condition analyses are "secondary". V7 says "prespecified secondary endpoint". Please confirm that this matches the frozen protocol.
2. **Title.** The PDF title is "Beyond the Blob: Localizing…", but OpenReview lists only "Localizing Inserted Lesions with Aligned Vessel Forecasts". Make them match before the 16 Nov deadline.
3. **Recovered numbers** (not printed anywhere in V6; recovered from the vector SVGs by `scripts/recover_svg.py`, ±0.02):
   - HiPaS localized-sensitivity CIs (Fig. 7a) and the frozen sensitivity/FPR CIs (Fig. 7b).
   - All ROC curves and bands (Fig. 6).
   - The CNN learning curves (Fig. 4).

   The point estimates match the printed tables (checked in `scripts/data.py::check`). Please regenerate them from the score arrays if possible.
4. **Learning curve.** The 46-patient development AUROC in Fig. 4 is 67.05 (single seed, recovered). The text reports 67.54 (two-seed average). The caption explains the difference; please confirm.
5. **"Local head" → "CT-only classifier".** V6 said the focused study's excess-FPR bound of 4 pp was set "relative to the local head". V7 reads this as the observed-CT-only classifier. Please confirm.
6. **Figure 1 is a phantom**, not patient data. If you'd rather have a BioRender illustration, the skill's BioRender → Times-relabel route is still available. I didn't use it here because exporting at full resolution needs the Overleaf link.
7. `tables/macros.tex` is no longer read by `main.tex`; the prose now lives in `main.tex`. `reproduce.sh` still regenerates the macros and tables, but they no longer update the paper text automatically.

## Files
- `scripts/style.py` — shared Times style. TrueType Termes conversions are in `scripts/fonts/` (GUST licence); see `make_ttf.py`.
- `scripts/data.py` — every plotted number, with its source.
- `scripts/recover_svg.py`, `scripts/recovered.json`, `scripts/assets/` — recovered values and the CT crops.
- `figures/v6_original/` — the V6 SVGs (input to the recovery script).

## Figure clarity pass (independent review + BioRender)
An agent that was not involved in making the figures reviewed all seven of them. Fixes applied:
- **One convention for every figure.**
  - Colour = readout: blue Fixed, green Profile aligned, orange Profile rotated, olive CT + shell, grey CT only.
  - Marker = endpoint: circle for crop sensitivity, diamond for localized sensitivity.
  - Method names are the same everywhere, tables included: "Fixed, aligned", "Profile, aligned", "CT only", and so on.
  - Every axis says "(pp, 95% CI)", and the threshold is always called the "frozen LUNA16 cutoff".
  - Table rows are now in the same order as the figures.
- **Figures are saved at their printed width** (6.875 in, or 3.25 in for strata), so the fonts print at the size they were set in the scripts (7–8.5 pt).
- **Fig. 1 redesigned:** (a) problem; (b) paired crops with a shared exterior and one forecast; (c) aligned vs rotated subtraction, with computed marks; a footer defines the two outputs and both endpoints. The four-gain list moved out of the figure into Sec. 4.
- **Fig. 2:** the 14-mm mask is now a thin solid circle (dashed/dotted always means the search core), the lesion is shown with a gold ring, and the row labels name the study, readout and endpoint. The caption now points out that the control already shows a compact vessel response near the insertion site. **Authors: please check this example.**
- **Fig. 3:** bars coloured by readout, the bar end is explained, and the CIs are printed in (b).
- **Fig. 4:** a chance line was added, and the easy and hard probes are named.
- **Fig. 5:** the rows are defined (HU values, ≥50% overlap); the hollow "CI includes 0" encoding was dropped.
- **Fig. 6:** the y-axis now reads crop sensitivity, frozen cutoffs are open squares, and the HiPaS shift is annotated.
- **Fig. 7:** markers follow the endpoint convention, overlapping points are annotated, the y-ticks are integers, and the caption's wrong reference to Fig. 3 is fixed.

**BioRender:** three drafts were generated (prompts in this session; reference sketch `figures/biorender_ref/overview_ref.jpg`). Draft 2 (https://app.biorender.com/illustrations/7ae800bf0ad2989a51521f89) is used for Fig. 1(a). Its BioRender lettering is cropped out and all labels are typeset in Times. The account then ran out of AI credits, so no further generations were possible.
- **To do before camera-ready:**
  - Export that figure as a PNG at 300 dpi or higher and save it over `figures/biorender/overview_draft2.jpg` (the crop box in `fig_overview.py` assumes the 1024 × 572 preview, so scale the box with the export). Rerun `python3 scripts/fig_overview.py`.
  - Add the named BioRender citation (the review copy only says "created in BioRender").
- With more credits, a fully illustrated Fig. 1(b) (paired crops, forecaster box) could replace the computed panel. The precise prompt is kept in `docs/paper5-localizing-inserted-lesions/biorender_prompt.md`.

The same reviewer then checked the revised figures. All but one of the remaining points were fixed:
- Fig. 1: shared exterior tinted blue, "=" replaced by a "same exterior" bracket, and the search-core key moved into the footer.
- Fig. 6 and Fig. 7(b): frozen cutoffs are open circles in both.
- Fig. 5: series labelled directly.
- Fig. 3: single zero line.

**Open:** Fig. 2(a) still shows no returned marks, because the V6 data for this example did not include them. Authors: add the computed marks (green + / red ×) from the score arrays if you have them.

## CVPR style pass
- **Structure.** The paper now follows the standard CVPR layout:
  1. Introduction
  2. Related Work
  3. Method (Problem Setup, Exterior Vessel Forecast, Forecast-Conditioned Readouts, Scoring, Baselines)
  4. Experimental Setup (Datasets, Model Selection and Evaluation)
  5. Results (Effect of Forecast Alignment, Acceptance vs. Localization, Readout Flexibility and Learned Baselines, Analysis by Insertion Condition, Transfer to Native Vessels, Ranking vs. Calibration)
  6. Discussion and Limitations
  7. Conclusion

  There are no question-style headings, and the Discussion no longer reports numbers.
- **One study, not a project history.** The paper now presents a *low-texture LUNA16 subset* (the former "focused/original/locked" study), a *broader held-out set* and *HiPaS native vessels*. The text still states openly that the low-texture cases informed the design of the readouts.
- **Fixed vocabulary**, defined in Sec. 3.1:
  - *readout*: CT-only, fixed subtraction, plug-in or (joint) profile;
  - *placement*: aligned or rotated;
  - *classifier*;
  - *scorer* = readout + classifier;
  - *shell*: 15.5–19.5 mm (CT + shell control);
  - *block*;
  - *insertion bank*.

  "Arm", "head" and "fixed residual" are no longer used.
- **Constants moved out of the main text.** Implementation constants (forecaster, sampling, lesion model, hyperparameter tuple, dominance-band counts, CNN sanity values, timing) now live in Supp. S1–S6. The main text points to them. A script confirmed that every number dropped from the main text appears in the supplement.
- **Notation.** Decimals have leading zeros, CIs are signed brackets everywhere, equations are cited as `Eq.~\eqref`, and spelling is American.
- **Supplement.** Audit-log sentences (CRC/ZIP checks, pilots, cohort search) were condensed into single statements.
- **New Related Work paragraph** on lesion insertion, with two verified references: Robins et al., PMB 2017; Gong et al., SPIE 2021.
- An independent CVPR-style audit of the writing guided this pass.
- **One reviewer suggestion not adopted:** cutting back to 8 pages. The group asked for more than 8 pages.

## Official CVPR 2027 author kit
The source now follows `author-kit-CVPR2027-v1-latex` exactly:
- `cvpr.sty` and `ieeenat_fullname.bst` are byte-identical to the kit (checked with `cmp`).
- `main.tex` is the kit's `main.tex`. Only the title, the anonymous author block (plus empty PDF author metadata) and the `\input{sec/...}` lines differ.
- `preamble.tex` is the kit's `preamble.tex`. It enables the kit's optional `microtype` line and appends this paper's packages and macros, all loaded before hyperref as the kit requires.
- The text is split the kit's way: `sec/0_abstract.tex` … `sec/7_conclusion.tex`. The bibliography is `main.bib` (renamed from `references.bib`).
- The supplement is the kit's `sec/X_suppl.tex` (`\maketitlesupplementary`, page counter reset). `supplement.tex` is a small wrapper with the same preamble, so it still compiles on its own. It can also be appended to the main paper by uncommenting the kit's `% \input{sec/X_suppl}` line. The kit's `rebuttal.tex` is included for the rebuttal phase.
- `\raggedbottom` was removed so page layout follows the template defaults.
- A script confirmed that the paper text is identical to the previous version.
