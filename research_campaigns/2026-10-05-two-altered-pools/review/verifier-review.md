**Provisional verdict: no correctness findings in reviewed scope.** The exact verifier matches the theorem's formulas and performs strictly stronger finite checks than the proof requires (brute-force coalition coverage rather than Lemma 1's reduction). The most notable limitation is that "boundary preservation" is checked against the same `coefficients` function rather than an archived earlier formula, so it establishes internal consistency, not agreement with the prior campaign.

## Findings

**1. Low — Boundary-preservation check is self-referential** (`verify_two_pools.py:162-174`, theorem lines 7-8, 26)
`old_boundary_checks` builds `expected` from `coefficients(r,h)`, the same function used by `payments`. It verifies the two-pool rule collapses to R^j, but cannot detect a drift of `coefficients` from the earlier campaign's a_h, b_h, c_h. Verification: compare against the earlier campaign's stored numerical payments or an independently transcribed formula.

**2. Low — Integer scaling relies on `lcm` without an exactness assertion** (`:129-131`)
`int(x * D)` is exact because `D` is a multiple of every denominator, so `x*D` is an integer-valued Fraction and `Fraction.__int__` truncates nothing. Correct as written; an explicit `check((x*D).denominator == 1)` would make the no-truncation guarantee self-evident. `D // r` is exact since `r` is an lcm argument.

**3. Info — Reduced-parameter last-low edge hardcodes the target** (`:210-211`)
When `h+1 == r`, `target = c_g` is written by hand rather than derived from `components`/`payments`. Matches Lemma 3-D, but slightly reduces independence. `full_labeled` covers this edge computationally for the seven (k,r) cases.

## Verified correct (by reading)

- `coefficients`: T_h, δ_h, z_h, a_h = (δ−z)_+/(r−h), b_h = 1−z_h match definitions; h<r prevents division by zero.
- `ahead_weight`: e(h,g) = ½∏_{s=g}^{h-1} a_s/b_{s+1}; checks b_{s+1}>0 (always true since z<1); zero products yield weight 0 to the advanced pool, consistent with theorem line 30-31.
- `components`/`payments`: tie → ½/½; h>g → e to h-pool, 1−e to g-pool; outside owners get z/(k−1)=c_h regardless of their own report (theorem line 17-18). Operator precedence at line 73 parses as intended.
- `all_profiles`: `local` excludes only the all-unit mask, so every "altered" pool has ≥1 low owner; count 1 + k(2^r−1) + C(k,2)(2^r−1)² is correct and asserted, confirming no duplicates and full labeled enumeration.
- Coverage loop: all 2^(kr) masks (including empty/grand); v(S)·r = min over pools of subset sums; bit layout j·r+i consistent across `pay`, `marginal`, and `local_capacity`. Comparison pay·D ≥ v(S)·D is exact.
- Marginal top-up: M_i = T − v(N∖i) computed exactly in units via `Q(int, r)`; `fair = max(y, M_i/k)` matches theorem line 130.
- Edges: every low owner of every family profile is raised; closure under increases is asserted; this exhausts all retained one-owner increases (the family is binary).
- `reduced_parameters`: F_h = r·z_h + h·b_h + (r−h)·a_h is k-independent, matching line 19; Lemma 2(i),(ii), the ratio identity, and all four Lemma 3 edge forms (A–D including the r−1 tie) are exercised for r ≤ 40 and four k values.
- No floats anywhere; `max(Fraction, 0)` and `lcm(...)` are exact (Python ≥ 3.9 required for variadic `lcm`).
- `status='PASS'` is only written after all checks complete since exceptions abort before the write.

## Scope limitations

- I did not execute the script; no runtime output or `EXACT_CHECKS.json` is in the packet.
- The earlier one-pool campaign's assignment is not supplied, so "agrees EXACTLY with the earlier assignment" is unverifiable here (Finding 1).
- Finite checks are for (k,r) ∈ {(2,2),(2,3),(2,4),(3,2),(3,3),(4,2),(3,4)} and r ≤ 40 parameter algebra; universal claims rest on the separately reviewed proof.

## Verdict

**No findings in reviewed scope** (correctness). Two low-severity robustness/independence notes; no divergence from the reviewed theorem detected.
