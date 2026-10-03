# Candidate universal aggregation of residual propagation and P-team differences

3 October 2026. Independent bounded algebraic investigation. **Candidate proof pending the parent's independent native/Fable audit and audit of the fractional replication reduction.** No optimizer, new numerical support cases, or held-out files were used. This note does not make a literature-novelty claim or mark the original research goal complete.

## Statement

There are three sectors of equal size m, nonnegative pair matrices, and only full triples produce their pair-sum worth. Let the original grand worth be T>0 and the original entire core be nonempty. Fix an optimal perfect matching and simultaneously label its teams diagonally. Write d_j for diagonal team j's worth, so sum_j d_j=T. Let P be any actual player-disjoint partial matching, r=|P|, k=m-r, W=w(P), and U its unmatched players. Each sector has exactly k players in U.

For player i=(s,j), let u_i be the sum of the two diagonal pair entries incident to i. Let H_i be its maximum payoff over the entire original core. For k>=1, the proposed conclusion is

    w(P) + (1/3) sum_{i in U} H_i - T
       <= [2(k-1)/(3(2k-1))] T.                         (A)

For k=0 the left side is W-T<=0. The statement permits repeated diagonal labels within a P-team and pairs shared between P and the diagonal matching. It requires **no sparse-support, connectedness, tree, or cycle hypothesis**.

More generally, (A) holds with H replaced by any vector h satisfying just the following three families:

1. h_i<=d_j for every player i=(s,j).
2. For every P-team e with sector labels (j_A,j_B,j_C), and every ordered permutation (s,t,u) of the three sectors,

       h_(u,j_u) - h_(u,j_t) >= w_e - d_(j_t) - u_(s,j_s).       (PD)

3. For every unmatched i,

       k h_i <= T-W + (k-1)u_i.                                 (RP)

The algebra below does not need h>=x, completion or range rows separately, or nonnegativity of h; all are present in the frozen relaxation nonetheless. For actual ideals, all three displayed families are proved below from original-core properties. Thus the frozen RP-relaxation sufficiency conjecture follows if the algebra is confirmed.

## Original-core derivations, including all quantifiers

Every core vector x is nonnegative, covers every full team, and has total T. Its diagonal covers sum to T, so each diagonal cover is tight:

    x_(A,j)+x_(B,j)+x_(C,j)=d_j.                         (1)

Hence x_i<=d_j. The core is a nonempty closed subset of the nonnegative simplex of total T, so each H_i exists and is attained. In particular H_i<=d_j.

For any sector s and labels a,b, complete the diagonal opposite pair at a by the sector-s player at b. The opposite pair has value d_a-u_(s,a); the team's other pair values are nonnegative. Its original core cover therefore gives

    x_(s,b)+d_a-x_(s,a) >= d_a-u_(s,a),
    x_(s,a)-x_(s,b) <= u_(s,a).                         (2)

This argument remains valid when a=b, and does not treat a pair by itself as a productive coalition. The opposite pair is used only as a nonnegative lower bound on a full team's worth.

Now fix a P-team e and an ordered permutation (s,t,u). Its cover and the tight diagonal at label j_t give

    x_(s,j_s)+x_(t,j_t)+x_(u,j_u) >= w_e,
    x_(s,j_t)+x_(t,j_t)+x_(u,j_t) = d_(j_t).

Subtract and then use (2) with sector s and labels j_s,j_t:

    x_(u,j_u)-x_(u,j_t)
       >= w_e-d_(j_t)+x_(s,j_t)-x_(s,j_s)
       >= w_e-d_(j_t)-u_(s,j_s).                       (3)

This is a pointwise inequality throughout the original core. Choose a core vector attaining H_(u,j_t). Its other coordinate x_(u,j_u) is at most H_(u,j_u), giving (PD) for the true ideals. The two ideals are not assumed to be simultaneously attained. If j_u=j_t the same argument gives the corresponding zero-left-side row, which is still valid. All six ordered sector permutations are counted even if some label positions coincide.

