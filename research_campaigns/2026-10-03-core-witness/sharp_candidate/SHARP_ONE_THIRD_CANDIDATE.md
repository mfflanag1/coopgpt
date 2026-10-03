# Candidate sharp one-third theorem from core-witness compatibility

3 October 2026. Conventional proof candidate; independent adversarial review and claim-specific source comparison are in progress. Do not replace the retained global frontier or claim a field-level breakthrough on the strength of this draft alone. The proposed new contribution is the aggregation in Sections3–5, not LP duality, matching tightness, core maxima, or the already retained lower family.

## 1. Frozen model and candidate conclusion

There are three sectors of equal finite size m>=1. Pair weights are nonnegative. Only complete triples are productive, with value the sum of their three pair weights. Every coalition's worth is its maximum integral disjoint-triple value. The original grand worth T is positive, and its entire original core C is nonempty. Define H_i=max{x_i:x in C}, before any intervention. The protected subsidy s is the minimum extra grand budget allowing all original coalition inequalities and y_i>=H_i/3.

**Candidate theorem.** Every such finite market has s/T<1/3, and the supremum over this class is exactly1/3. No assumptions on sparsity, incidence cycles, repeated diagonal labels, uniform weights, or simultaneous attainment of ideals are needed.

Choose an optimal perfect matching and label it diagonally. A maximum integral matching can be completed to a perfect one because sizes agree and all triple values are nonnegative. Put d_j=v(j,j,j), so sum_j d_j=T. Every original core point has nonnegative coordinates and makes every diagonal tight. Thus 0<=H_(r,j)<=d_j. The core is compact, so each maximum is attained.

Let u_(r,j) be the sum of the two diagonal pair weights incident to sector-r player at label j. Then sum_(r,j)u_(r,j)=2T.

## 2. Two pointwise core facts and a maximum comparison

For any sector r and labels a,b, completing the opposite diagonal pair at a with player(r,b) gives

    x_(r,b)+d_a-x_(r,a) >= d_a-u_(r,a).

Indeed its full-triple value is at least that opposite-pair value, by nonnegativity. Therefore, throughout C,

    x_(r,a)-x_(r,b) <= u_(r,a).                         (1)

For a triple e with player labels j_1,j_2,j_3, choose any ordered permutation(r,s,t) of the sectors. Subtract the diagonal equality at j_s from e's core inequality and use(1):

    x_(t,j_t)-x_(t,j_s)
      >= v(e)-d_(j_s)+x_(r,j_s)-x_(r,j_r)
      >= v(e)-d_(j_s)-u_(r,j_r).

Choose an original core point attaining H_(t,j_s). Its other coordinate is at most H_(t,j_t), giving

    H_(t,j_t)-H_(t,j_s) >= v(e)-d_(j_s)-u_(r,j_r).      (2)

These arguments remain valid when labels coincide. They never choose one allocation attaining two distinct ideals.

## 3. Six-comparison aggregation for an arbitrary fractional packing

Let lambda_e>=0 be any fractional partial matching. Put

    p_i=sum_(e contains i)lambda_e <=1,  q_i=1-p_i,
    W=sum_e lambda_e v(e),  k=m-sum_e lambda_e,
    S=sum_i q_i H_i,  B=sum_i q_i u_i,  V=3W+S.

Every sector has residual mass sum_(i in sector)q_i=k. Let n_j=sum_r p_(r,j), Htot_j=sum_r H_(r,j), and delta_i=d_(label(i))-H_i>=0. Define D_p=sum_i p_i d_(label(i)), U_p=sum_i p_i u_i, and H_p=sum_i p_i H_i.

Sum(2) over all six sector permutations of a fixed e, then weight by lambda_e and sum over e. The positive ideal terms contribute2H_p; the negative cross-sector terms contribute minus sum_j n_j Htot_j plus H_p. Hence

    6W <= 2D_p+2U_p+3H_p-sum_j n_j Htot_j.             (3)

Using U_p=2T-B, sum_i q_i d_i=3T-D_p, and H_i=d_i-delta_i, adding2S to(3) gives

    2V <=10T-2B-E,                                    (4)
    E=sum_(r,j) [sum_(t != r) q_(t,j)] delta_(r,j) >=0.

For clarity, the deficit coefficient before simplification is

    (3-n_j)p_(r,j)+(2-n_j)q_(r,j)
      =2-n_j+p_(r,j)=sum_(t != r)q_(t,j).

