# Improved universal upper bound

**Historical bound:** the newer [mixed donor construction](MIXED_DONOR_UPPER.md) improves the global upper bound to 2/5. The earlier theorem and its certificates below remain valid.

Date: 2026-09-07. **Goal ACTIVE; the sharp constant is not determined.**

The new conventional theorem gives

    1/3 <= S_3 <= (7-4 sqrt(2))/3 = 0.447715250169207...

The earlier universal upper bound was 2/3. The lower bound remains the explicit family proved in SHARP_SUBSIDY.md. Neither equality at the new upper bound nor worldwide novelty is claimed. The proof below is all-size; finite exact certificates corroborate the construction but do not replace this proof.

## 1. Target and reduction

The market has three equally sized sectors, nonnegative pair matrices, strict full-team production, original coalition worths given by integral matching, positive grand worth T, and nonempty original entire core C. H_i=max_{x in C}x_i is frozen before subsidy. The protection floor is H_i/3 and every original coalition inequality is retained.

By the primal-dual formula and the replication, sparsification and component arguments in REDUCTIONS.md, it suffices to prove

    J(M,P)=w(P)+sum_{i in U} H_i/3-T <= a*T                (6)

for an optimal diagonal matching mu and an ordinary partial matching P, where every diagonal label is incident to a player of P and U is its unmatched set. Briefly: an optimal fractional packing has rational coefficients; copies turn it into an integral partial matching without changing normalized ideals or subsidy. Deleting pair entries outside the two matchings preserves T and enlarges the original core, increasing the relevant claims. Restriction to connected label components only enlarges their local ideals and splits T. These comparisons are between original markets, not changes to the ideals of a subsidized market.

Put h=m-|P|, u=|U|=3h. If P is empty, diagonal bounds give J<=0. If h=0 then J=w(P)-T<=0. If h=1, nonnegativity and P's disjoint team inequalities give H_i<=T-w(P) for its three unmatched players, again giving J<=0. Isolated one-label components and zero-worth components therefore cause no exception. Below h>=2 and every label has used degree d_j in {1,2,3}.

We will explicitly construct a fractional matching lambda^(i) without each i in U such that their aggregate pair incidence dominates

    (u-5+t)*a_mu(e)+3*a_P(e) for every pair e,             (7)

where 0<=t<=t_*:=4 sqrt(2)-5. Here a_mu and a_P count appearances of a pair in their respective matchings; overlaps are counted additively.

For any original core point attaining H_i, coverage and nonnegativity imply

    value(lambda^(i)) <= T-H_i.

Multiplying (7) by the nonnegative pair coefficients and summing gives

    sum_i value(lambda^(i)) >= (u-5+t)T+3w(P),
    sum_U H_i <= (5-t)T-3w(P),
    J(M,P) <= (2-t)T/3.                                  (8)

Taking t=t_* yields the asserted universal upper bound. Thus the substantive proof task is the uniform construction of (7), given next.

## 2. Counting identity

For sector s, let L_s count labels of degree one whose unique used player lies in sector s. The two unmatched players at such a label form a residual diagonal pair. Let N_s count unmatched sector-s players at labels of degree two. Its other h-N_s unmatched players are at degree-one labels.

If ell is the total number of degree-one labels and N_total the number of degree-two labels, then

    ell=h-N_s+L_s,          3h=2ell+N_total.

Since N_total>=N_s, these identities imply

    0<=L_s<=h,  0<=N_s<=h,  2L_s<=h+N_s.                 (9)

No acyclicity assumption is used. In particular this holds for multiple junctions, cycles, and shared pairs of the two reference matchings.

## 3. Scalar inequality

For 0<=x,n<=1, n>=2x-1, and 0<=t<=t_*,

    t*x <= n*x+(1-n)(1-t).                               (10)

To prove this, subtract the left side. The resulting expression is affine in n, with coefficient x-1+t.

If x<=1-t, its minimum over n<=1 is (1-t)x>=0. Otherwise the coefficient is positive. For x<=1/2, its minimum over n>=0 is 1-t-tx>=1-3t/2>=0, since t_*<2/3. For x>=1/2, use n>=2x-1. The resulting lower bound is

    2x^2+(t-3)x+2-2t
      = 2[x-(3-t)/4]^2 + (7-10t-t^2)/8 >= 0.

The last inequality holds because t^2+10t-7<=0 exactly on the relevant parameter interval. At t=t_*, the remainder is zero and the square is 2[x-(2-sqrt(2))]^2. This proves (10).

## 4. Uniform transfer amounts

Set alpha=1/h, beta=1-alpha and delta=max(0,t-2alpha). For a fixed sector, abbreviate L=L_s and N=N_s. Construct nonnegative amounts x_{i,l}, with rows indexed by its unmatched players and columns by its residual-pair labels, satisfying

    sum_i x_{i,l}=delta,
    x_{i,l}<=alpha,
    b_i:=sum_l x_{i,l}<=beta-delta for degree-one rows,
    b_i<=beta for degree-two rows.                       (11)

When L=0 or delta=0, set every amount to zero. Otherwise define

    c_strong=min(alpha,beta/L),
    c_weak=min(alpha,(beta-delta)/L),
    F=N*c_strong+(h-N)*c_weak.

