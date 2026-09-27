# Universal upper bound 2/5 using degree-two and degree-three donors

Date: 2026-09-07. **Goal active.** Conventional all-size theorem, independent rational coefficient checks, and optional exact real-arithmetic checks of its scalar inequalities. Sharpness, novelty and specialist review remain unresolved.

**Theorem.** In the frozen original strict three-sector nonnegative pair-additive model,

    1/3 <= S_3 <= 2/5.

This improves the preceding upper bound 5/12. Equal finite sector sizes, positive original integral grand worth T, and nonempty original entire core are retained. H_i always denotes the original entire-core maximum.

## 1. Reduction and target

Use the replication, sparsification and component reduction in REDUCTIONS.md. Fix an optimal diagonal matching mu and a partial matching P in one nontrivial connected label component. Let h=m-|P|, u=3h, and U be the unmatched players. The elementary cases P empty, h=0 or h=1 have nonpositive obstruction. Assume h>=2 and label used degrees in {1,2,3}.

As in the preceding deletion proofs, it suffices to construct one fractional matching avoiding each i in U with aggregate pair coverage

    (u-21/5) a_mu(e) + 3 a_P(e).                         (1)

Original-core coverage bounds its value by T-H_i. Hence (1) gives

    sum_U H_i <= (21/5)T-3w(P),
    J(M,P)=w(P)+sum_U H_i/3-T <= (2/5)T.

Nonnegative pair weights and additive counting of shared mu/P pairs are essential here. The coefficient construction below uses no modified ideals.

## 2. Counts and the transfer shortfall

Let ell,n_2,n_3 be the numbers of labels of degrees 1,2,3. Connectedness and incidence counting, exactly as proved in SURPLUS_UPPER.md, give

    2ell+n_2=3h,      n_3>=ell-h-1.

For sector s let L_s count degree-one labels whose unique used player is in s, and N_s count unmatched sector-s players at degree-two labels. Then

    ell=h-N_s+L_s,      sum_s L_s=ell.

Set t=4/5, alpha=1/h, beta=1-alpha, and delta=max(0,t-2alpha). For fixed sector write L=L_s,N=N_s. Each of its h unmatched rows has initial transfer capacity

    c_i=min(L alpha,beta)        at a degree-two label,
    c_i=min(L alpha,beta-delta)  at a degree-one label.

Its residual-pair columns require total L delta. Define D_s=[L delta-sum_i c_i]_+, or zero when L=0 or delta=0.

If L=h, N=h and there is no shortfall. If L<=h-1, degree-two rows already have maximal column capacity L alpha. If all degree-one rows also have this capacity, there is no shortfall. In the remaining branch, put B=ell/h and x_s=L_s/h. Substitution gives

    D_s=[h f_B(x_s)-(x_s+B)]_+,
    f_B(x)=x(B-x)-B/5.                                  (2)

Also 0<=B<=3/2, sum_s x_s=B, and x_s>=B-1 when B>=1. A positive shortfall implies delta>0, so h>=3.

## 3. The mixed donor budget

Give every degree-two label budget 1/5 and every degree-three label budget 6/5. Their total is

    C=(n_2+6n_3)/5.                                     (3)

We prove sum_s D_s<=C.

Let q in {1,2,3} count sectors with positive D_s. If q=0 the claim is immediate. For q positive, sum (2) only over these sectors. Let X be their sum of x_s. Concavity gives sum x_s(B-x_s)<=BX-X^2/q.

First suppose B<=1. The following upper bounds on sum f_B(x_s) hold for q=1,2,3 respectively:

    F_1=B^2/4-B/5,
    F_2=B^2/2-2B/5,
    F_3=2B^2/3-3B/5.

For q=1 maximize a single quadratic freely. For q=2, X<=B and BX-X^2/2 is increasing up to B. For q=3, X=B. Each F_q is at most (3-2B)/5 on [0,1]. More precisely their gaps are at least 3/20, 1/10 and 2/15. Thus sum D_s<=h(3-2B)/5=n_2/5<=C.

Now suppose 1<=B<=3/2. Connectedness yields

    C>=h G(B)-6/5,       G(B)=4B/5-3/5.                 (4)

For q=1 retain F_1. On this interval G-F_1>=3/20. The correction subtracted in (2) is x_s+B>=B>=1. Since h>=3,

    h(G-F_1)+(x_s+B) >= 9/20+1 > 6/5.

This absorbs the finite subtraction in (4).

For q=2 the remaining sector has x>=B-1, so X<=1. Since BX-X^2/2 is increasing for X<=1<=B,

    sum f_B(x_s) <= F_2'=3B/5-1/2,
    G-F_2'=B/5-1/10>=1/10.

The correction X+2B is at least 2, again absorbing 6/5.

For q=3 retain F_3. Here

    G-F_3=(2/3)(3/2-B)(B-3/5)>=0.

