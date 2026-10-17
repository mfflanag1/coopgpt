**Provisional verdict: no mathematical defects found in reviewed scope.** The most important check — the high-profile kernels (3) and the identity (6) — reproduces exactly by hand; the forced law at p=1 then underpays coalition {1,3} by t·(1/(2+t)) > 0.

## Independent derivation

**Low profile** z_L=(2,t,−1,0), S ranging over subsets of the three others:
- Owner 0: marginals 1 on S={2} (p(1−p)), 1−t on S={1,2} (p²) ⇒ B₀ = p − tp², K₀ = 1−tp ✓
- Owner 1: t on S={2} only ⇒ K₁ = t(1−p) ✓
- Owner 2: 1 on {0}, t on {1}, 1 on {0,1} ⇒ K₂ = 1+t−tp ✓
- Owner 3: 0 ✓

Lipschitz step: from (2,t,0,0) all residual kernels vanish identically, so restoring owner 2's capacity gives u₀+u₂ ≤ 1; coverage of {0,2} (worth 1) gives ≥. Hence (2+t)m_L − 2t h_L = 1 and U = (1−t²h_L)/(2+t) ✓.

**High profile** z_H=(2,t,−1,−t), t<1:
- Owner 0: (1+t)p(1−p)² + 2p²(1−p) + p³ ⇒ K₀ = 1+t(1−p)² ✓; owner 2 identical by enumeration ✓
- Owner 1: 2tp(1−p)² + tp²(1−p) ⇒ K₁ = t(1−p)(2−p) ✓
- Owner 3: tp[2(1−p)² + 2p(1−p) + p²] ⇒ K₃ = t[1+(1−p)²] ✓

Endpoints at p=0 match the stated K⁰ formula (1, t, 1+t, 0 and 1+t, 2t, 1+t, 2t) ✓, and B/p has no constant term so the "derivative at 0" closure is just polynomial evaluation.

**Identity (6):** (2+t)(L+S) − (1+t)(2L+S) = S − tL = t(m+a) − t(m+ta) = t(1−t)a ✓. Using L+S ≤ U+t and −(1+t)(2L+S) ≤ −(1+t)², bound is (2+t)U − 1 = −t²h_L ✓. Since t(1−t)>0, a=h_L=0, both inequalities tight.

**Final step:** a=0 with ν_H ≥ 0 forces support {1}; 2m+tm=1+t ⇒ m=(1+t)/(2+t); K₁(1)=0, K₃(1)=t ⇒ u₁+u₃ = t(1+t)/(2+t) < t = v({1,3}) ✓. At t=1/2: 3/10 vs 1/2, shortfall 1/5 ✓.

**Null padding:** z=0 owners contribute zero to every worth, so each marginal is unchanged and the Bernoulli weights over null-inclusion sum to 1 — kernels unchanged ✓.

**Checker (read, not executed):** polynomial arithmetic, `kernels` (p^k(1−p)^{n−1−k} weights, division by p via `poly[1:]`), assertions on (1),(3), identity (6), worths, 3/10, and line 72 affine check all agree with the above.

## Findings

**Low (clarity, not a defect) — CLOSED_SAMPLING_CONE.txt lines 16 vs 22.** Line 16 lets ν depend "on the reports," line 22 on z only. The proof survives full-report dependence because in every compared profile the owner whose restoration yields the upper bound (owner 2 at the low profile) is pure, so the low identity holds for the measure at the *mixed* low profile reached from z_H (owner 3 holding (t,t)). This should be said explicitly rather than relying on the "z → ν_z" notation. Verification: restate the low identity as holding at any profile with z=z_L and owner 2 pure.

## Scope limitations
- The definition of pair-TCWM and the necessity argument for the upper Lipschitz inequality live in LIPSCHITZ_REDUCTION.txt §3 (self-contained here) and in unseen files (PAIRWISE_GAIN_TRANSLATION_REDUCTION.txt). Only §3 necessity is used, and I accept its stated reading of pair-TCWM (restoring member may be joined by an unchanged member).
- Checker not executed; verified by reading.
- The "limits of conic combinations" remark (lines 107–109) is not proved and is not needed for the theorem as stated.

## Verdict
**No findings in reviewed scope** beyond one presentational clarification. Kernels, moment identity, forced p=1 support, and {1,3} coverage contradiction are all exact.
