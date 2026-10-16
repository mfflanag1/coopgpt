**Provisional verdict: no substantive findings in reviewed scope.** All algebraic reductions, sign orientations, convexity/tangent steps, and rational-bound directions recompute correctly. Most important concrete point: the weight-four certificate rests on very thin margins (EW4 ≈ 0.0018, F′(5/6) ≈ 0.0058), so the rational bounds must be used exactly as directed — the script does this correctly.

## Findings

**1. Low — negative-gap set definition (SUBSET_ENTROPY…, L19–20, L65; root context L44).**
The note uses strict `d_i < a_i`; the root context defines the negative gap as `g_i ≥ 0`. SE2 needs strictness (or `a_i<1`) so that `d_i = p_i+z_i` and `a_J ≥ Zminus+v`. The sharpness construction (§4) also requires that the zero-gap `q=c` owners be *excluded* from J; including them raises Zminus without raising v and makes the construction non-tight (perspective derivative in Zminus is `c−r ≤ 0`). Verification: state explicitly in the certificate that J = {g_i > 0}.

**2. Low — sharpness scope overstated (§4, L104–105).**
Attainment is constructed only for `r ∈ [c,1/2]`. "Cannot be strengthened using only (v,Zminus,delta) on this face" should be restricted to that range; no profile with `δ=0, v=rn, Zminus=(1−r)n, r<c` is exhibited.

**3. Informational — unverifiable comparative claims.**
"Improves earlier coefficient A+1" (L24) and "strengthens requested spill 51/50" (EW L16) reference material outside the packet; only `65/64 < 51/50` is checked.

## Recomputed items (all confirmed)
- `s∈[0,1]`, `A ≥ s/2` via `g(t)=c−t+s/2`, `g(c)=0`, `g'=1/(2t)−1 ≥ 0`; `A−sq ≥ 0` since `q ≤ 1/2`.
- Deficit identity `δ_j = T(c + q log 2q)` from total payment `T(1−q+qρ)` and `1−ρ = log 2q`; `f` convex, tangent SE4 correct.
- Hardware-short: `A a_J − s(1−q)a_J = a_J(c−t+sq) ≤ a_J f(q) ≤ δ_j`; spill term vanishes (h=T).
- Power-short: clipping loss `h − ρT` exact; SE5 uses `a_J ≤ h` with nonnegative coefficient `A−sq`; residual bound uses `h ≥ ρT` with `D−A = 1/2 > 0`. `F(x)` expansion, `F(0) = t−s/2 ≥ 0` (⇔ `log 2t ≤ 2t−1`), `F' ≥ 1/2−q ≥ 0` all correct.
- SE2 substitution signs: `A ≥ 0` (for `a_J ≥ v+Zminus`), `s ≥ 0` (for `U_J ≤ Zminus`). SE3 at t=1/2 correct.
- §3: `U_J ≥ a_J/2` holds in short and tie orientations (tie gives exactly `h_i/2`); `r ≤ 1/2`; derivative `n(r/t−1)`, maximizers and SE6 values correct; `2cv` at `r=1/2`.
- §4 totals: `Z = C − n f(r)`, `δ = n f(r)`, `P+M ≥ H`, `S = P+Z ≥ 1`, all hardware-short (`ρ>1` for `r<1/2`, tie at `r=1/2`).
- EW3 expansion, decomposition `F = 4f + G + x/64`, `G(1)=0` (uses `e^{−1}=2c`), `G' = 1/2−c−(x/2)e^{−x} > 0`, `F' = 33/64−c+q(3x−4)`, `F'' = q(7−3x) > 0` on [0,1], EW4 coefficients `9c/4 = 9/(8e)`, `−29/256`, `−11/16` correct.
- Script: Taylor tail bound valid (`j!/19! ≥ 20^{j−19}`), every bound direction (cl/cu, 1/au, 1/bl, 1/eu) chosen conservatively for the sign asserted; exceptions not `assert`.

## Scope limitations
No code executed; numeric sanity values computed by hand. Model facts (payment formula, `Z=Σ_j Z_j`, tie continuity) taken from the root context as given. "Records all fractions" is only partly true (two checks record no values) — cosmetic.

## Verdict
**No findings of error in reviewed scope.** Recommend pinning the strict negative-gap definition and the `r∈[c,1/2]` sharpness range before certificate use.
