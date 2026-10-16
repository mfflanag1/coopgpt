**Provisional verdict: no findings in reviewed scope (scalar/analytic content recomputes correctly); two provenance/premise flags.**

Most important point: the EHM coefficient c[K−2−K log 2] and the IG5 bound 1+exp(−1+3C/8)<8/5 both recompute exactly from the stated hypotheses, but each rests on dependencies the packet labels inconsistently or omits (see Findings 1–2).

## Findings

**1. (Low — provenance) EHM calls INCOMING_RETENTION_PENALTY "accepted"; that file self-labels "Candidate; independent review pending."**
EHM.txt:3–4, 73 vs INCOMING_RETENTION_PENALTY.txt:2. Likewise EHM:19 treats the one-capped lower −c[e+1+K log 2] as accepted while INCOMING_RETENTION:198–200 conditions it on acceptance. (10) and the "exact width 2cK" claim inherit this status. Verification: confirm review status of both dependencies before promoting (10).

**2. (Low — unverified step in EHM (3), post-switch case D_j ≥ V_j.)**
EHM:78–79 justifies I_j ≤ K V_j v_j by the pre-switch formula I ≤ qT(e^d−1)v. After a pool switch the correct route is INCOMING_RETENTION (4): since 1+t−v ≥ 1, (4) gives 1−q_new ≤ q(1+Kd), hence I ≤ v(1−q−q_new) ≤ Kvqd = KVv. The conclusion holds, but the cited formula is not the switch-case justification. Suggest an explicit one-line reference to (4).

**3. (Info — missing premise, IG5.)** INDIVIDUAL_PAYMENT_GAP_COUPLING.txt:73–74 uses "E_i ≤ a_i − (4/5)q0(a_i−d_i) because δ=0" and the positive-gap comparison E_i ≤ a_i+q0 exp(Kz_i)g_i. Neither is in the packet; I cannot confirm the 4/5 constant or its exact hypotheses (e.g., whether a restoration-type condition is needed at H=M=1). MARGINAL_FLOOR_STABILITY (4) is likewise cited but absent.

## Recomputed items (all consistent)
- EHM (2): q=1/(1+ud), v=1+1/u+log(w/2)−w/u, max of log w−w/u is log u−1, and log(1+2x) ≥ x log 3 ≥ x on [0,1]. Correct; no lower bound on q or d needed.
- EHM (1): (a_i−d_i)_+ ≤ a_i−U_i using d_i ≥ z_i ≥ U_i (z_i ≤ M ≤ 1) and ΣU_i ≥ A. Correct.
- EHM (4)–(7): Jensen with weights W_j, W_j/V_j ≤ K; R-derivative −g[log(·)−1]+β(g+1) < 0 for log ≥ L/2−log 2, g ≥ 3/4; V-derivative Kg[log((A+2ε)/2V)−1]−g−β(g+1) > 0; (7) follows; log(1+2ε/A) ≤ 2√ε.
- EHM (8)–(9): stationarity x+log x = L+1−log 2−β/K; value K(x−2+1/x)−β = K(L−log L−1−log 2)−2+o(1). Outer ratio 1+cα exp{(α−1+εQ)/α} expands to C+cKε(L−log L)+c[K−2−K log 2]ε. Width c[K−2−K log 2]+c[e+1+K log 2]=2cK. Correct.
- Excluded regions: (K/2)εL and (3/4)KεL leading terms are eventually below cKε(L−log L). Correct.
- IG1: hardware-short residual ≤ (q−c)_+T by separate linear maximization; power-short residual T[2−q−Ch/T] ≤ TB(ρ) using q ≤ 1/2 ≤ 1−c, 1−c+C=2, h/T ≥ ρ; Cauchy–Schwarz with δ=Σδ_j. IG2/IG3 via C−c=1. Correct.
- SD4–SD5: B(1)=Kc, B' ≤ −2Kc ⇔ c ≥ 1/6 ⇔ e ≤ 3; (1−u)[4u−e^u] ≥ 0 via e^u/u decreasing, 2√e < 4. Correct.
- IG7: coefficient of v is 6/5−(3/4)(1−c)/c < 0 since (1−c)/c = 2e−1 > 13/3; max_r e^{−r}[r+3C/8] = e^{−1+3C/8}; e^{71/128} > 1+71/128+(71/128)²/2 ≈ 1.708 > 5/3. Correct.
- IG9: h'(2/3) = 351/206−7/4 = −19/412; h'(7/10) = 3900/1971−7/4 > 0; tangent bound log(103/32)−4813/4120 ≈ 0.00076 > 0 (tight but positive); 39/64 < (3/4)(1−c) ⇔ c < 3/16. Correct.

## Scope limitations
No execution; no access to GLOBAL_DIFFUSE_SECOND_ORDER, SHARP_LOCAL_ONLY_ENTROPY, MARGINAL_FLOOR_STABILITY, JOINT_ROLE_TRADEOFF, DIFFUSE_ONE_CAPPED_GRID_LOWER, or the negative-gap 4/5 theorem. The Taylor certificate at IG:108 was not numerically re-executed beyond a decimal sanity check.

## Verdict
No findings in reviewed scope on the new analytic content; two low-severity provenance/citation flags (Findings 1–2) and one unverifiable external premise (Finding 3).
