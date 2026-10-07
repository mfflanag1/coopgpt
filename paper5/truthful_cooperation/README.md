# Sharp subsidies for truthful production and network cooperation

**Consolidated working manuscript, 7 October 2026 — Maxwell Flanagan.**

[Current manuscript](manuscript.tex) · [Current specialist brief](specialist_brief.tex) · [Portable review packet](truthful_cooperation_review.zip) · [Consolidation ledger and audits](../../review_packages/2026-10-07/consolidation/README.md)

For every finite nonnegative min-linear production technology with K fixed forms, a deterministic rule is truthful for binding underreports of whole owner bundles, covers every coalition, and pays at most **(1+o(1)) T log K/log log K**. A matching fixed-owner lower bound holds even on simple DAGs, for the worst case with at most K structural cuts. Both owner count and resource dimension can grow. Total-payment factor and external-subsidy factor differ by one.

The main text contains the general upper, shared-fan lower, earlier sharp multi-glove hierarchy, concave-production extension, owner/dimension bounds, and finite-sample all-profile certification. The appendices incorporate the remaining finite-pool mechanisms, TTSP and Wheatstone results, monotone-envelope obstruction, structural/noise-class results, and scoped failures of alternative approaches. The ledger maps each result to its original research record; superseded drafts remain historical evidence.

Historical priority, field-level significance and human specialist validation remain **unconfirmed**. Internal model audits and finite exact tests do not constitute external peer review. Polynomial post-certification evaluation does not imply polynomial preprocessing. The owner-count/resource-dimension gap remains open.

- [Source comparisons](SOURCE_COMPARISON.txt), [reviewer plan](REVIEWERS.txt), [unsent drafts](OUTREACH_DRAFTS.txt).
- [Current integration and validation record](../../review_packages/2026-10-07/consolidation/README.md).
- Earlier audit and verification records under `review/` and `validation/` remain snapshots of their dated source versions.

The existing [manuscript PDF](output/pdf/manuscript.pdf) and [brief PDF](output/pdf/specialist_brief.pdf) are **historical pre-hierarchy exports**, not current manuscripts. Use the revised sources and native editor preview. Export current PDFs before sending PDF attachments. No replacement editor tab is needed.

## Reproduce

Unzip the current packet and keep its repository-relative directories. From the extracted root, run the commands in `REPRODUCE.txt`. The general campaign checks use Python standard library and `-B -O`; earlier routines that create reports are replayed in fresh scratch directories. The archive excludes stale PDFs, third-party papers, contact lists and private model transcripts. The canonical private repository contains the full provenance.
