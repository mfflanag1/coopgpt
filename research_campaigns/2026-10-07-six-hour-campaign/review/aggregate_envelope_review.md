**Provisional verdict: no findings in reviewed scope.** Every formula, cut count, effective-capacity value, mean, Hoeffding/Chebyshev constant, and union-bound arithmetic in the note checks out by hand; the only dependency I could not verify from the packet is the exact definition of the payment rule and envelope (see Scope limitations).

## Findings

**No correctness findings.** Items I re-derived independently:

- **Cut enumeration (§2).** Type (i): if e is cut, the only surviving paths are y_i–h_i; one of each per branch, minimality holds. Type (ii): e uncut forces all Z; per branch h_i or {y_i,g_i}. 2^{m+1} per module; series composition confines minimal cuts to one module; R bundle is a single cut. K=2^{401r+1}+1 correct.
- **Effective caps (4).** D_e=min(q,prefix≥a+1,suffix=1)=q; D_g=D_Z=q via prefix q; D_y=a/m; D_h=min(2, q+a/m, 1). Unchanged in other modules because the lowered module still has raw flow a+t>1 and 1+a/m ≤ a+t. The m≥6 remark is actually unnecessary (suffix bound 1 already dominates), not an error.
- **Means.** (5) integrates correctly to u/2−u²/(6v); A_high=3/5−6/(25m), A_low=11/25. (13) gives u[1/3−ρ/6+ρ²/30] via Beta integrals (1/3, 1/12, 1/30); A_low=166/625 correct.
- **Concentration.** Range sums a²/m and k·t²=9/(10m); exponents m/200, m/800, 9409m/4500, 1849m/1125000, 1024m/1125 all recompute exactly. Chebyshev 1/120 and 5/72 correct. Union totals 23/60 and 457/2304 correct given r≥4, e>2.
- **Good event ⇒ e_j ∈ W.** Containing score ≤ t+A_low <.48 (resp. <.31), all competitors >.53 (resp. ≥47/150>.31), strict inequality, independent of U_{e_j}. Payment t·Pr(good) > t/2.
- **Passage to one profile.** Each y_{e_j}(c) ≥ z_{e_j}(c^{t,j}) uses only the focal owner's own unilateral underreport; summing suprema over distinct owners at the single profile c is legitimate and does not conflate profiles. §5's p≥y argument for any own-monotone majorant is correct.
- **Simple DAG (§4).** Lifted minimal cuts use exactly one copy per subdivided edge; 4^m and 4^m2^k counts and 2^{19201r}≤K≤3·2^{19201r} verified. Random path cap qV with V=min(U₁,U₂) correct; summand ranges still a/m.

**Low (presentational):** §4 asserts Q≤53/150<.36 but only the lower bound Q≥47/150 is needed. Harmless.

**Low (verification coverage):** `aggregate_envelope.py` simple cases use k=1, R=2 and only n≤16 for exhaustive vertex-cut checks, so the parallel-Z subdivision and multi-module simple regime are tested only lightly. The analytic argument carries the burden here, and I found it sound.

## Scope limitations

- The rule's payment convention (z_e = D_e·Pr(e∈W), used in (11)) and the envelope definition (sup over own reports ≤ c_e) are defined in files outside the packet. If payments were instead E[D_eU_e·1(e∈W)], constants halve but the Ω(K^{1/401}/log K) order survives.
- `flow_verify` (effective-cap/cutset oracle) was not supplied; I cannot confirm the script's assertions ran as reported.
- No tests executed by me.

## Verdict

**No findings in reviewed scope.** The superlogarithmic aggregate-envelope lower bound and its simple-DAG variant are supported by the supplied argument; the only unverified element is the external payment/envelope definition, which affects constants, not the order.
