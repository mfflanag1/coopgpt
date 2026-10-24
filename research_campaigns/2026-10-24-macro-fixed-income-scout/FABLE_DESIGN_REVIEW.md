**Provisional verdict: findings (scope/novelty corrections; the core arithmetic checks out).** Most important: Design A's prototype F(c)=max{p'x: Ax≤c, x≥0} is Owen's (1975) linear production game, uncited, and the "(K−1)F under the theorem" bound invokes a funding factor that RESEARCH_CONTEXT.txt says is established only for the unit-profit P4/complete-blowup rule (lines 19–20), not for general nonnegative A.

## Findings

**1. Design A — missing antecedent and over-extended theorem (CANDIDATE_DESIGNS.txt:54–60; Medium).**
Evidence: the LP prototype is exactly a linear production game; its core is nonempty via dual (shadow) prices, which is precisely the "fixed public prices give an immediate efficient rule" stop condition at line 66–67. Line 59 says outside funding is "at most (K−1)F under the theorem," but the context states arbitrary trees are open and only one graph class has factor 1+1/√2. Verification: state that no K is known for general A; name Owen 1975 and test whether the Owen/dual-price allocation satisfies the OUT property on degenerate LPs (non-unique duals) before claiming any new result.

**2. Design C — one-factor identity verified, but its consequence is understated (lines 130–149; Medium).**
Checked: C({i})=a_i⁺k⁺+a_i⁻k⁻, C(S)=(A_S⁺−A_S⁻)k⁺ or (A_S⁻−A_S⁺)k⁻, so v(S)=(k⁺+k⁻)min(A_S⁺,A_S⁻); k⁺+k⁻≥0 from subadditivity and ρ(0)=0. Cost-core→savings-core map (lines 124–126) is correct by subtraction and is a bijection. What the draft misses: this is a glove game, so the core has dimension ≤1 for any n. If A⁺≠A⁻ and no single owner is pivotal (A⁺−a_i≥A⁻ ∀i>0), the core is a singleton—no fairness conflict at all; only the riskless-aggregate case (ΣA_i=0, line 142) leaves a segment whose two endpoints already separate maximally. Hence the gate "do extremes survive one factor" is answered by the derivation itself; the genuine open question is core dimension/geometry of Euclidean norm games v(S)=κ(Σ_S‖b_i‖−‖Σ_S b_i‖) in R². Also: k⁺=k⁻ and C(S)=κ√(a_S'Σa_S) require mean-zero factors; state this. Verification: compute core dimension for small two-factor instances with ΣA_i=0 and check whether it is bounded independent of n.

**3. Design B — grounded lane with essentially no theorem transfer (lines 82–120; Low–Medium).**
Lines 18–19 exclude strategic default, renegotiation, bankruptcy priority and intertemporal commitment—exactly the content of the two-date model. The claimed CoopGPT contribution ("coalition deviation accounting") is unused by a Hart–Moore-type hold-up model. Label this independent applied work; the 2026 Van Nieuwerburgh and Gete/Mercader citations are unverifiable here and should be marked as leads.

**Institutional statements:** SEC dates (31 Dec 2026 cash, 30 Jun 2027 repo) and the clearing-mandate framing match my prior knowledge but are unverified in-packet; the Garratt "Shapley need not lie in the core" attribution (line 73) and Mayo/Wellman (line 76) are unverified leads. Budget lines (189–194) are internally consistent; no baseline confusion found.

## Scope limitations
No tools; no literature access; cannot confirm URLs, 2026 working papers, or regulatory pages. Did not verify context result 1's normalization, so whether one-factor glove endpoints realize that specific separation is unchecked.

## Verdict
Findings in reviewed scope: mathematics correct; scope/novelty statements need the three corrections above.
