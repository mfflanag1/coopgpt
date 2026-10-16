**Provisional verdict: no findings of error in reviewed scope.** Both analytic reductions check by hand; all certificate inequality directions are correct. Most important observation: two TP constants have very thin margins (TP3 ≈ 8e-5, TP7 ≈ 8e-4) and the 4/e second-endpoint max (≈1.4706 by my spot evaluation near v≈0.34) sits ≈4e-4 below 1471/1000 and ≈9e-4 below 4/e — correctness rests entirely on the exact rational scripts, which I did not execute.

## Findings

**1. (Info) TP identities verified by hand — not covered by the script.**
`TWO_PARAMETER_ENTROPY_SPILL.txt` L45–50, L69–73: I confirmed R_t(1)=0, R_t'=A−D0+sqx (using (q(1+x))'=−qx), the substitution R_t=(A−3sc)u+scΨ(u) (via ∫(1−v)eᵛ=(2−v)eᵛ), f(x)=cφ(u), Ψ(u)≤u³eᵘ/6 termwise (coefficients (m−2)/m! vs 1/(6(m−3)!)), (1−u)(1/2+u/3+u²/8)=1/2−u/6−5u²/24−u³/8 decreasing, and the Fbar2 algebra (101/600=81/600+20/600; tangent constants −2c/5, −17/500, 19/90). `verify_two_parameter_entropy.py` only certifies scalars (L19–35); directions are correct (cu/dl/yl in TP3, cl/9−Bupper² in TP6, ru/sl/su bounds in slopes/tangent). The eta-reduction (f≥x/60 ⇒ ∂/∂η≥0 for η≥2) and the h/T=ρ minimization (coefficient D0+1/(15η)−A≥0) are valid. Verification: run the script under `python3 -I`; optionally add a symbolic check of (TP5) and Fbar2.

**2. (Info) Thin margins.** TP3 numerically 0.134918 vs 0.135; TP7 ≈ +0.00081. Rational arithmetic with 19-term tails (~1e-17) suffices, but any transcription change to the constants (27/200, 101/600, 15) will break the proof. Verification: confirm script margins are reported in the JSON.

**3. (Info) 4/e proof: signed accounting is genuine.** `SIGNED_OTHER_LOCAL_LOSS_THREE_HALVES.txt` L69–75 lower-bounds the *new* total other payments (q_new W ≥ q_min(t)A, (1−q_new)v ≥ v/2), so (4) bounds the signed loss, not a positive-part sum; the W≥t step for A>t holds (either some h_k≥t, or W=A>t). (5)–(7) and the endpoint argument (derivative numerator increasing in d) check. Certificate directions (`certify_signed_other_four_over_e.py` L30–32, L60–63): U_12(u), 2−l, L_N((1−l)/l), +u are all in the upper direction; bracket nonnegativity is checked in `cover` and automatic in the small loop (L_N≤e^{−x}≤1). e≤2222710781/817689600<87/32 ⇒ 4/e>128/87>1.471>1.4 ✓.

**4. (Low) Unverified dependency.** The original-short case (FOUR_OVER_E L20–32) rests on SHORT_STAGE's claim that the long-role derivative q[ρ²−m(ρ−1)]≤2/e bounds the sum of other positive losses; I checked ρ² e^{1−ρ}/2≤2/e and m≤ρ, but not the full SNL lemma. The 3/2 note's "accepted" status is assumed.

**5. (Info) Sharpness example (TP L86–90)** is consistent: ρ=2, h=2T, all hardware uncapped ⇒ U_J=2cT, A·a_J−sU_J=2(A−sc)T=D0(h−T).

## Scope limitations
No code executed; claimed cell counts (321, 128, 7) and reported maxima (1.470992672, 1.479760521) unverified. PARAMETRIC_ENTROPY_DEFICIT_SPILL.txt and NONLINEAR_OUTGOING_LOSS.txt not in packet. Primitive definitions (pool orientation by raw totals, cap convention at ties) taken as described.

## Verdict
**No findings** (no errors identified in the reviewed scope); conditional on exact script execution and the accepted SNL dependency.
