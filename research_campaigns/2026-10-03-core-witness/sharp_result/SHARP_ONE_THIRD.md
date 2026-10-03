# Sharp one-third subsidy theorem from core-witness compatibility

3 October 2026. **Internally proved by the all-size argument below**, independently rederived and checked with exact symbolic identities. Two model reviews found no correctness gap; these reviews are corroboration, not the proof. Historical novelty and independent human specialist validation remain unresolved. See [review adjudication](../reviews/sharp_theorem/ADJUDICATION.md) and [source comparison](SOURCE_COMPARISON.md).

The proposed contribution is the aggregate compatibility inequality in Sections 3–5 and its consequences. Core duality, tight optimal teams, coordinate extrema and the previously retained lower family are established ingredients or earlier project work. The reviewed candidate is preserved unchanged in `../sharp_candidate/` for hash-bound provenance.

## 1. Frozen model and conclusion

There are three sectors of equal finite size m>=1. Pair weights are nonnegative. Only complete triples are productive, with value the sum of their three pair weights. Every coalition's worth is its maximum integral disjoint-triple value. The original grand worth T is positive, and its entire original core C is nonempty. Define H_i=max{x_i:x in C}, before any intervention. The protected subsidy s is the minimum extra grand budget allowing all original coalition inequalities and y_i>=H_i/3.

**Theorem.** Every such finite market has s/T<1/3, and the supremum over this class is exactly1/3. No assumptions on sparsity, incidence cycles, repeated diagonal labels, uniform weights, or simultaneous attainment of ideals are needed.

Choose an optimal perfect matching and label it diagonally. A maximum integral matching can be completed to a perfect one because sizes agree and all triple values are nonnegative. Put d_j=v(j,j,j), so sum_j d_j=T. Every original core point has nonnegative coordinates and makes every diagonal tight. Thus 0<=H_(r,j)<=d_j. The core is compact, so each maximum is attained.

Let u_(r,j) be the sum of the two diagonal pair weights incident to sector-r player at label j. Then sum_(r,j)u_(r,j)=2T. Pair-additivity is used through this budget identity and the pair-completion range bound below; no assumption of productive two-player coalitions is made.

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

The retained chain family has m=2q+1, T=3(2q+1), every original ideal 3, and exact subsidy 2q for every integer q>=1. Section 7 includes its complete proof, rechecked during this campaign. Its ratio tends to 1/3. Together with the upper proof this gives supremum S3=1/3, unattained by any finite market.

## 6. Sharper finite integral-obstruction theorem

Write J(M,P)=W+S/3-T=V/3-T for the lower obstruction associated with the named partial matching P.

If lambda is the indicator of an integral partial matching P and k=m-|P|>=1, then q_i is0 or1, so C_2=B and(8) becomes

    V <=3T+((k-1)/k)B.

Combine this with(5), using weights k/(2k-1) and(k-1)/(2k-1), respectively:

    V <=(4-1/(2k-1))T,
    J(M,P)<=2(k-1)T/[3(2k-1)].                        (10)

For k=1 this gives J<=0; for k=0, W<=T and there are no unmatched players. Empty P causes no difficulty. The same retained chain family with q=k-1 attains equality for every k>=2. Thus(10) is sharp as a bound indexed by the integral obstruction's unmatched count, not an asserted exact subsidy formula for every market of that size.

This finite-k formula applies to **integral** P only. Fractional residual mass cannot be substituted for k in (10), because C_2 need not equal B. An exact countercontrol in the verifier uses a half-diagonal/half-special packing with fractional k=1 and positive J.

An exact nonnegative-slack identity records the aggregation. Let L be the sum over P of all six slacks in(2), let E be as in(4), and set

    F=sum_(i unmatched)[T-W+(k-1)u_i-kH_i] >=0.

Then

    (8k-5)T-(2k-1)V = ((k-1)/2)(E+L)+F.              (11)

All three terms vanish for the retained equality family. Identity(11) can be checked by exact coefficient arithmetic; its all-size justification is the incidence counting above, not finite enumeration.

## 7. The retained sharpness family (complete proof)

For q>=1 set m=2q+1, with labels 0,...,2q in each sector. Initialize all three pair matrices to the identity matrix. For s=0,...,q-1 let

    e_s=(s, q+s, s-1) for s>0;
    e_0=(0, q, 2q).