The correction is X+3B=4B>=4, also sufficient. This proves (3) covers all shortfalls. All scalar inequalities are elementary quadratic bounds; verify_mixed_budget.py independently asks for counterexamples on their full real domains.

## 4. Explicit allocation of transfers

For each sector with no shortfall, scale the capacities by theta=L delta/sum c_i, set b_i=theta c_i and e_i=0. If L=0 or delta=0 set both to zero.

For a sector with shortfall D_s>0, set b_i=c_i and define q_i=L alpha-c_i. The total headroom is L-sum c_i>=D_s. Set

    e_i=D_s q_i/sum_j q_j.

Then sum_i(b_i+e_i)=L delta and b_i+e_i<=L alpha. Crucially, degree-two rows have q_i=0, so **every row with e_i>0 is at a degree-one label**. Further,

    e_i<=q_i=L alpha-(beta-delta)<=delta<beta.

The last inequality uses L<=h-1 in the positive-shortfall branch.

For every donor label d of degree two or three let gamma_d be its budget 1/5 or 6/5. Allocate the row reduction proportionally:

    z_{i,d}=e_i gamma_d/C.

If there is no shortfall use zero reductions. When a shortfall exists, C>0 by Section 3. Each z_{i,d}<=e_i<beta and each donor's aggregate reduction is at most gamma_d. A row needing transfers is a leaf row, so its excluded label is never a donor. No missing-diagonal or forbidden-player exception arises.

## 5. Fractional deletion matching

For i in sector s at label j, use:

1. beta on all diagonal teams except j, subtracting z_{i,d} at each donor label d;
2. alpha on every P-team;
3. mass beta-b_i on the pair of other-sector players at j, and mass b_i/L on each residual-pair column; complete each pair uniformly with the h-1 sector-s players in U other than i;
4. for each donor d and residual-pair column l, mass z_{i,d}/L on the triple with sector-s player d and the two residual players at l.

Terms with L in the denominator are omitted when L=0. Step 4 is omitted when e_i=0. The step-3 masses total beta. Each column's combined extra load is (b_i+e_i)/L<=alpha, and its sum across rows is delta.

The capacity proof from SURPLUS_UPPER.md applies with one additional case: a degree-two donor's sector-s player can itself be unmatched. Such a player previously receives beta from its diagonal and alpha from step 3; subtracting z_{i,d} from its diagonal and adding exactly z_{i,d} in step 4 preserves load one. Used donor players likewise have load beta-z+alpha+z=1. At the other sectors of a donor label, load only decreases. Donors cannot equal the excluded label in a nonzero-transfer row.

All other capacity cases are unchanged: each residual-column player has beta+(b_i+e_i)/L<=1; partners at the excluded label have at most beta plus any P load alpha; all other players have at most their diagonal and P loads. Coefficients are nonnegative and the excluded player is absent.

## 6. Aggregate pair coverage and subsidy consequence

The P contribution is u alpha=3 copies. A degree-three diagonal label starts with u-3 copies of each pair and loses at most 6/5, leaving u-21/5. A degree-two label starts with u-4+alpha and loses at most 1/5, also sufficient.

Leaf labels are never donors. Their initial coverage is u-5+2alpha, with deficit delta. For either pair incident to the unique used player, the opposite unmatched player's deletion row supplies beta-b_i>=delta. The residual pair receives column sum delta. This proves (1), and therefore S_3<=2/5 for the whole original market class through the established reduction.

The original protected-allocation primal LP remains the constructive allocation procedure. Strong duality and this all-size coefficient construction bound its required subsidy by 2T/5. The LP formulation itself is an established ingredient, not a novelty claim.

## 7. Verification and next obstruction

mixed_donor_template.py generates 14 rational certificates. The independent verify_mixed_donor.py checks 127,618 packing entries against every deletion exclusion, player capacity and demanded pair coefficient. Its examples include degree-two-only cycles that need the new transfer, shared pairs, and multiple-junction trees. With --smt, verify_mixed_budget.py returns UNSAT for counterexamples to all six scalar budget estimates. These finite certificates and scalar checks support, but do not replace, the full proof above.

A balanced multiple-junction tree with h=2b+2 has L_s=h/2,N_s=0 in every sector, n_2=0 and n_3=b=h/2-1. Raising t in the same construction would require total extra mass

    D_total=h(9t/2-3)-6

when all three shortfalls are positive. Degree-three donor capacity would be

    (2-t)(h/2-1).

Their difference is h(5t-4)-(4+t), positive for sufficiently large h whenever t>4/5. For h=30,t=5/6 it is exactly 1/6. This is a limitation of the present row-capacity and diagonal-surplus construction, not a lower bound above one-third for the actual subsidy problem.

The next direction must change the coupling of transfers, for example recovering pair coverage from the other two players at a reduced donor label. Simply raising t in this same budget is ruled out by that family. The global gap is now 1/3 to 2/5; the sharp constant, matching extremal family, complete free-original priority audit and specialist review remain open. No paid consultation, purchase or outreach occurred.