This identity is valid for fractional loads, including n_j>2; no integer-incidence sign argument is being applied to unrelated deficits. Equation(4) implies

    V <=5T-B.                                         (5)

## 4. Weighted residual budget at an attaining witness

For every x in C, weighting all team covers by lambda gives sum_i p_i x_i>=W. Efficiency therefore gives

    sum_i q_i x_i <=T-W=:R.                            (6)

In particular R>=0. Suppose k>0. Fix i in sector r and choose a core point attaining H_i. For every other sector-r player j, equation(1) gives x_j>=H_i-u_i. Retain the exact contribution q_i H_i of i and use nonnegativity outside sector r. Equations(6) and sum_(j in sector r)q_j=k imply

    kH_i <=R+(k-q_i)u_i.                              (7)

Here k-q_i is the sum of the other residual masses in that sector, so it is nonnegative. Multiply by q_i and sum over all players. Since sum_i q_i=3k, with C_2=sum_i q_i^2 u_i>=0 we obtain

    kS <=3kR+kB-C_2,
    V <=3T+B-C_2/k <=3T+B.                            (8)

Average(5) and(8): V<=4T. More precisely, retaining E gives

    V <=4T-E/4-C_2/(2k).                              (9)

If C_2>0 this is strict. If C_2=0, nonnegativity implies q_i u_i=0 for every i, so B=0; then(8) gives V<=3T<4T. If k=0, every q_i=0 and W<=T by(6), again V<=3T<4T. Thus every fractional packing has V<4T.

## 5. Protected allocation duality and sharpness

Nonnegative full-team covers are equivalent to all original coalition inequalities, by summing along integral matchings. Substitute y=H/3+z with z>=0 in the minimum-total-payment LP. Its fractional-packing dual is

    s=max_lambda [sum_e lambda_e v(e)
                  +(1/3)sum_i(1-p_i)H_i-T]
     =max_lambda (V/3-T).

The primal is feasible with sufficiently large payoffs and has finite minimum. The packing polytope is nonempty and compact; each lambda_e<=1. LP duality and attainment therefore apply, even for real pair weights. Because every lambda satisfies V<4T, the attained maximum gives s<T/3. This argument uses the full fractional packing directly and does not require replication or sparsification.

The retained chain family in SHARP_SUBSIDY.md has m=2q+1, T=3(2q+1), every original ideal3, and exact subsidy2q for every integer q>=1. Its ratio tends to1/3. Its all-parameter core witnesses and protected-allocation proof must be rechecked as part of this candidate's release. Together with the upper proof they give supremum S3=1/3, unattained by any finite market.

## 6. Sharper finite integral-obstruction theorem

If lambda is the indicator of an integral partial matching P and k=m-|P|>=1, then q_i is0 or1, so C_2=B and(8) becomes

    V <=3T+((k-1)/k)B.

Combine this with(5), using weights k/(2k-1) and(k-1)/(2k-1), respectively:

    V <=(4-1/(2k-1))T,
    J(M,P)<=2(k-1)T/[3(2k-1)].                        (10)

For k=1 this gives J<=0; for k=0, W<=T and there are no unmatched players. Empty P causes no difficulty. The same retained chain family with q=k-1 attains equality for every k>=2. Thus(10) is sharp as a bound indexed by the integral obstruction's unmatched count, not an asserted exact subsidy formula for every market of that size.

An exact nonnegative-slack identity records the aggregation. Let L be the sum over P of all six slacks in(2), let E be as in(4), and set

    F=sum_(i unmatched)[T-W+(k-1)u_i-kH_i] >=0.

Then

    (8k-5)T-(2k-1)V = ((k-1)/2)(E+L)+F.              (11)

All three terms vanish for the retained equality family. Identity(11) can be checked by exact coefficient arithmetic; its all-size justification is the incidence counting above, not finite enumeration.

## 7. Review and priority obligations

This draft requires independent review of(1)->(2), the sixfold count, the fractional deficit identity, the weighted attaining-witness argument, LP duality/attainment, and the all-parameter lower family. No numerical optimizer is a proof of these implications. The old full-witness finite certificates and negative controls corroborate different bounded claims.

Established ingredients include core/matching duality, tight optimal teams, coordinate extrema, the retained pair-completion comparisons, residual/deletion budgets, and the earlier chain construction. The proposed contribution is their aggregate compatibility inequality closing the frozen sharp constant. Freely available original sources must be checked for this exact claim. Novelty, independent human specialist validation and field-level importance remain unresolved until separately established. No outreach or paid-source access is authorized.
