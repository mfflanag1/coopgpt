# Acyclicity and simultaneous protection of individual core maxima

Journal preparation updated 17 October 2026. Inherited author name: Maxwell Flanagan; final author confirmation remains outstanding.
This is the current presentation of the former chain-cycle paper and the later
sector-graph and simultaneous-protection results. The earlier manuscript is
preserved as history, not counted as another independent paper.

**Current publication preparation (17 October 2026):** [readiness sheet](submission_prep_2026-10-17/SUBMISSION_READINESS.txt) · [dated manuscript](submission_prep_2026-10-17/manuscript.pdf) · [editable source](submission_prep_2026-10-17/manuscript.tex) · [author decisions](submission_prep_2026-10-17/AUTHOR_DECISIONS.txt). The eleven-page successor fixes journal presentation and installation instructions; the model, theorem statements and proofs are unchanged. The fresh Python 3.10.14 / Z3 5.0.0.0 full suite and compilation passed. It is prepared for a focused specialist read, subject to the author's sending approval; author declarations and source-priority questions still prevent calling it ready for journal submission. The [October14 bundle](submission_2026-10-14/Acyclicity_IJGT_candidate.zip) and October15 packet remain frozen. No submission or outreach occurred.

[Fresh source comparison](submission_2026-10-14/GRAPH_LITERATURE.txt) distinguishes inspected originals from remaining gaps. [Truthful-production assessment](submission_2026-10-14/TRUTHFUL_NEXT_PAPER.txt) plans the next ambitious candidate without rewriting it. Historical `VALIDATION.json`, `SHA256SUMS`, `review/` and `sharing/graph_core_protection.zip` below refer to the September version; the new package records current source/PDF hashes and preserves those archives.

[Read the manuscript](submission_prep_2026-10-17/manuscript.pdf) · [LaTeX source](submission_prep_2026-10-17/manuscript.tex) · [Historical specialist brief](SPECIALIST_BRIEF.md) · [Source boundaries](SOURCES.md)

## Result

Fix a connected allowed sector graph G with K>=2, equal sector sizes,
nonnegative pair matrices (zeros permitted), productive full teams only,
integral coalition matching worth, positive total worth, and nonempty entire core.
Both the full nominal-leximin guarantee and the best simultaneous fraction of
individual entire-core maxima are 1/K for trees and zero for cyclic graphs.
The triangle family has exact best simultaneous fraction 1/(2q+3).
A poorly protected player may depend on the chosen core allocation; every
finite market still has a strictly positive best fraction.

## What's consolidated

1. Entire-core tree cut representation and all-stage clipping proof.
2. The original fixed-alphabet triangle family and its pinned leximin target.
3. Entire triangular simplex, all individual ideals, and exact optimal protection.
4. Selective subdivision and zero-sector embedding for every cyclic allowed graph.

The subsidy program is separate and is not claimed as part of this theorem.
Novelty and independent human specialist assessment remain unconfirmed.
No submission, outreach, or purchase was performed.

## Reproduce

Use the [dated Online Resource1](submission_prep_2026-10-17/ESM_1.zip) and [reproduction record](submission_prep_2026-10-17/REPRODUCIBILITY.txt). Extract into a new writable directory; the runner regenerates its reports. From the extraction, with Python **3.10.14**:

```sh
python3.10 -m venv .venv
.venv/bin/python -m pip install -r requirements-tested.txt
COOPGT_PYTHON="$PWD/.venv/bin/python" bash build.sh --smt
```

`requirements-tested.txt` pins **z3-solver==5.0.0.0**, matching both the October14 replay and the fresh October17 install and complete replay. The historical `requirements-smt.txt` pin **5.1.0.0** is preserved for provenance and was not freshly tested; it is not the recommended reproduction route.

The standard-library subset is `bash build.sh`; it omits tree/raw-core SMT checks. In the dated supplement, `bash build.sh --pdf` builds the current manuscript with an existing conventional LaTeX installation. The package has no private-checkout imports. The top-level `paper/manuscript.tex` and `output/pdf/manuscript.pdf` retain the October14 presentation; use the dated successor links above for current preparation.

Source files are unchanged scientifically. Reports record failures and subprocess timeouts, and checks run with `python -O` using explicit validation guards. The new [exact artifact record](submission_prep_2026-10-17/EXACT_ARTIFACTS.json) binds the successor; older manifests still bind their own frozen versions.

## Executed coverage

- Trees: 120 clipping checks against raw core constraints, 56 strict improvements,
  path/star/binary shapes on 2 through 6 sectors.
- Cyclic graph family: 822,002 full-team cover inequalities over 13 cases;
  33,864 graph edge masks for the finite embedding check; 12 raw-core UNSAT
  queries; four rejected corrupt certificates.
- Simultaneous protection: 2,553,912 full-team cover inequalities; simplex,
  ideal and protection queries for q=1..4 (16 UNSAT queries); triangle vertices
  and optimal witnesses for q=1..8; six cyclic extensions; three rejected
  corrupt inputs.

These finite checks corroborate the self-contained all-parameter proofs. They
are not an exhaustive census of all markets, proof-assistant formalization,
or evidence of historical priority. Review findings and coordinator responses
are retained in review/RESPONSE.md. VALIDATION.json records final build,
visual checks, clean-archive replay and review status.
