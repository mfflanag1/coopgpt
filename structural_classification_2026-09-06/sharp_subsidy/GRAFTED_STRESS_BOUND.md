# The near-worst count pattern is not a stronger obstruction

Date: 2026-09-07. Evidence: exact bounded-pattern theorem, with solver-free primal and rounded-dual verification. The global sharp constant remains unresolved.

## Statement and scope

Take m=23 and optimal diagonal matching mu. Fix the partial matching

```
(0,1,4), (1,2,5), (2,3,6), (7,0,8), (9,10,0),
(11,12,1), (13,14,2), (3,15,16), (17,18,3),
(4,19,20), (5,21,22).
```

For every nonnegative three-sector pair-additive market with nonempty original core, T>0, and this diagonal matching optimal, the fixed obstruction

    J(M,P)/T = w(P)/T + sum_{i unmatched by P} H_i/(3T) - 1

is at most **318841253/1000000000 = 0.318841253 < 1/3**. Some such market has J/T at least **22/69 = 0.3188405797...**. Thus the supremum for this fixed P lies in that small certified interval. Exact equality at 22/69 is not claimed.

This is a bound on this fixed obstruction over all admissible pair weights, not an upper bound on the complete subsidy of every 23-player-per-sector market. Other partial or fractional packings in the same market are outside the statement.

The pattern has h=12 unmatched players per sector and, in sector B, L=7 residual-pair columns and N=2 degree-two rows. It is the four-junction pattern with two grafts already used to stress the universal construction. Its ratios 7/12 and 1/6 approach the worst scalar ratios of that proof. This one fixed pattern cannot itself establish a global lower bound above 1/3. No conclusion for all patterns sharing those counts follows.

## Why the finite LP covers all weights in the stated class

Normalize T=1. Delete pair entries outside mu and P. This keeps both matching values, keeps mu optimal, and enlarges the original core, so it can only increase the fixed obstruction. It therefore suffices to use the union of their pair supports.

Use a nonnegative variable for each retained pair value. For each unmatched player i use a separate nonnegative vector x^(i), constrain its sum to 1, and impose every full triple inequality. Constrain the total diagonal worth to 1. Every x^(i) is then an original core point: the diagonal attains 1 and a covering vector of total 1 upper-bounds all integral matchings. Maximize w(P)+sum_i x_i^(i)/3-1. The separate witnesses can attain their own core maxima, so this optimizes exactly the fixed obstruction over the sparse market class. We do not replace the entire core by a selected core face.

Every variable is at most 1: witness coordinates are nonnegative and sum to 1; any retained pair can be completed to a triple whose worth is bounded by such a witness's total. These bounds are valid consequences, and support the exact certificate correction below. There are 2,586 variables and 79,632 potentially nontrivial triple-witness inequalities. Zero-value triples are covered automatically by nonnegativity.

## Rational verification without exact basis recovery

Write the model as maximize c.z-1 subject to A.z<=0, E.z=1, and 0<=z<=1. For any rational lambda>=0 and unrestricted rational nu define r=c-A^T lambda-E^T nu. Then

    c.z-1 <= sum(nu)-1 + sum_j max(0,r_j).

This is ordinary weak duality plus the valid coordinate upper bounds. It tolerates rounded dual multipliers without assuming that their coefficient residuals vanish.

The stored certificate rounds 1,460 nonzero inequality multipliers and the equality multipliers to denominator 10^9. The independent verifier reconstructs every coefficient with integers at common denominator 3*10^9. Its total positive residual correction is exactly 137/200000000. The resulting rational upper bound is the one stated above. The floating solver's success message or objective is not used as proof.

A separate integer primal witness has scale 69. The verifier checks its diagonal worth, every unmatched player's full core witness, and objective 22/69 exactly. The certificate therefore contains both a feasible lower example and a rigorous nearby upper bound. An empty-dual negative control must fail.

## Reproduce and interpret

Run `python3 -O verify_sparse_graft.py` with `SPARSE_GRAFT_4_2.json` alongside it; no numerical libraries or optimizer are required. The discovery generator `discovery/sparse_fixed_probe.py 4 2` uses SciPy and writes a new certificate alongside itself. Copy that certificate next to a copy of the verifier before checking it. Discovery is optional and is not run by the default build.

The result isolates slack in the universal deletion template on a structurally relevant stress case. It supports investigating richer transfers of diagonal-pair coverage. It does not prove the one-third conjecture, exhaust all grafted trees, establish a new global bound, or confirm novelty.
