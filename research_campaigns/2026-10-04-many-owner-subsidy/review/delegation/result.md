**Result: the 5/6 factor fails for larger owner counts, and the best dimension-independent Shapley coalition factor is exactly 1/2.** Both halves are proved below by hand; I had no code-execution tool, so every number is a hand derivation awaiting exact verification.

Notation: z_i = +c_i for i in R, −c_i for i in L; Z(U) = Σ_{i∈U} z_i; D = Z(N). Then v(U) = (c(U) − |Z(U)|)/2. By pool symmetry assume D ≥ 0 (L is the weakly short pool). M_i = T − v(N∖i).

## 1. Exact rational counterexample to 5/6 (5 owners)

Profile L = {l: 2}, R = {r: 2, q1: 1, q2: 1, q3: 1}, S = {l, r}, so v(S) = T = 2.

- **φ_l:** l is a veto owner with marginal min(2, R-capacity before l). The predecessor count k is uniform on 0..4. The conditional means are 0 for k=0, 5/4 for k=1, and 2 for k=2,3,4. So φ_l = (5/4 + 6)/5 = 29/20.
- **φ_r:** the marginal is 2 if the predecessor set is {l} (k=1, probability 1/4), 1 if it is {l, one unit} (k=2, probability 1/2), and 0 otherwise. So φ_r = (1/2 + 1/2)/5 = 1/5.
- **Ratio:** φ(S) = 33/20, so φ(S)/v(S) = 33/40 < 5/6, and (6/5)φ(S) = 99/50 < 2. The 6/5 mechanism fails coverage here.

Family: for (L = {l: m} | R = {r: m, n unit owners}) with m ≤ n, φ(S)/v(S) = 1 − (m+1)(3n−2m+2)/(6(n+1)(n+2)). At n=4k, m=3k this decreases to 13/16. No ownership cloning is used; these are distinct fixed owners.

## 2. Lemma A (all profiles, all owner counts): φ_i ≥ M_i/2 ≥ H_i/2

For i ∉ U, the marginal is Δ_i(U) = (c_i + |Z(U)| − |Z(U)+z_i|)/2.

Pair each predecessor set P with its complement P' = N∖i∖P; this is order reversal and preserves the Shapley weights. Here Z(P') = D − z_i − Z(P). With d = Z(P):

Δ_i(P) + Δ_i(P') = c_i + ½[ψ(d) − ψ(d+z_i)], where ψ(x) = |x| − |D−x| = clamp(2x−D, −D, D).

ψ is nondecreasing, 2-Lipschitz, and has oscillation 2D.

- **i in L (z_i ≤ 0):** the bracket is ≥ 0, so the paired sum is ≥ c_i = M_i.
- **i in R:** the bracket is ≥ −2·min(c_i, D), so the paired sum is ≥ (c_i − D)^+ = M_i.

Hence φ_i ≥ M_i/2. For any x in the original efficient core, x_i = T − x(N∖i) ≤ T − v(N∖i) = M_i, so H_i ≤ M_i and φ_i ≥ H_i/2. H is never replaced by M in the definition.

This is sharp at (1|1): H_i = 1, φ_i = 1/2. No division or positivity is used; ties (D=0) and zero capacities are covered; at T=0 everything is 0.

## 3. Lemma B (all profiles): φ(S) ≥ v(S)/2 for every coalition

Summing Lemma A over S gives φ(S) ≥ ½[L(S) + Σ_{i∈S∩R}(c_i − D)^+] ≥ ½L(S) ≥ ½v(S).

## 4. Sharpness of 1/2: asymptotic family, proved

Profile: L = n unit owners; R = {r: capacity n} plus m unit owners q. S = L ∪ {r}, so v(S) = T = n and φ(S) = n − Σφ_q.

- Each q has marginal 1 exactly when r is not before it and (#L before) > (#other q before); otherwise 0.
- With i.i.d. uniform arrival times, φ_q = ∫₀¹ (1−t)·P(Bin(n,t) > Bin(m−1,t)) dt.
- By Chebyshev, P(A − B ≤ 0) ≤ 2nt/((n−m+1)t)² = K/t, with K = 2n/(n−m+1)².
- So φ_q ≥ 1/2 − K(1 + ln(1/K)).
- Take m = n − ⌈n^{3/4}⌉, so K ≤ 2n^{−1/2} → 0. Then φ(S)/v(S) ≤ 1 − (m/n)(1/2 − o(1)) → 1/2.
- Lemma B gives the matching lower bound 1 − m/(2n).

Exact small checks: (1,1|2,1) gives 7/8, consistent with the 2+2 theorem; (1,1,1|3,1,1) gives exactly 5/6.

**Named obstruction — long-side fringe dilution.** Shapley pays a zero-core long-side fringe (H_q = 0) about half its capacity whenever a long-side atom is in S. The coalition "short pool + atom" therefore loses about m/2.

**Consequence.** A constant multiple μφ covers all coalitions for all owner counts if and only if μ ≥ 2. That gives budget 2T, i.e. β = 1, which is worse than the aggregate-price baseline of 1/2. Scaled individual Shapley cannot deliver any dimension-independent β < 1.

## 5. Side lemma (pairs only, proved)

For a cross pair S = {l, r} with any capacities and any other owners, φ(S) ≥ (3/4)v(S).

Proof sketch: normalize c_l = 1 ≤ c_r = b and use the multilinear formula with the others' offset Z_t. Then φ(S) = ∫E[(1−t)q(Z_t) + t·p(Z_t)]dt, where q(z) = clamp(z,0,1) + clamp(−z,0,b) and p(z) = clamp(1−z,0,b) + clamp(z+b,0,1). A case check gives min_z[(1−t)q + t·p] = min(2t, 1), which integrates to 3/4.

So the pair infimum lies in [3/4, 13/16]; its exact value is unresolved.

## 6. Monotonicity

Lemma 3 of the supplied four-owner theorem (own-capacity monotonicity of every marginal) is count-independent. So 2φ is a valid truthful mechanism under binding underreports, with coverage and a floor of H_i — but at β = 1.

## Limitations and unresolved items

- **Scope of the negative result:** this is a failure of constant-scaled individual Shapley only. It says nothing against other monotone ownership-dependent mechanisms; the [1/8, 1/2] interval for arbitrary counts is unchanged.
- **Surviving target:** find a non-Shapley ownership-dependent rule with β < 1/2, or a lower bound above 1/8. A natural idea is to damp payments to owners with M_i = 0, but its monotonicity is unproved.
- **Not determined:** the smallest owner count or pool shape where 5/6 fails. The witness is a 1+4 split, and the supplied theorem covers only 2+2.
- **No general closed form:** the family-4 ratio at finite n is given only as an integral, plus the two small exact values above.
- **Novelty:** unconfirmed; no literature search was run.
