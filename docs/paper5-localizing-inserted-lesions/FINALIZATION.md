# Paper 5 — finalization notes (working notes, not part of the manuscript)

**Scope set by the authors.** Figures, plus minor structure and paragraph changes. The science, claims and numbers stay unchanged.

**Contribution (one sentence).** A paired shared-exterior intervention with a value-preserving rotation sham shows that a correctly placed vessel forecast mainly improves *where* a candidate scorer looks (+6.09 pp localized sensitivity on held-out LUNA16, +2.76 pp on HiPaS native vessels), not how many crops it accepts. Fixed subtraction is enough.

## Baseline independent review (rubric 0–10)
| Originality | Soundness | Evidence | Clarity | Presentation | Overall | Confidence |
|---|---|---|---|---|---|---|
| 6 | 7 | 6 | 6 | 5 | **5** | 4/5 |

The reviewer flagged three objections that need new evidence and are outside this pass:
- all lesions are inserted;
- the primary crop endpoint failed, and robustness was checked post hoc;
- absolute localized sensitivity is low.

## Round 1: figures
- **Fig. 1 is now a graphical abstract.** It has a new panel (d) with the outcome: crop +2.1 vs localized +6.1 pp, with CIs, from `data.py`. The clipped footer strip is gone; its definitions are now in the caption. The figure is more compact.
- **Duplicate figure removed.** The old Fig. 6 (native transfer) repeated Table 4 and Fig. 5(b); the references now point there.
- **CNN learning curves moved** to Supplement Fig. S1, as low-information for the main paper.
- **Figure fixes:**
  - Fig. 3(b): group labels are now on the y-axis instead of being struck through by lines, and the legend is moved.
  - Fig. 3(a): legend spacing fixed.
  - Fig. 4 (strata): duplicate inline labels removed.
  - Fig. 2(a): scale-bar label overlap fixed.
  - All plots: no doubled zero line.

## Round 2: structure and paragraphs
- Contributions are a connected paragraph with bold labels ("Our paper offers the following contributions.").
- Related Work is two connected paragraphs that state what is unresolved: no prior work isolates placement.
- Sec. 5.1 leads with the prespecified held-out result (crop criterion not met; localization gain). The low-texture subset follows as supporting development evidence. The run-in mini-headings in Results were removed.
- Discussion and Conclusion are merged into one section of three paragraphs: takeaway, ranking vs calibration, and scope with a concrete next step. Setup run-ins were merged ("Operating points and metrics").

## Checks
- Both PDFs compile with no overfull boxes or undefined references.
- Only Times-family fonts appear (plus CM/STIX math); PDF author metadata is empty; the template is the official CVPR 2027 kit in review mode.
- Cross-document numbers were updated: ROC is now main Fig. 5; learning curves are Fig. S1.

## Round 3: cosmetic fixes from the final review
- Fig. 1(d): larger, with the labels as y-ticks. One dashed circle style is now used for the search core in every panel.
- Fig. 2(a): the scale bar no longer overlaps the circle.
- Fig. 3(a): the legend has a solid background.
- Table 2: a footnote explains the dashes.
- Sec. 5.6: the low-texture transfer conditions have their own run-in heading.

## Final independent review (same rubric, same reviewer, no target given)
| Originality | Soundness | Evidence | Clarity | Presentation | Overall | Confidence |
|---|---|---|---|---|---|---|
| 6 | 7 | 6 | 7 (+1) | 6.5 (+1.5) | **5.5** (+0.5) | 4/5 |

**Why the score stops at 5.5.** The 7.5 target is not reachable within this scope. The remaining objections are about evidence, not presentation:
1. All lesions are inserted, with no real-nodule or scan-level evaluation.
2. The prespecified primary crop endpoint failed, and the localization robustness was checked post hoc.
3. Absolute localized sensitivity is low, and the learned CNN shows no placement effect.

The most decisive next study would be a new prespecified held-out evaluation with localized sensitivity as the primary endpoint, ideally on adjudicated real nodules at scan level.

**Not adopted, because it would change content.**
- Merging Tables 4 and 5.
- Showing a single readout per subset across figures. The figures label the readout in every row instead.
- Adding returned-location markers to Fig. 2(a). These data are not in the V6 materials.

**Status.** Expanded working draft (about 9 pages of text). It has not been checked against the 8-page submission limit.
