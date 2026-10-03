# Independent adversarial audit of the sharp aggregation argument

3 October 2026. Scope: the exact frozen three-sector, nonnegative pair-additive model in `SHARP_SUBSIDY.md`; original entire-core ideals; the original subsidy LP. No support or ideal optimizations were run. This audit rederived the inequalities from original core points rather than treating the proposed aggregation as an assumption. It used no held-out campaign case.

**Verdict:** no logical gap or counterexample was found. The load-bearing argument is valid under the frozen hypotheses. In fact its aggregate inequality and residual propagation extend directly to every fractional packing, so replication and sparsification are unnecessary for the universal upper bound. The result is a conventional proof candidate for `s_3<=T/3`; together with the retained all-parameter lower family it gives `S_3=1/3`. This is the mathematical consequence of the derivation below, not a claim of established literature novelty, completed external review, or authorization to release a theorem. The coordinator should preserve independent cross-model adjudication and verification of the lower family.

## 1. Hypotheses and notation checked

There are m players in each of three sectors. Only full triples are productive, and

    w(a,b,c) = AB[a,b]+AC[a,c]+BC[b,c],

with all pair entries nonnegative. Original coalition worth is the maximum integral matching worth. The original grand worth is `T>0`, and the entire original core C is nonempty.

An optimal integral matching can be completed to a perfect matching: the unmatched counts agree in the sectors, and added triples have nonnegative worth. Since the original matching is already optimal, its completion remains optimal. Relabel such a perfect matching as the diagonal. Put

    d_j = w(j,j,j),               sum_j d_j=T,
    u_A,j = AB[j,j]+AC[j,j],
    u_B,j = AB[j,j]+BC[j,j],
    u_C,j = AC[j,j]+BC[j,j].

Every original core point x is nonnegative, totals T, and covers every full triple. Conversely those conditions imply all original coalition inequalities by summing over integral matchings. Every diagonal is tight at every original core point. Therefore

    0<=H_s,j:=max_(x in C) x_s,j<=d_j,
    delta_s,j:=d_j-H_s,j>=0,
    sum_(s,j) d_j=3T,             sum_(s,j) u_s,j=2T.          (1)

Maxima exist: C is a nonempty closed subset of the nonnegative total-T simplex. No choice of a common coordinate-maximizing core point is made anywhere below.

Zero-valued diagonals are allowed. Their corresponding H and u are zero; none of the proof divides by an individual diagonal value.

## 2. The diagonal incident-budget range bound

For a fixed original core point x, put `ell_s=min_j x_s,j`. Complete the opposite-sector diagonal pair at label j with a player attaining ell_s. Its full-team worth is at least the opposite pair's value, by pair nonnegativity. The core inequality and tight diagonal then give

    ell_s + d_j-x_s,j >= opposite_diagonal_pair_j,
    x_s,j-ell_s <= u_s,j.

Consequently, for any two labels a,b,

    x_s,a-x_s,b <= u_s,a.                                    (2)

This is valid in the dense original market and when labels coincide. Its proof uses the fact that a completed pair is an allowed full triple; it does not treat a pair as a productive coalition. The nonnegativity assumption is essential to discarding the two extra pair entries.

## 3. Every full triple gives six true ideal comparisons

Take a full triple with one player at label a_s in each sector s and worth v. For an ordered permutation `(s,t,u)` of the sectors, subtract the tight diagonal at a_t from that triple's core inequality:

    x_u,a_u-x_u,a_t
      >= v-d_a_t+x_s,a_t-x_s,a_s
      >= v-d_a_t-u_s,a_s.                                    (3)

The second step is (2). Since (3) holds at every original core point, choose a core point attaining `H_u,a_t`; its other coordinate is at most `H_u,a_u`. This proves

    H_u,a_u-H_u,a_t >= v-d_a_t-u_s,a_s.                       (4)