We first prove F>=delta. If L=h, (9) forces N=h, so F=beta>=delta. Suppose L<=h-1. Then c_strong=alpha. If c_weak=alpha, F=1>=delta. In the remaining case,

    L*F=N*L/h+(h-N)(beta-delta).

For positive delta, beta-delta=1-t+alpha>=1-t. Apply (10) with x=L/h and n=N/h, which satisfy its hypotheses by (9). It gives

    t*L <= N*L/h+(h-N)(1-t) <= L*F.

Since delta<=t, F>=delta as required. Also F>0 in this branch.

Now put theta=delta/F and set x_{i,l}=theta*c_strong for degree-two rows, and theta*c_weak for degree-one rows. The column sum equals delta and 0<=theta<=1. The entry and row bounds in (11) follow immediately. This is an explicit formula; no unproved transportation or matching-existence claim is being used.

## 5. Construct and check the deletion matchings

Fix an unmatched i in sector s at label j. Define lambda^(i) by adding these team coefficients:

1. beta on every diagonal team except j;
2. alpha on every team of P;
3. mass beta-b_i on the pair formed by the other two players at j, and mass x_{i,l} on each residual pair in sector-s column l. Complete each pair with every player in U_s other than i, distributing its mass equally over those h-1 players.

The masses in step 3 sum to beta. Each unmatched sector-s player other than i therefore receives additional load beta/(h-1)=alpha. No column label equals j, since its sector-s player is used whereas i is unmatched.

Player i is excluded. In its sector, every other unmatched player has load beta+alpha=1, and every used player has the same load from steps 1 and 2. In either other sector, a player at label j has no diagonal load; its total is at most alpha+beta=1 if used, and at most beta if unmatched. A residual-pair player at a column label is unmatched and outside j, giving load beta+x_{i,l}<=1. Other used players have load beta+alpha=1, and other unmatched players have load beta. Distinct column labels give disjoint residual pairs. These cases exhaust all players, so every lambda^(i) is a feasible fractional matching without i.

## 6. Check aggregate pair domination

Step 2 contributes u*alpha=3 copies of every P pair. Count that contribution separately even if the pair also lies in mu.

At a diagonal label with k_j=3-d_j unmatched players, step 1 contributes (u-k_j)beta copies of each diagonal pair. If d_j=3 this is u-3; if d_j=2 it is u-4+alpha. Both are at least u-5+t because t<1.

If d_j=1, the contribution is u-5+2alpha. If t<=2alpha it is already sufficient. Otherwise its deficit is delta. For either pair incident to the unique used player, its opposite unmatched player i supplies at least beta-b_i>=delta in step 3, by the degree-one row bound in (11). For the residual pair between the two unmatched players, the column sum in (11) supplies exactly delta. Every diagonal pair therefore receives at least u-5+t copies. Other pair incidences are nonnegative. This proves (7), and hence the global bound through (8).

## 7. Reproducible exact certificates and allocation implications

universal_template.py implements this formula without an optimizer. Its default rational parameter is t=13137/20000, which satisfies t^2+10t-7<0 and yields the rational universal bound

    S_3 <= 26863/60000 = 0.4477166666... .

verify_universal.py independently reconstructs pair demands and every player capacity from the retained certificates. It does not use the transfer formula or trust its metadata. Ten checks include chains, one through four junctions, a cyclic multiple-junction component, shared pairs, and counts L/h=7/12, N/h=1/6 close to the scalar inequality's worst ratio. It checks 13,590 rational entries and rejects both an empty certificate and an out-of-range parameter. The earlier one-third certificates remain valid for their specified classes.

With --smt, verify_upper_lemma.py also asks Z3 for a real counterexample to (10) over its full polynomial domain. The result is UNSAT. Removing the parameter restriction and fixing t=3/4 produces a SAT negative control. This independently checks the scalar lemma, not the whole market theorem or its novelty.

The exact irrational bound is supplied by the all-parameter proof, not inferred from those finite checks. Equivalently, apply the proved rational construction for parameters tending upward to t_* and take the infimum of the resulting upper bounds on s_3(M)/T. No limiting payoff argument or change to the frozen ideals is needed.

For a given rational market, original ideals and the protected allocation can be computed by the finite LPs already recorded in SHARP_SUBSIDY.md; their rational primal-dual outputs can be checked directly. This theorem supplies a new universal cost bound for that established allocation procedure. It does not assert a new LP formulation or that this algorithm alone settles the sharp-constant objective.

## 8. Remaining gap and evidence level

The lower construction still approaches 1/3, while the new bound is about 0.447715. No matching family for the new upper bound is known, and the one-third universal inequality remains unproved. The new construction relaxes its diagonal-pair target; pushing its parameter beyond t_* invalidates the scalar estimate used here. That failure would be a limitation of this estimate, not a counterexample to the original one-third conjecture.

The next task is to improve the use of pair coverage or find a stronger lower construction. The most informative count profiles for auditing this method have L/h near 2-sqrt(2), N/h near 3-2sqrt(2), which are approximated by the grafted-junction certificate. Any claim of the primary goal's completion still requires matching bounds, a complete source audit, and the requested constructive and verification deliverables. Novelty and external review remain unconfirmed; no paid consultation or outreach accompanied this work.
