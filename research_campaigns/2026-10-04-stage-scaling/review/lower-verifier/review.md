## Verdict: findings — no blocking error in the proof; the verifiers have evidential gaps

I could not execute anything; this is a static read of the packet only. The `lp-*.json` inputs and the `EXACT_*.json` outputs are not in the packet.

## Blocking errors

None found. I rechecked every inequality in `LOWER_BOUND_FAMILIES.txt` by hand.

- **Symmetrization (l.13–23):** sound. Averaging over the pool permutations and owner swaps preserves nonnegativity, coverage, budget and one-coordinate monotonicity, and the Y→X and X→Z raises land on the owner types claimed.
- **Profile X:** T=2, both coalition values are right, and a ≥ 1−2β and d ≤ 4β/(k−1) follow.
- **Family I:** A ≥ 1/2−β and A ≤ d give β ≥ (k−1)/(2(k+3)), which is 1/6 at k=3 and 3/14 at k=4.
- **Family II:** T=3 and k(1−2β) ≤ 2+3β give β ≥ (k−2)/(2k+3).
- **Limit 1/2:** correct as a supremum (not attained); the families cross at k=9.
- **Separation:** 3/14 > 1/(2e) is equivalent to e > 7/3, which holds.
- **`verify_duals` implication:** sound. Signs are right, the floor row's core witness is valid, and nonpositive residuals with y ≥ 0 give β ≥ rhs/b.
- **`verify_thresholds` integration:** the signed subset-sum knots, CDF/density pieces and [0,1] domain are correct. I confirmed 7/24, 7/48, 43/60 and 17/60 by hand.

## Findings (non-blocking, important)

1. **Medium — the budget check is vacuous (`verify_thresholds.py` l.116–120).**
   - Evidence: the loop gives R=4 for k=2,3 and R=5 for k=4,5, so the bound is 6T or 7T. Every tested pool has at most 4 owners, so ρ_j ≤ 4 and the payment total is at most 5T regardless of the probabilities.
   - Consequence: no instance can fail, so Claim C's tail bound has no finite support from this check.
   - Verify: assert p_j ≤ (e/ρ_j)^ρ_j with a rational upper bound, or add instances with ρ above R+2.

2. **Medium — `verify_duals` does not tie certificates to the theorem (l.49, 55–60).**
   - Evidence: it only checks the bound against each file's own `objective_rational_guess`. It never requires k=3,4 files to exist, to equal 1/6 and 3/14, or to have `floor_rows==0`.
   - Consequence: the l.72 provenance claim and the "no floors" claim are not enforced by code.
   - Verify: add explicit expected-value and zero-floor assertions per file.

3. **Medium — mutation coverage misses load-bearing branches (`verify_duals.py` l.68–76).**
   - Evidence: there are no mutations for "nonpositive payment residuals", "positive beta coefficient", "floor only in bottleneck pool", reversed or equal monotone direction, or an out-of-range owner.
   - Consequence: the residual check is the core of soundness and is untested. The whole `bottleneck_floor` branch is likely unexercised if the calibration file has no floor rows.
   - Verify: add a mutation that drops a budget row, one that swaps `profile` and `low_profile`, and a floor-row fixture.

4. **Low — the separation relies on evidence outside the packet (l.64).**
   - Evidence: the two-pool 1/(2e) ceiling with the H/2 floor is cited, not shown. CONTRACT l.27 words it ambiguously ("under H/3; … protects H/2").
   - Consequence: the strict separation is conditional on that result.

5. **Low — `verify_thresholds` has thin negative controls and some trivial comparisons.**
   - Evidence: the only negative control is floor omission. The seam base `(0,1,1,1,1)` has T=0 for every owner except the first, which inflates `seam_comparisons` with trivial 0 ≥ 0 checks. Integer grids only cover pools of at most 2 owners.

## Optional improvements

- Add an exact script that instantiates the Family I and II multipliers for k=3..N through `verify()`.
- Reject float and bool capacities in `profile`.
- Add a mutated-knot control for the integrator.

## Scope limitations

- The inputs and outputs of both verifiers were unseen, so I cannot say whether any certificate actually passes.
- Claims A–E of the draft were only checked where the verifier depends on them.
- Novelty was not assessed.
