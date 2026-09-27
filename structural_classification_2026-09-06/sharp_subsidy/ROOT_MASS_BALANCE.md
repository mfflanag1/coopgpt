# Root mass and a single unit of hub slack

Date: 2026-09-07. Necessary all-size identities in the specified tree certificate model; exact attainment on two seeds. Arbitrary-tree existence remains unresolved. Global sharp bounds remain 1/3 <= S_3 <= 2/5. No novelty or external review is claimed.

## 1. Model and statement

Let a label/P incidence tree have r P-teams, g degree-three labels, n2 degree-two labels, and ell leaves. Thus

    m=2r+1, n2=r-2g-1, ell=r+g+2, u=3(r+1).

Use same-sector fractional deletion certificates with E_i=0, maximal nonroot diagonals, three aggregate copies of every P-team, and zero P weights in rows rooted at degree-two labels. Section 8 of LEAF_DILATION_THEOREM.md then makes P weights constant through degree-two blocks. Sector balance is not needed for the identities below, although the retained examples satisfy it.

For a leaf j, let e(j) be its incident P-team and i1,i2 its two unmatched players. Define

    a_j = p_(i1,e(j))+p_(i2,e(j)),
    R = sum_{leaf j} a_j.

For a hub v define A_v=sum_i max_{e incident to v} p_(i,e). Let F_(i,j) be the extra diagonal-pair coverage at destination label j from same-sector transfers in row i, beyond its diagonal team. Put L_i=sum_e p_(i,e)-sum_j F_(i,j), the unused source capacity.

**Theorem.** Every such one-third certificate satisfies

    R >= g+2,                                      (1)
    sum_{hub v} A_v = R+3g-3.                     (2)

If R=g+2, then:

- every L_i is zero;
- every extra transfer destination is a leaf;
- each leaf has delta_j=1-a_j>=0 and receives exactly delta_j extra coverage in each of its three diagonal pairs;
- every hub has A_v<=4 and

      sum_{hub v}(4-A_v)=1.                       (3)

This is an equality characterization within the stated sufficient certificate model, not a proof of existence. For g=0, identity (2) forces R=3, so equality R=g+2 is impossible; the equality existence target below is restricted to g>=1. Zero-hub trees are already covered by ONE_HUB_THEOREM.md.

## 2. Proof of the root-mass lower bound

In any nonroot leaf row the maximal diagonal at j has mass 1-p_(i,e(j)). Its two root rows have zero diagonal. Since the P column sums to three, aggregate diagonal coverage at j is

    u-5+a_j.

All three diagonal pairs require u-4, so each requires extra mass at least delta_j=1-a_j. The three pairs are supplied by three distinct deletion sectors. Each same-sector transfer contributes to one diagonal pair only. Therefore total extra mass at leaves is at least

    3 sum_j delta_j = 3ell-3R.                    (4)

The inequality remains true if some delta_j is negative; extra masses themselves remain nonnegative.

For E_i=0, the rooted-tree supply identity gives residual source supply sum_e p_(i,e) in row i. Thus all extra mass, including nonleaf destinations, is at most

    sum_i sum_e p_(i,e)=3r.                       (5)

Combining (4) and (5) gives R>=ell-r=g+2.

## 3. Equality consequences

If R=g+2, then 3ell-3R=3r, so both bounds (4)-(5) are equalities. All row supplies are exhausted, there are no extra masses at nonleaf destinations, and every leaf pair meets its lower bound delta_j exactly. Since actual pair extras are nonnegative, all delta_j>=0. Any negative deficit or excess leaf-pair coverage would make the aggregate inequality strict.

At a hub, its diagonal coverage is u-A_v. With no extra mass there, the target u-4 forces A_v<=4.

## 4. Hub identity

Sum diagonal masses over all rows and labels. The E_i=0 identity gives

    sum_i D_i = u(m-1)-6r.                        (6)

By block constancy, each degree-two label has aggregate diagonal mass u-4. Each leaf has u-5+a_j, and a hub has u-A_v. Hence the same sum is

    m u -4n2-5ell+R-sum_v A_v.                   (7)

Equate (6) and (7), then substitute the tree counts in Section 1. This yields sum_v A_v=R+3g-3. At R=g+2 it becomes sum_v A_v=4g-1, proving (3).

As a consequence, any leaf-only E=0 formula assigning the same P weight to every team within a row is impossible when g>=2. In that case all P-bearing rows are leaf-rooted and the common P column total gives R=3, violating (1). This does not rule out the older uniform templates with nonzero degree-two-root P weights.

## 5. Exact attainment and checks

ROOT_MASS_CERTIFICATES.json contains full rational certificates for the two minimal two-hub port configurations:

| Ports | m | R | Full entries |
|---|---:|---:|---:|
| Different | 11 | 4 | 366 |
| Same | 13 | 4 | 491 |

The independent `verify_root_mass.py` checks all packing capacities, exclusions and required pair coefficients, then verifies the leaf-only restriction, sector balance, maximal diagonals, E_i=0, R=4, exhaustion of every row's source supply, absence of nonleaf extras, and equality at each leaf pair. Thus (1) is sharp on these two fixed supports. An empty-certificate negative control fails.

The exact coefficients were recovered from an LP minimizing R in the compressed system, then realized as full packings. Optimality of these two objective values follows from the conventional lower bound (1) plus exact feasible attainment, not a floating dual.

A deterministic numerical test imposed R=4 on each of the 500 two-hub count arrays from BLOCK_STRESS_RESULTS.json. Every case was feasible, including strong imbalances. These are nonexhaustive numerical observations, not an arbitrary-count theorem. Results and the driver are retained in discovery/ROOT_MASS_STRESS.json and discovery/root_mass_stress.py.

## 6. The next existence lemma

For trees with g>=1, seek a feasible fractional assignment of block weights and leaf transfers that simultaneously gives R=g+2, all root and leaf-pair equalities, and nonnegative hub slacks summing to one. This would eliminate hub transfers and identify an explicit balance condition for composition. Attaching a hub would have to raise R by one while redistributing, rather than increasing, the single unit of hub slack. These are necessary targets for an equality construction, not a proved joining operation.

Do not assume equality is without loss: if the R=g+2 face fails on some tree, check the unrestricted compressed system and then the actual subsidy obstruction. Failure of a stronger equality construction would not refute S_3=1/3. Cyclic supports and the original global target remain unresolved.

The attempted sector-specific affine formula with denominators equal to the number of leaf-rooted deletion rows in each sector returned numerical infeasibility in both port cases. Rational rounding of its attempted duals failed verification; no exact no-go for that formula is claimed. Discovery status is recorded separately. The root-mass theorem above is derived directly from necessary packing inequalities and does not rely on those failed reconstructions.