The maximizer in this step can differ across comparisons. Each resulting statement is an ordinary inequality in the fixed numbers H, so summing them is legitimate. This is not common attainment.

Let `Htot_j=sum_s H_s,j`. Summing all six ordered sector permutations gives

    6v <= 2 sum_s d_a_s + 2 sum_s u_s,a_s
                       +3 sum_s H_s,a_s - sum_s Htot_a_s.    (5)

Independent counting check: each participating ideal appears twice as a positive term in (4); the negative cross terms equal `sum_s Htot_a_s-sum_s H_s,a_s`. This gives the coefficient 3 in (5), rather than 2. Each diagonal and each incident budget appears twice.

Repeated diagonal labels do not invalidate this count. Different sector players remain different actual players; sums over a_s retain their multiplicities. No simple-graph interpretation or distinct-label assumption enters.

## 4. Fractional aggregation: explicit nonpositive remainder

Let lambda be any fractional partial matching, not necessarily rational. Define

    p_s,j = sum_(teams containing (s,j)) lambda_team <= 1,
    q_s,j = 1-p_s,j >=0,
    W = sum_team lambda_team * worth_team,
    Lambda = sum_team lambda_team,
    k = m-Lambda = sum_j q_s,j              for each sector s,
    S = sum_(s,j) q_s,j H_s,j,
    B = sum_(s,j) q_s,j u_s,j,
    V = 3W+S.

Equal sector sizes and one player per sector in a full team give the same k in every sector. Write `n_j=sum_s p_s,j`; it may be any real number in `[0,3]`.

For compact bookkeeping let

    D_P=sum p_s,j*d_j,  D_U=sum q_s,j*d_j,
    U_P=sum p_s,j*u_s,j, H_P=sum p_s,j*H_s,j.

Weight (5) by lambda and sum all teams:

    6W <= 2D_P+2U_P+3H_P-sum_j n_j Htot_j.                  (6)

Add `2S`. At a fixed diagonal label j the ideal part is

    sum_s [3p_s,j+2q_s,j-n_j] H_s,j
      = 2 (sum_s q_s,j) d_j
        - sum_s (sum_(t!=s) q_t,j) delta_s,j.                (7)

This identity follows by inserting `H=d-delta` and `p=1-q`. In particular the remainder has a sign even for fractional loads; one must not rely on the integral shortcut `n_j=3 implies no unmatched player` to justify the fractional case.

Put

    E = sum_(s,j) (sum_(t!=s) q_t,j) delta_s,j >=0.

Using `D_P+D_U=3T` and `U_P+B=2T`, (6)-(7) yield

    6W+2S <= 10T-2B-E,
    V <= 5T-B-E/2 <= 5T-B.                                 (8)

For integral P, n_j is the number of its used actual players at label j. The question's remainder

    (n_j-2) delta_U(j) - (3-n_j) delta_P(j)

is exactly `-sum_s(sum_(t!=s) q_t,j)delta_s,j`. The n=0,1,2,3 sign argument is therefore correct, including repeated-label P-teams.

## 5. Independent residual propagation bound

For any original core point x, weighting all full-team inequalities by lambda gives

    sum_(s,j) p_s,j x_s,j >= W,
    sum_(s,j) q_s,j x_s,j <= T-W=:R.                         (9)

Thus R is nonnegative. Fix an actual player i in sector s and choose a core point attaining H_i. Equation (2) gives `x_s,j>=H_i-u_i` for every other player of its sector. Keeping the target's own residual coefficient q_i exactly,

    sum_j q_s,j x_s,j >= q_i H_i+(k-q_i)(H_i-u_i)
                         = kH_i-(k-q_i)u_i.

The remaining sectors have nonnegative residual payoffs. Combining with (9) proves

    kH_i <= R+(k-q_i)u_i.                                   (10)

This remains valid for q_i=0; no positive-residual assumption is hidden. Also `k-q_i>=0` because q_i is one nonnegative summand of its sector's total k.

