# Adaptive cycle-pair zero reduction fails

2026-09-07. Exact fixed-support theorem. Global sharp constant unresolved: 1/3 <= S_3 <= 2/5. No novelty or completed external review claimed.

## The stronger boundary claim is false

The previous CYCLE_BOUNDARY_LIMIT.md rejected zeroing an arbitrary prescribed cycle pair while preserving the optimal fixed-P obstruction. It left open whether some cycle pair could always be selected adaptively. The present example rejects that stronger claim, even when every other weight is freely reoptimized.

Use m=6 with diagonal matching and

    P = [(0,1,3), (2,4,1), (5,2,0)].

Keep only the pair entries of these matchings, all nonnegative, with original diagonal worth T=1 and nonempty entire original core. Define F(P) as the supremum of the original fixed-P obstruction over these weights, retaining independent coordinate-attaining original core witnesses.

The unique incidence cycle uses labels 0,1,2 and all three P-team nodes. Labels 3,4,5 are leaves. The three pair coordinates joining cycle labels within P-teams are exactly

    AB(0,1), AC(2,1), BC(2,0).

Their successive sector-incidence colors around the cycle are A,B,C,A,B,C. The earlier sampled patterns did not expose this counterexample.

**Certified theorem.**

    F(P) = 2/9,
    F(P | e=0) <= 58/267 for every one of the three cycle pairs e,
    F(P) - max_e F(P | e=0) >= 4/801 > 0.

Consequently every weight system attaining F(P) has all three cycle pair values strictly positive. No adaptive choice of a cycle pair permits an optimum-preserving move to its zero boundary, even allowing all other supported weights to change. This concerns actual original-core ideals, not the rejected difference-only proxy.

## Proof and independent arithmetic

ADAPTIVE_BOUNDARY_COUNTEREXAMPLE.json supplies an unrestricted rational primal and dual attaining the same value 2/9. It also supplies three rational duals for the three zero-coordinate restrictions. The existing full-team fixed-pattern verifier checks the unrestricted pair. The independent restricted-dual arithmetic reconstructs pair variables and full-team inequalities from P, checks multiplier signs, and bounds residuals using 0<=pair weights<=1 and 0<=core payoffs<=1. The forced-zero variable contributes zero rather than its usual upper bound. Each resulting upper is exactly 58/267. Separate original-core witnesses are retained for all nine unmatched players, so the objective bound applies to their actual coordinate maxima by compactness.

The support has nine incidence vertices and nine incidence edges, is connected, and has only the three stated nonleaf labels. Hence there is precisely one incidence cycle and the three listed coordinates exhaust its candidate pairs. The verifier requires all three restriction cases; omitting one fails. An empty-dual negative control also fails. No solver status or floating objective is accepted as evidence. The certificate proves the upper 58/267, without needing to claim exact restricted attainability.

Run `python3 -O verify_adaptive_boundary.py`. The source driver, retained discovery runs and certificate-generation script are in discovery/adaptive_boundary_archive.zip. The preliminary two repeated-label and twelve distinct-label probes were non-exhaustive discovery; their numerical successes are not universal results.

## Scope and pivot

This rejects both the prescribed-edge and adaptive-edge versions of the same fixed-support zero-coordinate mechanism. Retire it under the goal's two-failed-variants rule. Zeroing a pair does not itself eliminate all hypergraph incidence of its P-team; neither result rules out a different transformation that splits labels, changes P, or explicitly pays for lost obstruction. Nor does either result refute S_3=1/3.

The unresolved proof must control the interior of the admissible weight region or establish a transformation with a sufficient quantitative loss bound. Further experiments that merely choose a different cycle pair do not repair this mechanism. No additional search of that type is warranted without a new invariant.
