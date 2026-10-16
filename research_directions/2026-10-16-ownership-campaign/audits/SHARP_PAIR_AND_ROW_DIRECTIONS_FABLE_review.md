**Provisional verdict: no substantive findings in the reviewed scope for the lower construction; two low-severity cautions on the certificate directions; dependencies on unsupplied notes (PD1, one-cap scalar result, NEGATIVE_GAP_SAVINGS, SUBSET_HARDWARE_DEFICIT_COUPLING) are unverifiable.**

Most important concrete point: every exact identity in SHARP_SIGNED_RESPONSE_DIFFUSE_PAIR_LOWER.txt I could recompute by hand checks out, including the sign-sensitive Δ in (8) and the residual constant in (1).

## Findings

**1. Lower construction — verified, no error found (informational).**
- Module (lines 27–46): branch k has hardware t, local (1+v)t, so hardware short, ρ=1+v, q=e^{-v}/2=v. z_J=3vt=ε; z_{D_k}=(1−v+v²)t; t<ε iff v>1/3 ✓. After J deletes, ρ=1, q=1/2, D_k paid vt=ε/3; loss 3(1−v)²t=(1−v)²ε/v=Λε ✓; (1−v)(2e^v−1)=(1−v)²/v via e^v=1/(2v) ✓. Opponents are genuinely mixed (hardware+local), matching the two-owner attainment in SHARP_SIGNED_OTHER_LOCAL_LOSS §4.
- Core (lines 49–70): q_core=exp(1−ρ)/2=ε/T ✓; Z_core=T+ε(ρ−1) ✓; H=T+2τ+a=1, M=T+2τ ✓; max z_i=ε at B₁,G,A ✓.
- Caps (lines 73–83): S=1+(1−Z+2ε)+(Z−2ε)=2 exactly ✓; only G capped; outer q=c, raw total C ✓; (7) ✓.
- Reports: Δ=ε[K(ρ−1)−K−1]=ε[Kρ−(2e−1)] ✓ (>0 since ρ≥3); g₁,g_G,g_A in (9)–(11) ✓. Expansion: Δ=ε[K(L−log L−log2)−e], TΔ=Kε+o(ε), giving g₁=cKε(L−log L)−c[2e+K log2]ε+o(ε) ✓; g_G,g_A=cΛε+o(ε) since εZ=o(ε) ✓. Hence (1) holds as stated. Copy count (two modules: one capped, one uncapped distinguished owner) is consistent with S=2 exactly.
- Checker (check_sharp_signed_pair_lower.py) replays these identities with matching branch indices and S targets; I did not run it.

**2. One-cap coefficient (RATIONAL_CAP…AUDIT lines 5–16) — low.**
Derivatives of T are correct (∂T/∂p=b(b+αμ)/(b+αp)²>0, ∂T/∂b≥0, ∂T/∂μ<0, ∂T/∂α≤0) and the positive part preserves monotonicity. Caution: μ and λ enter the row twice with opposite safe directions (μ_hi for the Zplus coefficient but μ_lo inside T; λ_hi in λG but b_hi=1−λ_lo inside T). The note only addresses T. Validity of the base inequality itself rests on PD1/“exact one-cap scalar result,” not in the packet.

**3. Negative chord grouped prefactor (lines 26–38) — verified.** v+Zminus≤1 follows from z_i+g_i≤a_i−p_i≤a_i and Σa_i=H=1 (negative-gap owners uncapped); vZminus≤1/4, a=4K²/15<4 gives a nonnegative bracket; ordering b0→b_lo then v²→v_h² is valid. Suggest recording the v+Zminus≤1 derivation explicitly.

**4. Linear PF support row (lines 40–52) — verified** given COUPLING_PROFILEWISE: Y≤q0[2(r+v)+γZplus]; Zplus≤Z−Zminus and Zplus≤C, η≤1−M+K√(c·dh) are all valid monotone enclosures; r e^{−r} peaks at r=1 ✓.

## Scope limitations
- No execution; checker output not observed.
- “Improves prior constructions” (line 22) and the Λ upper-bound proof (SHARP_SIGNED_OTHER_LOCAL_LOSS §§1–3) not audited; the lower bound does not depend on them.
- IG4/IG8/NS1 source lemmas not in packet.

## Verdict
No findings in reviewed scope for the lower construction; low-severity cautions on certificate-row interval directions; insufficient evidence for upstream dependencies. These rows are not a complete 8/5 proof.
