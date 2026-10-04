# Result: no constant mechanism found; one class-wide obstruction proved, two envelope failures, two reusable lemmas

**Status.** I did not find a constant-budget mechanism. The independent-threshold route is closed with a proved obstruction, the monotone-envelope route fails for two concrete base rules, and the unrestricted question stays open. Everything below is hand proof only: no computation was run, nothing was independently reviewed, and no literature search was done (no novelty claim).

**Setting.** Notation is as in `SCALING_THEOREM.txt`: fixed pools N_1..N_k, real c ≥ 0, T = min_j A_j, d_i = min(c_i,T), ρ_j = D_j/T, M_i = T − v(N∖i). All payments are 0 at T = 0. "Base" means the covering payment before the floor; the floor top-up max(·, M_i/k) costs at most T by Lemma B and preserves coverage and monotonicity, so it is ignored below.

## Lemma 1 (coverage as per-pool knapsack; reusable)

For y ≥ 0 and T > 0, let K_j(s) = min{ y(S_j) : S_j ⊆ N_j, c(S_j) ≥ s }. Then y covers every coalition if and only if Σ_j K_j(s) ≥ s for every s ∈ (0,T].

*Proof.* If v(S) = s > 0, each S∩N_j has capacity at least s, so y(S) ≥ Σ_j K_j(s) ≥ s. Conversely, the union of the minimisers has value at least s and costs Σ_j K_j(s). ∎

Coverage only; it says nothing about monotonicity.

## Lemma 2 (envelope reduction; reusable)

For any covering rule y⁰ ≥ 0, monotone or not, define y*_i(c) = sup_{0≤x≤c_i} y⁰_i(x, c_{-i}). Then y* covers, is nondecreasing in own report, and vanishes at T = 0 provided y⁰ ≤ T·const. So a monotone covering rule with budget (1+β)T exists if and only if some covering rule has envelope total at most (1+β)T at every profile.

*Proof.* y* ≥ y⁰ gives coverage; a sup over a growing set gives monotonicity; the converse takes y⁰ = y. ∎

This restates the target rather than solving it. Its value is that it turns candidate base rules into exact budget computations (Failures 1 and 2).

## Lemma 3 (generalised independent-threshold class: coverage and monotonicity)

Let U_i be i.i.d. uniform on [0,1], Z_j = (U_h d_h)_{h∈N_j}, and let Φ_j be any measurable, coordinatewise nondecreasing statistic (it may depend on label j and on k). Let W be the minimiser of Φ_j(Z_j), with ties broken by a fixed priority order, p_j = P(W = j), and y_i = d_i p_j. The existing rule is Φ_j = sum.

