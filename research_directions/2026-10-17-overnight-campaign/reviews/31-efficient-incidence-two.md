**Provisional verdict: no findings in reviewed scope.** The most important check — that the fixed shift `c_ε = −(1/ε)·1` drops out of the own-row derivative (eq. 2) and that restricting to the positive set J preserves (R)/(C) — holds; I could not construct a counterexample to the efficient selector `e` under either hypothesis.

## Findings

**No correctness findings.** Items below are verification notes / minor gaps in exposition, not errors.

1. **Shift handling (lines 37–56) — verified.** On an open piece with zero set Z and active rows S, the minimizer is the projection of c onto the affine face `{x_Z=0, A_S x=b_S}`; normal space is spanned by rows of `A_S` and `{e_z}`, so `x_J − c_J ∈ rowspace(A_S|_J)`, giving (1). Derivative w.r.t. `b_r` for basis row r is `B^T(BB^T)^{-1}e_r`, independent of c. Dependence of `a_r|_J` on other restricted rows forces `b_r = Σc_s b_s` (Z-support of the discrepancy is killed by `x_Z=0`), so a dependent changed row cannot stay active on an open interval. Empty restricted row ⇒ `b_r=0` constant. All correct.

2. **(R) case (lines 58–68) — verified against RANK_TWO file.** Converting pair rows with one endpoint in Z into singleton anchors introduces no new independent component types. I re-derived: unanchored tree edge gives `b/(a+b)` at i and `a/(a+b)` at j; one-anchor tree gives 0/1; odd cycle edge gives 1/2 at both ends (uses `y_1 = (−1)^{n−1} y_2`); branch edge off odd cycle gives 0/1 because odd-cycle homogeneous equations force cycle values to 0. All nonnegative.

3. **(C) case (lines 70–80) — verified.** `G_rr ≥ Σ_{s≠r} G_rs` holds for `B = A_S|_J` (each J-column lies in ≤2 basis rows). Maximum-principle: equality case forces `|w_t|=M` with opposite sign at all neighbours; unreached component yields `Gv=0`, contradicting PD; components not containing r have `w=0`. Minor imprecision: lines 78–80 should say "one or two *basis* incidences" — a second active-but-dependent incidence contributes nothing to `(B^T w)_i`, so derivative is `w_r>0`. Conclusion unaffected.

4. **ε-limit (lines 87–99) — verified.** `‖x^ε‖ ≤ ‖e‖` from optimality vs. e and `Σx^ε ≥ T`; every accumulation point lies on the efficient face with norm ≤ ‖e‖, hence equals e. Weak inequalities survive pointwise limits. No gap.

5. **Hand spot checks (not tool-executed):** triangle `{12},{13},{23}` with b=1 raised to `b_{12}=1.5` and 2 (e₁: ½→¾→1); 4-cycle (e₁: ½→¾); star with m leaves (leaf raising its edge: 0→½→1, center nondecreasing); path 1-2-3-4; star+private singletons where center starts in Z (e₀: 0→½). All monotone, including cases where nonnegativity is active.

6. **Expository gaps (low severity):** (a) finiteness/closedness of KKT critical intervals in `b_r` is asserted, not argued — standard for one-parameter strictly convex QP but worth one sentence; (b) the (R) proof is by reference to another file; the audit depends on that file's component classification, which I checked and found correct.

## Scope limitations
- Only the three supplied files reviewed; ABV2016 / priority not assessed.
- Fixed-generator/all-profile caveat (lines 101–107) is correctly stated; I did not evaluate any production instantiation.
- No coalition-total (TCWM) claim is made or reviewed.

## Verdict
**No findings in reviewed scope.** The extension from raw projection to the shifted, nonnegativity-active regime is handled correctly via J-restriction; the limit step is sound. Suggested verification: numerically sweep random small (R)/(C) instances (including zero demands and simultaneous multi-row increases) computing `e(b)` via LP+QP to confirm.
