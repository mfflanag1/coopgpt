**Provisional verdict: no findings in reviewed scope.** I could not break any step. Every check below was re-derived by hand from the packet; nothing was executed.

## Findings

No invalid step or counterexample found. What I checked:

**§1 Pair inequality and matching (lines 8–28): holds.**
- Conditional on own arrival t, the marginals are f_a(D + b·1[j before]) and f_b(−D + a·1[i before]), with D having the same law in both.
- The case split at D = a−b is exhaustive, and the dropped (1−t) terms are nonnegative.
- The matching sum equals Σ_i (φ_i/c_i)·rowsum_i + Σ_j (φ_j/c_j)·colsum_j ≤ φ(S), using φ ≥ 0 and the row/column caps.

**§2 Individual floor (lines 31–38): holds.**
- f_a is nondecreasing and subadditive, which gives f_a(z) + f_a(D−z) ≥ f_a(D) for all real z, D.
- Complementary predecessor sets have equal Shapley weight, and T − v(N\{i}) = f_a(B−A).
- Minor gap: H_i ≤ T − v(N\{i}) is used without a stated reason. It is the standard bound x_i = T − x(N\{i}) ≤ T − v(N\{i}); add one line.

**§3 Sharpness (lines 41–61): holds.**
- If b precedes a left unit, the right-minus-left predecessor capacity is at least m − (m−1) = 1, so it earns 1. Otherwise it earns 1 iff Y − X ≥ 1; strict Y > X is correct by integrality.
- Mean −D0·t is correct, and variance (m−1+r)t(1−t) ≤ m/2 holds since m−1+r < 2m.
- Chebyshev applies because Y > X forces a deviation above D0·t.
- ∫₀¹ min(1, h²/t²) dt = 2h − h² ≤ 2h for h < 1, and ≤ 1 ≤ 2h for h ≥ 1.
- Giant owner: its marginal is min(X, Y+m) − min(X, Y) = (X−Y)₊ since X ≤ m. E(X−Y)₊ ≤ δt + sd, with sd ≤ √((m+r)/4) ≤ √(m/2).
- The final algebra is correct: √(2m)/D0 = √2·q²/(q³−1) and φ_b/m ≤ 1/(2q) + 1/(√2·q²).
- Efficiency cross-check is consistent: the right units absorb about m/2.

**Calibration (lines 72–74): reproduced by integration.**
- Left unit: ∫[(1−t)(1−(1−t)³) + t(t + (1−t)t²)] dt = 3/10 + 23/60 = 41/60.
- Right unit: ∫[2t(1−t)³ + t²(1−t)] dt = 1/10 + 1/12 = 11/60.
- Giant: 4/15 by efficiency. φ(S) = 49/30, and 6/5 of that is 49/25 < 2.

**Consequence (lines 64–69): correctly scoped, with two low-severity caveats.**
- λ ≥ 2 is shown only for a single constant λ applied to unweighted individual Shapley across all owner counts. It does not exclude owner-count-dependent λ(n), profile-dependent scaling, weighted Shapley, or other mechanisms. Line 68–69 says most of this; consider naming λ(n) explicitly as open.
- "Truthful" for 2φ rests on φ_i being nondecreasing in own capacity. That is true (f_a(z) is monotone in a for each predecessor set) but is not written in the file.
- The factor 1/2 is shown as an infimum only; attainment is neither claimed nor proved, and line 61 is worded consistently with that.

## Suggested verification

- Exact rational enumeration of φ for the q = 2 instance (m = 16, r = 8) using the symmetric count state, to confirm φ(S)/m sits below the stated bound.
- Brute-force check of φ(S) ≥ v(S)/2 and φ_i ≥ f_a(D)/2 on small integer profiles.
- Contract calibration (2,1|1,1) → 5/6, which this file does not reproduce.

## Scope limitations

- Only the two supplied files were reviewed.
- H_i and the core were taken as defined in the contract.
- The existing 50% aggregate-price construction, the 1/8 lower bound and the four-owner 20% theorem were not reviewed.
- No novelty or source assessment was made.

## Verdict

No findings in reviewed scope. Two optional one-line additions: the core marginal bound in §2 and the monotonicity of φ_i in own capacity.