- **Coverage.** Σ_j p_j = 1, so y(S) = Σ_j p_j d(S∩N_j) ≥ min_j d(S∩N_j) = v(S), as in Theorem A.
- **Own-report monotonicity.** Fix i ∈ N_j, own-pool remainder a, least other pool total B > 0, report x, so T(x) = min(x+a, B).
  - The other own-pool coordinates U_h·min(c_h, T(x)) do not depend on x (Theorem A's argument).
  - Every other pool's coordinates are nondecreasing in x, hence so is each Φ_l(Z_l).
  - Conditional on U_{-i}, the set of z = U_i d_i for which j wins is a down-set with supremum s(x), nondecreasing in x (strict or weak comparisons by priority both give down-sets).
  - So the conditional payment is min(d_i(x), s(x)), nondecreasing in x; take expectations. ∎

## Theorem 4 (obstruction for the whole Lemma-3 class)

Let r ≥ 2 with k−1 ≥ 2r^r, and let every pool have at least r owners. For every family (Φ_j) as in Lemma 3 there is a profile with base total at least (1 + (r−1)(1−e^{-1})/2)·T. Hence every rule in the class, with or without the floor, has β ≥ 0.316(r−1) = Ω(log k / log log k).

*Proof.*
1. Use r designated owners per pool; all others report 0. Let V be uniform on Q = [0,1/r]^r and t_j = inf{t : P(Φ_j(V) ≤ t) ≥ 1/2}. Then P(Φ_j(V) ≤ t_j) ≥ 1/2 and P(Φ_j(V) ≥ t_j) ≥ 1/2.
2. Choose s maximising t_j; among maximisers, take the one with lowest tie-break priority.
3. Profile: pool s has r owners of capacity 1/r; every other pool has r owners of capacity 1. Then T = 1, d = c, ρ_s = 1, ρ_l = r.
4. Z_s is uniform on Q, so P(Φ_s(Z_s) ≥ t_s) ≥ 1/2.
5. For l ≠ s, Z_l is uniform on [0,1]^r, lies in Q with probability r^{-r}, and is uniform on Q given that. So q_l = P(Φ_l(Z_l) ≤ t_l) ≥ r^{-r}/2.
6. On {Φ_s(Z_s) ≥ t_s} ∩ {some l ≠ s has Φ_l(Z_l) ≤ t_l}, we have Φ_l ≤ t_l ≤ t_s ≤ Φ_s. Equality throughout forces t_l = t_s, and then l outranks s by step 2. So s does not win.
7. By independence across pools, 1 − p_s ≥ ½(1 − (1 − r^{-r}/2)^{k−1}) ≥ ½(1 − e^{-1}).
8. Base total = p_s + r(1 − p_s) = 1 + (r−1)(1 − p_s). ∎

**Consequences and scope.**
- With Theorem C, the sum statistic is order-optimal in this class. No choice of statistic (max, ℓ_q, order statistics, label- or k-dependent) reaches a constant.
- *Correlated randomness.* The pathwise step in Lemma 3 needs U_i uniform conditional on U_{-i} for every i. If each coordinate is independent of all the others, the joint law factorises by induction, so the U_i are i.i.d. This blocks correlated thresholds only within that proof template. A correlated rule that is monotone in expectation but not pathwise is not excluded.
- Not excluded: statistics that depend on d or T separately from Z, bounded owner counts (fewer than r per pool), and non-threshold rules.
- On the witness profile the pivotal rule y = M costs exactly T (pool s is tight, the other pools have M = 0). So Theorem 4 is not an unrestricted lower bound.

## Failure 1: envelope of the bottleneck core rule is the marginal vector

Take y⁰_i = c_i on the bottleneck pool (fixed tie-break) and 0 elsewhere. For i ∈ N_j, pool j is the bottleneck exactly when x + a ≤ B, so y*_i = min(c_i, (B−a)_+) = M_i (up to tie-break at x + a = B).

- Coverage and monotonicity hold by Lemma 2.
- Budget: Σ M_i ≤ kT by Lemma B, attained when every pool is tight (all A_j = T gives M_i = c_i).
- So β = k−1 exactly for this rule. It is good where the Banzhaf rule is bad and bad on tight profiles.

## Failure 2: envelope of exponential soft-min ratio prices

Take y⁰_i = d_i p_j with p_j ∝ exp(−λ(ρ_j−1)), any λ ≥ 0 (possibly depending on k). It covers because Σ p_j = 1. Suppose its envelope total is at most B·T everywhere.

- **Tight profile.** Each pool has two owners of capacity 1/2, T = 1. One owner lowers to x = 1/6: T' = 2/3, own ρ = 1, other pools have ρ = 3/2, so y⁰ = (1/6)/(1 + (k−1)e^{-λ/2}). Over 2k owners the envelope total is at least (k/3)/(1 + (k−1)e^{-λ/2}). Hence e^{-λ/2} ≥ (k/(3B) − 1)/(k−1), i.e. λ ≤ 2 ln(3B) + o(1).
- **Spread profile.** Pool 1 has one unit owner; the other pools have R unit owners each. With w = (k−1)e^{-λ(R−1)} the base total is (1 + Rw)/(1 + w). Taking R = ⌈1 + ln(k−1)/λ⌉ gives w ∈ (e^{-λ}, 1], so the total is at least R·e^{-λ}/2.
- Combining: B ≥ ln(k−1) / (18 B² · (2 ln 3B + o(1))), so B → ∞, crudely B = Ω((log k / log log k)^{1/3}).

This is an obstruction for this one-parameter family only. Sharp weights fail on tight profiles through the envelope; flat weights fail on spread profiles through the base cost.

## Precise remaining gap

**Open lemma (equivalent to the frozen target by Lemma 2).** Is there a constant C and a covering base rule y⁰ with Σ_i sup_{x≤c_i} y⁰_i(x, c_{-i}) ≤ C·T for all k, owner sets and c?

What a successful y⁰ must do, from the results above:
- By Theorem 4 it cannot be an independent-threshold winner rule.
- By Theorem E it cannot be capped-ratio-only.
- By Failures 1 and 2 it must behave like M on profiles such as (one tight pool, others at ρ = r), and like uniform 1/k prices on near-tight profiles such as ρ = (1, 3/2, …, 3/2).

I found no proof that these two requirements are incompatible. The profiles forcing each behaviour differ in which pool is concentrated, and a symmetric-profile chain argument fails because symmetric big-owner profiles have ρ ≤ 2.

Two mechanism failures plus one class-wide obstruction are recorded; under the contract's stop rule this side reports the gap, not a solution.
