# Fair core selections: pairs and triples

**Author:** Maxwell Flanagan. **Status:** draft for external correctness and priority review; no specialist response has been obtained.

The standalone manuscript compares two established fairness rules on the **entire core** of unit-capacity matching games: ascending leximin and lexicographic minimization of descending payoffs. With total matching surplus `T>0`, their normalized distance is `rho = ||x-z||_1/T`. Half that distance is the minimum fraction of surplus that changes recipients when switching rules.

The main candidate contribution combines a sharp finite pairwise distance bound with a sparse three-sided construction whose distance approaches two. The bipartite half-payoff guarantee is explicitly credited as a deduction from Vazirani's prior algorithm; the general-graph extension and additive benchmark are supporting results. This package makes no claim that priority or field-level significance has been established.

## Contents

- `manuscript.tex`: complete conventional proofs, common conventions, scope and source comparison. It has no external TeX inputs.
- `CLAIMS_AND_SOURCES.md`: claim-level priority assessment, primary-source theorem anchors and remaining access gaps.
- `REVIEW_REQUEST.md`: concrete questions for an external specialist; prepared text only.
- `PROVENANCE.json`: source commit and file hashes, local adaptations, AI assistance and review status.
- `source_notes/`: preserved detailed research source audits. These are historical notes; paths they mention are provenance references and are not required to run this package. The fresh ledger supersedes older bibliographic status.
- `verification/`: all Python sources and fresh bounded verification results.

Build the paper with `bash build.sh`; the PDF is `output/pdf/manuscript.pdf`. The enclosing release records PDF inspection and clean-archive replay in `BUILD_AND_REPLAY.json`. `SHA256SUMS` identifies the files supplied in this package.

## Reproduce the checks

Use Python 3.10 or newer; this package was tested with Python 3.13.5 and Z3 5.1.0. Install the pinned dependency once:

```sh
python -m pip install -r requirements.txt
```

From this package's root, the single verification command is:

```sh
python verification/run_checks.py
```

The entrypoint works from other current directories when invoked by absolute path. It reads only package-local Python files and regenerates its evidence. It removes the eight prior output JSON files before starting, runs every child under `python -O`, checks exact bounded input coverage, writes logs and JSON under `verification/results/`, and returns nonzero on an exception, solver failure, timeout or failed check. Its summary is `verification/results/verification_summary.json`. A typical run takes a few minutes; the per-stage timeout is 30 minutes. No network, repository checkout, external certificate archive or machine-specific path is needed at runtime.

## What is checked

| Stage | Evidence |
|---|---|
| Pair calibration | All 255 nonzero 2-by-2 weight matrices with entries 0–3; full coalition constraints and every selector stage. |
| Pair theorem | Coordinate core maxima and a violation query over **every** minimax point for the small cases; seven further matrices, attaining families with 2–6 matched pairs, exactness and two negative controls. |
| Triple calibration | All 256 binary 2-by-2-by-2 arrays, including empty and zero cores; Lucas's criterion as recorded in the inspected later source; 12 fixed-seed 3-by-3-by-3 controls; three additive sharp-family cases. |
| Triple construction | Eleven shifted/unshifted raw markets with matching and covering allocations; all selector stages; removing anchors and removing recurrence as separate controls. |
| Second construction generator | Four raw markets through 192 players, full selectors, coordinate maxima and entire-core inclusion. |
| Extensions | Six general-graph cases, including an empty odd triangle and nonbipartite sharp examples; eight nonuniform/additive cases and three additive distance-sharpness cases. |
| Source-class exclusions | Four parameters for the nonzero third mixed difference and positive recurrence powers; these check our deductions, not priority. |
| Independent corroboration | A fresh generator and SAT formulation, importing neither construction nor selector code: six raw triple markets, both core inclusions, uniqueness of the first nonfixed optimal floor and minimax face, and integer matching exceedance queries for three cases. Separately, 510 insertion-sort/lex-improvement queries recheck both full selectors on all 255 pair matrices; 987 player-padding counts. |

All arithmetic used for acceptance is rational or exact SMT arithmetic. The two main progressive-floor implementations are supported by the separate sorting formulation on the bounded pair census. Large raw-triple checks use the positive team inequalities and nonnegativity; omitted zero-weight team constraints are implied by nonnegativity. The matching/cover certificates identify the **integral** coalition value before selector optimization.

These are finite corroborations using Z3, not a proof-assistant formalization or an independently certified solver kernel. All-parameter theorems rest on the manuscript's proofs. The independent checks were developed in the same AI-assisted project and do not constitute external human review.

## Scope and open review items

All players, including zero-payoff dummies and padded isolates, count in `n`. The graph theorem assumes a nonempty entire core; the unit-weight odd triangle explains why that matters. The triple result permits arbitrary nonnegative array entries and asserts a supremum over increasing player counts, not an exact finite-player three-sided extremum. The additive theorem assumes complete markets and equal sector sizes. Neither construction is an exact TU game; exact rational computation is a different use of the word “exact.” Nothing is asserted about capacities greater than one, arbitrary perturbation robustness or typical empirical markets.

Original full texts of Quint (1991), Lucas (1995), and several older equality/egalitarian references remain access gaps. The 2026 implementation thesis was subsequently inspected through its full author LaTeX source; its PDF remains uninspected. It studies leximin implementation and runtime/memory, and lists leximax implementation as future work. See `SOURCE_ACCESS_FOLLOWUP.md` for the precise comparison and source version. The reviewer should assess these gaps before any priority claim. See `CLAIMS_AND_SOURCES.md`.

## Revised priority assessment

Read `PRIORITY_REVIEW.md` before making novelty claims. It records the deeper 5September2026 source comparisons and material downgrades; `priority_review/` preserves authored evidence and normalized ledgers. Mathematical correctness and priority are separate. No outreach has been sent and no external review is recorded.
