**Provisional verdict: findings (disclosure/interpretation defects; no computational errors found in reviewed code).** Most important: the ~0 selector difference is structurally underexplained, and `run_summary.json` under-itemizes ~77 silently dropped holdout observations.

## Findings

**1. Missing-row disclosure is incomplete in the artifact (Medium).** `run_gate.py:110` sets `last=None` after any sentinel row, so the *next* valid day also yields no difference, but only the sentinel row is appended to `excluded`. Arithmetic check: 2019–2025 has 1827 weekdays; `run_summary.json` lists 77 sentinel dates → 1750 valid rows; 1750 − 77 = 1673 = reported `holdout_n`. So exactly 77 holiday-spanning quote changes (4.4%) are dropped without itemization. Weekends (no row) are spanned while holiday rows are not — an asymmetric convention. POST_OUTCOME_QA_PLAN.txt acknowledges this, but `run_summary.json` does not; `data_audit.json` is not in the packet. Direction: the dropped intervals are multi-day (e.g. Fri→Tue) and higher-variance, so their omission likely *flatters* calibration; the failed calibration gate is directionally robust. Verify via the declared diagnostic rerun.

**2. d ≈ 1e-17 in all 84 months needs a structural explanation before "selectors coincide" is reported (High, interpretive).** The book has exact offsets: q({1,4}) = (20,0) = q(N), q({2,3,5,6}) = (0,0). Hence every core allocation satisfies y(1,4) = b₁+b₄−r and y(2,3,5,6) = b₂+b₃+b₅+b₆ exactly, collapsing core dimension. Machine-precision agreement between lex-max-min and lex-min-max across 84 covariances is as consistent with a (near-)singleton core as with genuine selector agreement. If so, the material gate was untestable for this book, and CONTRACT.txt line 13's "not tuned separation witnesses" needs qualification. Verify from `results.json` (not in packet): per-month `stages[0].fixed_indices` (does stage 1 freeze all six coordinates?), `distance_from_euler_fraction_T` (≈0 would indicate singleton core), and cap-restricted results.

**3. Unit-level failure not labeled (Low).** Protocol §Gates requires reporting which unit fails. Rolling ratios: units 1,3,4,6 and aggregate fail; unit 5 = 1.2605 > 1.25 also fails; only unit 2 (1.238) passes. `run_summary.json` gives positional arrays only.

**4. Vacuous pre-period provision (Low).** 2010-01-01 is a sentinel row, so the December 2009 observation is never differenced; first training difference is 2010-01-05 (matches `training_start`). Harmless but the protocol's "preceding valid observation" clause had no effect.

**5. Lex tolerance (Low).** Frozen-coordinate test uses 1e-8 (`line 55`) against LP tolerances 1e-9; near-degenerate coordinates could be misclassified, bounded by the 1e-7 residual gate in `verify`.

## Verified as correct (by reading)
- Coalition matrix covers all 63 nonempty subsets; `costs[-1]` is the grand coalition; constraints `My ≥ v`, Σy = T, cap on Σmax(y−b,0) ≤ L/T·T; infeasibility returned as infeasibility.
- Lex stages: level LP, then max/min probe per active coordinate on the optimal face; "universally fixed" logic is correct. Self-check values [2,1,1,1,1] and [4/3,2/3,4/3,4/3,4/3] agree with my hand derivation.
- Units: Q in $k/bp × Δy in bp → $k; normalization by B with explicit `_thousand_dollars` outputs; proportional/Euler formulas correct.
- Chronology: window = 252 differences strictly before first scored difference; checked at line 137; no lookahead.
- Tail mean with fractional boundary mass (99.2 check correct); ratio vs κ = φ(z)/α; block bootstrap circular, seed 20261025, aggregate column.
- Aggregate ≡ unit 1 series (identical 1.7786), per amendment.

## Scope limitations
`results.json`, `daily_scores.json`, `data_audit.json`, freeze hashes and raw CSV not supplied; amendment's sequencing claims unverifiable; I did not execute code.
