# Stable core without egalitarian stability

Focused specialist-review package, 2026-09-05.

`manuscript.tex` contains the full six-player counterexample, its direct external-stability proof, the sharp player bound, and the three-regime additive ray. A secondary appendix supplies an exact arrangement cross-check. The previous general polyhedral algorithm and unrelated five-player discovery data are excluded from this package.

The core is the whole segment between `(1,1,0,1,3,0)` and `(2,0,1,0,1,2)`. Its terminal egalitarian claims sum to `13/2`, above the grand worth `6`, even though every imputation outside the core is dominated by a core point. This answers the stable-core inclusion asked in Dietzenbacher (2021), subject to specialist priority review. The exact-game counterexample was already computed by Mauri Masdeu (2017), Example5, and is explicitly credited as prior work.

## Reproduce

From this directory, run:

```sh
python3 verification/run_checks.py
```

Python 3.9 or later is sufficient; the package uses only the standard library. No network, solver, or installation is required. The command invalidates any previous result as `RUNNING` before reading inputs, records `FAIL` on an exception, exits nonzero on failure, and writes `verification/results/verification.json` and `verification/results/verification.log`. It also works when invoked by absolute path from another directory.

The command checks:

- All 63 nonempty coalition values in each supplied six-player table, their generator representation, exactness, monotonicity, and superadditivity.
- The main two-round procedural trace, two published calibration examples, Mauri's prior example, and the stated permutation/additive relation between the two supplied witnesses.
- The ray for **every real parameter `t>=0`**, by exact affine inequalities on 37 comparison cells plus every finite boundary. Seven additional point evaluations use a separate procedural implementation as diagnostics.
- The entire segment-core description, all 20,349 arrangement bases for each of two normalizations, and a rational core dominator for each of their 102 outside-core imputation vertices.
- Six negative controls, including missing zero-valued coalitions, duplicate keys/coalitions, and incorrect claims. Guard conditions remain active under `python3 -O`; the verification source contains no `assert` statements.

The main direct theorem is a written mathematical proof. The ray has a written induction over its player strata and a complete finite exact certificate of the affine comparisons. Neither a finite sample nor an optimization restricted to the generator hull is substituted for the full core.

## Files and review status

`CLAIMS_AND_SOURCES.md` records claim-level priority boundaries and fresh searches. `REVIEW_REQUEST.md` contains the specialist questions. `PROVENANCE.json` records source commit and file hashes. `IMPLEMENTATION_SUMMARY.md` describes extraction and verification changes.

**Independent human specialist review: PENDING.** Internal checks and successful program runs are not an external referee report. Full-text comparison with the final 2025 population-monotonicity article remains pending; its accessible 2024 working paper was inspected. The source manuscript makes no claim that this package has been submitted, accepted, or independently reviewed by a human.

Build the paper with `bash build.sh`; the PDF is `output/pdf/manuscript.pdf`. The enclosing release records PDF inspection and clean-archive replay in `BUILD_AND_REPLAY.json`. `SHA256SUMS` identifies the files supplied in this package.

## Revised priority assessment

Read `PRIORITY_REVIEW.md` before making novelty claims. It records the deeper 5September2026 source comparisons and material downgrades; `priority_review/` preserves authored evidence and normalized ledgers. Mathematical correctness and priority are separate. No outreach has been sent and no external review is recorded.
