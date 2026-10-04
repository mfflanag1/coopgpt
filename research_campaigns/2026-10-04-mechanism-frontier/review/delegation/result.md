**Result: an ownership-dependent rule with β = 1/(2e) ≈ 0.18394 < 1/2 on all weighted glove games, with H/2 floors (stronger than the required H/3).** This is a hand proof with two hand-computed spot profiles; nothing was machine-checked and no solver was used. No novelty is claimed.

## Rule ("truncated exponential pricing")

Contract as in CONTRACT.txt. Let A = c(L), B = c(R), T = min(A,B).

- If T = 0, set y ≡ 0.
- Otherwise truncate every owner: ĉ_k = min(c_k, T).
- Call a pool with total T "short" and the other "long". Short-pool owners are untruncated and sum to T.
- Let Ĉ be the truncated total of the long pool, ρ = Ĉ/T, and p = ½·e^{1−ρ}.
- Long-pool owners get y_i = p·ĉ_i. Short-pool owners get y_i = (1−p)·c_i.
- If A = B, then ρ = 1 and p = ½ under either labelling, so the rule is well defined.

The rule is ownership-dependent: Ĉ depends on how the long pool is partitioned, so a giant counts at most T. It is neither scalar Shapley nor a partition-invariant pool-total price.

## Theorem

For every finite L, R and every real c ≥ 0:

- (a) y ≥ 0 and y(S) ≥ v(S) for all S.
- (b) y_i is nondecreasing in c_i with the other reports fixed.
- (c) y_i ≥ M_i/2 ≥ H_i/2 ≥ H_i/3.
- (d) T ≤ Σy ≤ (1 + 1/(2e))·T.

The constant in (d) is attained by this rule at (1,1 | 1).

## Proof

**Fact 0: ρ ≥ 1 and 0 < p ≤ ½.** If some long owner has c_k ≥ T then Ĉ ≥ T. Otherwise Ĉ equals the long total, which is ≥ T.

**(a) Coverage.** For any set X in one pool, min(ĉ(X), T) = min(c(X), T): if some c_k ≥ T both sides equal T, otherwise ĉ = c on X. Since v(S) ≤ T, this gives v(S) = min(c(S_L), c(S_R), T) ≤ min(ĉ(S_L), ĉ(S_R)). Then y(S) = p·ĉ(S_long) + (1−p)·ĉ(S_short) ≥ min(ĉ(S_L), ĉ(S_R)) ≥ v(S). If T = 0, then v ≡ 0.

**(d) Budget.** Σy = (1−p)T + pρT = T(1 + u·e^{−u}/2) with u = ρ−1 ≥ 0. Since 0 ≤ u·e^{−u} ≤ 1/e, with the maximum at u = 1, the bound follows.

**(c) Floors.** H_i ≤ M_i := T − v(N∖i), because x_i = T − x(N∖i) ≤ T − v(N∖i) for every core x. Only this inequality is used; M is never substituted for H.

- Short owner: y_i = (1−p)c_i ≥ c_i/2 and M_i ≤ c_i.
- Long owner, say i ∈ L with A ≥ B = T > 0 and a_i = A − c_i: M_i = (B − a_i)_+.
  - If a_i ≥ B, then M_i = 0 and the floor is trivial.
  - If a_i < B, every other L-owner has c_k ≤ a_i < B and is untruncated, so Ĉ = a_i + ĉ_i. Also ĉ_i ≥ B − a_i = M_i, because c_i ≥ B − a_i and B ≥ M_i. Hence ρ − 1 = (ĉ_i − M_i)/B, and y_i = ½·e^{M_i/B}·(ĉ_i·e^{−ĉ_i/B}). The map t ↦ t·e^{−t/B} is nondecreasing on [0,B] and M_i ≤ ĉ_i ≤ B, so y_i ≥ M_i/2.

**(b) Monotonicity.** Fix i ∈ L with x = c_i, same-pool others totalling a, and R fixed with total B.

- If B = 0, then y_i ≡ 0.
- Long region (x + a ≥ B, B > 0): T = B is fixed and α = Σ_{k≠i} min(c_k, B) is fixed. With m = min(x, B), y_i = ½·e^{1−α/B}·m·e^{−m/B}. This is nondecreasing in m ∈ [0,B], and m is nondecreasing in x.
- Short region (0 < A = x + a ≤ B): y_i = x(1 − ½·e^{1−ρ}) with ρ(x) = Σ_{j∈R} min(c_j/A, 1).
  - y_i is continuous and C¹ except at the finitely many points where A = c_j.
  - On each smooth piece, ρ′ = −Σ_{j: c_j<A} c_j/A², so 0 ≥ ρ′ ≥ −ρ/A.
  - Then y_i′ = 1 − p + x·p·ρ′ ≥ 1 − p(1+ρ), using x ≤ A.
  - h(ρ) = ½(1+ρ)e^{1−ρ} has h(1) = 1 and h′ = −½·ρ·e^{1−ρ} < 0, so h ≤ 1 on ρ ≥ 1 and y_i′ ≥ 0.
  - Continuity plus a nonnegative derivative on finitely many pieces gives nondecreasing.
- Seam A = B: the short formula gives ρ = 1 and y_i = x/2. The long formula gives Ĉ = A = B (every c_k ≤ B), so ρ = 1 and y_i = x/2. The two closed regions agree, so y_i is monotone across the seam.
- Boundary A = 0 (x = a = 0): y_i = 0 ≤ any later value.

The same argument applies to R by symmetry. ∎

## Boundary and spot checks (hand arithmetic)

- **(1,1 | 1):** ρ = 2, y = (1/(2e), 1/(2e) | 1 − 1/(2e)). Each coalition {L_k, R} is paid exactly 1, and the total is 1 + 1/(2e), so the constant is tight for this rule.
- **(2,1 | 1,1):** ρ = 3/2, y ≈ (0.6065, 0.3033 | 0.6967, 0.6967). Coalitions {L₂, R₁} and {L₁, R₁, R₂} are tight.
- **Single giant (M | 1):** truncates to (1 | 1) and pays ½ each with no subsidy.
- **All-fringe long pool:** as ρ → ∞ the subsidy tends to 0.

## Limitations and unresolved items

- Whether 1/(2e) is optimal among arbitrary rules is open; the interval becomes [1/8, 1/(2e)] if this proof survives QA.
- The claim β = 1/(2e) is below the recorded 2+2-domain upper bound of 1/5 and should be cross-checked against that file's contract.
- Unproved heuristic: within prices of the form p(ρ) with p(1) = ½, long-region monotonicity seems to force p′ ≥ −p, which would make the exponential optimal in that family. I did not prove necessity.
- No lower bound above 1/8 was obtained. An uncertified side calculation on giant-plus-fringe profiles suggested that family alone may not force more than about 0.10, which is below 1/8.
- Only own-capacity underreports are covered; group deviations, overreports and cloning are not addressed, as in the contract.
- Suggested verification: an exact or interval check of (a)–(d) on a grid, including the non-smooth points A = c_j and the seam A = B.
