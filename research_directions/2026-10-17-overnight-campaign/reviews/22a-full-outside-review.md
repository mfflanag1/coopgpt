**Provisional verdict: no findings in reviewed scope.** I attempted to break the joint directional proof (Cases A–C), the zero/support conventions, the F-vs-G funding comparison, and the exact checker, and found no error. Most important observation: the proof is correct but Case A relies on `Z ≤ kG` and `f − k r f_r = 0` in a way that leaves no slack; this is where any later modification of `f` (e.g., restoring the TCWM-only amplitude `A_k`) would break full OUT, since `d_P ≥ F(d)` is only recovered exactly.

## Findings

**No correctness findings.** Verification notes on each audited step:

1. **Case A (r<C), lines 47–62.** Recomputed `r' = d_P(G − t_cap P/C)/G² − rL/G`; first term ≥0 since `g_j ≤ P/C` for capped branches. `f_r r' Z ≥ −k r f_r L` uses `Z ≤ kG` (valid: `s_jl ≤ x_jl`). Private-minimized branch: the two `l_j` terms of (5) sum to `d_{j,l_j}` exactly when `x_{j,l_j}=g_j`; other terms ≥0. Tied cap/private rows on an open interval are identical affine functions, so assignment choice doesn't change slopes. `Y' ≥ d_P ≥ F(d)` holds.

2. **Case B (r>C), lines 66–74.** `Y' = Cθ G' + h(1−θ)d_P + Z'` checks out algebraically; `Z_j' ≥ g_j'` by the same two-term identity; `ΣG' ≥ Σ_j min_l d_jl ≥ F(d)`.

3. **Case C and switches.** `h=f=1` at `r=C`, both continuous there; `g_j` continuous; branch activation at `t>0` is continuous because `g_j s_jl/x_jl ≤ g_j ≤ x_jl → 0`. Initial-endpoint limits: `(C+k)G → 0` and `F ≤ P → 0`. The claim `F(c(t)) ≥ tF(d)` (homogeneity + monotonicity) correctly confines zero production to `t=0`.

4. **Funding uses actual F.** `F ≥ min(P,G)` since `g_j ≤ min_l x_jl`; case `r≤1` gives `F=P` exactly; case `r>1` uses `F ≥ G` only as a lower bound. Bound (8) and the choice of C giving (2) verified, including `C=1` (k=1 or M=1).

5. **Floor counterexample (lines 122–126, checker line 44–46).** Recomputed by hand: `g=1/C, r=C, h=f=1`, one-row owner gets `1/C`. Correct.

6. **Code.** `parameter` finds smallest integer C with `C^{2k} ≥ k^k M^{k-1}` ⇔ `C ≥ √k M^{(k−1)/(2k)}`; using a larger integer C only weakens the second entry of (8), so testing against `(C+k)·F` is valid. `coalition_payment` returns `s_P h + Z·rad^{1/k}` with `h=1` when `rad<1`, matching (3)–(4). `Radical.compare` sign logic and `root_interval` bracketing (`lo ≤ q^{1/k} < hi`) are correct; unresolved two-root cases raise rather than pass.

**Minor (non-blocking):**
- Formula (5) formally divides by `x_jl`; zero rows are only covered by the Section 1 convention, not restated at (5).
- Case B's "min over currently minimizing rows" is redundant on an open interval (tied slopes are identical) — harmless.

## Scope limitations
- `HETEROGENEOUS_COMMON_CAP_COROLLARY.txt` (Section 6 transfer) is not in the packet; the layer-identity claim is unverified.
- The lower bound (other file) was read only as context; I did not independently audit it beyond confirming (4) follows from the stated TCWM step and that full OUT ⇒ TCWM (take `F(d) ≥ 0`), so the Θ claim's dependency is logically consistent.
- No tests executed; `COMMON_CAP_FULL_OUTSIDE_CHECKS.json` output not inspected.

## Verdict
**No findings in reviewed scope.** The joint directional proof, tie handling, zero-support conventions, actual-F funding argument, and exact implementation are internally consistent with the stated model (fixed owners, public C, nonnegative withheld bundle).
