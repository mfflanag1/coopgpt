**Provisional verdict: no load-bearing defects found in reviewed scope** (static review only; I could not execute the script or inspect the raw parquet, `M100_PANEL_INSPECTION.json`, or `M100_PANEL_SUPPLEMENT.json`). Most important item: the optional reference comparison hard-indexes keys I cannot confirm exist in the preserved INSPECTION report; a missing key would turn a valid replay into `ERROR` rather than a false `PASS`, so this is a robustness issue, not a correctness one.

## Findings

**1. Low — reference comparison depends on unverified key names** (`reproduce_m100_gate.py:286-295`)
`original["node_count_per_time_histogram"]`, `original["all_observed_nodes"]`, `original["preselected_nodes_0_and_1"]` and `report["simultaneity"][name]` are indexed directly. The supplied SUMMARY shows `all_observed_nodes`/`preselected_nodes_0_and_1` but no histogram key; INSPECTION may differ. Also `inspection["simultaneity"]` names must be a subset of `{ps0_input_power, ps1_input_power, total_power, psu_sum, triples}`. Failure mode is `KeyError` → `status: ERROR` (fail-safe, not silent). Verification: run with `--reference-dir checks/`; fix by reporting a structured "missing reference key" difference instead of raising.

**2. Low — order-dependent float in reference check** (`:282-283`, `:244`)
`inspection["triples"]` is compared wholesale, including `mean_relative_delta`, a DOUBLE `avg` whose summation order depends on `threads` (fixed at 2 here; original run's thread count unknown). `rel_tol=1e-12` likely absorbs ULP drift over 4.75M terms but is not guaranteed; a spurious `DISCREPANCY` is possible. `mean_delta_w` (integer avg) and `quantile_cont` are deterministic. Verification: compare that one field after a real run; consider a slightly looser tolerance for that key only, documented.

**3. Low — output written outside the try block** (`:363-365`)
`json.dump(..., allow_nan=False)` runs after `open("x")`. If any value is NaN/non-serializable (only plausible on degenerate inputs, e.g. empty tables → `avg` NULL is fine, but `quantile_cont` on empty input returns NULL, also fine; NaN only via 0/0 paths), a partially written file remains and the exception is uncaught. Fix: serialize to a string first, then open/write.

**Verified as sound (static):**
- Timestamps: `epoch_ns` on TIMESTAMPTZ → exact ns integers; `//1_000_000` exact for ms-stored values; sub-second/sub-ms checks present; `TimeZone='UTC'` set (relies on ICU bundled in the Python wheel; if unavailable → `ERROR`, not silent).
- Node identity: `try_cast` range check plus round-trip string equality catches `' 0'`, `'+0'`, `'1e2'`, `'0.0'` style aliases; distinct-node = 980 with zero unmapped/noncanonical implies exactly `'0'..'979'`, so `count(DISTINCT node)=980` per time is a valid all-node test.
- Joins: grouping to `(metric,node,t)` before joining makes PSU and triple joins 1:1; conflicting/all-null/negative keys excluded; mixed-null retained only if values agree, counted separately.
- Run detection in `times_summary` is correct (strict-increase guard, `run` reset on non-20s gaps, endpoints = `(cells-1)*20s`). Global gap uses distinct times per metric with `NULLS LAST`.
- `ACCEPTED` appears only in `compare_reports`; `NODES`/`CADENCE_NS` are definitional, not accepted results. Reference units (`gap`/`from_ms` in ms → ns) convert correctly.
- Safety: scratch DB in `TemporaryDirectory`; raw dir and reference dir only read; `--output` must be new and outside `--raw-dir`, opened with `"x"`; input hashes rechecked post-analysis; `autoinstall/autoload_known_extensions=false`; no network code paths.

## Scope limitations
No execution; raw parquet, INSPECTION/SUPPLEMENT JSON and DuckDB 1.4.1 function behavior not independently verified. Embedded targets were not used to infer correctness.

## Verdict
No verified defects; three low-severity robustness items above.
