**Provisional verdict: no findings in reviewed scope (conditional on the frozen dependency); one evidence gap for the C=1 endpoint.** The most important point: the one-block capped KKT certificate (§2) checks out exactly, including signs, budget tightness, zero coordinates, and the reduction of outside nonnegativity to the source's strict inequality (I).

## Findings

**1. [Low / evidence gap] C=1 not supported by the packet.** `selection_cap_two_analysis.txt:109-111` restricts §3 to C>1 (A=(C_Q−C)/(C−1) is undefined at C=1) and defers C=1 to an "efficient-core selector barrier" not supplied. The task's "EVERY FIXED C>=1" is therefore only verified here for C>1. Verification: supply that separate note or restate the headline as C>1.

**2. [Info] All §2 arithmetic and KKT steps verified by hand.**
- Budget: 2p+(Q−1)d·z = [2h+(Q−1)d]/D = C_Q (line 41) ✓; Q=3 gives C_Q=2, p=1/11 ✓; general closed form (line 84) ✓ (both equal 2(Q²+Q−1)/(2Q+5)).
- Retained own rows (focal, veto, exactly d−h neighbors): 2p+(d−h)z=1, tight ✓. Off rows (veto + ≥d neighbors per source Part I.6): ≥p+dz=1 ✓. Deleted rows RHS 0 ✓. Coalition values are maxima over generators, so generator coverage suffices ✓.
- Stationarity with x=Aᵀλ−τ·1+ν: veto and focal λ−τ=p; neighbor λa₀−τ=z forces λ=(p−z)/(1−a₀) ✓; λ>0 needs h>1 and a₀<1 ✓.
- Outside ν_i=τ−λb>0 ⇔ (h−1)(1−b)>h(1−a₀) ⇔ h(a₀−b)>1−b, which is exactly the source's h(β−μ)−β>0 (source lines 198-200; holds for d-multiples since hδ≥2) ✓.
- Q=3 numerics: a₀=9/20, b₀=49/120, λ=(20−200/d)/121, τ=(9−200/d)/121, τ−λb₀=(5d−710)/(726d)≥1/242 at d≥480, and λ/m<1/242 for m>40 ✓. Strict (I) is stronger than needed; ν≥0 suffices.
- Uniqueness by strict convexity ✓. Cap binds consistently: the uncapped B=1 total at the deviation ≈k/t≈1/b₀≈2.45>2.

**3. [Info] §3 additive-owner reduction verified.** Coverage factors (singleton forces x_Y≥A; mixed coalitions then reduce to old coverage). Lowering any excess above A preserves all constraints and lowers the objective, so x_Y=A; residual old budget C(1+A)−A=C_Q ✓. Finite-min-of-binary-forms preserved ✓. T=1+A at full and selected profiles ✓. Q,A fixed while d grows gives Ω_C(N) ✓.

**4. [Info] Dependency use is faithful.** Only uniform neighbor marginal a₀, uniform outside marginal b, "exactly d−h neighbors" on support, "≥d neighbors" on off rows, strict (I), the growing-d quantifier, and the Part II.B same-owner Boolean realization (hiding Z_j yields w^j exactly, T=1) are invoked; each appears in the supplied source.

**5. [Info] §4 many-block upper bound is correct as stated** (orbit-averaging gives x(block)≥a(1−u); clipping arguments valid because all demands ≤1) and correctly framed as compatible with §2's B=1 scaling.

## Scope limitations
- I did not re-prove the frozen source (transport lemma, all-Q scalar bounds, Part II.B); it is treated as verified input.
- `CONSOLIDATED_THEOREM.txt` and the C=1 "efficient-core selector barrier" are not in the packet.
- No code executed; all checks are by hand on symbolic/rational expressions.
- Result is, as the note says, architecture-specific; no unrestricted mechanism lower bound or novelty is assessed.

## Verdict
**No findings in reviewed scope** for the C>1 claim (§2–§3 certificate is exact and correctly reduces to the frozen input); **insufficient evidence** for the C=1 endpoint within this packet.
