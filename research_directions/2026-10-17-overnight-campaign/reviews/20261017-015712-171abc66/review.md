**Provisional verdict: no findings in reviewed scope.** The exact six-resource certificate, the kernel construction, the stationarity/IFT branch, multiplier positivity, and the owner-derivative sign all check by hand; the stated conclusions stay within the architecture's limits. Most important observation: the argument is sound, but its only load-bearing analytic step not covered by the checker is the persistence of the strictly positive KKT branch for small `t` (Section 5, lines 92–98), which rests on injectivity of `T^T` (rank `n−1 = m`) and continuity — correct, but unverified numerically.

## Findings

**1. Section 1 arithmetic (verified by hand) — no issue.**
All five edges tight at both profiles (e.g. `(0,1,2)`: 13+9+13=35). Incident multiplier sums match `2c_v p_v` at every vertex for both profiles (e.g. `v=2` high: 44+22+28+36=130 = 2·5·13). Payments 11/3 and 128/35 are correct; 385/105 − 384/105 = 1/105 > 0. Direction is correct: the lower report yields the higher payment. All prices lie in (0,1/2), so the p≥0 multipliers are inactive and uniqueness follows from local strict convexity + global convexity (segment argument, line 31–32).

**2. Section 4 kernel — verified.** Base equations force `z_01=z_02=z_03`, `z_u=−2z_0`; each level-k edge forces `z_ki = −(z_(k−1)1+z_(k−1)2) = −2z_(k−1)1`. Kernel is one-dimensional, `m = n−1`, so `T^T` is injective and multipliers are unique. Script indexing (`z=[-2]+...`) matches the paper's vertex order.

**3. Section 5/6 derivative — rederived.** With `G(t,θ)=Σ(c_v+t1_j)z_v h'(a+θz_v)`, `∂_θG(0,0)=h''(a)D`, `∂_tG(0,0)=Z h'(a)`, giving `θ'(0)=−Z h'/(h''D)`. Owner payment `P(t)=Σ_{z_v>0}c_v p_v(t)+t p_j(t)` has `P'(0)=a+θ'(0)S`, matching (7). τ→0 limit `S/D→2/6` is correct. Quantifier order (L, then τ, then t) is stated and necessary since `|θ z_v|` scales as `2^L`.

**4. Minor (low): hypothesis `h'(1/3)>0` is slightly stronger than needed to be "any smooth potential," but the excluded cases (`h'(1/3)≤0`) make all cover constraints slack or multipliers zero and cannot provide funding; the text already lists exclusions explicitly (lines 61–63). No overclaim.**

**5. Section 8 — verified.** Relies only on `F_H(y)>0 ⇔` some edge has both endpoints positive, which holds for unit-profit graph LP. Sum-of-lifts extension is valid since summands are nonnegative.

## Scope limitations
- Did not execute `verify_rank_three_potential_obstruction.py`; JSON spot-checked (`4/5 = 28/35`, `S/D≈1/3`).
- Checker covers only the quadratic case and `θ'(0)` sign; it does not test branch persistence or multiplier positivity at `t>0`.
- Section 2 funding bound `(r+1)/2` checked analytically (at most one endpoint ≥1/2 under tightness); not the focus.
- No attempt to assess whether rank-three TCWM has a universal constant (explicitly left open, line 125).

## Verdict
**No findings in reviewed scope.** Claims do not exceed the architecture; limitations (graph-dependent `h`, nonseparable/owner-aware rules, nonsmooth at 1/3, nonlinear lifts) are correctly disclaimed.
