# Sharp subsidies for protecting core maxima

**Consolidated working manuscript, 7 October 2026 — Maxwell Flanagan.**

[Current LaTeX source](manuscript.tex) · [Portable review packet](sharp_subsidy_review.zip) · [Consolidation ledger and audits](../../review_packages/2026-10-07/consolidation/README.md)

The main theorem is unchanged: in the stated strict three-sector pair-additive model, the supremal subsidy needed to protect one third of every original-core ideal is **S3=1/3**; every finite-market ratio is strictly smaller. The matching construction and full proof remain in the main text.

New appendices consolidate all surviving unincorporated results from this track: the general sector-count upper and integral-obstruction bound; sharp unit-capacity short-flow and one-sided-quota results; an entire-core transportation embedding; a rational endpoint-ideal incompatibility example; sparse core representation; incompatible ideal faces; an all-size ring perturbation with no size-uniform subsidy modulus; and a computer-assisted 33-player obstruction to forest-only optimal duals.

These are pointwise original-core protection results. They do not assert truthful reporting across profiles. The general rational-capacity short-flow bound and sharpness beyond three sectors remain open. The endpoint-incompatibility example itself has zero protected subsidy. Established max-flow/min-cut, salary-lattice, side-optimality and cut-ideal ingredients are credited.

The [existing ten-page PDF](output/pdf/manuscript.pdf) is a **historical 3 October export** containing the original sharp theorem; it does not contain the new appendices. Use the current source/native preview and export a refreshed PDF before sending. Earlier `review/BUILD_QA.json`, `review/VERIFICATION.json` and `MANIFEST.json` describe that historical release, not this source revision. The current hashes and validation are in the linked consolidation record.

## Reproduce

The portable packet preserves repository paths. Its `REPRODUCE.txt` lists the standard-library and optional solver-dependent commands separately. The main sharp theorem's standard-library verifier still checks 3,603,804 full-team inequalities, 27 label patterns, 48 rational packing cases and negative controls with assertions disabled. Additional structural and flow verifiers cover their separate finite certificates; written proofs establish the all-size statements.

Historical novelty and independent human specialist review remain **pending**. No journal submission or human endorsement is implied by model audits. The separate truthful-cooperation paper studies incentives and has a separate specialist request.
