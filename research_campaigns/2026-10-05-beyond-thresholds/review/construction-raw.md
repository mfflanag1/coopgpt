# Result: no constant-budget mechanism found; two partial results outside the blocked classes

The main question stays open. I did not obtain a constant-budget truthful covering mechanism. What I have is one explicit nonlinear rule that fails coverage (with an exact counterexample) and one new class obstruction with a proof. Everything below is hand derivation: nothing was executed, no files were written, and no literature search was done, so novelty is unassessed.

Notation: for owner i in pool j, a_i = C_j − c_i, B_j = least other pool total, e_j = (C_j − T)+, M_i = min(c_i, (B_j − a_i)+).

## 1. Pivotal-height sharing rule H: monotone and budget-bounded, but not covering

**Rule.** Let q_j = C_j − max_{i∈N_j} c_i and Q(h) = #{pools j' : q_j' ≤ h}. Pay

y_i = ∫ from a_i to min(C_j, B_j) of dh / Q(h), and 0 if a_i ≥ B_j.

Equivalently y_i = ∫_0^{M_i} du / (1 + #{j'≠j : q_j' ≤ a_i + u}). Each pivotal unit is split equally with every pool whose largest owner would also be pivotal at that height.

**How it escapes the old class.** Payments are not of the form d_i·P(pool wins). They are a nonlinear function of M_i, with a report-dependent statistic (q of the other pools) and no randomisation, so the conditional-independence proof plays no role.

**Own-monotonicity (proved).**
- The own pool is always counted, because q_j ≤ a_i ≤ h on the integration range.
- For j' ≠ j, q_j' does not depend on c_i, so the integrand is independent of c_i.
- The lower limit a_i is independent of c_i and the upper limit min(a_i + c_i, B_j) is nondecreasing in c_i.
- At T = 0 the range is empty, so all payments vanish.

**Budget (proved, non-constant, so PARTIAL).** The upper limit equals T for every pool, so Σy = ∫_0^T Σ_j n_j(h)/Q(h) dh, where n_j(h) = #{i ∈ N_j : c_i ≥ C_j − h}.
- n_j(h) = 0 unless pool j is counted, and n_j(h) ≤ min(m, T/(T−h)), giving Σy ≤ T(1 + ln m).
- ∫ n_j = Σ_i M_i ≤ T, and the pool of q-rank ρ has Q ≥ ρ, giving Σy ≤ T·H_k.
- So Σy ≤ T·min(1 + ln m, H_k), where m is the maximum owner count.
- The log is real: tight pools of 2^r owners of size T/2^r, with pool counts growing geometrically in r, cost about T(1 + #scales/2).

**Bounds on H.** M_i/k ≤ y_i ≤ M_i always. Hence H covers at every all-tight profile, where M = c.

**Coverage (FAILS; exact counterexample at k = 2).**
- Pool 1 = {1/2, 1/2}, pool 2 = {1, 1/4, 1/4}, so T = 1.
- Heights: both pool-1 owners and the big owner occupy [1/2, 1), where Q = 2, so each gets 1/4. The two small owners have a = 5/4 ≥ T and get 0.
- Coalition {one pool-1 owner, both small owners} has value 1/2 but is paid 1/4.
- With k−1 copies of pool 2 the shortfall factor is k.

**Why it fails.** Non-pivotal owners are free, so a pool that takes a share through one pivotal owner can be bypassed by the coalition.

**Two repairs I checked, both dead.**
- Counting a pool only once all its positive owners are pivotal restores equal treatment but costs about kT. Witness: one pool of R owners of 1/R, and k−1 pools {1−1/R, 1/R}.
- Weighting toward pools with the smallest n_j(h) is still monotone (the weight is nonincreasing in own n_j, and n_j is nonincreasing in c_i), but it has the same free-rider failure.

**What does hold.** H reproduces the payments I derived by hand as covering at exact cost T, under equal treatment of like owners, on three tie-adjacent families:
- the softmax-barrier profile (two half-owners per pool, one lowered to 1/6), where every coalition is paid at least its value and Σy = 2/3 = T;
- the profile with h owners of size 2 per pool and one owner lowered to 1;
- all-single-owner pools.

**Falsifiable claim from the counterexample (argued by hand on one profile, not a full proof).** A constant rule must sometimes pay owners with M_i = 0.
- Take pool 1 = {1/2, 1/2} and pools 2..k = {1, 1/4, 1/4}; lower one big owner to 1/4.
- If that owner's payment is O(1/k), as a constant budget forces for some pool via its envelope, then each coalition {lowered owner, one pool-1 half, one small owner per other pool} of value 1/4 must be covered either by the halves (about 1/4 each) or by the non-pivotal small owners.
- So the open design question is how to pay non-pivotal owners without the linear d_i·w_j softmax cost.

## 2. New class obstruction: report-independent random-order values

**Class.** Fix any report-independent distribution μ over arrival orders of owner slots and a scale λ ≥ 1. Pay y_i = λ·E_μ[v(Pred_i ∪ i) − v(Pred_i)]. Shapley is one member, and arbitrary cross-pool correlation of orders is allowed.

**Not in the threshold class.** Payments are expected marginal contributions, which are nonlinear in the owner's capacity, and the coupling is arbitrary.

**Monotonicity, budget (proved).** The marginal min(x + a, B) − min(a, B) is nondecreasing in x, so payments are nonnegative and own-monotone. The budget is exactly λT by telescoping. Payments vanish at T = 0.

**Lemma (coverage forces λ to grow).** Let Λ = ⌈λ⌉, p = (16Λ)^(−2Λ), G = ⌈ln(8Λ)/p⌉. If every pool has at least 32Λ² slots and k > 4ΛG, the rule fails coverage at some profile. Hence λ = Ω(log k / log log k) for the whole class.

**Proof.**
1. Set L = 2Λ, g = 8Λ, n = 2Lg designated slots per pool. Pool s gets one unit owner in a uniformly random slot; every other pool gets a uniformly random L-subset of unit owners. So T = 1.
2. Let S be the pool-s owner plus one uniformly random unit owner from each other pool, so v(S) = 1. In any order v jumps once, at the first unit owner of the last pool to be completed. So E[φ(S)] ≤ P_s + 1/L, where P_s = P(pool s completes last).
3. Coverage for every realisation needs avg_s P_s ≥ 1/λ − 1/L ≥ 1/(2Λ).
4. Fix an order π. Let b_j be the position of the first of pool j's last n/g designated slots. Then P(X_s ≥ b_s) = 1/g, and for an L-pool P(first unit ≥ b_j) = C(n/g, L)/C(n, L) ≥ (1/(2g))^L = p.
5. Given π, pools are independent because the placements are. For any s with at least G pools of larger b, P(s last) ≤ 1/g + (1 − p)^G.
6. Averaging: avg_s P_s ≤ G/k + 1/(8Λ) + 1/(8Λ) < 1/(2Λ) when k > 4ΛG. This contradicts step 3.

Symmetrisation over slot labels is done by the adversary's random placement, so the order distribution need not be exchangeable.

**Scope.** This is a class bound, not an unrestricted one: M costs T on the witness.

**Sign lemma for report-dependent orders (sufficient condition only).** A realised marginal stays own-monotone if raising c_i moves other-pool owners weakly earlier and pool-mates weakly later relative to i, because the marginal is nondecreasing in B and nonincreasing in a. Pool-level priority rules satisfying this put abundant pools late, which is the anti-coverage direction. I did not prove that every monotone report-dependent order rule fails.

## Limitations and open questions

- No valid mechanism came out of this work; H is not one. If a covering repair of H kept its budget, O(log m) would improve on the bounded-owner factor m, but no such repair exists yet.
- The H budget bound is non-constant and is worse in k than the existing O(log k / log log k) rule.
- Unresolved: whether constant-budget rules that pay only pivotal owners exist; whether some payment to non-pivotal owners that is consistent along own-coordinates rescues height sharing; whether report-dependent order distributions beyond the sign lemma help.
- The proofs in sections 1 and 2 need independent review and exact finite checks before promotion.
