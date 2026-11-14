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

## Cross-paper comments (applied 2026-11-13)
| Comment | Applied to paper 5 |
|---|---|
| Abstract: less technical, one message | Rewritten in plain language around the message "placement changes where the detector looks"; one headline number (about 6 per 100 insertions). |
| Contributions as connected sentences | Already a connected paragraph ("Our paper offers the following contributions…"). |
| Literature review | Present (two connected paragraphs); kept. |
| Toy example at end of intro | Added: a two-location example (vessel 1.0 vs lesion 0.8) showing the location moving with no change in the crop decision, plus the general condition $d_v-d_\ell>m(x_v)-m(x_\ell)$. |
| Variables defined before formulas; expand the math | Sec. 3.3 rewritten: $W_x$, the inner product and norm, $B$ and $P_x$ (explicit formula), $[\cdot]_+$, $\rho$, $\lambda$, $G$, $\tau$ all defined before use. Added: closed form for $g_0$, the 1-D nonnegative least-squares step $\Delta J=[a]_+^2/d$, a side-by-side table of $a$ and $d$ for the four readouts, the derivation of the profile loss via $g(h)$, the absorption inequality, and a motivation for the score normalization. All derivations were checked by hand. |
| Formulas within column width | Profile equation split onto two lines; no overfull boxes. |
| Tables hold results only | Cohort table (text inventory) moved to Supplement Table S1; the text keeps the numbers. |
| Fig. 2 one column, visible error bars, matching fonts | Placement figure is now one column (crops above, forest plot with capped CIs below), in Times. |
| Figs. 3/4 one column; no text over points; arrow colour | Localization and ROC figures are now one column (stacked panels). The ROC callout arrow is dark ink, not a data colour. The strata figure was already one column. |
| Conclusion reflecting the intro, shortcomings, future directions | Discussion and Conclusion are separate again. The Conclusion answers the research question, lists the shortcomings (inserted lesions, failed primary criterion, post hoc robustness, modest absolute sensitivity, calibration transfer), and gives five directions: scan-level real-nodule study, learned scorers with explicit aligned subtraction, curved forecasts, target-domain calibration, placement shams as a general control. |
| Fig. 1 a+b one column; Heun substep | Not applicable. Fig. 1 is a five-step graphical abstract that needs full width, and there is no Heun solver in this paper. |

## Skill checklist pass (cvpr-paper-revision SKILL.md, 2026-11-13 evening)
- **Toy example:** now uses numbers computed from the Fig. 1 code (`scripts/fig_overview.py`): junction 1.00 vs lesion 0.91 observed; 0.00 vs 0.89 after aligned subtraction; 1.50 vs 1.08 after rotated subtraction.
- **Contributions:** "First, … Second, … Third, …", with no bold labels.
- **Method:**
  - Lemma 1 (nonnegative least-squares reduction), Proposition 1 (profile loss obtained by eliminating the gain) and Proposition 2 (absorption of the lesion by an in-window gain), each with a short proof, all checked by hand.
  - Constants are replaced by symbols ($R_a, R_1, R_2, R_t, \sigma_W, r_W, \mathcal{R}$), with values in a closing "Implementation details" paragraph.
- **Experiments** follow the 4.1 Datasets / 4.2 Experimental Settings / 4.3 Baselines / 4.4 Evaluation Metrics layout, as prose without run-in headings.
  - Baselines moved here from the Method section.
  - The text explains why complete detection systems are excluded: a placement sham cannot be applied to them.
  - The notation "+x pp [a, b]" is defined.
- **Results:**
  - Every scorer in Tables 1–3 is now discussed in the text (CT-only, CT + shell, Hessian, plug-in and the rotated readouts).
  - The sentence "crop sensitivities of 21–24% for all scorers" was corrected to "about 19–24%" to match Table 1 (rotated fixed 20.81, rotated profile under the aligned classifier 19.26).
  - Figures and tables are cited in numerical order.
- **One formal Conclusion** merges the Discussion: answer, implications, ranking vs calibration, limitations, future directions.
- **Tables:**
  - Results only. The calibration table's text column was folded into the row labels.
  - Bold now marks the best aligned readout (Fixed, aligned) rather than the preselected lead.
  - Bold was removed from the HiPaS table.
- **Captions:** shortened, no bold; definitions moved into Sec. 4.4.
- **Abstract:** two headline numbers (about 6 and about 3 per 100 insertions).
- **Disclosure:** BioRender is named for Fig. 1(a).
- **Not applied:** capitalizing method names as proper names (e.g. "Profile"). It would ripple through every figure and table for little gain; the group can decide.
- **Length:** about 10 pages of text plus references (expanded working draft).
