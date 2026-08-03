# Six-player quantitative carrier theorem

The current paper proves, by a two-level separation theorem and focused
rank-six incidence classification, that

\[
\eta_S(\psi) \geq \gamma_S(\psi)
\]

for every exact cooperative game with at most six players, every core
reference point `psi`, and every proper nonsingleton target coalition `S`.
The rendered paper is [`wrapper.pdf`](wrapper.pdf).  A larger complete exact
computation is retained only as independent redundancy.

The threshold is sharp.  A seven-player three-generator lower-envelope exact
game has `(gamma_S,eta_S)=(3/4,0)` at its exact leximin point and `(1,0)` at
the core reference zero; see
[`N7_EXACT_CARRIER_COUNTEREXAMPLE.md`](N7_EXACT_CARRIER_COUNTEREXAMPLE.md) and
the two `src/verify_n7_exact_carrier_counterexample*.py` verifiers.
Null-player extension gives a counterexample in every dimension `n>=7`, so
the six/seven boundary is the complete dimension threshold.

## Structural reduction

The main proof no longer requires optimizing all 1,489 eta-dual orbits.
If `eta<gamma`, the target-floor multipliers in an optimal dual strictly
separate the high-total core slice from the nonnegative orthant.  The
two-level separator theorem forces at least three distinct multiplier levels.
A focused rank-six incidence classification then leaves no such support in
the `3+3` split and one orbit in the `4+2` split:

```text
1_S + e_1 + 2 e_2 + 1_35 + 1_136 + 2 1_456 = 3 1_N.
```

Its objective is `s(35)+s(136)+2s(456)`, which is at least `2*gamma` directly
from the carrier inequality for `C={4}`.  The focused exact verifier checks
65,133 small incidence supports and replaces the former exact-cone census as
the logical proof.  The larger 1,489-orbit audit remains as independent
redundancy.

```sh
python src/verify_n6_three_level_eta_duals.py \
  --output results/n6_three_level_eta_duals.json
```

After deleting eta-dual columns dominated by the zero-cost target floor
variables, adjoining `S` with coefficient one identifies every relevant
eta-dual vertex with a minimal balanced collection containing `S`.  Such a
collection has at most six coalitions.  The exhaustive census therefore
checks 6,508,883 candidate supports for each of the two remaining splits.

| split | labeled collections | symmetry orbits | exact minimum |
| --- | ---: | ---: | ---: |
| `3+3` | 21,695 | 870 | 1 |
| `4+2` | 19,501 | 619 | 1 |

All 1,489 orbit objectives have exact rational lower-bound certificates.

## Reproduction

Run these commands from `coopgames/`.  The Python programs require NumPy and
SciPy; the census requires a C++17 compiler.

```sh
clang++ -O3 -std=c++17 -Wall -Wextra -pedantic \
  src/enumerate_n6_eta_dual_vertices.cpp \
  -o /tmp/enumerate_n6_eta_dual_vertices
/tmp/enumerate_n6_eta_dual_vertices \
  results/n6_eta_dual_vertex_census.json

python src/verify_n6_eta_dual_vertex_census.py \
  --census results/n6_eta_dual_vertex_census.json \
  --results-dir results \
  --output results/n6_eta_dual_vertex_census_verification.json

python src/audit_n6_eta_dual_vertices.py \
  --census results/n6_eta_dual_vertex_census.json \
  --output results/n6_eta_dual_vertex_audit.json

python src/verify_n6_eta_dual_vertex_audit.py \
  --audit results/n6_eta_dual_vertex_audit.json \
  --output results/n6_eta_dual_vertex_audit_verification.json
```

The final verifier does not call an optimizer.  It reconstructs the exact-game
cone and replays every saved rational stationarity identity and lower bound.
The two structural sample files used as an independent census cross-check are
`results/n6_s3_eta_dual_orbit_sample.json` and
`results/n6_s4_eta_dual_orbit_sample.json`.

To rebuild the attached paper, run:

```sh
cd paper3
latexmk -pdf -interaction=nonstopmode -halt-on-error wrapper.tex
```
