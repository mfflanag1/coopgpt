# Acyclicity and simultaneous protection of individual core maxima

Journal submission candidate, 14 October 2026. Author: Maxwell Flanagan.
This is the current presentation of the former chain-cycle paper and the later
sector-graph and simultaneous-protection results. The earlier manuscript is
preserved as history, not counted as another independent paper.

**Current publication preparation:** [decision and package](submission_2026-10-14/README.txt) · [candidate bundle](submission_2026-10-14/Acyclicity_IJGT_candidate.zip) · [cover-letter draft](submission_2026-10-14/COVER_LETTER_DRAFT.txt) · [outstanding items](submission_2026-10-14/UNRESOLVED.txt). The current PDF has 11 pages; its exact source compiled and passed visual review. A fresh independent universal-proof review found no substantive gap, and the unchanged full portable suite passed with the recorded Python/Z3 versions. Recommendation: complete the remaining author/source revisions, then target International Journal of Game Theory. No submission or publication occurred.

[Fresh source comparison](submission_2026-10-14/GRAPH_LITERATURE.txt) distinguishes inspected originals from remaining gaps. [Truthful-production assessment](submission_2026-10-14/TRUTHFUL_NEXT_PAPER.txt) plans the next ambitious candidate without rewriting it. Historical `VALIDATION.json`, `SHA256SUMS`, `review/` and `sharing/graph_core_protection.zip` below refer to the September version; the new package records current source/PDF hashes and preserves those archives.

[Read the manuscript](output/pdf/manuscript.pdf) · [LaTeX source](paper/manuscript.tex) · [Historical specialist brief](SPECIALIST_BRIEF.md) · [Source boundaries](SOURCES.md)

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

Python standard library checks for the cyclic and simultaneous constructions:

```sh
bash build.sh
```

For the complete retained scientific suite, including tree clipping and exact
raw-core queries, install requirements-smt.txt in a Python environment and run:

```sh
COOPGT_PYTHON=/path/to/python bash build.sh --smt
```

To build the PDF with a conventional LaTeX installation:

```sh
bash build.sh --pdf
```

`--full` runs the SMT suite and PDF build. The package is self-contained; no
imports or files from the original research checkout are needed. Source files
were copied unchanged, with hashes in SOURCE_PROVENANCE.json. Generated result
files are refreshed by the runner, which invalidates prior success before work,
records FAILED on errors, and propagates subprocess failures and timeouts.
Checks run with python -O, using explicit validation guards.

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
