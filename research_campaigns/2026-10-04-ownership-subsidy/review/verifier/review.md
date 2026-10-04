**Provisional verdict: no material defects in reviewed scope.** The direct reconstruction does prove beta ≥ 1/8 for `lp-012.json`; I re-derived that certificate by hand. `lp-01234.json` is not in the packet, so its 13-row/5-profile claim is unverified here.

## Findings

**No defect — `verify_dual` signs and `lp-012.json` (verify_shapley.py:67-110)**
- The rows are encoded correctly as ≥ constraints:
  - budget: `beta·T − Σy ≥ −T`
  - cover: `y(S) ≥ v(S)`
  - monotone: `y_i(c) − y_i(low) ≥ 0`, with `low_i < c_i` and other coordinates equal enforced
- Hand aggregation over profiles A=(1,1,1,1), B=(1,1,1,2), C=(2,1,1,1):
  - beta coefficient: ¼·2 + ¼·2 = 1
  - right side: −1 + 9/8 = 1/8
  - all ten touched payment coefficients cancel to exactly 0
- With y ≥ 0 the inference in the comment at lines 107-108 is valid. The count of 11 rows and 3 profiles matches REPRODUCE.txt.
- Omitting fairness only relaxes the problem, so the lower bound transfers to the full problem. It also holds for budget equality.

**No defect — discovery dual sign (discover_profile_lp.py:16-17, 35)**
- Rows are negated into `A_ub` form and `-res.ineqlin.marginals` gives nonnegative multipliers on the ≥ rows.
- `limit_denominator` output is only a guess; the exact verifier gates it.

**Low — corrupted-certificate control is narrow (verify_shapley.py:144-151)**
- The only mutation is `multiplier='-1'` on row 0, which exercises just the sign guard at line 74.
- The beta-coefficient, positive-residual, right-side, coalition-mask and monotone-pair guards have no negative control.
- By inspection they are sound; this is a test-coverage limitation, not a false-positive path.
- Suggested check: add mutations such as changing a cover coalition, dropping a monotone row, and scaling one budget weight, and confirm each is rejected.

**Low — reported check counts overstate independent evidence (verify_shapley.py:49-62, 131-134, 157-158)**
- `budget` is tautological given efficiency and y = (6/5)·phi.
- `coalition payment` is algebraically identical to `coalition factor`, yet both are reported as 15·n.
- `stronger fairness bound` is identical to `removal marginal bound`.
- When a random capacity is 0, halving gives the same profile, and that trivial comparison is still counted in `own_report_comparisons`.
- Suggested fix: report the distinct checks only, and skip or separately count the `c[i]==0` cases.

**Low — negative control at line 139 does not test the checker**
- It shows that 9/8-scaled Shapley fails on one coalition. It does not feed a bad rule through `check_profile`.

**Informational — input strictness**
- `F(...)` accepts JSON floats as exact binary values, and `isinstance(True, int)` passes for the mask and owner. Neither can produce an invalid proof.
- Malformed input raises `KeyError` or `IndexError` rather than `RuntimeError`; it is still rejected.
- All checks use `require`, not `assert`, so the `-O` flag is harmless.

## Precise limitations of what the stress checks test

- Fairness is tested against the removal marginal M_i, not against H_i. H is never computed, so the fairness check relies on Lemma 2's H_i ≤ M_i. REPRODUCE.txt states this accurately.
- Monotonicity is tested on phi over adjacent grid steps and halvings. This is adequate for the grid by transitivity, but it is not a continuum check.
- "These grids did not improve the known lower bound" rests on a floating-point objective of the fairness-omitted LP. It does not show that a fairness-including finite LP stays at 1/8.

## Scope limitations

- `lp-01234.json` and `EXACT_CHECKS.json` are absent, so the 13-row certificate, the SHA256 match and the reported counts are unconfirmed.
- Nothing was executed.
- The 697/6721 row counts were not recomputed.
- The analytic proof, novelty and sources were not reviewed, as instructed.

## Verdict

No findings of material severity in reviewed scope; low-severity reporting and test-coverage limitations only. For `lp-01234.json`: insufficient evidence.