If `k>0`, multiply (10) by q_i and sum all players. Since `sum_i q_i=3k`, defining `C2=sum_i q_i^2 u_i>=0` gives

    kS <= 3kR+kB-C2,
    V <= 3T+B-C2/k <= 3T+B.                                (11)

Only one coordinate is maximized in each application of (10); the witness may vary with i. Multiplying the resulting scalar inequalities by q_i and summing requires no common witness.

If `k=0`, every q_i is zero. Core coverage directly gives `W<=T`; hence `V=3W<=3T`. The division by k is not used in this case.

## 6. Universal upper and finite-market strictness

For k>0, adding (8) and (11) and dividing by two yields

    V <= 4T-E/4-C2/(2k) <= 4T.                              (12)

The simpler main proof can omit the two correction terms and merely average `V<=5T-B` and `V<=3T+B`.

In fact `V<4T` for every individual fractional packing in every finite admissible market. If C2>0, (12) is strict. If C2=0, the nonnegative terms `q_i^2 u_i` all vanish, so every `q_i u_i` vanishes too, and B=0. Then (11) gives `V<=3T<4T`. The k=0 case has the same conclusion.

This pointwise strictness does imply strictness of the optimal finite-market ratio: the fractional matching polytope is compact, and the relevant linear objective attains its maximum at some lambda. Apply the preceding case analysis to that maximizing lambda. No uniform lower bound on C2/k, and no limit interchange near k=0, is being assumed.

To connect to the original subsidy, substitute `y=H/3+z`, with `z>=0`, in its finite LP. Full-team covers suffice for all coalition covers. The dual has lambda>=0 and player loads at most one, and strong duality gives exactly

    s_3 = max_lambda [ W + S/3 - T ]
        = max_lambda [ V/3-T ].                              (13)

The primal is feasible by sufficiently large payoffs and bounded below; the finite dual is feasible and bounded. Thus (12) proves `s_3<=T/3`, and the strict argument proves `s_3<T/3` for each finite market with T>0. The supremum over market sizes may nevertheless be 1/3.

This is the same frozen-floor objective and entire original core as in the contract. Ideals are never recomputed after intervention.

## 7. Integral-P correction and sharpness of that indexed bound

For an ordinary player-disjoint partial matching P, q_i is zero or one and `k=m-|P|` is an integer. Then `C2=B`. For `k>=1`, put `alpha=(k-1)/k>=0`; (11) and (8) imply

    V <= 3T+alpha B,
    V <= 5T-B.

Add the first inequality to alpha times the second and divide by `1+alpha`:

    V <= (3+5alpha)/(1+alpha) T
       = (4-1/(2k-1)) T,
    J:=W+S/3-T <= 2(k-1)/(3(2k-1)) T.                       (14)

For k=1 the first inequality already gives `J<=0`. For k=0, P is perfect and `J=W-T<=0`. For empty P, k=m and the argument remains valid, although the elementary bound J<=0 is stronger.

**Scope restriction:** the finite correction (14) is an integral-P statement. One cannot insert a noninteger residual mass k into it: fractional C2 is generally not B, and `(k-1)/k` may be negative. The universal fractional bound (12) has its separate proof above.

The retained all-parameter chain from `SHARP_SUBSIDY.md` has, for q>=1,

    m=2q+1, |P|=q, k=q+1,
    T=3(2q+1), W=5q, H_i=3, u_i=2,
    S=9(q+1), B=6(q+1), delta_i=0.

Both inequalities used in (14) hold with equality, and `J=2q`. Thus (14) is sharp across all market sizes with a fixed integer k>=2, using q=k-1. This is not a statement of sharpness at every fixed pair (m,|P|). The same family's exact full subsidy is 2q, giving ratios approaching 1/3. Its rooting proof supplies separate core witnesses for every ideal; the explicit protected allocation supplies the matching subsidy upper bound. Combining that retained lower theorem with (12) gives the sharp supremum.