For (RP), fix unmatched i=(s,a) and an original core point attaining H_i. Equation (2) gives x_(s,b)>=H_i-u_i for each of the k-1 other unmatched players in sector s. Include x_i=H_i, sum these k inequalities, and use nonnegativity for unmatched players in the other two sectors:

    x(U) >= k H_i-(k-1)u_i.

The disjoint P-team covers imply x(players used by P)>=W. Since the full payoff is T,

    x(U)<=T-W.

Combining proves (RP). Each i uses its own attaining core point, which is legitimate because the final scalar row only involves H_i, fixed pair weights, and fixed P.

## Notation for the aggregation

Let V(P) be the set of players used by P. Set

    S = sum_{i in U} h_i,
    B = sum_{i in U} u_i,
    D_U = sum_{i in U} d_label(i),
    D_P = sum_{i in V(P)} d_label(i),
    U_P = sum_{i in V(P)} u_i,
    H_P = sum_{i in V(P)} h_i,
    A = 3W+S.

Every diagonal pair contributes to two incident budgets, and each diagonal value is repeated for its three players. Therefore

    U_P+B=2T,        D_P+D_U=3T.                       (4)

For each label j, let n_j be the number of its three players used by P. Player-disjointness gives n_j in {0,1,2,3}. Define

    h_total(j) = sum_s h_(s,j),
    delta_i = d_label(i)-h_i >=0,
    Delta_P(j) = sum_{i used by P at j} delta_i,
    Delta_U(j) = sum_{i unmatched at j} delta_i.

In particular Delta_U(j)=0 when n_j=3, and Delta_P(j)=0 when n_j=0.

## Sum all six P-team-induced inequalities

Rearrange (PD) as

    w_e <= d_(j_t)+u_(s,j_s)+h_(u,j_u)-h_(u,j_t).

Sum over all six ordered permutations of sectors and all teams e in P. Each P-player contributes twice to the diagonal term, twice to the incident-budget term, and twice to the positive h term. For its occurrence as the sector-t player, the two negative h terms are the other two sector coordinates at that same label. Thus its total h contribution is

    2h_i - [h_total(label(i))-h_i]
       = 3h_i-h_total(label(i)).

This counting is by actual player occurrences. It remains valid for repeated labels inside a P-team: the same label total is then counted repeatedly, exactly n_j times over P. Consequently,

    6W <= 2D_P+2U_P+3H_P-sum_j n_j h_total(j).          (5)

Adding 2S and substituting (4) and h_i=d_label(i)-delta_i yields the exact right-side expression

    6W+2S <= 10T-2B
       + sum_j [(n_j-2)Delta_U(j)-(3-n_j)Delta_P(j)].   (6)

For clarity, the added term at a label is:

| n_j | Added term |
| ---: | --- |
| 0 | -2 Delta_U(j) |
| 1 | -Delta_U(j)-2 Delta_P(j) |
| 2 | -Delta_P(j) |
| 3 | 0, because Delta_U(j)=0 |

Every term is nonpositive. Hence the P-induced rows and diagonal caps alone give

    A=3W+S <= 5T-B.                                   (7)

This is the missing complementary estimate: it gets stronger when incident diagonal budget is concentrated on unmatched players. In contrast, summed RP gets weaker with that same concentration.

## Sum RP and cancel the troublesome mass

There are 3k unmatched players. Sum (RP):

    k S <= 3k(T-W)+(k-1)B,
    k A <= 3kT+(k-1)B.                                (8)

Multiply (7) by k-1, which is nonnegative for k>=1, and add (8):

    (k-1)A + kA
      <= 5(k-1)T-(k-1)B + 3kT+(k-1)B,
    (2k-1)A <= (8k-5)T.                               (9)

The B terms cancel exactly. Equivalently,

    3W+S <= [4-1/(2k-1)]T,
    W+S/3-T <= [2(k-1)/(3(2k-1))]T,

which is (A). No restriction on whether B is above or below T is needed.

