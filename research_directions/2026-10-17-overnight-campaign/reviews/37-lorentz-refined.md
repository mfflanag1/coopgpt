**Provisional verdict: no findings in reviewed scope (no mathematical error located); several steps verified by hand, the full polynomial identity (4) only spot-checked.**

Most important point: identity (4) is the load-bearing step for all-coalition TCWM, and I could not replay it coefficient-by-coefficient. I verified it at three independent levels and all agree, so the risk of a hidden error is low but not zero.

## Findings

**1. (Info) Discriminant identity (4) — consistent at every point I could check by hand.**
- `CONE_LORENTZ_REFINED_RADIAL_OUTSIDE.txt:57–78`. Derived A_t, V from Y = t − f(s)⟨x,e⟩ and confirmed f = J/D², f′ = K/D², f/s = U/D², U−K = s, sD²−J = −cs(1−s)D, D²−J = bD(1−s)(1+c+s). The quadratic A, B, C matches the derivation and the scout code (lines 34–36).
- Leading coefficient: 4AC−B² has leading term −b⁴/4·s¹⁴ and b⁴ = c⁸ = 13−21c, giving r₇ = (13−21c)/4 ✓.
- Lowest coefficient: s² term is 4b²(1−4b²) = 324c−200 = c²·r₀ ✓.
- Vanishing order at s=1: the (1−s)² term cancels exactly ((3+2c)² both sides) and the (1−s)³ coefficient is 22+14c on both sides (R(1) = 8+6c) ✓.
- All eight signs follow from 77/125 < c < 13/21 (tightest: r₆ needs c > 0.616, r₇ needs c < 13/21) ✓.
- Verification: run `CONE_CHECK_LORENTZ_REFINED_RADIAL.py` (lines 16–18 assert the full identity); I did not execute it.

**2. (Low) Full-OUT derivative step is terse but correct.** Line 112–116: with α = λA_t ≥ 1 and β = λ‖V‖ ≤ α, the needed inequality (α−1)dt ≥ (β−1)‖dx‖ is not immediate when β > 1; it holds because (α−1)dt ≥ (α−1)‖dx‖ ≥ (β−1)‖dx‖. Suggest adding this line.

**3. (Low) Checker correctness depends on unseen code.** `CONE_CHECK_LORENTZ_REFINED_RADIAL.py:19,31,32` compare Q(c) elements with `Fraction`s; whether the `Q` class (from `CONE_CHECK_LORENTZ_PHI.py`, not in packet) implements that ordering correctly is unverifiable here. The finite-profile tests (lines 40–71) require `rays` whose subset sums have exactly rational norms; otherwise `norm()` is either inexact or raises. Verification: inspect `Q.__lt__/__gt__` and the `rays` construction.

**Verified without issue:** mixture bound 0 ≤ f ≤ 1; identity (3) (numerator c⁴ − 2c⁴s + c⁴s², c⁴ = 2−3c); f(1)=1, f′(1)=c; A_t ≥ 1−d(s) via h ≥ (s−1)/2; d = c·d_b + b·d₁ with the square identity (a−(1+a)s)²; d′ = H/[2(c+s)³]; H′ < 0 via 12−19c < 1 < 2−c; H(0) > 0 > H(1); root-bracket upper bound on d_* (line 29) is monotone-valid; numerics d_* ≈ 0.118471 < 0.1185 (margin ≈3·10⁻⁵), 2000φ/1763 ≈ 1.83555 < 1.836; s=0 case (f′(0)=2, ‖V‖ ≤ 1); phi-theorem limit (8) rederived, so γ ≥ c is a valid lower bound in the stated regular radial class (d ≥ 2), and f lies in that class.

## Scope limitations
- Did not execute any script; `Q`, `val`, `sumv`, `norm`, `rays` definitions absent.
- Boundary/zero-total handling is by reference to the phi theorem's concavity-segment argument; I checked it transfers (boundary-ray segments give F(D)=0), but did not re-derive every limit.
- No novelty or global-optimality assessment (none claimed).

## Verdict
No findings in reviewed scope. The proof chain is sound at every step I could reproduce; residual uncertainty is confined to the unreplayed middle coefficients of (4) and the unseen checker dependencies.
