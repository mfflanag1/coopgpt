**Provisional verdict: findings (non-blocking for gate logic; evidence/robustness gaps). Most important: PREPARATION_CHECKS asserts `client_answers_equal_existing_qualified_outputs: true` while `real_query_oracle_runs: 0` and `metal_commands: 0` — the claim is unsupported by anything in the packet.**

## Findings

**1. Medium — unexercised qualified-answer comparison path / unsupported check claim**
`service_driver.py:169` compares `top != expected[str(qid)]` where `expected` is raw `qualified_top10.json`. No test passes `expected` (tests/test_service.py:94,103 use `None`), and `PREPARATION_CHECKS.json:3` claims equality with qualified outputs despite `:18 real_query_oracle_runs: 0`. If the file's shape differs (list pairs, float distances, string keys ordering), every warmup fails at `:355` and the authorized phase aborts at window 1. Fix: add a unit test asserting `qualified_top10.json` is `{str(q): [{'id': int, 'distance': int}]*10}` for all 100 IDs, canonically ordered, distances in `0..8_323_200`; reword PREPARATION_CHECKS to state only what was checked (format), or delete the claim.

**2. Low/Medium — timeout evidence is uninformative; arrival thread failure uncovered**
`service_driver.py:118` `lines.get(timeout=)` raises `queue.Empty`; the recorded failure (`:226`) becomes `"Empty: "`, which is poor "timeout evidence" (PROTOCOL:142). Fix: catch `queue.Empty` and raise `TimeoutError(f'No backend response within {timeout}s')`. Separately, `offer()` (`:184-191`) has no exception handling; a thread crash leaves requests never offered and the main loop spins until the *shared* 600 s phase deadline (`:200`). Fix: wrap in try/except that stores the exception and set a flag the main loop checks.

**3. Low — arrival-validity risk from GIL scheduling (not a bug)**
At 200 req/s, inter-arrival ≈5 ms; the arrival thread competes with `validate_response`/`json.dumps`/file flushes (`:214-223`) under the default 5 ms switch interval. p99 ≤2 ms (`:251`) may fail for host reasons, invalidating the phase per protocol. Consider `sys.setswitchinterval(0.0005)` recorded in HOST.json before the freeze; otherwise note the risk in the approval.

**4. Low — build evidence gap**
`PREPARATION_CHECKS.json:24` `logs/build.log` hash `e3b0c4…b855` is SHA-256 of the empty string, yet notes claim initial build logs were retained. `swift_build_exit: 0` therefore has no captured log.

**5. Info — phase watchdog budget**
600 s covers 16 calibration windows including 16 cold Metal startups (cap 30 s each = 480 s) + warmups + ≥68 s of scheduled arrivals. Likely fine, but a slow host could truncate late windows into "unserved_after_offer" and void calibration. Accounting is correct; just note it.

## Verified consistent (no finding)
- Assessment: `assess` matches PROTOCOL §§77-83, 98-111 (all-request denominators, +inf→null p95, 99% per window, median ≤0.90 and ≥3/4 ratios, highest eligible rate from immediate windows only, invalid/incomplete → no selection/pass).
- Scheduling: planned-arrival wait cap not restarted (`:80`), FIFO, 16-cap, immediate singleton; seeds disjoint; identical pair schedules.
- Latency: delivery after full decode/validation, measured from planned offer (`:220-222`).
- Arithmetic: `reconstruct` bounds/integrality; `ok` requires oracle full-sort equality (`main.swift:113`); Float32 partial sums ≤8.3M < 2²⁴ exact. Synthetic fixtures in Python/Swift agree.

## Scope limitations
Cannot verify file hashes, binary, data files, `qualified_top10.json` contents, test execution, or real MPS behavior. No Git diff available.

## Verdict
Findings — none invalidate the gate logic; item 1 should be resolved before the parent authorizes a freeze.
