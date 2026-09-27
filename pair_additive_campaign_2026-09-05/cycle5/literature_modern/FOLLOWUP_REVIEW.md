# Followup: 2026 core extrema and the fixed-size certificate bound

6 September 2026, direct source retrieval completed by 12:48 UTC. No additional search queries were run. Root files were read only.

## The distinct 2026 extrema paper

This source was **not** the 2026 fixed-order many-to-one salary paper in the modern report. F. Javier Martínez-de-Albéniz, Carlos Rafels and Neus Ybern, *Maximum and minimum core payoffs for supermodular multisided assignment markets with local monotonicity*, Discrete Applied Mathematics 379 (2026), 605–612, [DOI10.1016/j.dam.2025.10.006](https://doi.org/10.1016/j.dam.2025.10.006), is available as a [full institutional original](https://diposit.ub.edu/server/api/core/bitstreams/82079683-149e-4510-a3a4-5cc1e1c57c65/content). The PDF records acceptance on 1 October 2025. The local downloaded PDF has SHA-256 `12a529ca63f3daf389ad6c7e12a38610e4ba93cba3dfad7d9678cba20125b4ac`.

It treats strict, equal-size multisided markets, with product-order supermodularity (1) and local monotonicity (4), p.607. Theorem 3.1, p.608, constructs a core point. Theorem 3.2, p.609, gives the **whole-core** coordinate maxima/minima and simultaneous within-side attainment: one point attains all maxima of a chosen side, and a possibly different point attains its minima. These are genuine H-type results, not marginal-utopia bounds. The theorem does not identify full sorted leximin.

Its proof bounds every consecutive within-side payoff difference below by a local array increment, which condition (4) makes nonnegative. Thus every core allocation respects one common order within each sector. This yields a direct exclusion test, stronger than checking one inconvenient original ordering.

For the canonical cycle4 market, its verified first-face witness has `(a_0,a_3)=(4/3,1/3)`, while its verified ideal witness has `(a_0,a_3)=(2,3)`. Their differences are respectively `+1` and `-1`. No ordering of those same first-sector players can satisfy the common-order property on the entire core. Hence the actual array cannot lie in this supermodular/local-monotonicity class after within-sector relabeling, and neither can an identical labeled payoff-core representation that preserves their sector membership. This is a structural exclusion, not a novelty certificate or an exclusion of arbitrary transformed/auxiliary representations. It does not assert that every market in the source class has a particular leximin ideal ratio.

The web tool returned a cache miss and then a server error on the institutional URL variants. A subsequent authorized direct HTTP retrieval returned status200 and the full PDF; the source is therefore inspected, not an unresolved access gap. The relevant read covers model definitions, assumptions, Theorems3.1–3.2 and the payoff-difference portion of their proof. Extracted text is saved beside the PDF.

## Independent audit of the fixed-size bound

Reviewed [root/FIXED_SIZE_CERTIFICATE_BOUND.md](../root/FIXED_SIZE_CERTIFICATE_BOUND.md), lines5–39. **No mathematical gap found.** Under its explicit hypotheses the conclusion

    H_i/tau <= n * 3^((n-1)/2)

is valid. The proof does not use pair additivity, rational weights, or strict complementarity.

- **Residual optimum, lines13–17.** A first-floor core point gives value `L=T-n*tau`. Summing a residual cover over an optimal integral matching gives the lower bound. Even if the definition permits unmatched players, positive first floor and core efficiency force every optimal matching to cover all players: an unmatched positive payoff would make the total exceed the matching value. Every residual optimum therefore corresponds exactly to the first face.
- **Auxiliary dual, lines17–22.** For maximizing `q_i` with `Eq>=r`, `q>=0`, and `1.q=L`, the displayed dual is correct: `mu*1-E^T alpha>=e_i`, `alpha>=0`, `mu` free, objective `mu L-alpha.r`. Its attained optimum is zero. The target constraint gives `mu>=1`, so division is legitimate. With `lambda=alpha/mu`, residual feasibility and objective equality hold, and the target deficit satisfies `d_i>=1/mu>0`. This is an ordinary strong-duality argument.
- **Optimal vertex, lines24–30.** Every edge variable is bounded by one, since each triple has incident players. The feasible polytope is compact; decomposing an optimal point with positive target deficit produces an optimal vertex with that property. Its positive support has full column rank on its tight load rows, by the stated two-sided perturbation argument. The target row is slack, so support size is at most `n-1`. Cramer's rule and the column norm bound `sqrt(3)` give the claimed positive-deficit denominator bound, including the empty-support case.
- **Identity and conclusion, lines32–37.** The left side of the displayed identity expands to `T-lambda.w`. Residual optimality gives `lambda.w=T-tau*(n-3 sum(lambda))`; triple incidence gives `sum(d)=n-3 sum(lambda)`. Hence the identity is exact. Every summand is nonnegative at every full-core point, and maximizing its target coordinate proves `H_i<=tau*sum(d)/d_i`, followed by the stated determinant bound.

The zero residual-total case `L=0` causes no failure: the auxiliary dual still has a feasible optimum with `mu>=1`, and an empty support can be treated with determinant one. The bound is valid for arbitrary real nonnegative team values because the rational denominator step concerns vertices of the fixed zero-one incidence polytope, not the objective coefficients.

The implication is exactly the stated one: a vanishing-ratio family whose targets are fixed at a positive first global level must have unbounded player count. It does not bound later leximin levels, establish a size-independent constant, or preclude growing-size constructions with bounded entries. The observation is an application of classical LP duality and determinant bounds; this audit supplies a conventional proof check, not formal proof certification or a methodological priority claim.

## New vanishing-family candidate: independent supermodularity exclusion

The later candidate family is a separate market from cycle4. Its claimed target ratio is `1/[3(q+1)]`; the all-parameter core and selector proof is being audited by other workers. I do not transfer cycle4's payoff-order reversal to this new family. The following independent test uses its pair matrix directly.

**Lemma.** A nonnegative matrix with an all-zero row and three nonzero rows having pairwise disjoint supports cannot become supermodular under any row and column permutations.

Proof. Suppose rows and columns have been ordered so that increasing differences hold:

    A_ij + A_i'j' >= A_ij' + A_i'j  whenever i<i' and j<j'.

Let z be an all-zero row. For a row r above z, this inequality says `A_rj>=A_rj'` when `j<j'`; that row is nonincreasing. Because it is nonnegative, its nonempty positive support is an initial segment of the columns. A row r below z is nondecreasing, with terminal-segment support. Of three nonzero rows, two lie on the same side of z. Two nonempty initial segments intersect, as do two nonempty terminal segments, contradicting disjointness. The opposite Monge sign convention swaps the two segment types and leaves the contradiction unchanged.

In the specified family, each output row `O_s` of A has value2 exactly in columns `{O_s,R_s}`, with these two-element supports disjoint for distinct s. There is an all-zero L row. Thus the lemma applies for every `q>=3`.

For the full tensor `w_ijk=A_ij+B_ik+C_jk`, fix k and take a mixed difference in i,j. The B and C terms cancel, leaving exactly the corresponding mixed difference of A. Consequently supermodularity of the full tensor in any within-sector orders would imply supermodularity of A in those row/column orders, which the lemma forbids. This argument is also unaffected by a different pair decomposition of the same tensor: the relevant mixed differences are intrinsic.

Therefore the actual family for `q>=3` lies outside both the 2020 assortative supermodular class and the 2026 supermodular/local-monotonicity class under **every within-sector relabeling**. The obstruction already concerns supermodularity; no monotonicity or selector premise is needed. No exclusion is asserted here for q=1 or q=2, nor for arbitrary transformed payoff-core representations.

**Priority implication.** Those two sources do not directly cover this family by their stated array hypotheses. The result, if its independent mathematical audit succeeds, should be framed as vanishing ideal protection in a fixed three-sector complete nonnegative pair-additive class. It does not introduce vanishing protection across combinatorial games in general, as the earlier flow-path example already gives that phenomenon. This structural exclusion does not resolve the distinct unread 2023 SSRN4369524 general extreme-core paper, exclude alternate earlier constructions, or certify novelty.
