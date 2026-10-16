**Provisional verdict: no findings (no errors located in reviewed scope).** The most consequential step I checked—the one-cap ceiling E_j ≤ 1 in ONE_CAP_POSITIVE_DUAL_COUPLING §1—is sound given the packet's definitions, but it rests on E_j being the *outer-primitive* payment only (see scope limitations).

## Findings

**None of error severity.** Items below are verification notes (low severity / clarity).

1. **SHARP_SIGNED_OTHER_LOCAL_LOSS §1–§3 (and the transcribed short proof).** Verified: accounting identity (2)/(SS2) is exact; tr ≤ R ≤ r holds since min(c_k,t) ≥ t·c_k for c_k,t ∈ [0,1]; the R-derivative sign 1−(R−v)/t gives unimodality, so the subtracted term's minimum (hence L_aug's maximum) is at an endpoint; (r−v)/(1−v) = r[1+(r−1)/y] with y = r(1−v)/v; r²+1 ≤ 2e^{r−1} from three Taylor terms; q(r+1) ≤ 1 for r ≥ 1. Pool-switch loss (6) is exact: (1−q)A + qv − (1−q_new)v − q_new W. Case A ≤ v correctly forces W = A. Derivative numerator of (7), 2e^{d+v−1}(d−1)+1, is increasing in d, so endpoint reduction is valid; endpoints give 1 and (1−v)(2e^v−1). f′(v) = 1−2ve^v; v_*e^{v_*} = 1/2 gives Λ = (1−v_*)²/v_* ≈ 1.1948 (spot-checked numerically). Equality construction reproduces: z_i = q, loss (1−q)(1−v_*), ratio = Λ. Pre-switch bound (5): d+v−1 ≤ dv since −(1−d)(1−v) ≤ 0; K/4 < 1 < Λ. *Clarity note (§3, line 89–92):* s is dropped to (1−q)(1−v) before the "decreases with s" remark; harmless, s = 0 is still the ratio maximizer.

2. **SHARP_DEFICIT_OWNER_GAP_CEILING.** Verified both branches of (4): hardware-short gives (c−q)h_i + qℓ_i ≤ max(c,q)T; local-short needs 1−q−max(c,q) ≤ ρ−1, true via e^{1−ρ} ≥ 2−ρ on [1,2] and trivially for ρ ≥ 2; q ≤ 1/2 < α ≈ 0.816 used correctly. δ_j = T(c + q log 2q) is exact from Z_j = T + q(ρ−1)T. f convex (f″ = 1/q), f(c) = 0, f(1/2) = c, so 0 ≤ δ ≤ cM and Q is well-defined. Jensen direction and f(q̄) ≤ f(q) are correct. Tangent (5) checks: c + t log2t + s(q̄−t) = c − t + sq̄. Equality family: z_G = q, g_G = 1, δ = f(q), RHS = α + q. Diagnostic numbers (1.10674 vs 1.11946) reproduce.

3. **ONE_CAP_POSITIVE_DUAL_COUPLING.** S < 2 ⇒ at most one d_i = 1 (correct). Uncapped owners have w_i = 0 so PD1's min collapses to min(p,μ)z_i. OC2 is an exact rewrite of min{λg+pz, g}. Scalar maximization: intersection z* = bB/(b+αp), g* = pB/(b+αp), z*+αg* = B, value abB/(b+αp); feasibility and monotone/antitone lines verified. 0 < λ < 1 for S ≥ 1 (λ ≥ 1/(2S) per PD file). OC3 follows with G = S−1+v, Z_+ ≤ Z−z_−, μ ≥ 0. Tied-at-1 owner (b_j = 1) has w_j = 0 and is covered by the stronger branch.

## Scope limitations
- E_j ≤ 1 (OC §1) is valid only if E_j denotes the outer-primitive payment alone, bounded by outer short total ≤ reported hardware ≤ 1. The packet does not define E_i beyond "own-report envelope of the raw nested rule"; verify against the mechanism definition.
- PD1/PD3 taken as accepted; B_old from INDIVIDUAL_PAYMENT_GAP_COUPLING.txt not in packet.
- No code run; Λ and Q(δ) values spot-checked by hand only.
- OC1 feeding an 8/5 certificate is not evaluated (not claimed).

## Verdict
**No findings in reviewed scope.** All three lemmas' restrictions, endpoints, convexity directions, scalar maxima, and equality constructions check out as stated, subject to the E_j-definition caveat above.
