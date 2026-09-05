# Sharp separation in assignment games

Internal mathematical checkpoint, 2026-09-04. For weighted bipartite assignment games with positive total matching value T, the exact largest normalized L1 distance between full leximin and leximax-min core allocations is

    s_n = floor(n/2) / (floor(n/2)+1)   for n >= 4,
    s_2 = s_3 = 0.

Here n counts all players, including isolated players. The result applies to the entire core of arbitrary assignment games; exactness is not assumed. The maximum tends to one. Within exact assignment games the two selections coincide, a consequence of known pairwise egalitarian structure.

The key structural theorem is stronger than the distance bound: leximin gives every player at least half their payoff in every other core allocation. Combining this with matching complementarity and a minimax directional witness gives the finite bound against **any minimax allocation**, including a nonunique optimal face. Complete markets with identical rows (1,...,1,2) attain it.

## Reading order

1. `output/pdf/sharp_assignment_separation.pdf`: four-page conventional proof, with editable LaTeX source.
2. `REVIEW_PACKET.md`: exact claim, prior-art boundaries and specialist questions.
3. `SOURCE_AUDIT.md`: dated primary-source review, including a reproducible discrepancy in a published example.
4. `INDEPENDENT_PROOF_AUDIT.md`: adversarial proof review covering degeneracy, fixed zeros, minimax faces and exactness.
5. `ALTERNATIVE_PROOF.md`: independent derivation of the finite bound using the largest-displacement block.

The prior unrestricted exact-game result remains at `../asymptotic_constant_two/` and commit `99e6e08499b945c97c8533dc526abcc8065ff80b`. Its files are unchanged. These game classes should not be confused: arbitrary assignment games need not be exact.

## Reproduction

From this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -O exact_assignment.py
.venv/bin/python -O verify_assignment_theorem.py
.venv/bin/python -O verify_identical_rows.py
.venv/bin/python -O verify_published_example.py
```

Run the first two commands in order: the structural checker consumes the bounded calibration produced by `exact_assignment.py`. The remaining scripts are independent of those generated results. All checks fail explicitly on a violated claim or a solver UNKNOWN/timeout; Python optimization cannot remove them. Arithmetic is exact rational arithmetic. The released environment used Python 3.13.5 and z3-solver 5.1.0.0.

| Replay | Coverage and independent evidence |
|---|---|
| `exact_assignment.py` | Every nonzero 2-by-2 matrix with entries 0,1,2,3: 255 markets, no symmetry quotient. Computes all coalition values by exact matching enumeration and both full selectors. |
| `verify_assignment_theorem.py` | All 255 cases: maximizes each individual payoff to check half domination; excludes every violating minimax point using an exact piecewise linear L1 query. Also checks seven targeted rectangular/degenerate markets, exactness where stated, and five attaining families through k=6 directly from full coalition constraints. |
| `verify_identical_rows.py` | Separate implementation: ten attaining-family cases with total n=4 through 13, including isolated players, from uncompressed matching-dual constraints. Proves no core point lies outside the segment. |
| `verify_published_example.py` | Reconstructs the six-edge published graph; verifies both full selectors and explicit strict improvements over its printed vectors. |

Four negative controls pass: first-stage maximin can fail the half guarantee; an arbitrary non-minimax comparison point can violate the finite correction; flat identical rows and diagonal-only markets make both selectors agree. These check hypotheses and construction mechanisms rather than asserting a failed theorem.

Finite replays support the conventional all-parameter proof. They are not proof-assistant formalization and do not certify novelty.

## Manuscript build

```sh
mkdir -p output/pdf
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf sharp_assignment_separation.tex
```

The release used TeX Live 2026 and latexmk 4.88. Its log has no overfull/underfull or undefined-reference warnings. All four rendered pages were visually checked. Source and evidence hashes are recorded in `SHA256SUMS`; PDF timestamp metadata may differ on rebuild, so byte-identical PDF rebuilding is not claimed.

## Status

Two mathematical lanes independently derived the structural restriction and attaining family. The shorter finite-bound proof received independent hostile review, and a further reviewer who did not participate in discovery checked the final manuscript. The final portable exact replay passed. External correctness, novelty and significance review remain pending; no external message or publication was made.
