**Provisional verdict: no findings in reviewed scope.** All four audited components check out exactly; the most important observation is only a dependency gap (file 2 §1 relies on an own-incidence RHS lemma not in the packet), not an error.

## Findings

**1. Low — `theory/selection_own_local_weights.txt` lines 20–29: adaptive invariant depends on an unsupplied lemma.**
The all-profile eligibility of `x(b)=L_{w(b)}(v_b)` composes (a) own-weight monotonicity (proved here, lines 7–18, verified: identical stages before i freezes, levels nonincreasing, witness row S forces `x'_i ≥ x_i`) with (b) "own-incidence RHS monotonicity" from `selection_weighted_lex_route.txt`, which is not in the snapshot. I checked (b) independently by the same stage-comparison argument (i-row densities only rise; i freezes no later and at a level ≥ its old level) and it holds, but the packet does not contain the cited proof. Verification: supply the route file or inline the argument.

**2. Low — `theory/selection_own_local_weights.txt` line 1 ("matching square-root barrier").**
The bound is Ω(√n) in n only; `d=(k+1)k^{r-1}` is super-exponential in √n, so against the benchmark `β(n,d)` the barrier matches `n√(2/(n+1))` but says nothing about guarantees like O(log d). Lines 85–86 already disclose this; the title overstates slightly. No correctness issue.

## Verified items (no gap found)

- **Petal technology (file 1 §1, file 2 §2):** `min{X_0, Σ_l min_{P_l} X_j}` and the Leontief `min_q X_q` on `R ∪ [k]^r` are monotone, concave, degree-1 homogeneous; coalition values are exactly 1 iff root + full petal; the full cover polyhedron reduces to the r rows at lines 26/52.
- **Exact lex formula:** `(w_0+rm)/(w_0+m)`, increasing in m, ≥ (r+1)/2 when m ≥ w_0. Correct.
- **Rank bound (file 1 §3):** `(t−1)/(n−1) < 1/2` for `t ≤ ⌊n/2⌋`; `r·2^{-k} ≤ 1/4`; `⌊n/2⌋/n ≥ 1/3` for n ≥ 3; product gives (r+1)/8. Correct.
- **All-profile quantifier (file 1 §4):** pointwise-in-w bound, Fubini over D, then existence of a single π. Correct; technology and ownership fixed; profiles only select the failing point, no illegal ownership change.
- **Exchangeability (file 2 §2):** `(o_s, B_s)_{s=0..k}` is an independent product of a uniform ordered owner tuple and a uniform ordered equal-block partition, hence exchangeable; `P(root strictly unique max) ≤ 1/(k+1)`; union bound `r/(2r+1) < 1/2`. Holds for arbitrary asymmetric, correlated, label- and coordinate-dependent own-local functions.
- **Two-row iff counterexample (file 3):** with `a = r + ½min{r'−r, w_i/(w_j+w_k)}`, both strict ratio inequalities hold; under w, i pays `a−r>0`; under w', `x_j=r'>a` so i pays 0. Realized by `min{y_j, a z_i + z_k}` at unit basis with other owners reporting 0; extra zero/dominated rows do not alter pinning. Own-relative step correct.
- **Projective factorization (file 3 corollary):** ratio-preservation is an equality, so it transfers along decreases too; `g_i` is well-defined independent of j; the n ≥ 3 pivot `k` argument is sound; monotonicity of `g_i` follows from `W'_i ≥ cW_i`.

## Scope limitations
- `selection_weighted_lex_route.txt` and `dual_report_dependent_weights.txt` are cited but absent.
- The "separate rational checker" (file 1 line 81) was not supplied; I did not run anything.
- No literature check performed.

**Verdict:** no findings in reviewed scope (two low-severity completeness notes above).
