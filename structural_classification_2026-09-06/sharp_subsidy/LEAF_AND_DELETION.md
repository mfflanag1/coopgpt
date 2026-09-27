# Leaf obstruction bound and deletion certificates

Current global bounds and the new all-size construction are in [current universal proof](MIXED_DONOR_UPPER.md). The one-third statements below retain their stated scope.

Date: 2026-09-07. Primary goal **ACTIVE**. Universal bounds remain 1/3 <= S_3 <= 2/5. The results below restrict where a counterexample to the proposed one-third upper bound can occur. They do not prove that bound in full.

## 1. A global obstruction bound from leaf counts

Fix an original market, an optimal diagonal matching mu of worth T, and an ordinary partial matching P of worth W. Write U for its unmatched players, h=|U|/3, and R=T-W. Since the original core is nonempty, R>=0. Let w_j be diagonal team j's value and k_j the number of its players in U.

For every i in U, **H_i <= min(w_j,R)**, where j is its diagonal label. The first bound follows from diagonal tightness and nonnegativity. The second follows from x(U)<=T-W for every original core point x: sum the disjoint P-team inequalities and use nonnegativity. Taking the maximum of one coordinate preserves the bound. Consequently,

    sum_{i in U} H_i <= sum_j k_j min(w_j,R).                 (1)

Define E=sum_j max(k_j-1,0). For k_j>=1, the right side of (1) at label j is at most w_j+(k_j-1)R. Labels with k_j=0 contribute zero. Hence

    sum_{i in U} H_i <= T+E*R,
    J(M,P):=W+sum_U H_i/3-T <= T/3+(E-3)*R/3.              (2)

This proof requires no pair additivity; in particular it is valid throughout the frozen class. It retains original core ideals throughout.

In a nontrivial connected component of the reduction in REDUCTIONS.md, every diagonal label is incident to a player of P. Thus k_j<=2. A label with exactly one player used by P has k_j=2; call it a leaf label, and let ell be their number. Then E=ell.

**Theorem.** Any associated partial-matching obstruction in a reduced connected component with at most three leaf labels is at most T/3. This includes arbitrarily large cyclic components satisfying that leaf condition. It does not assert that an arbitrary other partial matching in the same market has the same leaf condition.

By the replication and sparsification reduction, a counterexample to S_3<=1/3 must produce a connected associated obstruction with **at least four leaf labels**. Moreover it must have R>0, h>=2, and

    sum_j k_j min(w_j,R) > T+3R.                            (3)

These are necessary, not sufficient, conditions. The original positive lower-bound family itself does not violate the proposed one-third upper bound. Its limiting ratio remains one-third.

When h=1, the simpler bound sum_U H_i<=3R gives J<=0. When P is empty, diagonal tightness gives sum_i H_i<=3T and again J<=0. When U is empty, W<=T gives J<=0. These cases require no division by R and include R=0.

## 2. A weight-independent deletion template

For each i in U, seek a fractional matching lambda^(i) using no i, with every other player loaded at most one. Let its aggregate pair incidence be c(e), summing over all these deletion matchings. Let a_mu(e) and a_P(e) count appearances of pair e in the two reference matchings; overlaps are counted additively. Consider the coefficient condition

    c(e) >= (|U|-4)*a_mu(e)+3*a_P(e) for every pair e.       (4)

For |U|>=6, all requested coefficients are nonnegative. Such a certificate would imply the target obstruction inequality for every nonnegative choice of pair coefficients with mu optimal and nonempty original core. Indeed, original-core coverage implies

    H_i <= T-value(lambda^(i)).

This follows by applying the deletion matching to a core point attaining H_i; the total payoff on players other than i is T-H_i. Multiply (4) by the nonnegative pair values and sum. Then

    sum_i value(lambda^(i)) >= (|U|-4)T+3W,
    sum_U H_i <= 4T-3W,
    J(M,P) <= T/3.

Thus a universal construction satisfying (4), together with the already handled empty and h=1 cases, would prove S_3=1/3. **No universal construction is currently proved.** This is a sufficient combinatorial route, not an asserted equivalence or a substitute definition of completion.

## 3. Exact all-coefficient certificates beyond the leaf theorem

DELETION_CERTIFICATES.json records rational deletion matchings for these fixed reference configurations:

| Sector size | Partial matching P | Leaf labels |
| --- | --- | --- |
| 3 | (0,1,2) | 3 |
| 5 | (0,2,4), (1,3,0) | 4 |
| 7 | (0,3,6), (1,4,0), (2,5,1) | 5 |
| 9 | (0,4,8), (1,5,0), (2,6,1), (3,7,2) | 6 |
| 7 | (0,1,2), (3,0,4), (5,6,0) | 6 |

The independent standard-library verifier checks the exact configuration list, all deleted-player exclusions, nonnegative rational packing coefficients, every player capacity, and aggregate pair domination (4). It checks 523 retained packing entries and rejects an empty damaged certificate. It does not import SciPy or trust floating feasibility.

These are all-coefficient obstruction bounds for each specified P and diagonal mu, including additional nonnegative pair entries outside their support. They are **not** a proof that every obstruction at these sizes, or every market with these sizes, has subsidy at most one-third. The fixed configurations include four-leaf and larger cases not covered by Section 1. The optional generator is discovery/deletion_certificate.py; the exact verifier is verify_deletion.py.

## 4. Discovery ledger and limits

- The ordinary integral-deletion marginal relaxation was solved numerically for 60 fixed matching instances at sizes 3 and 4, and one five-label chain. The largest relaxation ratios were 4/15 and 1/3 respectively. These substitute upper claims for actual H and do not establish those subsidy values.
- A cutting-plane relaxation using fractional deletion matching values reproduced the original chain obstruction optimum for sizes 3,5,7,9,11. The size-13 run reached its declared 150-cut iteration limit and failed; no size-13 conclusion is claimed. This program is not an exact proof.
- A direct test of (4) returned floating feasibility for 180 seeded configurations at sizes 3 through 8 and ten at size 9. A subsequent larger exploratory run was deliberately terminated after the proof direction changed; unfinished configurations are not counted. No exhaustion or universal theorem follows from these runs.
- Initial coefficient rationalization failed at the nine-label chain. Minimizing the total packing mass instead of a zero objective produced exact rational certificates that passed the independent checker. No numerical tolerance is accepted as a substitute for the final exact inequalities.

The next mathematical task is to construct deletion certificates uniformly for leaf-rich connected components, or find a certified violation of the proposed one-third bound there. A failed deletion template would only refute this sufficient route; it would not by itself refute the original subsidy bound. Cycles with four or more leaves and heterogeneous diagonal values remain live.

## 5. Source comparison advanced this turn

Nguyen and Zick's [Resource Based Cooperative Games: Optimization, Fairness and Stability](https://people.umass.edu/yzick/papers/resource.coopgames.comsoc2018.pdf), Section 2, defines its cost-of-stability ratio as the minimum total stable payment divided by optimal coalition-structure worth. Its resource model values a coalition by its best feasible task. The displayed stability LP has no frozen individual-core-maximum floors; its fairness discussion introduces the Shapley value. These definitions and LP are established ingredients, not our contribution. The retrieved source does not supply the present sharp frozen-floor assignment bound. This closes that specific model-definition comparison, not the entire literature audit.

The claims-constrained-core literature and the earlier free-original gaps remain open. No source search here establishes novelty, and no paid consultation, purchase or outreach was made.
