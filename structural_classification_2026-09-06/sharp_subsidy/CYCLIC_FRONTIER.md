# Exact cyclic frontier: topology and the choice of obstruction

Date: 2026-09-07. Global bounds remain 1/3 <= S_3 <= 2/5. The universal inequality remains open. No novelty or completed external review is claimed.

## What is being bounded

Fix a diagonal matching and a partial matching P, with all pair entries outside their union zero. Normalize the diagonal grand worth to 1 and require a nonempty entire original core. For each player outside P, introduce an independent core witness for that player's coordinate maximum. Maximize

    J(M,P) = w(P) + (1/3) sum_{i outside P} H_i - 1

over all admissible nonnegative pair weights. This is the fixed-obstruction optimum F(P). Compactness allows each witness to attain its own maximum; the witnesses need not coincide. The LP therefore maximizes the actual fixed-P obstruction, not a proxy in which ideals are replaced by diagonal worths.

A dual bounds F(P) over all weights on that named support. It does not bound J(M,Q) for another matching Q in the same market. We separately certify the full subsidy of each retained witness market, using either conservative diagonal ideal upper bounds with matching primal/lower objectives, or exact full original ideals and a full subsidy primal-dual pair.

## Twenty-one retained unicyclic cases

The exact fixed-obstruction optimum equals (r-1)/(3r) in every retained unicyclic case, where r is the number of P-teams. All have m=2r diagonal labels and distinct labels within each P-team.

| r | m | Retained cases | Exact F(P) |
|---|---|---|---|
| 2 | 4 | 3 | 1/6 |
| 3 | 6 | 3 | 2/9 |
| 4 | 8 | 3 | 1/4 |
| 6 | 12 | 4 | 5/18 |
| 8 | 16 | 4 | 7/24 |
| 10 | 20 | 4 | 3/10 |

Each retained witness market has full subsidy equal to its listed F(P). These are 21 certificate records, not a claim of 21 distinct isomorphism classes or an exhaustive classification. The supports were obtained by generating incidence trees and merging compatible labels. These fixed-support results, together with BROKEN_RING_THEOREM.md, support investigating a general unicyclic theorem. They do not prove it. Arbitrary unicyclic topology and repeated-label teams remain obligations.

## Degree and sector leaf counts do not determine F(P)

Two connected two-cycle supports have m=15, r=8, degree counts (degree-one, degree-two, degree-three labels)=(7,7,1), and used-sector leaf counts (A,B,C)=(3,3,1), but their exact fixed-obstruction optima differ:

    CYCLIC_FRONTIER_8_2_0:       F(P)=3/11,
    CYCLIC_FRONTIER_COUNT_TWIN:  F(P)=4/15.

The gap is 1/165. Both equalities have an exact feasible primal and an exact dual with matching objective. Both have full-subsidy witness markets attaining those values. The second is a sector-permuted version of CYCLIC_FRONTIER_8_2_1, selected to make the sector leaf counts agree literally.

This disproves the proposition that F(P) is determined solely by these counts. It does not rule out a common count-based upper bound, nor prove that either value is the largest full subsidy over all markets on that support and all choices of obstruction.

## A chosen P can miss the strongest obstruction even on its own market

For the retained m=19 market CYCLIC_FRONTIER_10_2_3, all 57 original ideals are certified by paired primal and dual witnesses. They give

    J(M,P)=16/57,
    s_3(M)=869/3078,
    s_3(M)-J(M,P)=5/3078 > 0.

Delete the single team (12,9,11) from P, with sectors ordered A,B,C and labels starting at zero. The resulting partial matching Q already attains the full subsidy lower bound J(M,Q)=869/3078. The removed team contributes less matching worth than the protected floors of its three players; returning those players to the unmatched set improves the obstruction. An explicit protected allocation attains the same total, proving full optimality.

The retained all-weight dual upper for F(P), 56140447/200000000, is also strictly below this market's full subsidy. Thus even an exact fixed-P all-weight upper must not be interpreted as a full-market subsidy upper.

## Full-ideal verification resolves six cases

Six retained markets could not be settled using the conservative floor 'diagonal worth / 3'. The independent verifier now checks every original ideal and the full subsidy for all six:

| Record suffix | m | Exact full subsidy |
|---|---|---|
| 6_2_0 | 11 | 76/303 |
| 6_2_1 | 11 | 337/1377 |
| 6_2_2 | 11 | 3218/13089 |
| 6_2_3 | 11 | 1684/6705 |
| 10_2_1 | 19 | 7840/27891 |
| 10_2_3 | 19 | 869/3078 |

These are exact subsidies of specified markets. Except where primal and fixed-P dual explicitly coincide, do not report them as exact all-weight optima F(P). The other bicyclic fixed-pattern bounds remain valid rational upper bounds, sometimes with a small positive gap to the retained primal. Every retained full witness subsidy is below one-third.

## Certificate logic and independent reproduction

Run `python3 -O verify_cyclic_frontier.py` from this directory. It reads CYCLIC_FRONTIER_CERTIFICATES.json, containing 33 original records and the one sector-permuted count twin. It checks the declared inventory, matching validity, connected incidence graph, cycle ranks, degree and sector counts, fixed-pattern dual inequalities and exact primal witnesses. The fixed-pattern verifier retains its original default behavior; an explicit fixed-only mode is used solely when the separate full-market certificate is supplied.

For each of the six full-ideal markets, the new checker independently reconstructs supported pairs and every potentially nonzero full team. It checks nonnegative core witnesses of total 1 attaining each H_i and covering all teams. The diagonal matching attains 1, so these witnesses also establish grand worth 1 and a nonempty original core. For the maximum of coordinate i it verifies nonnegative team multipliers lambda and a free total multiplier nu with

    nu - sum_{teams containing j} lambda_t >= 1_{j=i},
    nu - sum_t lambda_t w_t = H_i.

Multiplying the original core inequalities proves each upper bound, and the attained witness gives equality. For the subsidy it checks a nonnegative protected payoff covering all teams and floors H_i/3, plus nonnegative multipliers lambda,mu with

    sum_{teams containing j} lambda_t + mu_j <= 1,
    sum_t lambda_t w_t + sum_j mu_j H_j/3 = sum_j y_j.

This proves optimality against every fractional subsidy obstruction, not just P. Omitted zero-worth teams follow from nonnegativity. All original coalition constraints follow by summing disjoint-team constraints.

The six full-ideal certificates entail 239,802 exact core/team checks. Negative controls reject a damaged ideal dual, an over-capacity subsidy dual, and an empty fixed-pattern dual. Floating objectives and discovery metadata are excluded from accepted certificate data. The standard-library checker imports no numerical solver and shares no layout implementation with the discovery generator. Its fixed-pattern component reuses the independently developed existing rational verifier.

Historical discovery scripts and raw outputs are archived in discovery/cyclic_frontier_archive.zip. Some record the original local import path and intermediate filenames; they are provenance, not the acceptance test. Certificate reproduction is the solver-free command above, which reconstructs all mathematical inequalities from the retained market data. The archive's manifest records SHA-256 for each member.

## Next load-bearing step

Prove or refute the one-third inequality for all unicyclic supports, tracking actual ideals and allowing the obstruction to change. The count-twin example rejects an exact classification by coarse counts, while the deletion example demands optimization over submatchings. Neither defeats the one-third conjecture. Further finite search is useful only when it tests a stated structural lemma or produces an actual stronger counterexample.