## 8. Adversarial checks and identified scope hazards

The following were specifically challenged rather than assumed:

- **Could two different maximum witnesses be silently combined?** No. Each comparison (4) uses one attained denominator ideal; each residual inequality (10) uses one target ideal. Summation happens only after obtaining scalar inequalities in fixed H.
- **Could a repeated label make the six comparisons overcount a player?** No. The six sector orders count actual sector players. Their label coincidences are retained as multiplicities in n_j and Htot_j. The identity (7) covers those coincidences.
- **Does the nonpositive remainder require sparsity, connectedness, a tree, or integral degrees?** No. Its fractional form is explicitly `-E`, with nonnegative residual loads and diagonal deficits.
- **Does completing an opposite pair change the productive-coalition model?** No. It uses an original full-team constraint. Pair nonnegativity supplies the comparison to the opposite pair alone.
- **Does the proof require an optimal fractional grand matching?** No additional assumption is made. A nonempty original core covers every fractional packing and proves `W<=T` directly. This is a consequence of the original core, not a relaxation of grand worth.
- **Could zero diagonals or k=0 invalidate division or signs?** Zero diagonals cause no division; k=0 is treated separately.
- **Can the integral correction be asserted for fractional residual mass?** No; that would be an actual scope error. The corrected fractional proof uses C2, not B.
- **Could a finite-market equality s/T=1/3 remain possible?** Not under this argument. Compact attainment and the C2=0 case rule it out. This is consistent with a supremum approached by growing chains.
- **Does the argument rely on numerical feasibility or solver status?** No. The proof is algebraic; the checks below are corroboration only.

No defect was found among these attack points. Remaining review tasks concern independent adjudication of this proof, validation of the retained lower-family argument, and literature priority—not an identified mathematical gap in the displayed upper-bound derivation.

## 9. Review of the existing lifting route

The all-size integral route would also suffice. The replication proof in `REDUCTIONS.md` is valid here: repeating an optimal perfect matching and any original core point pins copied grand worth at DT. Tight matched teams and substitutions of same-player copies force equal copied payoffs throughout the copied core. Hence copied ideals equal the original H. A rational fractional packing lifts to an actual matching by giving each occurrence unused copies of its three players; capacities guarantee enough copies. Its obstruction scales by D. A maximizing vertex can be chosen rational because the bounded packing polytope has a rational constraint matrix, even if the objective's pair values or ideals are real.

Sparsification and component restriction are not needed for either the diagonal-range proof or direct fractional aggregation. Avoiding them removes possible confusion about enlarging the core or changing ideals. The direct proof uses the original market and original H throughout.

## 10. Exact corroboration executed

A fresh symbolic calculation expanded the per-label left side of (7), independently starting from `3*p*H+2*q*H-n*Htot`, and returned precisely

    -delta0*q1-delta0*q2-delta1*q0-delta1*q2-delta2*q0-delta2*q1

after subtracting the diagonal term. A separate six-permutation symbolic count recovered the coefficient 3, and coefficient dictionaries agreed for all 27 three-label assignments to the three participating sector players, including every repeated-label pattern. Rational checks covered all 125 residual triples with q_s in `{0,1/4,1/2,3/4,1}`. For k=1,...,30, exact Fraction arithmetic checked the convex-combination identity and simultaneous equality of both bounds on the chain parameters. All checks passed. These finite checks do not establish the all-size statement; Sections 1-7 provide its proof.

Executed output:

    PASS: symbolic labelwise delta identity; six-permutation count;
    125 rational residual triples; convex combination and chain equality for k=1..30

Reviewed inputs: `structural_classification_2026-09-06/sharp_subsidy/REDUCTIONS.md`, `SHARP_SUBSIDY.md`, and the existing ideal-difference/sector-minimum formulas already examined in the earlier scoped task. No canonical project files were edited, and no recursive delegation was performed.
