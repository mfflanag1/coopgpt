# Stage-scaling: an O(log k) all-profile mechanism, with constant-B still open

I did not settle whether a constant B exists. What I have is a hand-proved rule with β ≤ 1 + (1+√e)(2 ln k + 2), independent of owner counts, plus two exact obstructions and one small unrestricted lower bound. Nothing was run numerically, no files were changed, and I used only the three supplied files; no novelty is claimed.

## Notation

- A_j is the total of pool j, T = min_j A_j, and d_i = min(c_i, T).
- D_j = Σ_{i∈N_j} d_i, ρ_j = D_j/T ≥ 1, u_j = ρ_j − 1.
- M_i = T − v(N∖i), so H_i ≤ M_i (as in both existing proofs).
- A pool s with A_s = T has all c_i ≤ T, hence D_s = T and u_s = 0.

## Lemma A: capping preserves v for k pools

Claim: v(S) = min_j d(S∩N_j) for every S.

Proof. For X ⊆ N_j, min(c(X),T) = min(d(X),T): if some c_i ≥ T in X both sides are T, otherwise nothing is capped. Also v(S) ≤ c(S∩N_s) ≤ T. So v(S) = min_j min(c(S_j),T) = min_j min(d(S_j),T) = min_j d(S_j), the last step because d(S_s) ≤ T. ∎

Consequence: any rule y_i = p_j·d_i with p ≥ 0 and Σ_j p_j ≥ 1 covers every coalition.

## Lemma B: the H/k floor costs at most +1 in β

Let z_i = M_i/k.

- **Monotone:** v(N∖i) does not depend on c_i and T is nondecreasing in c_i, so z_i is nondecreasing in c_i.
- **Floor:** z_i ≥ H_i/k.
- **Bounded:** Σ_i z_i ≤ T. In pool j put δ = A_j − T ≥ 0. Then M_i = (c_i − δ)_+ (if A_j − c_i ≥ T then v(N∖i) = T; otherwise v(N∖i) = A_j − c_i because the other pools are ≥ T). If r ≥ 1 owners have c_i > δ, the sum is ≤ A_j − rδ ≤ T. So Σ_{i∈N_j} M_i ≤ T and Σ_i M_i ≤ kT.

Hence for any covering, own-monotone, nonnegative rule y, the rule max(y_i, M_i/k) is covering, monotone, floor-respecting, and its total is at most y(N) + T. The scaling question therefore reduces to coverage plus monotonicity alone, up to an additive 1. ∎

## Theorem: random-owner-threshold rule Θ

**Rule.** If T = 0, pay y = 0. If T > 0, let (θ_i) be i.i.d. U[0,1]. These are an analysis device only; the payments are deterministic expectations. Define

- X_j = Σ_{i∈N_j} θ_i d_i,
- p_j = P(X_j < X_l for all l ≠ j),
- y_i = max(p_j d_i, M_i/k) for i ∈ N_j.

**Claim.** For all k ≥ 2, all finite ownership structures and all real c ≥ 0:

- (a) y ≥ 0 and y(S) ≥ v(S) for every S;
- (b) y_i is nondecreasing in c_i;
- (c) y_i ≥ H_i/k;
- (d) Σ_i y_i ≤ (2 + (1+√e)(2 ln k + 2))·T.

**Well-definedness.** If T > 0, every pool has some d_i > 0, so each X_l has a density. Ties have probability 0 and Σ_j p_j = 1.

**Proof of (a).** Lemma A with Σ p_j = 1, and the max only raises payments. At T = 0 every coalition value is 0.

**Proof of (c).** Lemma B. At T = 0 the core is {0}.

**Proof of (b).** By Lemma B it suffices to show p_j d_i is monotone. Fix i ∈ N_j with report x. Let a = c(N_j∖i) and B = min_{l≠j} A_l, so T(x) = min(x+a, B).

