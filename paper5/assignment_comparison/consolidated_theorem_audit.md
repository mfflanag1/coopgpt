# Independent consolidated theorem and interpretation audit

5 September2026. Read both current full manuscripts directly. The pairwise and three-sided results can form one honest sharp structural boundary theorem, provided the comparison is stated for **unit-capacity matching games with nonempty entire cores**, with the same normalized distance and full sorted selections. No material gap found in the load-bearing all-parameter proofs.

## Common definitions and boundary statement

For a finite weighted graph or three-uniform hypergraph, coalition value is the weight of a maximum integral matching inside it. Assume nonnegative values and positive matching optimum T. The entire core is the nonnegative efficient edge/triple covering polytope. For graph matching games, explicitly condition on nonempty core if dropping bipartiteness; this condition is automatic only for bipartite graphs. For the three-sided class, require disjoint sectors and one player of each sector per triple. Both construction and proof establish nonemptiness rather than substituting a fractional relaxation.

Let x be full ascending leximin and z full descending lexicographic minimum. Define rho=||x-z||_1/T. Count all players, including fixed zeros. On any compact convex core these full payoff vectors are unique. The graph result actually controls distance to every first-stage minimax point, a strengthening consistent with using full z in the comparison.

**Consolidated boundary.** For nonempty-core graph matching games on n>=4 players, the exact maximum rho is floor(n/2)/(floor(n/2)+1); it is zero for n=2,3. Every player's leximin payoff is at least half their payoff at any other core point. Already for three-sided triple matching games, the supremum over all finite games is2, the n-player supremum tends to2, and no positive dimension-independent individual core-maximum fraction survives. The triple examples have equal sector sizes, integer values in {0,1,2,3}, and only three degrees of freedom in the entire core.

The triple construction does not establish a sharp finite-n formula or a sharp convergence rate. Its O(log n/n) deficit upper bound and the subsequence limit are valid as written. The graph finite formula includes zero-edge and unmatched-player degeneracies by deleting zero-weight edges from a fixed optimal matching.

## Conventional proof: extension from bipartite graphs to all graphs

Fix an optimal matching M and discard zero-weight edges; write its positive weights s_1,...,s_k. For every core allocation p, summing M's inequalities and using efficiency forces each matched pair to sum to s_j and every player unmatched by this positive matching to have payoff0.

Let x be full leximin and y any core allocation. Put d=y-x and suppose d_a=delta>0. Define global sets

  A={v:d_v>=delta}, B={v:d_v<=-delta}.

Each matched pair has opposite changes, so M bijects A and B, giving |A|=|B|. Every unmatched player has zero change. Define h=1_A-1_B. If an edge uv is tight at x and u belongs to B, then v must belong to A: otherwise d_u+d_v<0, contradicting y's feasibility at that tight edge. In particular, a tight edge cannot have both endpoints in B. Therefore h_u+h_v>=0 for every tight edge; h also preserves the total. For all v in B, y_v>=0 implies x_v>=-d_v>=delta>0. Finitely many slack inequalities and positive decreasing coordinates ensure x+epsilon h remains in the entire core for sufficiently small epsilon>0.

If min_B x>min_A x, this step increases the lowest affected coordinates and decreases only strictly larger ones, strictly improving the full ascending sorted vector. Thus

  delta<=min_B x<=min_A x<=x_a,

and y_a=x_a+delta<=2x_a. Coordinates with d_a<=0 satisfy this directly. This proves y<=2x componentwise without any graph bipartition.

For a minimax core allocation z, put q_j=|z_u-x_u| on pair j and D=sum_j q_j, so ||x-z||_1=2D. Nonnegativity and the half guarantee give x_u,x_v>=q_j, hence s_j>=2q_j. On an increasing endpoint, z>=2q_j, so if Mmax=max_i z_i then D<=k Mmax/2. Some player a satisfies z_a=Mmax and x_a>=Mmax, since otherwise a short step from z toward x would lower all maximum coordinates. On that player's matched pair p, s_p>=Mmax+2q_p. Thus

  T>=2D+Mmax>=2D(1+1/k),

proving rho<=k/(k+1). When k=1 the nonzero part of the core is an interval of splits of T, and maximizing its minimum and minimizing its maximum select the same unique closest-to-equal split. The bipartite identical-row family already attains k/(k+1) for k>=2 and remains admissible in the larger class. Since k<=floor(n/2), the sharp finite formula follows.

This is an immediate extension of the existing signed-threshold proof, not a separate research campaign or a separate priority claim.

## Conventional quantitative corollary: complete balanced additive markets

Consider three equal sectors of m players and a complete additive array

  w_ijk=a_i+b_j+c_k>=0.

