# Sharp subsidies for truthful production and network cooperation

**Focused Economic Theory candidate, 14 October 2026 — Maxwell Flanagan. Local and unsubmitted.**

[Main source](manuscript.tex) · [Main PDF](output/pdf/manuscript.pdf) · [Indexed supplement](supplement.tex) · [Supplement PDF](output/pdf/ESM_1.pdf) · [Two-page comparison](output/pdf/specialist_brief.pdf) · [Current candidate archive](submission_2026-10-14/Truthful_Economic_Theory_candidate.zip) · [Author decision sheet](submission_2026-10-14/DECISION.txt)

For every finite nonnegative min-linear technology with K fixed forms, a deterministic rule is truthful for binding underreports of whole owner bundles, covers every coalition, and pays at most **(1+o(1)) T log K/log log K**. A matching fixed-owner lower holds even on simple DAGs, for the worst case with at most K structural cuts. Total-payment and external-subsidy factors differ by one. K can be exponential in a compact description.

The nine-page main contains the complete general upper and shared-fan lower proofs. The 63-page indexed supplement preserves the earlier hierarchy, concave-production extension, owner/dimension bounds, all-profile certification, restricted mechanisms and exact obstructions. Its foundational proofs are repeated for independent readability. These are supporting results within this paper, not additional paper candidates. The original [October compendium](research_record/manuscript_2026-10-07.tex) and brief are preserved unchanged.

The fresh audit repaired a scope error in an auxiliary two-owner example; its replacement now works on the full bundle domain. The cut-budget inversion explicitly requires 0 < epsilon < 1. The central theorem is unchanged. [Adjudication](submission_2026-10-14/ADJUDICATION.txt) records the correction, independent reviews and proof/source bindings. [Source comparison](SOURCE_COMPARISON.txt) incorporates the final 2007 Brânzei original and ABV author manuscript, with version limits.

Historical priority, field-level significance and human specialist validation remain **unconfirmed**. Internal model audits and finite exact tests are not external peer review. Author affiliation, correspondence, declarations and responsibility still require confirmation. The owner-count/resource-dimension gap and potentially exponential certification preprocessing remain explicit.

## Reproduce

Extract the [scoped verification archive](submission_2026-10-14/ESM_2.zip), retain its relative paths, and follow [REPRODUCE.txt](submission_2026-10-14/REPRODUCE.txt). Five bounded checks run with standard-library Python and `-B -O`; they test the general mechanism, weighted lower, projection diagnostic, two-owner repair and cut/ownership symmetries. The [fresh record](submission_2026-10-14/validation/scoped_replay.json) contains hashes and full outputs.

The [October 7 consolidation ledger](../../review_packages/2026-10-07/consolidation/README.md) retains the broader historical audits and replay evidence. The old `truthful_cooperation_review.zip` is a historical source/check package, not the current candidate. Current PDFs above are freshly compiled and visually inspected. No outreach or submission was sent; GitHub has not been updated by this local preparation.
