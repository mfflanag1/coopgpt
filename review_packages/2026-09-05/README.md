# CoopGPT specialist review packages

Prepared 5 September 2026 from the portfolio audit at commit `21443c59`.

This release consolidates three research lines into focused manuscripts with local source comparisons, portable verification code, and precise requests for specialist review. External review is **pending**. Neither successful internal checks nor a prepared email counts as a specialist assessment.

| Package | Manuscript and reproduction | Priority questions |
|---|---|---|
| Stable core versus egalitarian stability | [Package instructions](stable_core/README.md), [manuscript source](stable_core/manuscript.tex), [review questions](stable_core/REVIEW_REQUEST.md) | The sharp six-player stable-core separation, with the classical segment and Mauri exact-game precedent credited. |
| Sharp unrestricted asymptotic separation | [Package instructions](asymptotic/README.md), [manuscript source](asymptotic/manuscript.tex), [review questions](asymptotic/REVIEW_REQUEST.md) | The first-order deficit constant 2 and exact whole-core constructions; earlier equivalent quantitative statements or standard realization results. |
| Fair core selections in assignment games | [Package instructions](assignment/README.md), [manuscript source](assignment/manuscript.tex), [review questions](assignment/REVIEW_REQUEST.md) | Sharp finite graph distance and sparse bounded-value triple constructions, with the prior algorithmic half guarantee correctly attributed. |

Each package contains `CLAIMS_AND_SOURCES.md`, `PROVENANCE.json`, `SHA256SUMS`, `verification/run_checks.py`, and its PDF under `output/pdf/`. Run verification with a Python environment satisfying that package's `requirements.txt`, where supplied:

```sh
python verification/run_checks.py
```

Build the manuscript with a LaTeX installation containing `latexmk`:

```sh
bash build.sh
```

The verification code was tested from clean archive extractions. A subsequent documentation update closed the implementation-thesis text gap and corrected the final 2025 article access statement; fresh archive checks confirmed that all scientific files and PDFs remain byte-identical to the tested release. `BUILD_AND_REPLAY.json` records the actual results and scope; these are finite corroborations of the conventional proofs, not exhaustive enumeration of every game or external novelty certification.

The [specialist shortlist](coordination/SPECIALISTS.md) uses verified institutional contacts. The [exact proposed requests](coordination/OUTREACH.md), [review status](coordination/EXTERNAL_REVIEW_STATUS.json), and [preliminary paper decisions](coordination/DECISIONS.md) keep external evidence distinct from preparation. Actual responses must identify the assessed manuscript version and be addressed before the goal can be completed.

The earlier 183-page divergence manuscript and PXC archive remain historical records. Their superseded matching upper-bound targets, the proposed coefficient `3+2 sqrt(2)`, and the incomplete fixed-player attainment argument are not established claims in these focused packages. The earlier portfolio inventory is [retained separately](../../portfolio_review_2026-09-05/REVIEW.md).

This work was developed with AI assistance. The packages disclose their internal proof and computational checks and do not assert independent human endorsement. No new research branches are part of this consolidation stage.