The coefficients themselves may be real: nonnegativity is required of the triple values. Let a0=min a, b0=min b, c0=min c, S=a0+b0+c0=min w>=0. Subtract each sector's minimum to obtain nonnegative sector baselines beta_s,i. Set B=sum beta_s,i. Every perfect matching has the same total T=B+mS; nonnegative values permit completion of any partial matching, so this is the integral optimum. Assume T>0.

Every triple belongs to an optimal perfect matching, so complementarity makes every triple inequality an equality at every core allocation. Differencing triples that differ in one player proves that the entire core is exactly

  p_s,i=beta_s,i+t_s, t_s>=0, t_A+t_B+t_C=S.

The converse follows immediately from triple equality and efficiency. This is the usual additive sector-shift core description; the quantitative conclusion below is a short corollary, not a claim to have newly discovered that core description.

If S=0 the core is a singleton. Otherwise each sector has a baseline-zero player, so the minimum core payoff is min_s t_s. Full leximin is uniquely t_A=t_B=t_C=S/3. For any other core allocation y,

  y_s,i<=beta_s,i+S<=3(beta_s,i+S/3)=3x_s,i.

Also the largest l1 distance between (S/3,S/3,S/3) and the shift simplex is4S/3, attained at its vertices. Hence for every y in the entire core,

  ||x-y||_1/T <= 4mS/(3T) <= 4/3.

This includes the full descending selector z. The existing calibration w_ijk=1+1{i distinguished}+1{j distinguished}, m>=2, has S=1, B=2 and full z at the shift vertex (0,0,1), giving rho=4m/[3(m+2)] and proving that4/3 is the sharp asymptotic bound within this additive class. The individual factor1/3 is sharp, for example in a constant positive triple-value market where a shift vertex gives one sector its full maximum.

No assertion here covers unequal sector sizes, general assortative arrays, b-matching, capacities greater than one, or broader network assignment models.

## Exact TU games and terminology

An exact TU game requires every coalition's lower core bound to be attained somewhere. This is distinct from exact rational computation and from using the entire core. Neither extremal family is an exact TU game: the pair family has a distinguished player's positive core minimum, and the triple family's root U players have core minimum1 despite singleton worth0. Therefore neither result contradicts the separate unrestricted exact-TU asymptotic theorem.

Exact bipartite assignment games have coincident selectors by the established halfsplit/majorization argument. The same conclusion extends immediately to exact graph matching games once the half guarantee above is available: exactness of singletons gives every player's core minimum0, so the matched partner's maximum equals the pair's total s_j. The half guarantee forces both leximin payoffs in the pair to be at least s_j/2, hence exactly s_j/2. This halfsplit is majorized by every vector with those fixed pair totals, so it is also the full descending minimum. This corollary needs only singleton exactness, not full exactness. Avoid presenting this routine deduction as a central new theorem.

## Interpretation and calibrated contribution

Half rho is the minimum fraction of total surplus that must change recipients between the allocations. Thus the graph bound approaches one-half of the surplus and the triple construction approaches all of it. All allocations remain efficient and core-feasible; this is a disagreement between egalitarian criteria, not a welfare loss or a proof that one rule is normatively unfair.

The mechanism is arity of binding constraints, not bipartiteness. Pair sums preserve signed-threshold transfers. At a tight triple, a feasible change proportional to (2,-1,-1) can have zero sum, while thresholding it to (1,-1,-1) produces a negative sum and violates the inequality. The explicit triple market realizes repeated versions of this obstruction through q_l=(J-I)q_(l-1), with root offsets fixing minimax and repeated top pairs carrying almost all surplus.

The triple arrays are deliberate gadgets. Equal sector sizes and bounded small integer values make the failure mathematically robust, but they do not establish prevalence in empirical matching markets. The core dimension is only3; the construction's depth and payoff propagation, rather than increasing core dimension or numerical precision, do the work. Dummy players count toward n and force exact complement identities; positive triples involving three nonfixed players are essential, so the construction is not merely a two-player market with decorative zeros.

The additive corollary supplies a clear protected three-sided class and prevents overstatement: three-way matching permits failure, but it does not force failure. Nonadditive value patterns are necessary to exceed4/3 within the complete balanced setting under consideration. Do not extrapolate this to every economically meaningful restricted class.

The minimal potentially nontrivial contribution is the quantitative link between full core selections: the graph half-maximum guarantee plus sharp finite distance, and the explicit bounded-value three-sided family with distance tending to the absolute maximum. If prior core-geometry or selector results imply these immediately, the novelty case shrinks accordingly. This audit verifies mathematics and framing, not priority; source agents are separately checking that question.
