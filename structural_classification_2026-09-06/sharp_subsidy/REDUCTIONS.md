# Exact reductions for the unresolved sharp constant

Current global bounds and the new all-size construction are in [current universal proof](CORE_COMPATIBILITY_UPPER.md). The one-third statements below retain their stated scope.

Date: 2026-09-07. The primary goal remains active and the bounds remain 1/3 <= S_3 <= 2/5. These reductions change the live proof problem; they do not solve its final inequality.

## 1. Replication preserves the original entire core and subsidy

Let M satisfy the frozen hypotheses and let D>=1 be an integer. Replace each player i by D copies. Every pair of copies inherits the original pair value. Write M^[D] for the resulting strict three-sector market.

**Theorem.** T(M^[D])=D*T(M), its original core is exactly the set of D-fold repetitions of points of C(M), each copy has ideal H_i(M), and s_3(M^[D])=D*s_3(M).

Proof. Repeat an optimal perfect matching D times to obtain worth D*T. Repeat any original core vector; it covers every copied team and has total D*T. Therefore the new grand worth is D*T and the repeated vector is in the new core.

For any point X in the new core, all teams in the repeated optimal matching are tight. Fix two copies i^a,i^b of the same player. Replace i^a by i^b in the tight team containing i^a; the team value is unchanged, so X(i^b)>=X(i^a). Reverse the argument using the tight team containing i^b to obtain equality. Thus every copy of each original player has the same payoff. The resulting original vector covers every original team and sums to T. This proves the asserted entire-core identity and ideal identity, with no recomputation under subsidy.

Lifting a protected allocation gives s_3(M^[D])<=D*s_3(M). Conversely, given any protected copied allocation Y, average its D coordinates for each original player. Average the copied-team inequality over all D^3 choices of copies of a fixed original team. This gives the original team inequality for the averaged vector. The frozen floors also survive averaging. The averaged total is T+s/D, proving the reverse inequality.

This proof uses matching tightness and symmetry, not a general claim that every cooperative game's core treats identical players equally.

## 2. Fractional obstructions can be lifted to partial matchings

Let lambda be a rational fractional partial matching and choose D so that all D*lambda_t are integers. In M^[D], realize D*lambda_t copies of each team t, assigning distinct unused copies of every player to each occurrence. This is possible because sum_{t containing i} D*lambda_t<=D. The realized teams form an ordinary partial matching P. Its weight is D*sum_t lambda_t*w_t; the number of unmatched copies of i is D*(1-d_i). Hence

    w(P)+(1/3)*sum_{copies unmatched} H_i-D*T
      = D*[sum_t lambda_t*w_t+(1/3)*sum_i(1-d_i)*H_i-T].

The packing polytope has a rational constraint matrix and is bounded, so every linear objective has a rational optimal vertex, even when pair values and ideals are real. Thus an all-size bound proved for integral partial matchings implies the full fractional bound. Checking integral matchings at a fixed size still does not suffice.

## 3. Sparsification and connected components

Fix an optimal perfect matching mu and an ordinary partial matching P. Relabel mu as the diagonal matching. Set every pair entry to zero unless it occurs in a team of mu or P. Call the resulting market M0.

Nonnegativity implies all team values weakly decrease. The diagonal matching keeps its value T, while any original core point remains a cover of total T. Thus M0 still has grand worth T and a nonempty core, with C(M) contained in C(M0). In particular H_i(M0)>=H_i(M). Every team of P retains all its pair entries and its value. Its obstruction

    J(M,P)=w(P)+(1/3)*sum_{i unmatched by P}H_i(M)-T

therefore weakly increases under sparsification. Each pair matrix now has at most two nonzero positions per row or column, because each player appears in at most one team of either matching.

Make a graph on diagonal labels by joining labels that occur together in a team of P. Restrict M0 to each connected component L, keeping all three sector players at each of its labels. Let T_L be its sum of diagonal values. Restricting a core point gives a cover of total T_L: every diagonal team was tight. The diagonal matching attains T_L, so the component has grand worth T_L and nonempty core. Each component ideal is at least the corresponding global ideal, since restriction maps the global core into its local core. Therefore

    J(M0,P) <= sum_L J(M_L,P_L),     T=sum_L T_L.

If T_L=0, all component coordinates and all its nonnegative team values are zero, and its contribution is zero. At least one positive-worth component has J(M_L,P_L)/T_L at least the global ratio. Cross-component full teams need not be assigned an additive decomposition for this argument; it uses restrictions of actual core points and inequalities on their ideals.

**Corollary.** The supremum S_3 is unchanged if it is restricted to connected markets supported on the pair entries of a diagonal optimal matching and one ordinary partial matching. To prove S_3<=1/3 it suffices to establish

    3*w(P)+sum_{i unmatched by P}H_i <= 4*T

