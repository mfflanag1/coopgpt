**Provisional verdict: no findings (no error located) in reviewed scope; one imported dependency unverifiable from the packet.**

Most important point: every step I could check replays correctly, but the whole outer comparison (8)/(P) rests on the imported sharp outgoing bound O_i ≤ K z_i (others' losses), which is not in the packet. It is at least consistent with the v2 §3 family (hardware owner loses exactly K z_i), so it is plausibly tight, but I cannot verify it here.

## Findings

**F1 (Info, no error) — v2 §1–2 long-stage/switch and composition verified.**
- Switch case: q = e^{-u}/2, total ≤ q(e^u − v); with v = 1+u−d, (e^u−v)/d ≤ (e^u−1)/u ≤ K for 0<u≤d≤1; u=0 gives ratio 1. Non-switch: q(e^u−1)(ρ−d) ≤ KVρ. Both ≤ KVρ, ρ ≤ 1+log(T/2V). Correct.
- Composition order: ∂f/∂T = V/T > 0 unconditionally; ∂f/∂V = log(T/2V) ≥ 0 on [V_int, V_full] ⊂ (0, T_full/2] since V_full = q_full·d_full ≤ T_full/2 and V is nonincreasing during the short stage (q′ ≥ 0 in T, min(l,T) nondecreasing). Correct.
- (2): g(α) = (K−1)(1−α) + Kα log(2α), g′ = 1 + K log(2α), minimum K−1−(K/2)e^{−1/K} > 0; rational bound (7/8)(7/11)=49/88<2/3 valid since (K/2)e^{−1/K} is increasing in K. Correct.
- Mixed-role/tie cases: tie at start forces u=0 (gain ≤ V ≤ KV); post-switch stage is the role-agnostic §2 bound (1/2 per unit; capped recipients have d_k=T′≥s_k). No missing condition found.

**F2 (Info) — Sharpness family (v2 §3).** q′ = eq, each of n−1 resource owners gains Kq, denominator q(n+log2); ratio → K. Also shows G_i/z_i = K(n−1) unbounded. Correct and feasible (single own-coordinate underreport, fixed identities).

**F3 (Minor, scope of "rate coefficient") — v2 §6.** Expansion of D(ε) is correct: D = C + cKε log(1/ε) + 3cKε + O(ε² log²(1/ε)). But the matching family only gives W(ε) ≥ C (truthful raw total); no lower bound of order ε log(1/ε) is provided, so cK is sharp only as the rate of the *upper bound*, not of W. The file does not claim more, but readers should not infer rate sharpness.

**F4 (Info) — Heavy-owner file.** (P),(N) follow from v1 (8),(9) with per-owner O_i ≤ Kz_i, G_i ≤ K f_M(z_i); zero-gap E_i = N_i holds (restored payment = a_i). b_M convexity (b″ = [K/z + K² log²(M/z)]b > 0, continuous extension at 0) and weighted Jensen direction correct; W_−/G_− ≤ t ≤ M. (T-fixed): G_+^L − G_-^L = r − Q_J, G_-^L ≤ 1−a_J; (T-heavy) unimodality at r = 1−v/u, r_min = max(0, Q_J−(1−a_J)); (T-simple) derivative sign (B−1)−(A−1)r ≤ 0 so max at r=0. Calibration: 33797/48000, 19003/96000, 4025/18496, lcm 27744000, 545633/27744000, |J| ≤ 23, 638112000 all replay by hand.

**F5 (Minor) — check_sharp_incoming_constants.py** verifies v2 §5 only; it does not cover the heavy-owner rationals (F4) or v1 §7 (80/73, 59/128, 6931/4995 — hand-verified: A²/(2(A+B)) = 1936/4995). Suggest extending the checker.

## Scope limitations
Not verifiable here: SHARP_OUTGOING_LOSS (O_i ≤ Kz_i), primitive coverage/own-monotonicity (root summary only), the actual checker run. No tests executed. Review is independent of the Root/Codex rederivations; agreement with them is not used as evidence.

## Verdict
No findings of error in reviewed scope; F3/F5 are clarifications, not defects. Conditional on the imported outgoing bound.
