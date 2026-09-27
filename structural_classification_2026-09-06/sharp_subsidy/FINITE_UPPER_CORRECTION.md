# Finite correction to the universal two-fifths bound

2026-09-07. Conventional proof with exact coefficient and real-domain checks. External review and novelty remain unconfirmed. The supremum bounds remain 1/3 <= S_3 <= 2/5.

## Statement

For a nontrivial connected diagonal/P reduction with h=m-|P|>=2 unmatched players per sector,

    J(M,P)/T <= 2/5 - 1/(60h).

Consequently no finite market in the original class attains subsidy ratio 2/5. A size-only consequence, for m original players per sector, is

    s_3(M)/T <= 2/5 - 1/(60m * 3^(3m/2)) < 2/5.

These are finite-size improvements. They do not imply S_3<2/5: the correction tends to zero with size. The lower family, sharp-constant target and frozen original ideals are unchanged.

## Improved donor budget

Use the notation and construction of MIXED_DONOR_UPPER.md. Put epsilon=1/20 and

    t=4/5+epsilon/h, alpha=1/h, beta=1-alpha,
    delta=max(0,t-2/h).

Give a degree-two donor budget 1-t, and a degree-three donor budget 2-t. Both are positive. All transfer and capacity arguments in the original construction continue to apply whenever the total donor budget covers the shortfall. In particular t<1, delta<beta, extra-transfer rows are leaves, and a donor is never the excluded label of such a row.

For a sector with positive shortfall, h>=3. With B=ell/h and x=L/h, the exact positive-branch shortfall is

    D=h[x(B-x)-B/5]-(x+B)+epsilon B.

This follows by substituting beta-delta=1-t+1/h into the original row capacities. The branch L=h and the branch where every row has capacity L/h have no shortfall, exactly as before. Let q be the number of positive-shortfall sectors, and X their sum of x. Then their total demand is at most

    h F_q(B)-X-qB+epsilon qB,

using the same quadratic upper functions F as the original proof. This estimate does not assume the corresponding shortfalls were positive at t=4/5; it applies to the newly selected positive sectors directly.

For 0<=B<=1, discard degree-three donors. The remaining donor budget is

    h(3-2B)/5-epsilon(3-2B).

The original three quadratic estimates each have gap at least 1/10 against (3-2B)/5. Discarding the nonnegative X+qB correction gives budget minus demand at least

    h/10-epsilon[3+(q-2)B] >= 3/10-4/20 > 0.

For 1<=B<=3/2, use n3>=h(B-1)-1 and n2=h(3-2B). Since 2-t>0, even when this lower bound on n3 is negative it yields the valid budget lower bound

    h G(B)-6/5-epsilon(2-B-1/h), G(B)=4B/5-3/5.

The total additional penalty relative to the original q-sector budget comparison is at most

    epsilon[2+(q-1)B-1/h] <=5epsilon=1/4.

The original proof's lower slack estimates, valid on these domains, are respectively:

* q=1: h(3/20)+B-6/5 >=1/4;
* q=2: h(1/10)+2B-6/5 >=11/10;
* q=3: 4B-6/5 >=14/5.

Thus the finite penalty is absorbed in all cases. For q=3, the original quadratic gap is nonnegative; for q=2, use X<=1 in the quadratic bound and X>=0 in the correction. For h=2, delta=0, so no donor-budget estimate is needed. This proves the increased-parameter construction feasible for every reduced support, including shared diagonal/P pairs and cycles.

## Aggregate coverage and obstruction

The P contribution remains three copies. At a degree-three label, starting coverage u-3 loses at most 2-t and leaves u-5+t. At a degree-two label, starting coverage u-4+alpha loses at most 1-t and leaves at least u-5+t. Leaf deficits are handled by delta and the unchanged row/column transfer construction. Thus aggregate deletion coverage is at least

    (u-5+t) a_mu(e)+3 a_P(e)

for every pair e, counting overlap additively. Apply each deletion packing to its own original core point attaining H_i. Nonnegative pair weights give sum_U H_i <=(5-t)T-3w(P). Therefore J/T <=(2-t)/3=2/5-1/(60h).

## Original finite markets and fractional obstructions

If subsidy is zero the displayed size bound holds immediately. Otherwise choose a rational optimal vertex lambda of the team-packing dual. The incidence matrix is integral with at most three unit entries per column. If its positive support has k columns, a vertex admits a nonsingular k-by-k submatrix of tight player constraints. Cramer's rule permits a common denominator D equal to the absolute determinant; Hadamard gives D<=3^(k/2)<=3^(3m/2).

Replicate D times as in REDUCTIONS.md. The rational obstruction becomes an integral P, with h'=D(m-sum lambda)<=Dm. Sparsification and component restriction retain or increase the obstruction. Each component's unmatched count is at most Dm. Nonpositive elementary components satisfy the same positive upper bound automatically; every other component satisfies 2/5-1/(60Dm). Weighting by component worth and using the replication identity proves the original ratio bound. Substituting the determinant bound gives the displayed size-only correction. All ideals in these comparisons are original core ideals of the relevant markets; none are recomputed during subsidy intervention.

## Reproduction and limits

The existing mixed-donor generator now accepts the original parameter or the proved finite parameter; its default is unchanged. `finite_mixed_donor.py` generates the finite versions of the existing fourteen test supports. `verify_finite_mixed_donor.py` checks deletion exclusion, all player capacities and aggregate pair coverage using exact rational arithmetic. With --smt, six real-domain inequalities are checked over all real h>=3 and the stated B intervals. These computations corroborate the conventional all-size proof above.

The strict finite bound explains why finite searches cannot attain the present upper constant. It supplies no uniform positive gap below 2/5 as m grows. Do not report it as an improved bound on S_3 or as a sharp finite-size theorem.
