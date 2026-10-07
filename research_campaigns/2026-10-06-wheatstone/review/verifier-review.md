**Provisional verdict: no concrete errors found in reviewed scope.** The script certifies exactly what it claims — a rational *lower bound* on the actual payment drop (ideal drop minus a simplex tail bound), not exact payments — and the pieces I could check by hand are consistent with OBSTRUCTION_CANDIDATE.txt. The most important point is a scope limitation, not a bug: the script never evaluates the k-bridge payment itself, so the lower bound's validity rests on proof formula (3) and inequality (4), which verify.py imports from the proof rather than checks.

## Findings

No defects of severity ≥ Low identified. Items checked:

**Cut/coalition enumeration (verify.py 21–31, 107–108, 122–128, 136–142).** `vertex_cuts` enumerates vertex sets containing s and excluding t, collecting outgoing edges; `minimal` filters by inclusion. Hand-derived minimal cut families for both the 5-edge bridge (`BRIDGE_CUTS`) and the k=10 graph match proof eq. (1), with edge indices consistent with the edge list at line 123 (x=0, y=1, z=2..11, w=12, h=13, p=14, r=15,16). Minimizing over minimal cuts only is sound for nonnegative capacities. Coalition-value preservation is checked over all 2^17 masks for both profiles.

**Fixed-owner comparison (129–131).** `low`/`high` differ only at index 0 (18 vs 19 in scale-20 units = 9/10 vs 19/20); grand maxflow asserted equal to 20 at both.

**Effective caps (38–46, 134–135).** `graph_caps` = min(c_e, mincut(s,a), mincut(b,t)); exact on a DAG by the vertex-disjointness argument (any shared vertex would close a cycle through a→b). Hand-recomputed caps: D_x=x, D_y=ε, D_z=x, D_w=x+ε, D_h=x, D_p=1, D_r=1/2 — matches `ds` and proof eq. (2).

**Conditional tests (57–73, 112–120).** `conditional` computes min(X+a, b)−min(a,b)=min(D_e,(b−a)_+) in units scaled by 2 (u∈{0,1,2} encodes 2U, hence `2*d[e]`); consistent. I also re-derived proof eq. (3) from the cut family: b−a = Z+min(H,(W−Y)_+) ∧ (R−P−A). Correct.

**Moment arithmetic (84–90).** Eq. (6) re-derived by integrating j·a^{j−1}(1−a/ε)(1−a/b); matches `moment`. `p4` and eq. (7) assembled correctly.

**Independent CDF ideal (93–99).** E[min(R,S+x)]−E[min(R,S)] with S=P+A equals E[min(x,(R−S)_+)] in all three cases (R≤S, S<R≤S+x, R>S+x); A, P, R distributions match proof §3. `expectation` with upper=1 is valid since R≤1 and the normalization guard fails closed.

**Error bound (150–157).** Pr(Z<1) ≤ (1/x0)^k/k! with x0=9/10 gives (10/9)^10/10!; applied only to the low profile, as the proof requires (high side uses z≤I). Ratio check for k=11..100 matches the proof's (10/9)/(k+1)<1.

**Dependency/fail-closed.** `require` raises `ValueError`; missing prior module raises on `spec.loader`; `graph_caps` guards `s != t` before `min()` on possibly-empty cut sets.

## Scope limitations

- Proof eq. (3) and the sandwich (4) are not exercised by code on the k-bridge network; I verified them by hand only.
- Hard-coded rationals at lines 149/152 were not recomputed by me; any mismatch would fail loudly.
- The 5-edge monotonicity check is a 3-point-per-coordinate grid, not a proof (acknowledged in docstring).
- Correctness of the imported CDF algebra is assumed from its prior audit.

## Verdict
No findings in reviewed scope.
