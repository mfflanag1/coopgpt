**Provisional verdict: no blocking findings in reviewed scope; one medium scope gap (zero-face price convention is asserted, not tested independently), two low items.**

## Findings

**1. Medium — Zero-face price values are a convention shared by code and reference, so PASS does not verify them against the accepted theorem.**
`POLYMATROID_ORACLE_PRICES.py:31-32,39` returns all-zero prices when P=0, all c=0, or r(J)=0, and `:68-70` sets zero-capacity rows to 0. A literal "average (r(S),1_{E\S}) along the lower envelope" would give, e.g., q_P=r(E) when P=0 (unique minimizer S=E), or q_j=1 for non-loop j when all c=0 (maximal minimizer L), or q_j = mass of z where j has positive marginal rank for a zero-capacity j. Payments are unaffected (price × 0), but TCWM/threshold claims depend on price values. `POLYMATROID_ORACLE_CHECK.py:13,49-50` hard-codes the same zeroing, so the 195 comparisons are not independent on this point. The note's line 91 correctly limits exactness to "active faces"; lines 29-33 extend to zero faces without citing the theorem's definition. *Verify:* quote the accepted theorem's price definition on degenerate profiles, or prove zero-face price values are immaterial to coverage/TCWM.

**2. Low — Terminal case does not check M == A.**
`PRICES.py:54-55` records an edge whenever the oracle's value ties the endpoint, regardless of the returned mask. Nagano–Kawahara's rule (SOURCE_GATE lines 21-22) tests M = T' (the larger set). Under a correct maximal oracle M must equal A (M ⊆ A by nesting since alpha < z*, A ⊆ M by maximality since A minimizes at z*), so correctness is unaffected, but a defective oracle that returns a non-maximal tie-set passes undetected here. Add `M != A → raise`.

**3. Low — Rank-call count slightly understated.**
Note line 77: "|J|+1 rank calls to find loops and the initial rank." Code makes rr(0), rr(full), and n singleton calls = n+2, plus memoized chain ranks. Cosmetic.

## Verified (by reading)
- Nesting lemma holds strongly with all active c_j>0: any minimizer at z₂ ⊆ any minimizer at z₁<z₂; hence maximal minimizers have positive-length intervals, cuts are strictly increasing, and the `Bad chain order` check (`:62`) is a genuine guard that would fire with a non-extremal oracle. Maximality is therefore required, as claimed.
- Strict case: B ⊊ M ⊊ A with strict rank inequalities follows from affine ordering; `:57` is sound. z*=alpha is impossible in the strict case.
- Count: binary tree with k−2 strict nodes → 2k−3 ≤ 2n−1; enforced at `:64`. Explicit stack, ≤ n pending pairs; no recursion depth issue.
- Oracle sign convention (`:48`, a=zP, minimize a·r(S)−c(S)) matches argmin of zP r(S)+c(E\S). `ordinary_to_maximal_sfm` is correct (n+1 calls).
- Tied all-at-once breakpoint (free matroid test, z*=1) handled; G(1)=1/2 on both branches; all-Fraction arithmetic; floats rejected.
- Test counts (195/16/32) match loop structure; test rank is normalized monotone submodular.
- Exponential vs polynomial: `exhaustive_maximal_sfm` and the 2^m rank table are the exponential test backend only; the note (lines 96-104), docstring, and JSON state this explicitly. Polynomial claim is correctly conditioned on an external exact maximal-SFM routine and bounded encoding; no overclaim found.

## Scope limitations
Accepted theorem file, the three cited sources, and test execution are outside the packet; I cannot confirm the Iwata–Orlin real-valued maximal-minimizer property or the theorem's degenerate-profile price definition. Holding-box assertions are mechanism-level and not reviewed.

## Verdict
Findings (non-blocking): the corollary and implementation are correct on active faces; zero-face price conventions require confirmation against the accepted theorem before this note is accepted as "exactly the accepted rule" on all profiles.