For k=1, (8) alone gives A<=3T and J<=0, agreeing with the formula. For k=0, U is empty and P is perfect; any original core cover gives W<=T and J<=0. If P is empty, the independent diagonal caps also give the stronger elementary statement S<=3T and J<=0. The main derivation does not divide by W, R=T-W, B, any individual weight, or any deficit; zero values cause no problem.

## Exact nonnegative-slack identity

This identity is useful for an independent coefficient audit. Define the aggregate nonnegative PD slack

    L = sum_{e in P} sum_{(s,t,u)}
          [d_(j_t)+u_(s,j_s)+h_(u,j_u)-h_(u,j_t)-w_e],

the cap-deficit contribution

    E = sum_j [(3-n_j)Delta_P(j)+(2-n_j)Delta_U(j)],

and the aggregate RP slack

    M = sum_{i in U} [T-W+(k-1)u_i-kh_i].

E is nonnegative by the four-row table above, including the n_j=3 empty unmatched sum. The counting identity gives

    L+E = 2(5T-B-A),
    M = 3kT+(k-1)B-kA.

Thus, for k>=1,

    (8k-5)T-(2k-1)A = M + [(k-1)/2](L+E) >=0.         (10)

This displays the precise combination of the frozen relaxation's rows and diagonal caps. It does not introduce an extra compatibility assumption or rely on a fixed-support numerical dual.

## Concentration interpretation and scope of the genuine core witness

Partition diagonal pair mass into Q_0,Q_1,Q_2 according to whether zero, one, or two endpoints are in U. Then

    T=Q_0+Q_1+Q_2,
    B=Q_1+2Q_2=T+Q_2-Q_0.

The concern about residual leaf pairs versus used internal pairs is exactly the sign of Q_2-Q_0. Equation (7) is

    A <= 4T+Q_0-Q_2,

whereas (8) is

    A <= 3T+[(k-1)/k](T+Q_2-Q_0).

The opposing coefficients are what cancel; neither concentration regime remains uncontrolled. This explains why attempting to bound B by T in isolation was unnecessary.

For an abstract h satisfying the frozen rows, the retained actual core vector x is not needed again in the aggregation. For true ideals, nonempty original core, its pointwise comparisons, and separate attainment justify the rows. RP-feasible h remains distinct from an ideal vector; the conclusion bounds its relaxed objective without asserting attainability.

## Sharpness consistency check using the already retained chain family

SHARP_SUBSIDY.md gives an all-q chain family, q>=1, with m=2q+1, r=q, k=q+1, all diagonal pair entries one, each P-team worth five, and all original ideals three. Its established quantities are

    T=3(2k-1), W=5(k-1), R=k+2,
    S=9k, B=6k, u_i=2, h_i=d_label(i)=3.

Every PD row has right-side difference w_e-d_b-u_i=5-3-2=0 and all h differences are zero. Every cap deficit is zero. Every unmatched RP row has equality 3k=(k+2)+2(k-1). Therefore L=E=M=0 and (9) is attained:

    J/T = 2(k-1)/(3(2k-1)).

This is a consistency check against the already retained all-size construction, not a new finite support search. At k=1 the zero bound is attained by the elementary zero-obstruction calibrations. A complete global claim still requires independent review of this proof and the already established lifting from arbitrary fractional obstructions to all-size integral P; the parent is handling that separate obligation.

## Provenance and limits

The local range/P-induced inequalities and RP were established ingredients in IDEAL_DIFFERENCE_LIMITS.md and RESIDUAL_PROPAGATION.md. The proposed substantive implication is their all-size aggregate cancellation (7)-(10), with exact player/label multiplicities, and the matching finite-k bound. This is more than a new name for the individual old deletion packing: it proves the frozen sufficiency conjecture if correct. No priority claim is made. No statement here is accepted merely because two model instances agree; independent symbolic and reduction checks are still required.

Read sources: campaign interpretation/RESIDUAL_SUFFICIENCY_CONJECTURE.md, interpretation/RESIDUAL_PROPAGATION.md, src/residual_relaxation.py, PROOF_STATE.md, and structural_classification_2026-09-06/sharp_subsidy/SHARP_SUBSIDY.md. All canonical files remained unchanged.
