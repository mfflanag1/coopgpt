**Provisional verdict: no findings in reviewed scope.** Every step I could check in sections 1–3 is valid; the most delicate step — that the integrand in (1) is exactly `m − A_i^0` (not merely a lower bound on a positive part truncated at 1) — holds because `0 ≤ m − A_i^0 ≤ β < 1` is genuinely true in both orderings of `U_b, U_h`.

## Findings

No invalid steps, missing hypotheses, or failing edge cases found. Verification notes, by claim:

**Section 1 (truthfulness and coverage of p).**
- `A_e^0` is evaluated at `c_e=0`, so independent of `c_e` by construction. `B_e^c` is a min over the report-independent excluding family of sums of `D_h(c)U_h`; `D_h` nondecreasing in every report (THEOREM l.43, which follows from feasible-set inclusion) gives `B` nondecreasing in `c_e`. Hence `p_e` monotone; nonnegativity trivial.
- `A_e^0 ≤ A_e^c` pointwise in `U_{-e}` by the same monotonicity, so `(B−A^0)_+ ≥ (B−A^c)_+` and `p ≥ z` via THEOREM (4). Coverage inherits from `z`; `p ≥ y` by THEOREM l.174–179. `B=∞` and `D_e=0` cases agree with (4).

**Section 2 (network, cut enumeration, lower bound).**
- Cut enumeration checked: cuts containing `x_i` must hit `b+h` so are `{x_i,b},{x_i,h}`; cuts avoiding X must contain `a` and hit `b+h` and `g+h`, giving `{a,h},{a,b,g}`. `K=2k+2`. `T=1+β` with all `D_e = c_e` (verified `D_h=min(1,β+1)=1`, `D_g=1`).
- Deleted profile: only `b+h` survives, `D_b^0=D_h^0=β`, so `A_i^0 = β·min(U_b,U_h)`. Every excluding cut contains `b` or `h`, so `B ≥ m = min(βU_b,U_h)`.
- Case `U_b ≤ U_h`: `m = βU_b = A^0`. Case `U_h < U_b`: `A^0 = βU_h ≤ m`. So `m−A^0 ∈ [0,β]`, and with `D_i=1` the truncation is inactive. `E m = β/2 − β²/6` and `E A^0 = β/3` are correct; (1) and (2) follow (`k=(K−2)/2`, `T=3/2`).

**Asymptotic upper bound (k≥2).** `B ≤ M+m` via `{x_j,b},{x_j,h}`; 1-Lipschitz truncation gives `p_i ≤ β(1−β)/6 + E M`, `E M = 1/k` for `k−1` uniforms; other four owners `≤ ΣD_e = 3+β`. Correct.

**Section 3 (envelope bounded).** At report `t`, all serial caps and `D_a,D_g` equal `t`; `D_h=min(1,β+t)`. Selection of `{x_i,b}` or `{x_i,h}` over the same-type cut with `x_j` forces `tU_i ≤ tU_j`, so for `t>0` the event has probability `1/k`; `z_i(t) ≤ t/k`, `y_i ≤ 1/k`. Other envelopes `≤ D_e(c)` by monotonicity of `D` in every report. Total `≤ 4+β`. Correct; separation from `k/24` is unbounded.

**Edge cases.** `k=1`: cut enumeration, lower bound (1), and section 3 all hold (the `1/k` upper bound is correctly restricted to `k≥2`). `B=∞`: does not arise in this family (every owner has an excluding cut); the general definition handles it consistently with (4). Boundary `β∈(0,1)` is used only to make `m−A^0<1`; stated.

## Scope limitations
- The TTSP remark `A_e^0=A_e^c` (l.18–19) relies on an unsupplied co-cut theorem; it is not load-bearing for the obstruction.
- THEOREM.txt's formula (4), "D_h nondecreasing in every report", and the least-monotone-majorant fact were taken as supplied dependencies after a plausibility check, not independently re-proved.
- The 169-case QMC scan and "exact finite support checks" were not reviewed; no computations were run.

## Verdict
No findings in reviewed scope. The hybrid `p` is a truthful covering majorant of `z` and `y`; the all-`k` lower bound `Σp/T ≥ (K−2)/72`, the matching `k/24+O(1)` upper bound, and the uniform `Σy ≤ 9/2` bound are all correct as stated.
