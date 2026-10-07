**Provisional verdict: no substantive findings in reviewed scope (proof inspection only; nothing executed).** The most consequential step—the law-dependent mean separation (1) and the Hoeffding/Chebyshev constants—checks out algebraically for every nonconstant law on (0,1], atoms included.

## Findings

**F1 (Low, correctness confirmed) — Parameter arithmetic, FIXED_NOISE_OBSTRUCTION.txt L24–38.**
- `a·nu + b·mu = (mu+nu)/2 + d/4 = mu − d/4 = mu − 10δ` ✓.
- `min(aX,(a+b)X') ≤ min(aX,aX') + bX'` is the elementary `min(u,v+w) ≤ min(u,v)+w` ✓, giving λ ≤ mu−10δ.
- `a·mu − mu = mu·d/(2nu) > d/2 = 20δ` uses mu>nu strictly, which follows from `nu = mu − ½E|X−X'|` and nonconstancy ✓. Dominated convergence of `min(aX,mX') → aX` needs only X>0 a.s. (so support accumulating at 0 is fine; an atom at 0 would break it, correctly excluded L101).
- Hoeffding exponents: A-sums have m terms in [0,a/m] → range² sum a²/m, deviation 4δ → exp(−32δ²m/a²); Z_low has Cm terms in [0,b/m] → Cb²/m → exp(−32δ²m/(Cb²)); γ = min of these ✓. `B ≥ 2/γ` gives N·exp(−γm) ≤ 2^r·exp(−2r) ≤ 2^{−r} ≤ 1/16 (since e²>4) ✓. Chebyshev: Var(X) ≤ 1/4 on [0,1], M ≥ δ⁻² ✓. Union total 3/16 → 13/16 ✓.
- `t = b/(Br) ≤ b/B ≤ δ` ✓; `m ≥ B ≥ a+b` gives low D_h = (a+b)/m ≤ 1 ✓.

**F2 (Low, confirmed) — Effective caps L46–54.** D_h ≤ min(1, q+a/m) by suffix bound 1 (final bundle) and inflow to B_i ≤ c(y_i)+c(e); achievability needs only prefix ≥ min(1,q+a/m) ≤ 1, which every earlier module supplies (raw ≥ a+t > 1). The argument correctly avoids any raw-prefix equality. Other modules' caps are unaffected since the lowered module still has raw capacity > 1.

**F3 (Low, confirmed) — Simple-DAG transform L82–96.** Both serial copies of a subdivided edge carry identical D, and a minimal cut takes at most one copy, so the path score is D·min(X₁,X₂) = D·V with V nonconstant (survival Pr(X>x)²). Parameters are re-derived for V; focal e uses the original X only via X_e ≤ 1, and g via X_g ≥ 0, which is all that is needed. Cut count: 4^m containing, 2^{Cm}·4^m excluding, 2^M final → exponent p = 1+(C+2)B ✓.

**F4 (Low, confirmed) — Profile consistency and ties.** Each y_{e_j}(c) is lower-bounded by a *separate* unilateral deviation from the single original profile c, then summed at c (L78–79); no cross-profile summation. On the good event the focal containing class is strictly below every other cut (mu−5δ < mu−2δ < mu+6δ), so tie order is irrelevant ✓.

**F5 (Informational) — Baseline.** FIXED_CUT_BASELINE L7–15: monotonicity of min(c_e,T(c)) and `Σmin(a_i,T) ≥ min(Σa_i,T)` are correct; coverage via C∩S being a cut of S's subgraph ✓. Budget ≤ MT on the obstruction family ✓.

**Minor presentational points (no proof defect):**
- L14–16 asserts the bound for the family without stating the law-dependent onset `r ≥ r_0(X)` needed for (7)'s sandwich; L95/102 acknowledge it. Suggest stating "for all r ≥ r_0(X)" in the claim.
- L33: H_m is nondecreasing in m, so "for all m ≥ m0" is automatic; worth saying explicitly rather than relying on convergence alone.

## Scope limitations
- Pure proof inspection; no numerical/rational checks executed.
- Structural cut enumeration (2^{m+1} per module, no cross-module minimal cuts) and the exact Uniform construction were audited separately and are taken as given.
- Did not audit AGGREGATE_ENVELOPE_OBSTRUCTION.txt beyond what the general-law file relies on.

## Verdict
**No findings in reviewed scope** for the general-law extension and the fixed-cut baseline. Suggested verification: rational-arithmetic check of (1), γ, and the 13/16 union bound for one concrete atomic law (e.g. X ∈ {½,1} equiprobable) and its V = min(X₁,X₂).
