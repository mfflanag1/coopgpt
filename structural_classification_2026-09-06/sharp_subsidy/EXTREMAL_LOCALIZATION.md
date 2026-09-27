# Necessary structure for approaching the current two-fifths ceiling

2026-09-07. This is a localization lemma within the three-sector sharp-constant problem, not a claim of a sharp graph-dependent curve. Global bounds remain 1/3 <= S_3 <= 2/5. External review and novelty are unconfirmed.

## Main consequence

Consider any sequence of connected diagonal/P reductions with J/T tending to 2/5. Let h=m-|P|, ell be the number of degree-one labels, n2,n3 the degree-two/three counts, c the incidence multigraph cycle rank, and L_s the number of leaf labels whose used player is in sector s. Then necessarily

    h -> infinity,
    ell/h -> 3/2,
    n2/h -> 0,
    c/h -> 0,
    n3/h -> 1/2,
    L_s/h -> 1/2 for each sector s.

The unmatched degree-two counts N_s/h also tend to zero. Thus a potential sequence reaching the present ceiling must have asymptotically balanced leaf sectors and almost entirely degree-one/degree-three labels, with cycle rank negligible relative to h. This is a necessary condition, not existence of such a sequence. It does not prove that replacing those cycles by trees preserves subsidy.

If any original market sequence approaches 2/5, replication, sparsification and component selection from REDUCTIONS.md produce a sequence of reductions to which this statement applies. It is not a classification of every obstruction on the original unreplicated markets.

## Proof estimate

Put B=ell/h, x_s=L_s/h, g=c/h. Incidence counting, including parallel incidences, gives

    n2/h=3-2B, n3/h=B-1-1/h+g,
    sum_s x_s=B, 0<=B<=3/2,
    x_s>=B-1 when B>=1.

For 1<=B<=3/2 define

    A(B)=(2/3)(3/2-B)(B-3/5),
    V=sum_s (x_s-B/3)^2, eta=A(B)+V+g.

Use the same deletion construction as MIXED_DONOR_UPPER.md with t=4/5+d, where

    d=1/100                  if B<=1,
    d=min(1,eta)/100         if B>=1.

Either choice is valid at B=1; no continuity claim is needed. Donor budgets are 1-t and 2-t. We show they cover the shortfalls. This internal estimate implies J/T<=2/5-d/3 and is used only to derive the necessary asymptotic conditions.

For positive-shortfall sectors, h>=3 and

    D_s=h[x_s(B-x_s)-B/5]-(x_s+B)+d h B.

The formula applies to sectors active at the new t; no assumption about activity at t=4/5 is made. The no-shortfall branches and all capacity arguments are unchanged. In particular t<=81/100<1 and all donor masses remain nonnegative. When h=2, delta=max(0,t-2/h)=0.

If B<=1, ignore degree-three donors. The old quadratic budget gap is at least h/10 for each possible number q of active sectors. The increased t costs at most d h[3+(q-2)B]<=4dh. The remaining gap is positive.

If B>=1, the exact total donor budget at t=4/5 is hG(B)-6/5+(6/5)c, where G(B)=4B/5-3/5. Increasing t consumes h d[2+(q-1)B-1/h+g] in the combined budget-demand comparison. For q=1 and q=2, respectively, the old inequalities and d<=1/100 give lower gaps

    (13/100)h-1/5+(119/100)h g >0,
    (13/200)h+4/5+(119/100)h g >0.

For q=3, the quadratic concavity gap is retained exactly rather than discarded:

    G(B)-sum_s[x_s(B-x_s)-B/5] = A(B)+V.

Thus budget minus demand is at least

    h[A(B)+V+(6/5)g-d(5+g)]+4B-6/5.

Write z=A(B)+V>=0. The bracket is nonnegative because

    min(1,z+g)(5+g)/100 <= z+(6/5)g.

For z+g<=1 use 5+g<=6. For z+g>=1 use 1<=z+g to bound (5+g)/100 by z/20+3g/50. Both are at most the right side. The remaining finite correction is positive. This covers all branches and establishes feasible deletion packings. Their aggregate pair domination gives the stated internal obstruction estimate, retaining each original coordinate-attaining core witness.

## Deduction and quantitative check

Let e=2/5-J/T. If e<1/300, the B<=1 branch is excluded. Then min(1,eta)<=300e<1, hence eta<=300e. Since A(B)>=(4/15)(3/2-B),

    c/h <=300e,
    3/2-B <=1125e,
    |x_s-B/3| <=sqrt(300e).

The finite correction from FINITE_UPPER_CORRECTION.md gives h>=1/(60e). Letting e tend to zero proves all stated limits, using N_s/h=1-B+x_s and the exact incidence identities. These constants are deliberately conservative; optimizing them is not a research goal.

## Verification and implication for the next proof

`verify_extremal_localization.py --smt` checks eight scalar implications over their full real domains. The coefficient construction is the original mixed-donor construction with the displayed parameter; the same capacity and pair-coverage proof applies. The auxiliary parameter is calculated exactly using rational arithmetic in localization_parameter.py. `localization_certificates.py --generate` reconstructs fourteen sample certificates; its independent checker recomputes the parameter from incidence counts and verifies 127,618 rational packing entries. An empty-certificate negative control is rejected.

This lemma narrows attempts to improve the global upper bound: persistent cycle density, degree-two density or sector leaf imbalance cannot produce the current ceiling. The remaining difficult region is balanced branching structure with vanishing cycle density. A size-uniform improvement there would need an additional argument controlling actual original ideals. Neither count localization nor the finite-size correction provides that argument, and neither settles the one-third conjecture.
