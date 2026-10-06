**Provisional verdict: no findings (no mathematical errors located in the reviewed scope).** The most load-bearing step — the simultaneous base-profile export bound (eq:exports) — checks out: it uses only the changing owner's own-report comparison, the symmetrized equality of payments among the (h+1)(n_{h+1}+1) high owners of type h+1 at S_h, nonnegativity of all other payments at S_h, and T(S_h)=m.

## Findings

**No correctness findings.** Items independently re-derived from the packet:

1. **Symmetrization** (manuscript 312–317). ȳ(c)=|G|⁻¹Σ_g g⁻¹·y(g·c) over pool permutations × within-pool permutations preserves nonnegativity, coverage (v is G-invariant), budget (T is G-invariant), and own-monotonicity (g·(t,c₋ᵢ) varies only coordinate g(i)). Invariance gives equal payments for same-report owners in a pool and for same-type pools. Valid for arbitrary nonanonymous rules.
2. **Destinations retain T=m.** Type-h total is m+h(m−1); all-low pools have total m; n₀≥2 guarantees one survives at S₀, none is touched at S_h, h≥1.
3. **Coalitions.** C0: needs m−h≥1 ✓; worth 1. C1: needs m−h≥m−d+1 ⇔ h≤d−1 ✓; worth min{m−d+1, m}=m−d+1 (d≥1). Both are genuine subsets of N.
4. **Signs/combination.** (m−d)·C0 + d·C1: coefficient of Σ_{h<d}n_hx_h is (m−d)+d(m−d+1)=A, RHS is A, type-d coefficients (m−d)x_d+d z_d are exactly that type's budget. All dropped terms nonnegative.
5. **Asymptotics.** m=dq_d>d; bracket ≤1+AH_d/L≤1+1/(1+log d); A/m=d+1−d/q_d; log L=(2+o(1))log d; log k_d=(2+o(1))d log d; padding changes only n_{d-1}/(d(n_d+1)) downward. Inversion: d=⌊(½−ε)log k/log log k⌋ gives log k_d≤(1−2ε+o(1))log k<log k. Elementary family: A/m=(d+2)/2, bracket<3/2 ⇒ B>(d+2)/3 ✓.
6. **Compatibility with B_k.** Equal-size pools lie in 𝔓_k; bound holds for every y∈𝒴(P), so inf≥bound; floor only shrinks the feasible set, so the lower bound persists.
7. **Small-ball appendix.** Density unimodality by convolution argument ✓; F_j convex on [0,1]⊂(−∞,ρ_j/2] ✓; Jensen with Σb_i=1 ✓; ∫₀¹F_j=E(1−X_j)₊ ✓; convexity in coefficients and vertex structure ✓; t^{n+1}/(n+1)! and the θ-conditioned formula ∫₀¹(1−θu)^{n+1}du/(n+1)! = q(n+θ) ✓; endpoint agreement ✓; (k−1)q(t)<k(e/t)^t for t≥2 via 1/(n+1)!<(e/(n+1))^{n+1}≤(e/t)^t ✓; strictness on (R_k,∞) ✓.

**Minor (framing, not errors):**
- Manuscript 364 / brief 68: "same bounds with the floor" — the floored minimax is never formally defined; state it as inf over floor-satisfying rules.
- HIERARCHY_THEOREM.txt 2–3 ("independent model audit"), 126 ("resolves this project's target"): internal target language; manuscript/brief are correctly hedged (leading constant open, no human review). No claim that the ½–1 gap is solved was found.

## Scope limitations
- Static reading only. Verification scripts (`hierarchy_certificate.py`, `verify_small_ball.py`, etc.) and their reported counts are not in the packet; nothing was executed.
- Theorems thm:prop, thm:escape, thm:continuous, thm:binary-two were not re-audited beyond consistency with the new framing.
- Priority/literature claims cannot be assessed from the packet.

## Verdict
**No findings in reviewed scope.** The hierarchy lemma, order theorem, padding/inversion, and Q(k)<U(k) are correct as written.
