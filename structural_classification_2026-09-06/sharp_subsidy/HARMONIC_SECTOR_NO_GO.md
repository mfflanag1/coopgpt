# Sector-dependent harmonic weights do not give the universal one-third proof

Date: 2026-09-07. Exact counterexample to a specified certificate formula, with an exact positive control on the same tree. **The original subsidy conjecture remains unresolved, with 1/3 <= S_3 <= 2/5.**

## Statement

Let m=25 and let the optimal reference matching consist of diagonal triples. Fix the partial matching

    (1,0,2), (3,4,1), (0,5,6), (7,3,8),
    (9,10,5), (11,12,9), (8,13,14), (15,6,16),
    (17,11,18), (19,8,20), (21,22,10), (23,21,24).

Its label/P incidence graph is a tree. There are r=12 P-teams and h=13 unmatched players per sector, u=39 in total.

For sector s, make the labels of its unmatched players absorbing in the simple random walk on the incidence graph. Write HARM_i(e) for the probability that the walk started at P-node e first hits the unmatched label of player i. This notation denotes an auxiliary probability, not the original ideal H_i.

Consider the rule

    p_(i,e) = (1-theta_s)/h + theta_s HARM_i(e),
    0 <= theta_s <= 1,  i in U_s.

Allow the three sector parameters to vary independently. Also allow every diagonal and pair-block marginal to vary freely subject to the exact transportation conditions in VARIABLE_P_DIRECTION.md; no maximal-diagonal restriction is imposed.

Let t be the minimum guaranteed aggregate coverage parameter, so each diagonal pair must receive at least u-5+t copies, with three aggregate copies of every P pair. Then this rule has

    t <= 944938417/976562500 < 0.967618 < 1.

Consequently it cannot prove the one-third bound on this tree. It includes the earlier common-parameter rule as a special case, so optimizing one common mixing parameter cannot repair the failure either.

By contrast, **unrestricted P weights do admit t=1 on exactly the same tree**, using only transfers in the deleted player's sector. HARMONIC_FREE_CONTROL.json contains 1,605 rational packing entries establishing this claim. The result rejects the harmonic formula, not the transportation approach, the one-third conjecture, or this tree as a stable market class.

## Exact model

For deletion row i in sector s, let A_j be the residual capacity of the sector-s player at label j, with A_label(i)=0; let B_j be the minimum residual capacity of the other two players. Residual capacities subtract the unique incident P weight when a player is used by P.

Choose diagonal masses d_j and pair-block masses q_j with

    0 <= d_j <= A_j,     d_j <= q_j <= B_j.

Put R=sum_j(A_j-d_j). The exact transportation conditions are

    sum_j q_j + sum_e p_(i,e) <= m-1,
    q_j - 2d_j + A_j <= R  for every j.

The equality defining R is

    R + sum_j d_j + sum_e p_(i,e) = m-1.

These are the total and singleton cut conditions for transportation with the diagonal fixed. They are necessary and sufficient for realizing the chosen marginals by same-sector triples. Every sector's absorption probabilities sum to one at each P node; hence sum_i p_(i,e)=3 automatically, for any three sector parameters.

For every label j and missing sector a, impose

    sum_{i in U_a} q_(i,j) + sum_{i not in U_a} d_(i,j) >= u-5+t.

Substituting the harmonic formula eliminates the P variables and leaves 1,993 variables and 4,989 inequalities, plus 39 equalities. Valid bounds are d,q,theta in [0,1], R in [0,m-1], and t in [0,2]. Restricting t to [0,2] loses no possible certificate at the target t=1.

## Independent certificate verification

The discovery implementation computes harmonic probabilities by exact leaf elimination, then uses a floating LP to obtain candidate dual multipliers. Neither numerical success nor those elimination steps are trusted by the verifier.

verify_harmonic_sector.py independently reconstructs the incidence graph, validates matching and tree conditions, and checks 468 exact Dirichlet equations. Label values at nonabsorbing nodes are reconstructed as averages of neighboring P-node values; absorbing values are zero or one. It also checks probability bounds and sector totals. Connectedness and nonempty absorbing sets make the Dirichlet solution unique.

The verifier reconstructs the rational LP inequalities and checks 1,558 nonzero rounded nonnegative dual multipliers. If r=c-A^T lambda-E^T nu, variable upper bounds b give

    t <= lambda.b_ub + nu.b_eq + sum_j max(0,r_j)b_j.

All arithmetic is exact. The positive residual correction is included; it is not discarded as numerical error. The resulting upper bound is the rational value in the statement. Empty duals and damaged probabilities are rejected as negative controls.

For the positive control, the existing independent pair-coefficient verifier checks every deletion exclusion and player capacity, and aggregate coverage of (u-4)mu+3P. Additional checks verify the same-sector transfer restriction and exactly three copies of each P-team. The original entire core and its frozen ideals enter through the established deletion argument; no ideal is recomputed.

Run `python3 -O verify_harmonic_sector.py` alongside HARMONIC_SECTOR_NO_GO.json, HARMONIC_FREE_CONTROL.json, and verify_variable_p.py. The standard package build includes this check. Optional discovery/discover_harmonic_sector.py regenerates candidate certificate files using SciPy and the exact harmonic helper; run it in a scratch copy of the discovery folder with universal_template.py available on the Python path. Place the two generated JSON files beside a scratch copy of the independent verifier and verify_variable_p.py, and require exact verification before accepting them.

## Discovery scope and decision

The harmonic rule numerically reached t>1 on the earlier imbalanced chain and balanced junction tests, but failed on six deterministic random 12-edge trees. Only the displayed first tree's rejection is promoted to an exact theorem here. The seeds and floating records are retained in discovery/HARMONIC_SECTOR_DISCOVERY.json; this was not an exhaustive search over trees.

The independently certified failure persists with separate sector mixing parameters and flexible diagonals. Retire this formula. A new proof mechanism must allocate P weights using more than a convex mixture of uniform and these unweighted absorption probabilities. The full marginal-selection theorem remains open; the positive control shows that this failed rule is not an equivalent reformulation of that theorem.

No universal bound improved in this step. No novelty claim or paid consultation was made.
