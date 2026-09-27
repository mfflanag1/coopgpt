# A uniform bound for the diagonal-bonus subdivision route

Historical checkpoint: the [successor proof](../subdivision_uniform_bound/UNIFORM_BOUND.md) now excludes the entire family with a uniform1/676 bound. Remaining-regime statements below describe the frontier at this earlier checkpoint.

Conventional no-go lemma, reviewed by Claude with no correctness defect, for a specific C4 construction. It is not a bound on all C4 markets.

## Construction and hypotheses

Let a strict three-sector source market of equal size m have pair matrices A(a,b), B(a,c), C(b,c), all nonnegative, positive grand worth T computed by integral matching, and nonempty entire core. Only full teams produce value; arbitrary coalition worth is the maximum weight of a matching of full teams contained in it. In particular pairs have zero worth, while larger coalitions can have positive worth. Nonnegative values and equal sizes allow completion of an optimal matching without loss; relabel an optimal perfect full-team matching to the diagonal. Let

    D=max_j [A(j,j)+B(j,j)+C(j,j)].

Choose M>0 such that B(a,d)-B(a,c)<=M for every a,c,d. Form a strict four-sector C4 market on edges ab,bc,cd,ad with matrices A,C,M*identity,B respectively. Thus

    w'(a,b,c,d)=A(a,b)+C(b,c)+B(a,d)+M*1_{c=d}.

This is the usual attempt to replace the old ac edge by a path through a duplicate-index sector d. The hypothesis on M is sufficient for the following bound; no assertion is made when it is dropped.

## Exact worth and a uniform floor

For any source-core payoff z=(z_a,z_b,z_c), define extended payoffs

    p_a=z_a+M/4, p_b=z_b+M/4, p_c=z_c+M/4,
    p_d=M/4 for every new player.

Their total is T+mM. For any full four-team, the source core inequality gives

    p_a+p_b+p_c+p_d
      >= A(a,b)+C(b,c)+B(a,c)+M
      >= A(a,b)+C(b,c)+B(a,d)+M*1_{c=d}.

When c=d the last comparison is equality. When c!=d it follows from the defining bound on M. Thus p is a nonnegative full-team cover. The diagonal integral matching has worth T+mM, so weak duality proves the exact grand worth is T+mM and p is an entire-core point.

In particular the extended first optimal floor is at least M/4, and every coordinate of full leximin x' is at least M/4, including all later stages. No identification of p with full leximin is needed.

Every core point makes each team of the diagonal optimal matching tight. Individual nonnegativity therefore bounds every whole-core ideal by D+M. Hence every player with positive ideal satisfies

    x'_i/H'_i >= M/[4(D+M)].

Across a family, this is a positive uniform bound whenever D/M is bounded above. An upper bound on M is not necessary. In fact every ideal here is positive because it is at least M/4.

## Application to the existing vanishing family

The source family has pair entries {0,1,2}, diagonal team values1 or4, and nonempty positive core. Thus B has row range at most2 and D=4. Taking M=2 gives

    x'_i/H'_i >= 1/12

for every player and every family depth q, although the source target ratio tends to zero. Taking any M>=2 only increases this lower bound. Uniform rescaling of the entire construction leaves the ratio bound unchanged.

Therefore this diagonal-bonus subdivision of the existing family cannot establish c(C4)=0. This does not rule out smaller bonuses, anisotropic reweighting with a new proof, a different subdivision gadget, or a new C4 family. In particular it does not contradict the known C4 example at5/44>1/12 and is not a universal1/12 theorem for C4.

## Consequence for the campaign

Retire this specific transfer route. An amplification proof must change the mechanism rather than assume that a large diagonal consistency bonus preserves source fairness ratios. The first-face mapping proved for zero-valued added sectors does not apply here: these new sectors carry a nonzero diagonal interaction, which supplies a new payoff floor.

## Family-specific refinement: every fixed positive bonus

For the particular source family, the diagonal matching attains the row-maximum bound on every edge separately: A and B each contribute2q, C contributes2q+1, and M*identity contributes mM. Hence T(M)=6q+1+mM for every M>=0, not merely M>=2.

At M=0, use the row-price core point p^0 assigning max_b A(a,b)+max_d B(a,d) to each a-player, max_c C(b,c) to each b-player, and zero to every c- and d-player. It covers every team, and its total is6q+1. At M=2, the preceding construction gives p^2>=1/2 in every coordinate, total6q+1+2m.

For 0<M<2, the point p^M=(1-M/2)p^0+(M/2)p^2 covers every M-market team by taking the same convex combination of the two valid endpoint cover inequalities. Its total equals T(M) because T(M) is affine, so it is efficient and nonnegative, and each coordinate is at least M/4. The preceding proof already gives that floor for M>=2. Therefore, for this diagonal subdivision of the specified family, at every q and every M>0,

    x_i(M)/H_i(M) >= M/[4(4+M)].

In particular no fixed M>0, or sequence bounded away from zero, yields vanishing protection as q increases. This argument does not settle positive sequences M(q)->0; its lower bound then tends to zero. At M=0 exactly, the cd edge vanishes and the remaining allowed support is the path c-b-a-d; the already proved all-tree theorem gives1/4 protection for positive-ideal players. This is a path argument, not the zero-valued-added-sector transfer, since d still interacts with a. The bound does not apply to arbitrary C4 markets. The only live parameter regime within this exact family that could still produce vanishing is a positive bonus tending to zero, with a separate analysis of full leximin and ideals.

## The original target is protected even when the bonus shrinks

Use the source labels L_0, O_s,L_s,R_s for1<=s<=q. The source target is the c-player L_0. In the four-sector subdivision construct these disjoint full teams:

    (O_s,R_s,L_s,L_s)                1<=s<q;
    (O_q,R_q,R_q,L_q);
    (L_(s-1),L_(s-1),O_s,O_s)      1<=s<=q;
    (L_q,L_q,L_q,R_q);
    (R_s,O_s,R_s,R_s)              1<=s<q.

They form a partial matching of3q=m-1 teams. The unmatched players are exactly a_Rq, b_Oq, c_L0 and d_L0. Their respective team-value groups are (q-1) copies of5+M, one5, q copies of1+M, one1, and (q-1) copies ofM. Thus its total worth is

    6q+1+(3q-2)M = T(M)-3M.

Summing its core inequalities and using efficiency and individual nonnegativity gives H_(c,L0)<=3M. The earlier floor construction gives x_(c,L0)>=M/4. Therefore

    x_(c,L0)/H_(c,L0) >= 1/12

for every q>=1 and EVERY M>0, even for M=M(q) tending to zero. Its own diagonal team also gives H_(c,L0)<=1+M, but exact ideal attainment is unnecessary for the bound. This prevents the original target from transferring vanishing through this gadget at any positive bonus. A different target with M(q)->0 is not excluded by this last argument; the no-go scope must not be widened beyond what is proved.
