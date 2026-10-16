**Provisional verdict: no substantive findings in reviewed scope.** All displayed static payments, coalition worths, and inequality chains in Sections 2–3 check out by hand; the most notable item is a minor definitional inconsistency (floor only on A in §1 vs. floors on every owner in §4).

## Findings

**1. Low — Definition drift between §1 and §4 (lines 21–23 vs. 110–113).** B_f is defined with a floor only on A (`z_A>=f(b)`), but §4 uses `B_q=Q` at a zero-production profile with retainers q_i on *all* owners. The conclusion is correct for the obvious multi-floor extension (coalition constraints are trivial at zero production, so static minimum is Σq_i), but the text should state the extended definition. Verification: add one sentence defining B with per-owner floors.

**2. Low — Implicit domain of the sup in §2 (line 35).** `sup_b (Σy_i/T)` is undefined at T=0. The §1 convention (zero funding when B_f=0) resolves it since f_L=θL=0 when T=0, but the §2 statement should restrict to T>0 explicitly.

**3. Informational — Checks performed by hand (all pass).**
- Worth formula matches the flow oracle: source side {P, L_j}, sink side {h_j}, unit profits ⇒ max flow = Σ_I ell_j + min(P, Σ_I r_j); A-only and C-only cases reduce correctly.
- M_A = T − min(P,H) ≥ 0 since T = min(L+P, H) ≥ min(P,H); own-A monotone since T increasing in each L_j.
- Rule (θM_A, R, ell): coverage inherited from known rule (verified Σ_I ell + min(P,Σ_I r) ≤ Σ_I ell + R and min(P,Σ_I h) ≤ Σ_I ell + R); total ≤ (1+θ)T since M_A ≤ T; K_f ≤ 1+θ via B_f ≥ T; zero funding at B_f=0 holds.
- O=(1,1,1,1,1): T=2, M_A=1. Payment (θ, θ/2, 1−θ/2, 1−θ/2) covers all 15 nonempty coalitions (A+H_j: 1+θ/2 ≥ 1; C+H_j: 1; C+H1+H2: 2−θ/2 ≥ 1; A+C+H_j: 1+θ ≥ 1; grand: 2); nonnegativity needs θ ≤ 2, within stated range. Lower 2+θ/2 derivation correct.
- V=(2,1,1,1,1): M_A=0, (0,0,1,1) covers (C+H1+H2 worth 2 met exactly).
- U=(1,2,1,1,1): ell=(1,1), r=(1,0), R=1, T=3, M_A=2. Payment (2,1,0,0) covers all coalitions (A+C+H1 worth 2 vs 3; grand 3 vs 3); floor 2θ ≤ 2 needs θ ≤ 1, as stated.
- First lower: 2c_O+x_O+y_O ≥ 2 ⇒ c_O ≥ 2+θ−K(2+θ/2); c_V ≤ 2K−2; O→V changes only P (C's bundle) ⇒ c_O ≤ c_V ⇒ K ≥ (8+2θ)/(8+θ). ✓
- Second lower: x_U ≤ 3K−1−2θ; O→U changes only h1 ⇒ x_O ≤ x_U; 1 ≤ c_O+x_O ≤ 5K−3−2θ ⇒ K ≥ (4+2θ)/5. ✓ At θ=1/2: 18/17; at θ=1: 6/5. Crossover θ≈0.70; max{} statement consistent.
- §2 lower: h_j=L_j=1, P=m ⇒ r_j=0, R=0, T=L=m, C+all H worth min(m,m)=m; total ≥ (1+θ)m. Upper T+θL ≤ (1+θ)T. Sharp. ✓
- Verifier floor reconstruction (lines 29–33) matches f_L (grand minus C's mask → A+all H = L) and f_M (grand minus coalition without A = T−min(P,H)).

**4. Informational — Novelty.** The file explicitly disclaims historical novelty and confines sharpness of 18/17 and 6/5 to the finite {0,1,2}^5 domain. No overclaim detected in the text as written.

## Scope limitations
- I did not run `verify_floor_certificates.py` or `flow_oracle.py`; the 243-profile sharpness claim (lines 96–98) and the primal/dual certificates are unverified here.
- The "known efficient all-profile own-monotone rule" (line 19) is taken as given; I checked coverage and own-monotonicity of its components only as needed for §3.
- Economic-interpretation claims in §4–5 were checked for internal consistency only, not against literature.

## Verdict
**No findings of mathematical error in reviewed scope.** Two low-severity presentational gaps (per-owner floor definition in §4; T>0 restriction in §2's sup). Finite-domain sharpness remains unverified without executing the verifier.
