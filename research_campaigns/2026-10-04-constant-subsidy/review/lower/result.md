**Verdict: unresolved.** I found no divergent unrestricted lower-bound family. I did get one new obstruction theorem and two supporting lemmas that pin down what any divergent family must look like. All of it is pen-and-paper derivation from the two supplied files; nothing was computed, and no files were written.

Notation: pool j has total C_j and m_j owners, T = min_j C_j, m = max_j m_j, and j(i) is the pool of owner i.

## Theorem A (obstruction): bounded owners per pool gives bounded subsidy for every k

For k ≥ 2 define D_j(c) = min_{l≠j} C_l and the rule

  y_i(c) = min(c_i, D_{j(i)}(c)) / k.

For all real c ≥ 0 and every ownership partition:

1. **Nonnegative and own-monotone.** D_{j(i)} depends only on other pools, so y_i is nondecreasing in c_i.
2. **Covers every coalition S.** For each pool l, Σ_{i∈S_l} min(c_i, D_l) ≥ min(c(S_l), D_l): if some c_i ≥ D_l the sum is at least D_l, otherwise it equals c(S_l). Since v(S) ≤ c(S_l) and v(S) ≤ T ≤ D_l, each pool's capped sum is at least v(S). Averaging over the k pools gives y(S) ≥ v(S).
3. **Budget.** A non-min pool l has D_l = T, so it contributes at most min(C_l, m_l·T). A min pool contributes at most C_l = T, and there is at least one. Hence
  Σ_i y_i ≤ (T/k)·[1 + Σ_{l non-min} min(C_l/T, m_l)] ≤ T·(1 + (k−1)m)/k,
  so **β ≤ (k−1)(m−1)/k < m−1**.
4. **T = 0 gives all payments zero.** Non-min pools have D_l = 0; min pools have every c_i = 0.

Consequences for the lower-bound side:

- **Two owners per pool:** β ≤ (k−1)/k < 1 for all k and all real profiles. So no two-owner family, with any number of levels or deviations, can prove β ≥ 1. Combined with the existing family, the two-owner uniform constant lies in [1/2, 1].
- **Any divergent family** must have unbounded effective owner count n_l = Σ_{i∈N_l} min(c_i, T)/T, averaged over non-min pools. Growth in k alone cannot do it; if the frontier's O(log k / log log k) rule holds, both k and m must grow.
- **Floor caveat:** the contract does not define H_i, so the H_i/k floor is not verified. If H_i ≤ c_i on min pools and 0 elsewhere (my assumption, the maximum core payoff), the floor holds, since min-pool owners have c_i ≤ T ≤ D_j and so y_i = c_i/k.

## Lemma B: single-profile individual bounds are vacuous once β is large

Fix a profile, an owner i, and a pool l ≠ j(i). The allocation y_u = min(c_u, T) for u in N_l, zero elsewhere, covers every coalition (same argument as step 2) and costs n_l·T with y_i = 0.

So if 1+β ≥ min_{l≠j(i)} n_l, no set of inequalities from that one profile can force y_i > 0. In particular, the "a ≥ 1−2β, A ≥ 1/2−β" style of step in Families I and II dies at β < 1 with two owners. A generalised profile X with m owners per pool gives only a ≥ 1 − βm/(m−1), which is vacuous at β ≥ 1 − 1/m.

## Lemma C: exact dual form for any multi-profile family

Take any finite profile set, weights μ_P ≥ 0, and nonnegative flows f on pairs (P_low, P_high) that differ only in owner i's report. Set a_i(P) = μ_P + outflow_i(P) − inflow_i(P), required to be ≥ 0. This is μ with mass moved downward along each owner's own coordinate, separately per owner. Let W_P(a) = min{Σ_i a_i·y_i : y ≥ 0 covers all coalitions at P}.

For every feasible rule,

  Σ_P W_P(a(P)) ≤ Σ_P Σ_i a_i(P)·y_i(P) = Σ_P μ_P·y(N;P) + Σ f·(y_i(low) − y_i(high)) ≤ (1+β)·Σ_P μ_P·T_P.

So 1+β ≥ ΣW / ΣμT. This uses only coverage, budget and own-coordinate monotonicity. On finite grids, LP duality makes it the complete set of certificates; Families I and II are instances.

## Attempted divergent family and why it fails (heuristic, not a theorem)

I tried one-step certificates: L-profiles receive weight on a set R, and H-profiles donate from surplus owners Z.

- The gain at L is at most μ_L·T_L·κ_L, where κ_L = (cheapest cover with y_R = 0)/T_L − 1.
- By Lemma B, κ_L ≤ min_{l≠j} n_l − 1.
- A large gain therefore needs every other pool to hold at least (1+κ)·T_L of T_L-capped capacity.
- Each donor u at H must, by lowering alone, make its own pool the min, so C_{j(u)} − c_u < T_{L_u}.
- Two donors in different pools then need T_{L_u'} > κ·T_{L_u} and the reverse, which is contradictory for κ ≥ 1.
- Donors in the same pool make that pool the min at H, so zeroing them destroys W_H.

So the "many pools, one giant each, small owners elsewhere" generalisations of X, Y, Z stay at κ ≈ 1. I checked this for the natural giant-plus-smalls family but did not prove it for all one-step certificates. Multi-step chains, where H-profiles themselves receive from higher profiles, were not analysed.

## What remains open

- No lower bound above 1/2 was obtained. No ω(1) family and no constant upper bound for unbounded m.
- The precise open target: either a multi-step Lemma C certificate with n_l → ∞ and ratio → ∞, or a monotone rule that removes the m-dependence of Theorem A.
- Theorem A and Lemmas B and C need independent review. Novelty against the literature was not checked; no web sources were consulted.
