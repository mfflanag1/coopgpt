# Heterogeneous cyclic and multiple-cycle obstruction bounds

Date: 2026-09-07. Evidence: exact finite-pattern theorems and exact subsidies of six explicit markets. Global bounds remain **1/3 <= S_3 <= 2/5**. No all-size cyclic theorem or novelty claim is made.

## What is bounded

For an optimal diagonal matching mu and a specified integral partial matching P, write

    J(M,P) = w(P) + (1/3) sum_{i unmatched by P} H_i - T.

Here every H_i is the maximum over the original entire core. The following upper bounds cover **all admissible nonnegative pair coefficients** with nonempty original core and optimal mu, for each listed P. They bound that fixed obstruction, not other partial or fractional packings of a market.

| Pattern | Labels per sector | Exact subsidy of explicit witness market, divided by T | Universal bound on this fixed J/T |
|---|---:|---:|---:|
| Ring, b=2 | 8 | 1/4 | 0.250000070 |
| Ring, b=3 | 12 | 5/18 | 0.277777979 |
| Ring, b=4 | 16 | 7/24 | 0.291666975 |
| K3,3 incidence | 15 | 10/41 | 0.243902674 |
| Triangular-prism incidence | 15 | 10/41 | 0.243902698 |
| Cube incidence | 20 | 14/55 | 0.254545857 |

All terminating decimals in the last column are exact rational bounds. They include the positive-residual correction of rounded dual multipliers. The witness values and upper bounds bracket the optimal fixed obstruction; exact optimality over weights is not claimed.

## Patterns

The ring uses m=4b and

    P={(j,j+1 mod b,b+j):0<=j<b}
      union {(2b+2j,2b+2j+1,j):0<=j<b}.

Unlike RING_ZERO_SUBSIDY.md, the pair coefficients here vary freely. That earlier zero result applies only to its explicitly assigned weights.

For each cubic graph in the other three cases, create one hub label per vertex and one leaf label per edge. At each hub assign its three incident edges bijectively to sectors, requiring different sectors at the endpoints of each edge. The edge's P team consists of its two hub players and the edge-leaf player in the remaining sector. Thus P consists of disjoint actual teams. The hub graph has respectively 4, 4, and 5 independent cycles. The exact sector assignments and triples are the P arrays in MULTICYCLE_k33.json, MULTICYCLE_prism.json, and MULTICYCLE_cube.json. The generator chooses the first assignment in deterministic permutation order; no exhaustion over different sector assignments is claimed.

## Why the upper certificates cover arbitrary weights

Normalize T=1. Delete pair entries outside mu and P. This keeps both matching values, keeps mu optimal, and enlarges the original core, so J can only increase. It suffices to optimize the retained support.

For every unmatched player i, introduce a distinct nonnegative original-core witness x^(i), with total 1 and all full-triple inequalities. The diagonal matching has total 1. Maximize w(P)+(1/3)sum_i x_i^(i)-1. These independent witnesses can attain the coordinate maxima, so this LP optimizes precisely J over the retained markets. Zero-worth triples are covered automatically by nonnegativity. Every retained pair variable and witness coordinate is in [0,1]; each pair can be completed to a full triple bounded by a total-one witness.

For maximize c.z-1 with A.z<=0 and E.z=1, any lambda>=0 and unrestricted nu give

    c.z-1 <= sum(nu)-1 + sum_j max(0, c-A^T lambda-E^T nu)_j,

using those valid coordinate upper bounds. The verifier reconstructs all coefficients and evaluates this inequality with integer arithmetic at denominator 3*10^9. Across the six certificates it checks 3,330 nonzero inequality multipliers. All six upper bounds are strictly below 1/3. Empty-dual negative controls must fail.

These are bounded-pattern theorems. A failed sufficient transportation template was not used as a subsidy lower bound.

## Why the witness subsidies are exact

Each certificate includes rational pair matrices through their retained-support coordinates, total diagonal worth 1, and a full original-core witness for each unmatched player. These prove nonempty core, T=1, and a lower bound J at the listed value. In the subsidy dual the integral packing P is feasible, so s_3>=J.

A separate rational payoff y covers every original full triple and hence every coalition, and satisfies

    y_(s,j) >= w_mu(j)/3 >= H_(s,j)/3,
    sum(y) = 1 + the listed witness subsidy.

The second inequality follows from original diagonal tightness, which bounds every original-core coordinate by its diagonal team's worth. Thus this y proves the matching upper bound for the **full subsidy objective**, including all other packings. The verifier checks these inequalities exactly; it does not rely on the numerical coordinate-maximization outputs. Ideals are never recomputed after intervention.

## Reproduction

Run `python3 -O verify_cyclic_patterns.py` alongside the six certificate JSON files. No optimizer is needed. The package build includes this verifier.

For optional discovery, copy `discovery/cyclic_weights.py`, `discovery/cyclic_actual.py`, `discovery/multicycle_weights.py`, and their layout dependency `discovery/sparse_fixed_probe.py` into a scratch directory beside `universal_template.py`. With SciPy installed, run cyclic_weights.py for b=2,3,4, then multicycle_weights.py for k33, prism, cube, and finally cyclic_actual.py. The last script appends rational candidate protected allocations. Copy the resulting six JSON files beside a copy of verify_cyclic_patterns.py and require its exact PASS before accepting regenerated results. Floating LP success or rational reconstruction alone is not a proof.

## Consequence for the active goal

Six structurally relevant cyclic supports have now been tested over arbitrary pair weights. None of these selected obstructions can beat one-third. This supports returning to the unresolved sector-aware transportation/decomposition lemma, while retaining different sector assignments and other connected incidence patterns as live counterexample routes. It does not establish S_3=1/3, rule out all cyclic markets, or confirm novelty.