- If B = 0, the payment is 0 for all x.
- If B > 0 and x + a = 0, the payment is 0, which is ≤ every later payment.
- Otherwise T(x) > 0. Put d_i(x) = min(x, T(x)) = min(x, B), R = Σ_{i'∈N_j∖i} θ_{i'} min(c_{i'}, T(x)), and Y(x) = min_{l≠j} Σ_{i'∈N_l} θ_{i'} min(c_{i'}, T(x)).
  - R does not depend on x. If a ≤ B, each c_{i'} ≤ a ≤ T(x), so R = Σ θ_{i'} c_{i'}. If a > B, T(x) ≡ B.
  - Conditioning on θ_{−i}: d·P(θ_i d < Y − R) = min(d, (Y−R)_+). So p_j d_i = E[min(d_i(x), (Y(x) − R)_+)].
  - d_i(x) is nondecreasing, and Y(x) is pointwise nondecreasing because T(x) is. So the integrand is pointwise nondecreasing in x.

This single formula covers the short region, the long region, the seam x + a = B, the cap kink x = B, ties and zero reports. ∎

**Proof of (d).** Σ p_j D_j = T(1 + Σ_j p_j u_j). Let L = 2 ln k + 2, so 1 + L ≥ 3.

- Pools with u_j ≤ L contribute at most L·Σ p_j ≤ L.
- For a pool with ρ = ρ_j > 1 + L: p_j ≤ P(X_j < X_s) ≤ P(X_j ≤ T). Here E X_j = ρT/2 and X_j is a sum of independent variables in [0, d_i] with Σ d_i² ≤ T·ρT. Hoeffding gives p_j ≤ exp(−(ρ−2)²/(2ρ)) ≤ e^{2−ρ/2}.
- (ρ−1)e^{−ρ/2} is decreasing for ρ ≥ 3, so u_j p_j ≤ e²·L·e^{−(1+L)/2} = √e·L/k.
- There are at most k−1 such pools, so Σ p_j u_j ≤ (1+√e)L.

Add T for the floor top-up (Lemma B). ∎

**Limits of the theorem.**

- The constants are crude. The bound beats the baseline (k−1)/2 only for large k (roughly k in the mid-60s or above, by my hand estimate). For k = 3 it gives nothing better than the existing β ≤ 1.
- A tight three-pool constant for Θ is not derived; that step is missing.

## Exact witnesses about Θ

**Θ without the top-up violates H/3.** Take (1 | 1 | ½,½). Then p_3 = E[(1−Z)²] with Z = (θ+θ')/2, which equals 1/4 + 1/24 = 7/24. Each pool-3 owner gets 7/48, but H_i/3 = 1/6 = 8/48. So Lemma B is load-bearing.

**Θ is not uniformly bounded.** Take pool 1 = (1) and pools 2..k each with r owners of capacity 1. Then:

- p_1 = ∫₀¹ (1 − u^r/r!)^{k−1} du (Irwin–Hall on [0,1]);
- subsidy/T = (r−1)(1 − p_1), which tends to r−1 as k → ∞;
- for r = 2, k = 3: p_1 = 43/60 and the subsidy is 17/60.

So sup β_Θ is unbounded in k (heuristically at least of order log k / log log k), and Θ does not give a constant B.

## No-go for the direct k-extension of the exponential theorem

**Class.** y_i = p_j(ρ_1,…,ρ_k)·d_i, where prices depend only on capped ratios; pool labels are allowed. Assume k is a perfect square and each pool has n owners with √k dividing n.

**Claim.** Any such rule that is covering and own-monotone has 1 + β ≥ √k/2. No floors are used.

**Proof.**

1. At the all-(1/n) profile, ρ = (1,…,1) =: 𝟙. One owner per pool gives a coalition of value 1/n, so Σ_j p_j(𝟙) ≥ 1. The total is Σ_j p_j(𝟙) ≤ 1 + β. Pick j with p_j(𝟙) ≤ (1+β)/k.
2. Let pool j be (x, 0, …, 0) and all other pools be n owners of 1/n, with x = q/n ≤ 1. Then T = x, ρ_j = 1 and ρ_l = 1/x.
3. At x = 1 the ratio vector is again 𝟙, so own-monotonicity gives x·p_j(x) ≤ p_j(𝟙) ≤ (1+β)/k.
4. The coalition of s plus q owners per other pool has value x and is paid x·Σp, so Σ p ≥ 1.
5. The total is x p_j + Σ_{l≠j} p_l ≥ 1 − (1−x)p_j, and it is ≤ (1+β)x.
6. Hence (1+β)(x + (1−x)/(kx)) ≥ 1. Taking x = 1/√k gives 1 + β ≥ √k/2. ∎

**Load-bearing obstruction.** At an all-tied profile the price must distinguish a pool with one big owner from a pool of small owners. Capped ratios cannot see this, so softmax or exponential weights in u_j fail. Θ escapes because its prices depend on the within-pool distribution of the d_i.

## Unrestricted lower bound (uses floors): β ≥ 1/3 − 2/(3k)

Ownership is (1, 2, …, 2): pool 1 has a single owner s, and every other owner has capacity ½.

1. At c_s = ½, T = ½. Let e_j be the cheaper owner in pool j. The coalition {s, e_2, …, e_k} has value ½, so the total is ≥ y_s + 2(½ − y_s) = 1 − y_s. The total is ≤ (1+β)/2, so y_s ≥ (1−β)/2.
2. Raise c_s to 1. Then T = 1 and, by monotonicity, y_s ≥ (1−β)/2.
3. Each other owner has H_i = ½ (the pool-j cut payoff is in the core, and M_i = ½). The floors sum to (k−1)/k.
4. So (1−β)/2 + 1 − 1/k ≤ 1 + β, which gives β ≥ 1/3 − 2/(3k). ∎

This is 1/9 at k = 3, weaker than the 1/8 quoted in the contract — and I did not show that 1/8 transfers to three pools. It is 1/6 at k = 4 and tends to 1/3. It is a constant, not growth.

## Unresolved, explicitly

- **Constant B.** Existence is open. I found no growing unrestricted lower bound.
- **Why my lower-bound attempts stall.** A "big" owner's payment is forced only through its own short history. With several pools each holding a big owner, coverage forces only sums of their payments. For example, at pool 1 = (x, 1) and the others (1, 1), the payoff a_1 = 0, b_1 = 1 − x, others 2x in total covers every coalition with zero subsidy.
- **True order of β_Θ.** It lies between unbounded (about log k / log log k, heuristic) and O(log k), and is conjectured to be closer to the lower end. A Bernstein or Irwin–Hall tail bound in place of Hoeffding is not done.
- **Design freedom.** The proof of (b) works for any coordinatewise-increasing continuous aggregator X_j = Φ(θ_i d_i). Whether some Φ gives constant B is untested.
- **Two-pool aside (conjecture only).** For k = 2, sample profiles of Θ give 1/6, 4/27 and 1/8, all below 1/(2e); Θ happens to satisfy H/2 for k = 2. No proof of a two-pool supremum was attempted.
- **Verification.** Everything here is a conventional hand proof and needs coordinator and opposite-model checking, especially the Hoeffding step and the constancy of R in (b).
