**Provisional verdict: no findings in reviewed scope** (conditional on two external dependencies). Most important observation: the dominant-hardware total-down lemma is correct precisely because (DH) forces m≥1 on every cell; the scalar-retention obstruction is exactly the m=0, a=0 configuration where the same derivative, (1−q)/3−q(r−m)b_*/t, goes negative — the two files are mutually consistent.

## Findings

**1. DH theorem, §2 (DOMINANT_HARDWARE…, L54–79) — verified.**
Independently derived: on an opposing-short cap cell q′=q(r−m)/t; for a<t, W_t=q′(a−b)≤q(r−m)≤qr≤1/2; for a≥t, m≥1 so W_t=q+q′(t−b)≤q(1+r−m)≤qr≤1/2; W_b=1−q≥1/2. Hardware-short side: W_t=q(a−b)/H≤q=W_b (uses a≤H, b≥0). Tie at t=H gives (a+b)/2 on both sides. The G≤D / G>D case split yields (G−D)_+/2 correctly; no W_b≥1/2 is needed past the tie. No gap.

**2. DH §3 clipped path (L93–117) — verified.**
All three cells check: b_*=0 gives q′min(a,t)+q·1_{a≥t}≥0; b_*=t gives ≥1−q(1+r−m)≥1−qr≥1/2; interior gives ≥[1−q(3r−2)]/3, and q(r)(3r−2) is maximized at r=5/3 with value (3/2)e^{−2/3}<1 (e^{2/3}>5/3>3/2). The ε-transfer b≤b_*(t)+ε holds in both clipping cases; W_b≤1 closes (DH_down). ε_i reduces to [(Z−Z^i)/3−(z_i−z_i^i)−(2/3)η_i]_+ ≤ the (UR_multi) summand. No gap.

**3. Algebraic identity and sharpness (L128–142) — verified.** CB+(20/21)Δ_−+Δ_+ = C²F−CcP−(C−20/21)Δ_−−cΔ_+ with Z=CM−Δ_−−Δ_+, F=P+M. Four-owner example: Z=2C, H_A=2+2c=B, outer capped sum 2B, raw total C²·2=C²F.

**4. Dependency (U) lemma — re-derived, consistent.** J_i change q{e^u[x−y+ρ−1−2u]−(x−y+ρ−1)}, optimizer clip((x+ρ−3)/2,0,x), convexity pieces and transition continuity all check; 2δ−ρg_ρ(1) = 2q[(e^u−1−u)²+u²] on [2,4]; F(v) with F(2)=2[(e−2)²+1], F′(2)=2(e²−3e+3), F″>0 for ρ≥4. Low-ratio nonincrease bracket bound (≥−1 on [1,2]; ≥r−1 for r≥2 at m=r) correct.

**5. SCALAR_RETENTION_ONLY_OBSTRUCTION — verified.** W′(1)=λ(1−c)−2cβ; λ=1/3, β=9/10 gives (5−32c)/15<0 (c>5/32 ⇔ e<3.2); feasibility u<3/20; λ_available=(1−3c)/(1+c) from own/total derivatives 1−3c and C; incompatibility ⇔ 1−6c+c²<0, value −7/121 at c=2/11, decreasing. Correct.

**6. CAPPED_RETENTION_OBSTRUCTION / corollary — verified.** Defect c[(1−2u/3)e^u−1]−η/3 >13/1152−η/3 at u=1/4; N_D′/N_D=(1−u)exp(u+cue^u−η); exact rational 1+r+r²/2−4/3=1330009/1800000000 for r=8747/30000 confirmed; (3/4)(1+r+r²/2)=1+1330009/2400000000 confirmed. Outer unused slack c[1−(1−η)e^η]→0 correct. Raw-rule failure is genuine; OD/DH/Theorem B hypotheses all fail there, so no contradiction.

## Scope limitations
- Primitive own-coordinate monotonicity (used for hardware restoration, incl. across pool switch) is asserted, not proved, in the packet; I spot-checked the short-side derivative ≥1−q(1+ρ)≥0 but did not audit the general statement.
- (UR_multi) accepted per instructions; (U) is a second dependency, verified above only algebraically.
- Sharpness is for the aggregate bound on the class; the P and Δ saving coefficients are not shown optimal (DH file does not claim this, but could say so explicitly as OD does).
- No tests or external files consulted.

## Verdict
**No findings in reviewed scope.** Both obstructions are exact and correctly scoped (proof relaxations / raw rule, no subsidy lower bound). The DH theorem's derivations hold for all continuous whole-owner underreports, modulo the two stated dependencies.
