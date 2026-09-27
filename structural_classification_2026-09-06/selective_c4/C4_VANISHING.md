# Selective diagonal subdivision gives vanishing protection on C4

Conventional proof reviewed by Claude with no correctness defects; exact C4 certificates and raw-core checks pass. Entire strict core; no productive partial-sector coalitions. No priority claim.

## Definitions and theorem

Every sector has the same finite size m. Only full four-sector teams produce output, with value the sum of the four specified nonnegative edge matrices on ab,bc,cd,ad. Any coalition's worth is its maximum weight integral matching of contained full teams. The entire core is equivalently the set of individually nonnegative full-team covers with sum equal to grand worth T. The equivalence follows by summing team covers over coalition matchings and using nonnegativity for unmatched players. Full leximin maximizes the ascending sorted vector over this entire core, retaining every labeled coordinate. H_i is the maximum of the same coordinate over that entire core.

For every integer q>=1 there is such a C4 market with m=3q+1, all pair entries in {0,1,2}, T=10q+1, and a strictly positive core point, for which
    x_(c,L0)=1/[4(q+1)],  H_(c,L0)=1.
Thus c(C4)=0. This settles the remaining four-sector graph type at the conventional-proof and exact-certificate evidence tier. It does not claim novelty or field-level significance.

## A selective subdivision lemma

Start with a strict three-sector market with team value A(a,b)+C(b,c)+B(a,c), nonnegative matrices, nonempty core, and an optimal perfect diagonal matching of value T0. Let D_j>=max_a B(a,j). Add sector d of the same size and use
    w'(a,b,c,d)=A(a,b)+C(b,c)+B(a,d)+D_c*1_(c=d).
The last term equals D_d*1_(c=d). For every old core point z, the point (z_a,z_b,z_c,D_d) is a new full-team cover. Indeed:
* c=d: its sum is at least A+C+B(a,c)+D_c, exactly the required expression.
* c!=d: its sum is at least A+C+B(a,c)+D_d >= A+C+B(a,d), since B(a,c)>=0 and D_d>=B(a,d).
Its total is T0+sum_j D_j, attained by the diagonal full matching. Therefore this is the exact integral worth and the displayed cover is an entire-core point.

More generally, from any old core point z and any t>=0 such that z_i>=t/3 for every old player, form
    p_a=z_a-t/3, p_b=z_b-t/3, p_c=z_c-t/3,
    p_d=D_d+t.
This is nonnegative, has the same total, and each full team's sum is unchanged from the previous lift. Hence it is in the new entire core. If z_i>=tau throughout, choosing t=3tau/4 gives every coordinate of p at least t.

This lemma permits D_j=0 at zero B-columns. It is different from the retired uniform-positive-bonus construction: no uniform positive new-payoff floor is forced by D at those labels.

## Apply to the proved three-sector family

Use labels L_0 and O_s,L_s,R_s for 1<=s<=q, with indices L_0=0,O_s=3s-2,L_s=3s-1,R_s=3s. The nonzero matrices are
    A(O_s,O_s)=A(O_s,R_s)=2;
    B(O_s,O_s)=B(O_s,L_s)=2;
    C(L_s,L_s)=1, 0<=s<=q;
    C(R_s,R_s)=C(R_s,L_s)=C(L_(s-1),O_s)=1, 1<=s<=q.
All other entries are zero. The existing [symbolic source proof](SOURCE_FAMILY_PROOF.md) establishes diagonal worth T0=6q+1, a core point z with floor tau=1/[3(q+1)], and an ideal witness y giving c_L0 payoff1.

For completeness, z has the following (a,b,c) entries:
    L_s: (tau,1-(3s+2)tau,(3s+1)tau);
    R_s: (tau,1-2tau,tau);
    O_s: (4-(3s-1)tau,tau,(3s-2)tau).
The ideal witness has entries L_s:(0,0,1), R_s:(0,1,0), O_s:(3,0,1). The source proof checks every mixed triple symbolically; finite evaluations are not substituted for that proof.

Set D_j=2 for j in {O_s,L_s:1<=s<=q}, and D_j=0 at L_0 and every R_s. These are exactly B's column maxima. Thus sum D=4q, and the selective lemma gives exact worth T=10q+1 and the strictly positive floor witness p with t=3tau/4=1/[4(q+1)].

## A constant-shortfall partial matching pins the whole first face

Take the following 2q full four-sector teams:
    N_s=(O_s,R_s,L_s,L_s),
    E_s=(L_(s-1),L_(s-1),O_s,O_s), 1<=s<=q.
They are player-disjoint, since the old a,b,c labels are the disjoint source partial matching and the new d labels are precisely the distinct O_s,L_s labels. Each N_s has value 2+1+2+2=7; each E_s has value 0+1+0+2=3. Total value is 10q=T-1.

The unmatched set is
    U={a_Lq,b_Lq,c_L0,d_L0}
      union {a_Rs,b_Os,c_Rs,d_Rs:1<=s<=q},
with exactly 4(q+1) players, including the target c_L0. For every core point v, summing the matched cover inequalities and using efficiency gives
    sum_(i in U) v_i <= 1.
Thus the maximum common floor is at most 1/|U|=t. The positive cover p attains t. On the ENTIRE first optimal face, all payoffs are at least t, so the budget forces every U-coordinate to equal t. In particular the full leximin target is t through all later refinements. This conclusion does not identify an arbitrary floor witness with the full selector.

## Exact ideal

The diagonal team at label L_0 has value1: C(L_0,L_0)=1 and D_L0=0. It is tight in every core point because the diagonal matching is optimal. Nonnegativity gives H_(c,L0)<=1. Applying the unshifted selective lift to the source ideal witness y gives a new core point (y,D) with target1. Hence H_(c,L0)=1, and the ratio t tends to zero as q grows.

## Verification and scope

The proof is all-q and uses exact entire-core covers, an integral perfect matching, an integral partial matching with shortfall1, and ideal attainment. No fractional matching value, productive pair coalition, restricted face ideal, deleted coordinate, or numerical extrapolation is used. The bonus is selective and may be zero at some labels, as permitted by the objective. Every allowed C4 edge has some nonzero entries, and all pair entries remain in {0,1,2}.

This family supersedes the finite5/44 upper bound by proving zero, after review and exact verification. It does not invalidate the earlier uniform-bonus no-go theorem, whose hypothesis assigns a positive bonus to EVERY label. Novelty must be assessed separately against original sources and the existing source-family priority audit; the three paid originals remain skipped at the user's request.

Strict means full-team productivity here, not strictly positive edge entries. The actual construction additionally has a nonzero matrix on every cycle edge. The diagonal matching attains every edge's sum of row maxima, so pairwise matching incompatibility is NOT needed for vanishing.
