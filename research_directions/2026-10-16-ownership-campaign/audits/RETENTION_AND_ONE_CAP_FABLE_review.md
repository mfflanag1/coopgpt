**Provisional verdict: no invalidating findings in reviewed scope.** Most important concrete item: the only unverified step is a citation mismatch in the β constant of retention eq. (8); it does not affect any coefficient.

## Findings

**F1 (Low) — INCOMING_RETENTION_PENALTY.txt:115–118, β justification.** The text says "the uniform sharp incoming theorem gives I ≤ Kε(1+L)". The global file's (10)–(11) actually gives I ≤ ε + Kε[1+log(X/ε)], which exceeds Kε(1+L) by ε. The claim holds via SHARP_LOCAL_ONLY_ENTROPY (5)–(6): I ≤ max(KεL, eε) ≤ Kε(1+L) once L ≥ e/K−1. Since β→1 and enters only as β(2−X/2)ε with β=1+o(1), eq. (2) is unaffected. Verification: replace the citation with SLOE (5)–(6), or set β=exp[−eε−KεL].

**Verified (recomputed independently):**
- Retention (3): d/du[(1+d−u)e^u]=(d−u)e^u ≥0; q(e^d−1) ≤ KV. Switch case (4): f(d)=e^{−d}(1+Kd) has endpoints f(1)=1, f(1−v)≥1 by the chord inequality; (t+a)e^{−a} nonincreasing for a≥1−t; last step is exactly exp(1−t)+exp(1−1/t)≥2 (SLOE (3), derivative (1−v)²/v² checked).
- (5)–(6): case split correct; v_j=ρ_j−d_j ≤ log(T_j/(2V_j)) via log d ≤ d−1; Jensen with weights W_j and W_j/V_j ≤ K gives log(KX/(2W)).
- (8): S′−S ≤ I−D, q0′ ≥ q0 e^{D−I}, e^D(g+D) ≥ g+(g+1)D — all exact.
- J_X convex (sup of affine maps), J_X(0)=0, nonneg ⇒ superadditive-dominated and nondecreasing; chord argument correct. R-derivative −g[log(KX/2W)−1]+β(g+1) <0 and V-derivative Kg[log(X/2V)−1]−g−β(g+1) >0 uniformly on X∈[√ε,1/4], g≥7/8.
- (11)/(12): x+log x = L+1−β/K; value K(x−2+1/x)−β = K(L−log L−1)−2+o(1). Expansion of (13) gives C+cKε(L−log L)+c(K−2)ε+o(ε); consistent with SLOE (9) minus 2cε.
- Lower: q=ε/T, Z_core=T+ε(ρ−1), tiny branch ratio 2 ⇒ z_G=z_A=ε, (2e−1)/6<1, S=2 exactly, b_A∈(0,1), G_+−G_−=1 (checked including B_i positive gaps). Δ=ε[Kρ−(2e−1)]>0 since ρ≥3>2.58; ρ=L−log L+1−log 2; TΔ=Kε+o(ε); gain_1 and gain_A asymptotics correct; 2e−K=e+1. A's deviation: G's account 1+eε stays capped; hardware recipients lose exactly Kε; outer total 2−eε. Two reports are used in separate envelopes, not combined. Counts (k=⌊L⌋ branches, ~T/(kε) hardware fragments per branch) unbounded with fixed identities per instance.

**Observations (not errors; sources of the remaining gap):** the upper charges neither opponents' outgoing losses (realized Kε in gain_1) nor G's unrealized positive-gap allowance, and uses G_−≤1−X/2 where the entropy witness has G_−≈1−X. These explain why the lower's optimum is T≈1/L while the upper's is X≈2/L.

## Scope limitations
Snapshot only; no execution. Accepted dependencies (restoration lemma, outgoing Kz bound, SHARP_INCOMING_ENTROPY_v2, zero-local-branch convention giving zero local payment) taken as given. I did not re-derive the small-S exclusion or the X<ε bounds beyond checking their stated orders.

## Verdict
**No findings of substance in reviewed scope.** One low-severity citation fix (F1). Both the order-ε upper c(K−2) and the one-capped lower −c[e+1+K log 2] verify as stated; no coefficient equality is claimed and none is implied.
