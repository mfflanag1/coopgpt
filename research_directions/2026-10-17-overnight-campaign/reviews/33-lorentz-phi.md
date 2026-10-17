**Provisional verdict: no findings (no mathematical errors) in reviewed scope.** Most important observation: every algebraic identity I recomputed independently — (3), (4), (5), the coefficients A_2, A_1, A_0, q_*, (6), (7), the A>0 bound, the s=0 case, (8), and the Section 5 numerics — checks out. The only gap is an unstated (but true) justification in the s=1 boundary argument.

## Findings

**1. [Low] Section 3, lines 101–104 — boundary-segment dichotomy stated without proof.**
Claim: a feasible segment either stays on the s=1 ray throughout or meets s=1 only at an endpoint. This is true but needs the one-line argument: along a linear report path, f(λ)=T(λ)−‖X(λ)‖ is concave and ≥0, so an interior zero forces f≡0. Suggest adding this sentence; otherwise the continuity/integration step is correct (Y is continuous for T>0, differentiable on the interior).

**2. [Informational] Section 3, line 72 — P normalization.**
4(1+s)/(1−s²) = 4/(1−s); the stated form is correct but needlessly indirect. No error.

## Verified steps (independent recomputation)

- ‖v‖=a(s)=s/D ≤1 via D−s=c(1−s); coverage via Cauchy–Schwarz. ✔
- Total T(1−s²/D); D−s²=(1−s)(c+s) using b=1−c, giving (3); ratio increasing (derivative c²/D²>0), limit φ. ✔
- Gradient: A=1+sa′h, −∇ₓY=[a+a′h]e+(a/s)w, using ∇ₓ⟨x,e⟩=e+(x−⟨x,e⟩e)/‖X‖. ✔
- Ellipse (5): foci 0, se, major axis 1; distances (1±sq)/2. Using the necessary condition ‖x‖+‖X−x‖≤T is legitimate for sufficiency. ✔
- a′=c/D²; N expansion using D−1=−b(1−s), D²−s²=c(1−s)(D+s); coefficients A_2, A_1, A_0 match exactly. ✔
- q_* with D−c=bs; numerator−denominator with c²=1−c, bc=2c−1, b²=2−3c, b²c=5c−3 gives (7−11c)+(8c−5)s−(2−3c)s² = (1−s)[(7−11c)+(2−3c)s]. Constants ≈0.202, 0.146 >0. ✔
- (7): A−L=c(1−s)(D−h)/D², D−(1+s)/2=(c−½)(1−s). ✔
- A≥1−1/(8c)>0. ✔ s=0: A=1, ‖V‖≤1/(2c)<1. ✔
- (8): first-order expansion in ε=1−s gives 2ε(1−h₀)[γ+(γ²−1)h₀]; two boundary owners realize the ellipse boundary; necessity of A≥‖V‖ at a differentiable point is valid. γ≥c ⇔ γ²+γ≥1; (1) has γ=c/D(1)²=c, so φ is attained. ✔
- Section 5: y₁ before 1+1/(1+3c), after 2+1/(1+4c); increase ≈0.938 ∈ (0,1). Single interior owner receives F·(c+s)/(c+bs) > F. ✔

## Scope limitations

- Only this file reviewed; `CONE_LORENTZ_GAIN_TWO.txt` and the Djokovic inequality reference not inspected.
- Novelty/priority not assessed (explicitly disclaimed by the note).
- The definitions of "coverage," "TCWM," and "OUT" are taken as implicit in the note; I checked internal consistency, not conformance to an external spec.
- Sharpness result is correctly hedged as restricted to the regular radial class with reserve coefficient 1 and C¹ at s=1; I did not attempt to extend or refute beyond that class.

## Verdict

**No findings in reviewed scope** beyond one minor missing justification (concavity of T−‖X‖ along segments) at the s=1 boundary step. All stated inequalities, polynomial identities, limits, and counterexamples are correct as written.