For every e=(a,b,c), set A_ab=2, B_ac=1, C_bc=2. All three labels within each e are distinct. The special pair positions are therefore off-diagonal, and player-disjointness makes them pairwise distinct within each pair matrix; no diagonal entry is overwritten. The e_s are disjoint as actual teams (each sector's labels are distinct). Their label hypergraph has a tree incidence graph: consecutive edges share one label, each edge has a private b label, and the endpoints have the remaining private labels.

**Claim.** T=3m, every original ideal is 3, and s_3=2q. Consequently s_3/T=2q/[3(2q+1)] tends to 1/3.

### Original core and individual ideals

Root the label incidence tree at an arbitrary label r, and assign r an arbitrary color k in {A,B,C}. Traverse outward. When a special edge is reached through its already colored parent label, color its two new labels by their designated sectors in that edge. Each edge therefore has at least two labels whose color equals their designated sector. There are no conflicting assignments because the incidence graph is a tree.

For this coloring c define x_{j,v}=1_{j=k}+2*1_{c(v)=j}. Each diagonal triple receives 3 and the entire vector sums to 3m. At the chosen coordinate (k,r), the payoff is 3.

Here is a complete check of all full-team inequalities. Every team receives a baseline of 1. Two positive off-diagonal pair entries can occur together only in a special edge: their shared actual player belongs to at most one special edge. Such an edge has worth 5 and at least two designated color matches, so receives at least 5. Two diagonal pair entries force all three labels equal; those teams have worth and payoff 3. All other teams have at most one off-diagonal entry and at most one diagonal entry. An off-diagonal entry of value 2 is on AB or BC. At least one endpoint has its designated color, because at least two of the three labels of its special edge match; the team therefore receives at least 3, covering its worth of at most 3. For the off-diagonal AC entry of value 1, the same endpoint argument applies, covering its worth of at most 2. Teams without off-diagonal entries have worth at most 1 unless diagonal, already handled. This exhausts the cases.

Thus x covers all coalitions. The diagonal matching has value 3m, and x covers all matchings with total 3m, proving T=3m and x in the original core. Every core vector must make each diagonal team tight; nonnegativity gives each coordinate at most 3. Since r and k were arbitrary, H_i=3 for every player.

### Exact subsidy

Every protected payoff has y_i>=1. The q special teams form a partial matching of total worth 5q. Its 3m-3q unmatched players require at least 3m-3q. Hence sum y>=3m+2q, giving s>=2q.

Conversely start with y_i=1 for all players and add 2 to the A player of every special team. Each special team then receives 5. Every other team has value at most 3 by the preceding classification and receives at least 3. This covers all original coalitions, meets all frozen floors, and totals 3m+2q. Thus s=2q.

The retained exact standard-library verifier `../../../structural_classification_2026-09-06/sharp_subsidy/tree_certificate.py` constructs all 3m original-ideal witnesses separately, checks every team, verifies the matching lower bound and subsidy allocation, and rejects damaged allocations. For q=1,...,12 it passes 3,603,804 integer team checks and 12 negative controls. This is bounded computational corroboration; the preceding rooting argument supplies the all-q proof. No external review has occurred.


## 8. Exact slack certificate and sufficient relaxation

For arbitrary fractional lambda, define L as the lambda-weighted sum of the six nonnegative slacks in (2), and

    F=sum_i q_i [T-W+(k-q_i)u_i-kH_i] >=0.

For k>0, the following identity is exact:

    2k(4T-V) = (k/2)(E+L)+C_2+F.                    (12)

Every term on the right is nonnegative for the reasons proved above. This is an all-size algebraic certificate. The standard-library verifier checks its polynomial coefficients separately from the finite market corroboration.

For integral P, the argument also proves the frozen residual-propagation sufficiency conjecture: any numbers h_i satisfying the diagonal caps, all six P-induced comparisons and the residual inequalities obey (10), whether or not that h vector is realizable as the true original ideals. The missing necessary witness-budget inequalities thus suffice to remove the earlier false relaxation obstruction. This implication does not assert that the enriched relaxation exactly characterizes the entire core or the ideal vector.

## 9. Attribution, review and limitations

The upper theorem is a proof for arbitrary dense markets in the frozen model, including real nonnegative weights, repeated diagonal labels and zero-valued diagonals. It uses no numerical optimizer, replication, sparsification, forest restriction or common coordinate-maximizing allocation. Finite checks corroborate the arithmetic; they do not establish universality.

The reported novelty claim is limited to a **proposed contribution** pending source priority and human review. The half-optimal core, subsidy framework, LP duality and core extrema have antecedents. The free-source comparison records what was actually read and unresolved originals. The result has not been submitted, externally endorsed or established as a field-level breakthrough.

Reproduction and the exact tested scope are in [REPRODUCE.md](REPRODUCE.md); the short [specialist review packet](SPECIALIST_PACKET.md) identifies the load-bearing steps and open priority questions. No outreach or purchase was performed.
