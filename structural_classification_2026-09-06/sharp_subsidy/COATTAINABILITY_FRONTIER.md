# Simultaneous ideal attainment: a published safe class and an unbounded obstruction

Date: 2026-09-07. The active sharp-constant goal remains unresolved, with 1/3 <= S_3 <= 2/5. The safe class below is source-derived and is not claimed as a new theorem. The incompatibility result is a consequence of our retained lower-bound family; its priority has not been established.

## Sector-wise attainment gives zero subsidy

Suppose there are three original core allocations x^A,x^B,x^C such that x^s_i=H_i for every player i in sector s. Their average y=(x^A+x^B+x^C)/3 remains in the original core by convexity and satisfies y_i>=H_i/3 by nonnegativity. It totals T, so s_3=0. The construction uses original ideals throughout and changes no coalition values.

Martínez-de-Albéniz, Rafels and Ybern, [Maximum and minimum core payoffs for supermodular multisided assignment markets with local monotonicity](https://doi.org/10.1016/j.dam.2025.10.006), Discrete Applied Mathematics 379 (2026), Theorem 3.2, prove the required sector-wise simultaneous attainment for their square supermodular class satisfying condition (4). Their local condition requires that raising any one coordinate of a diagonal team to the next label cannot decrease its value. The averaging argument therefore gives zero frozen-ideal subsidy for the three-sector pair-additive intersection of that published class. It does not extend their theorem to arbitrary sparse supports.

The free original is linked and archived in FREE_SOURCE_ATTAINMENT_AUDIT.md. Sector-optimality is established prior work; we claim neither that concept nor this immediate averaging consequence as a field-level contribution.

## In the lower-bound family, distinct unmatched ideals cannot be attained together

Use the family M_q from SHARP_SUBSIDY.md, q>=1. It has m=2q+1 labels per sector, diagonal pair entries 1, diagonal worth 3, T=6q+3, and q disjoint P-teams each worth 5. Every original ideal is 3. Let U be the players outside P. There are q+1 members of U in each sector, hence |U|=3(q+1).

**Theorem.** Any original core allocation attains H_i=3 for at most one i in U. The nonempty faces

    F_i = {x in C(M_q): x_i=3},   i in U,

are pairwise disjoint. Exactly 3(q+1) core allocations are necessary and sufficient to attain all unmatched ideals collectively.

Proof. Let x be any original core point with x_i=3 for a player in sector s at label j. Diagonal tightness makes the two other coordinates at j zero. Their opposite-sector diagonal pair has value 1. Complete that pair with any sector-s player k. Its team worth is at least 1, while the two payoffs at j are zero. Therefore x_k>=1 for every sector-s player k.

A second ideal 3 in another sector t would analogously force every sector-t player to receive at least 1. But the sector-t player at label j receives zero. Thus a second attained ideal cannot be in a different sector.

Suppose instead two members of U in sector s both attain 3. All q+1 unmatched sector-s players receive at least 1; these two each receive two additional units. Hence x(U)>=x(U_s)>=q+5. On the other hand, summing the q disjoint P-team constraints gives x(P)>=5q, so x(U)<=T-5q=q+3. This contradiction excludes a second attained unmatched ideal in the same sector.

Each F_i is nonempty by the existing exact ideal witnesses. Since no core point belongs to two such faces, at least |U| points are needed to meet them all. Choosing one witness per face attains that bound. This proves the theorem for all q.

In particular, replacing individual witnesses by any fixed number of jointly maximizing core allocations cannot work uniformly over our market class, even on these incidence trees. This does not rule out averaging allocations that attain only fractions of the ideals, or a different fractional deletion certificate. The current one-third lower bound and two-fifths upper bound are unchanged.

## Reproduction

Run `python3 -O verify_coattainability.py`. It checks source-formula calibrations on the monotone supermodular pair-additive arrays

    v(a,b,c)=ab+2ac+3bc,  1<=a,b,c<=m,

at m=1,2,3,5,8. For each sector it constructs a core allocation attaining the coordinate-maximal formula, verifies every full team, and averages the three allocations to obtain the protected core point. The upper formula follows by summing adjacent diagonal-completion inequalities, and the constructed allocation attains it. These examples corroborate the cited safe class; they do not replace its published proof.

The checker also inspects the retained tree witnesses for q=1,...,12, verifies the scalar contradiction and checks that every unmatched face is represented separately. With `--smt`, it independently reconstructs all original triple constraints for q=1,2,3,4 and asks whether two unmatched payoffs can simultaneously be 3. All four queries are UNSAT; single-ideal controls are SAT. The conventional argument above supplies the all-size quantifier.

## Research consequence

The source audit narrows the boundary of the problem: simultaneous attainment resolves the ordered safe class, while the lower-bound family has linearly many mutually incompatible ideal faces. A successful universal bound must control aggregate protection despite that incompatibility. Neither assuming sector-wise attainment nor using a bounded collection of exact ideal-maximizing allocations can bridge the gap. The original sparse-core system retains the necessary independent witnesses.
