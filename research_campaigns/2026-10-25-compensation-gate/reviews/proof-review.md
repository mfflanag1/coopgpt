**Provisional verdict: no findings in reviewed scope.** The staircase obstruction, the finite-chain optimum 1+3L/4, the negative-variation bound (2), and the 1/2/∞ hierarchy all check out symbolically; the JSON values match independent recomputation.

## Findings

No invalid steps found. Items verified by hand:

1. **Price uniqueness off-diagonal (§2 L52–54).** For a<b, p≥0, p₁+p₂≥1, ap₁+bp₂=a forces p₂=0, p₁=1 (otherwise ap₁+bp₂ > a(p₁+p₂) ≥ a). So (1) is genuinely forced by the weak individual condition; no tie profile is used.

2. **Staircase domain (§2 L45–48).** Max coordinate is 1+(L+1)/(L+2) < 2; all profiles strictly interior, a≠b. Adjacent steps change exactly one coordinate by 2δ; nonadjacent pairs change both (a₂ⱼ₊₁=a₂ⱼ₊₂, b₂ⱼ=b₂ⱼ₊₁), so §3's claim that all single-owner comparisons are adjacent is correct.

3. **Arithmetic (§2 L70–71).** W_L = L + δL(L−1)/2 = 3L(L+1)/(2(L+2)); F_L = 2(L+1)/(L+2); ratio 3L/4. JSON entries (e.g. L=128: W=12384/65, K=97) recomputed and match. Comparison counts (L + L(L+1)/2; full box 585 = 180·2+225; crossing 8) also match.

4. **Finite-chain optimality (§3).** Lower bound uses only adjacent restoring-owner inequalities; the construction satisfies the stronger fullOUT on all comparable pairs of Q_L (superadditivity of min plus W_k ≥ W_j). Ratio monotonicity: F_k² − δW_k ≥ F_k(F_k − kδ) = F_k > 0. Exact K_L = 1+3L/4 is sound.

5. **Negative variation (§4).** Telescoping identity and R(q₀)≥0 give (2). Negatives confined to the passive owner since restoring-owner increments are ≥ F_{k−1} > 0. Output growth Lδ < 1 while V⁻ ≥ 3L/2 − 2(K−1) → ∞; unboundedness claim valid.

6. **Hierarchy (§5).** (a) y=(F,0): all coalition/fullOUT cases checked, including passive-member pair with singleton delta value 0. (b) y=(F,F): ρ_i = F−u_i ≥ 0 since each u_i ∈ [0,F]; K≥2 lower bound uses only off-tie points (t,1), t<1, so tie-price choice is irrelevant as stated. (c) follows from §2.

7. **Path-envelope divergence (§2 L73–78).** Owner 1 incurs ⌈L/2⌉ ≥ ⌊L/2⌋ losses ≥1, owner 2 ⌊L/2⌋; initial segment (0,0)→(1,0)→q₀ has zero charges (p₁=0 forced at (1,0)). Minimality of R*_i (§1 L34–37) follows by the standard path-accumulation argument.

**Minor observations (not defects):**
- §1 "least nonnegative reserve" relies on single-owner edges; the extension from l to h for monotonicity is always realizable by single-owner edges here, so the claim holds.
- Replay `price_charges` tie branch (a/2,b/2) is only exercised in the full-box grid; consistent with the symbolic proof, which avoids ties.
- The crossing fixture is correctly labelled prior calibration; CEA outputs recomputed and match expected.

## Scope limitations
- Cannot execute `check_compensation.py`; I recomputed JSON values independently by hand for all listed L and the comparison counts.
- Did not evaluate the general frontier √(s/6) ≤ K₃(s) ≤ 3s², which the document explicitly leaves unchanged.
- "Irreversibility" is correctly flagged as a design restriction, not a problem constraint; §5(c) must not be cited as a general lower bound (document already says so).

## Verdict
**No findings in reviewed scope.** The candidate rejection is mathematically valid, uses only the weaker individual condition, stays inside the fixed [0,2]² box with two fixed owners, and makes no novelty or frontier claims.