throughout this sparse connected class. Replication, sparsification and restriction give the converse reduction from arbitrary markets. The inequality itself is still unproved.

The incidence graph of the two matchings has degree at most three on diagonal labels. Special triples may involve only one or two diagonal labels; repeated incidences must not be silently discarded. Cyclic components and heterogeneous diagonal weights remain live.

## 4. Exact two-label calibration

**Certified theorem.** With two players in each of three sectors, every market in the frozen class has s_3=0. This is an all-coefficient statement at fixed size, not a sample of integer matrices. No novelty is claimed for it.

Normalize T=1 and relabel an optimal matching as diagonal. Introduce the 12 nonnegative pair entries and six independent original-core witnesses p^(i), each nonnegative, covering all eight teams and summing to 1. For any actual market choose each p^(i) to attain H_i; compactness of the original core permits this. The feasible linear system therefore includes every normalized market and its actual ideals.

For fixed packing lambda, its dual protected cost is the linear expression

    sum_t lambda_t*w_t+(1/3)*sum_i(1-d_i)*p_i^(i).

The packing polytope is {lambda>=0: incidence*lambda<=1}. It is bounded. A vertex with k positive coordinates has k linearly independent tight capacity constraints; k<=6. Enumerating every support of size k and every k-element tight-capacity set therefore covers all vertices, alongside the origin. Exact Gaussian elimination examines 3,002 nonempty bases and produces 23 vertices, of which 10 are fractional.

For each vertex, TWO_LABEL_CERTIFICATES.json supplies a rational LP dual proving that the displayed protected cost is at most 1. The independent standard-library verifier reconstructs every coefficient from the team definitions, reenumerates all packing vertices with rational arithmetic, checks coverage and dual feasibility, and rejects a damaged certificate. It does not trust the solver's status, floating objective, recorded conclusion, or certificate metadata. Since a linear packing objective reaches its maximum at a vertex, the upper bound holds for every packing and hence the subsidy primal costs at most T. Original stability requires at least T, yielding s_3=0.

two_label_exact.py is the optional SciPy certificate generator. verify_two_label.py is the independent exact checker included in build.sh. The separate verify_replication.py checks six copied constructions, 343,560 integer team inequalities, and rational-packing lifts. Those checks corroborate, rather than replace, the all-size replication proof.

## 5. New source comparison and search outcome

Equal treatment of same-sector substitutes is an established ingredient. Bejan and Gómez's author-uploaded January 17, 2017 manuscript, [Equal Treatment at Core Allocations](https://www.researchgate.net/publication/309650476_Equal_Treatment_at_Core_Allocations), Proposition 5.7, proves this for aspiration-core allocations in multisided assignment games. Its later replication results use their specified replica construction. We give a direct proof for our pair-matrix replication; priority is not claimed for equal treatment or replication itself. The frozen-floor subsidy identity and the extremal reduction need their own comparison.

The new floating search used 240 sparse random packing starts across sizes 2,3,4,5,6,8, followed by alternating market and packing LPs. It included 69 genuinely fractional starts and found no ratio above 1/3; its best was 3/11 at size 8. This is non-exhaustive discovery evidence only. The all-size supremum remains unresolved.

## 6. Rejected shortcuts and next mathematical action

Replacing every H_i by its diagonal team's whole worth destroys the target bound. For size 2, take A_00=A_01=B_00=B_01=1/2 and all other entries zero. T=1 and the original core is the singleton paying A_0 one unit. Thus s_3=0. The proposed replacement floor gives B_0 and C_0 one-third each, while team (A_0,B_1,C_1) still requires one unit, forcing subsidy 2/3. The sharp proof must retain actual core ideals.

A proposed stronger tree induction subtracting one-third of an arbitrary root's diagonal worth from the 1/3 bound fails already at three labels. ROOT_COUNTEREXAMPLE.json contains a rational market and original-core witnesses, independently checked by verify_rejected_root.py. Its T=1, root worth is 4/9, and a partial-matching obstruction gives s>=11/54. Thus s+root_worth/3>=19/54>1/3. Rescaling by 18 gives integer pair entries, T=18, root worth 8, and s>=11/3, exceeding the proposed (T-root_worth)/3=10/3. This is an exact rejection; do not use the strengthened lemma.

The next substantive target is the sparse connected partial-matching inequality in Section 3, including cycles and unequal diagonal values. A suitable proof must account for reductions in original ideals caused by these components. The two-label theorem rules out components of that size as positive obstructions. Further generic dense random searches are lower priority now that the exact sparse reduction is available.
