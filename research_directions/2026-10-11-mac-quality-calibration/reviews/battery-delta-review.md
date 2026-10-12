**Provisional verdict: no blocking findings in reviewed scope.** Most important item: an infrastructure-aborted request is persisted with `quality_pass=False` (calibrate.py:43–45), which is distinguishable from a semantic failure only via the stage-level `status`/`error` fields — low severity, but worth tightening given PROTOCOL.txt:56–57.

## Findings

**1. Low — aborted request recorded as `quality_pass=False` (calibrate.py:43–45)**
`entry` is appended with `quality_pass=False` before the `row['completed']` check raises. The STAGE.json of an aborted stage therefore contains a request row indistinguishable from a semantic miss except by `status='aborted'`/`error`. Promotion logic is unaffected (`run_gate` rejects non-completed stages; `gate_passed=False` in the except branch), so no false promotion is possible. Suggest `quality_pass=None` until scored, so the per-request record itself matches the protocol's "not a semantic rejection" wording.

**2. Low — CONFIG fields not cross-checked against hardcoded constants (calibrate.py:19,29,33,36,83; CONFIG.json:3,41,53)**
`budget_s`, `request_timeout_s`, `max_output_caps`, `candidate_order` are present in CONFIG but never read; code hardcodes 1800/90/95/100 and `('A','B')`. Currently consistent, but a future CONFIG edit would silently diverge from the frozen behaviour. `main` validates only `model/options/context/lock`. Verification: assert equality or drop the unused fields.

**3. Low — `check_host` overwrite guard admits `'before'`/`'after'` (server_control.py:152)**
The guard only rejects non-power-dict collisions; a caller passing `check_host('before')` would overwrite the launch snapshot and `original_endpoint_idle_before`. `calibrate.py` uses `before_<id>`/`after_<id>`, so not triggered here. Suggest adding `'before','after'` to the reserved set at line 148.

**4. Low — unguarded `killpg` after liveness race (server_control.py:314)**
If the group exits between `_group_alive()` and the SIGKILL, `ProcessLookupError` propagates; `_stopped` stays False and `dedicated_server_returncode` is not recorded, though `_finish` catches it as a `terminate` cleanup error. Harmless to safety (only the verified owned pgid is ever signalled), but wrap like lines 304–307.

**Checked and found consistent:** battery gate requires `allow_battery_quality is True` (bool-typed), pmset `'Battery Power'`, ioreg `ExternalConnected is False`, and integer 60–100 (server_control.py:134–141); `power_values` is applied to the same text pre- and post-`(id=…)` redaction, so `battery_percent` cannot differ between `snapshot()` and `_host_state`; tests at 141–187 cover 59, 60, 100, 101, −1, non-int, connected=True, missing ioreg, and default-strict-AC. Watchdog→`check_host`→`triggered` ordering (calibrate.py:37–40) does not require the owned server to be alive. Forced stop cannot yield `clean_unload_verified=True` (328, 356–357). Budget reservation of 300s before stage/job matches PROTOCOL.txt:62–63.

## Scope limitations
- `client.py`, `design.py`, `clock_bridge.py`, `development.json`, `confirmation.json`, `FREEZE.json` not supplied. In particular I cannot verify that per-job `max_output_tokens` overrides `options.num_predict=192` (CONFIG.json:49) inside `run_trace`; if it does not, the 512/1024 caps and the context-margin computation at calibrate.py:47 would be inconsistent with the actual request. This is the single most useful thing to confirm by inspecting `run_trace`/`wire_job`.
- No tools: tests not executed; real `pmset`/`ioreg` output formats not sampled.
- Battery drain across a ~45-request campaign may trigger a legitimate `<60%` postflight abort; that is protocol-consistent, not a bug.

## Verdict
No blocking findings. Four low-severity items above; one unverifiable step (num_predict override) flagged for confirmation before collection.
