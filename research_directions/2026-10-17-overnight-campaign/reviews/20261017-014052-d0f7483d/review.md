**Provisional verdict: no findings in reviewed scope.** The exact lift identity (1) and the funding-only FPTAS chain are internally sound; I found no invalid factor and no step that trades exact incentives for approximate ones. Most important observation: the FPTAS file has no replay evidence in the packet (the JSON covers only the exact vertex-grid lift), so its correctness rests entirely on the written argument, which I checked step by step below.

## Findings

**1. Low — FPTAS unreplayed (TWO_SPARSE_MECHANISM_FPTAS.txt, whole file; TWO_SPARSE_LIFT_CHECKS.json L1–68).**
The check summary tests "bounded original dual vertices versus … unit double-cover maxflow" with vertex-coordinate grids only; no case uses geometric grids, delta, or eta. Not a correctness defect, but the packet gives no empirical corroboration of (6) or of the rounding step at `M_v`. *Verification:* add a replay case where some optimal vertex coordinate falls strictly between geometric grid points and above the last geometric point below `M_v`, confirming `q_v ≤ (1+eta)p_v` and the cover cost `c.q`.

**2. Low — Section 7 impossibility remark (HETEROGENEOUS…LIFT.txt L126–130) depends on class match.**
The argument "exact positive same-owner representation ⇒ transferred 3/2 ⇒ contradiction with sharp factor 2" is valid only if the cited factor-2 lower bound is for the same mechanism class (TCWM with coalition-total incentives) and the transfer preserves it, which it does given the section-6 argument. Evidence is in an unsupplied root file; cannot confirm.

**3. Low — Coalition monotonicity transfer (LIFT L98–99; FPTAS L75–77) relies on the unit rule's hypothesis form for multi-vertex owners.**
Owner i holds copies at every bin of every resource where `b_iv>0`. The transfer is correct if the audited unit-Huber monotonicity holds for coordinatewise (linked) report decreases by multi-vertex owners; B preserves both coordinatewise order and scaling, so either hypothesis form transfers. The dependency file is not in the packet.

## Steps independently verified (no gap found)

- **Unary residualization (L29–40):** `p=gamma+q`, `q≥0` makes `r_e≤0` rows redundant; strong duality holds (primal feasible at 0, dual feasible since no positive-profit zero-resource column). (2) correct.
- **Clipping (L44–52):** if `p_u` clipped to `M_u ≥ w_e/a_e`, then `a_e M_u ≥ w_e`; `c≥0` so cost does not increase; all-M vector feasible, P nonempty compact.
- **Primal transport (L65–80):** heights lie in `[0,M]`; interior points give `l_I<s, l_J<t` hence strict (3); bin load `≤ a_e|I|x_e` per activity, summed `≤ |I|c_u`; lifted value `Σ w_e x_e`.
- **Dual cover (L82–90):** uncovered edge gives `a_e l_I+b_e l_J ≥ a_e p_u+b_e p_v ≥ w_e`, contradicting strict (3); `p_v` is a grid point so covered width is exactly `p_v`; cost `c.p`.
- **Cramer bound (FPTAS L36–46):** Leibniz gives `|det| ≤ n!H^n`; positive coordinate ⇒ numerator a nonzero integer ⇒ `≥1/D`. Lower-dimensional case handled correctly via n independent active normals.
- **Geometric rounding (L59–71):** for `p_v` above the last geometric point `g_K<M_v`, `q_v=M_v ≤ (1+eta)g_K < (1+eta)p_v`; zero coordinates round to zero; `F_res=0 ⇒ G=0`.
- **Factors:** `(3/2)(1+2eps/3)=3/2+eps`; `2(1+eps/2)=2+eps`; `gamma.c≥0` absorbed since factor ≥1. Coverage and monotonicity use only exact graph properties, not (6). Marginal-floor caveat (L87–91) is correctly stated.
- **Bit complexity (L93–112):** `log(1+eta)≥eta/2` for `eta≤1` holds; endpoint bit length `O(K·bits(eta))`; edge tests `mK^2` exact comparisons.

## Scope limitations

- Unit-Huber, full-OUT, exact solver, and root lower-bound files not supplied; treated as audited inputs.
- No tests run; no files inspected beyond the packet.
- Priority/novelty not assessed per instructions.

## Verdict

**No findings in reviewed scope.** The reduction and FPTAS proofs are complete as written; the three items above are evidentiary gaps and dependency caveats, not errors.
