**Provisional verdict: no substantive findings in reviewed scope.** The most consequential unverified step is the 64-mask feasibility claim in the six-owner witness, which relies on a checker not in the packet; I hand-verified all seven listed tight masks and ~10 others, all consistent.

## Findings

**F1 (Low, informational) — Six-owner KKT certificates hold for any g0 ≥ 0.** `SEPARABLE_OBSTRUCTION.txt:74–86`, invoked by `ALL_SEPARABLE_EXTENSION.txt:17–24`. Recomputed with bit masks 3={0,1}, 36={2,5}, 43={0,1,3,5}, 56={3,4,5}: low profile gradients (g(1),g(1),g(2),g(1),g(1),g(2)+g(1)=g(s)); high profile coordinate 3 gives r+g(1−δ)=g(1+δ−h), coordinate 5 gives g(2−h)+r+g(1−δ)=g(s+h) by (3). Positivity of λ₃₆, λ₅₆ needs g(·)>0 at positive arguments, true since g(x)>g0≥0. Existence of s>2 needs φ'(v)>0 and φ'(2v)+φ'(v)∈[g0,L), both satisfied. The extension's claim that g0=0 was not otherwise used is correct. Tightness checked: masks 0,3,36,39,43,56,59 all give X_Q=min(P_Q,N_Q) at (4).

**F2 (Low) — Case 2 sign chain is strict and correct.** `ALL_SEPARABLE_EXTENSION.txt:33–42`. With Lagrangian stationarity φ'(x_i)=Σ_{Q∋i}λ_Q+η_i: A1: λ₁=φ'(1−t); B: λ₁+λ₂=φ'(t); A2: λ₂+η=g0. λ₂>0 needs t>1−t (t>1/2 ✓). η≥0 needs λ₂≤g0: φ'(t)<L (strictly increasing, sup not attained) and φ'(1−t)>g0 give λ₂<L−g0≤g0 ✓. Grand constraint is tight with zero multiplier — permissible. Witness t=3/4→7/8: pair {A1,A2} total 1/4→1/8, changed owner's own payment 0→0, so this is a pairwise externality, correctly not labelled individual-IC.

**F3 (Low) — Case 3 is sound but broader than stated.** `ALL_SEPARABLE_EXTENSION.txt:49–55`. g0<0 fails the budget at every G=0 profile, not only the zero profile. Not an error; the zero profile suffices.

**F4 (Low) — Lipschitz necessity/sufficiency check.** `LIPSCHITZ_REDUCTION.txt:47–74`. Upper inequality: owner j at pure x′ restores x′−x of the other resource; f_j rises by x′−x, residual drops to x, pair total goes from u(Q;x′) to (x′−x)+u(Q;x); monotonicity gives (L)-upper ✓ (uses equivariance form (P), justified by averaging). Sufficiency: sign-crossing split uses u(Q;z_{−j},0) common to both signs since σ·0=0 ✓; sequential member restorations are legitimate because (iii) is quantified over all fixed z_{−j} ✓. The pair-TCWM constraints are linear/closed, and T_t preserves them (both compared profiles shift identically), so the imported averaging applies. Averaging bound is K G/L per the cancelling-boundary count ✓.

**F5 (Low) — Section 5 two-active-owner argument correct** (`LIPSCHITZ_REDUCTION.txt:83–89`): after restoring b of resource A to owner 2, S=b, G=0, budget+singleton coverage pin y₂=b, others 0; TCWM upper-bounds and pair coverage lower-bounds the initial active-pair total at b.

## Scope limitations
- `check_separable.py` / `separable_exact.json` not supplied; the all-64-mask polyhedral certificate is unverified beyond spot checks.
- Cited `ZERO_COOPERATION_GAIN_RESERVE_OBSTRUCTION.txt` and prior reviews not in packet.
- Did not assess novelty.

## Verdict
No findings in reviewed scope. KKT signs, derivative-range dichotomy (L>2g0 / L≤2g0 / g0<0, with L≤2g0 forcing g0>0), fixed-owner and zero-report handling, and finite sign-crossing sufficiency are all internally consistent. Recommended verification: include checker output in packet; add a one-line remark that Case 3 also fails at all same-sign profiles.
