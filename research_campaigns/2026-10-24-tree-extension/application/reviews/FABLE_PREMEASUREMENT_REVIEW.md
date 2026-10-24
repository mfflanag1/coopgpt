**Provisional verdict: findings (one correctness/robustness defect worth fixing before freeze; otherwise code and protocol are consistent in reviewed scope).**

## Findings

**1. Medium — sub-µs early wake aborts the whole 48-case phase (arrival_qualification.py:89–91, 159–160, 226–229, 265)**
`produce()` performs exactly one `stop.wait(remaining)` per request and never re-checks `clock() >= planned_ns`. `reconcile()` then raises `ValueError('Wake ordering')`/`'Early offer'` if `wake_ns < planned_ns` by even 1 ns; `run_case` converts that into `failure`, and `main` treats any `failure` as `aborted` and stops all remaining frozen cases. `threading.Event.wait` is only guaranteed to return "approximately" at the timeout; on CPython/macOS the condvar deadline is commonly derived from the realtime clock (no `pthread_condattr_setclock`), while `planned_ns` is monotonic. Clock slew of tens of ppm over a 50 ms–2.5 s wait can yield a legal microsecond-early wake. The protocol (lines 49–51) says timing-criterion failures must not prune later frozen cases, but this code path makes a timing anomaly an operational abort. I cannot confirm host Python version; this is a design fragility regardless.
*Suggested fix (pre-freeze, then re-run `--prepare`):* either loop `while clock() < planned_ns: stop.wait(...)` in `produce` (then an early `wake_ns` is impossible by construction), or have `reconcile` mark early rows `status='early'` and fail the case rather than raise. Update PROTOCOL.txt wording accordingly.

**2. Low — `switch_interval_changed: False` is asserted, not measured (line 257).** Harmless but is an unverified claim in EPOCH.json. Consider recording the value only.

**3. Low — spurious "CPU load did not run" (lines 218, 230).** `load_state` is written only on thread exit; if `load_worker.join(timeout=.5)` times out, the case fails and the phase aborts. Realistically ~100 µs per stop check, so low risk; noted for completeness.

## Verified consistent (no defect found)
- Denominators: all 50 planned IDs always emitted in RESULT; missing admission → `inf`→`None`, stays in percentile; `qualification_pass` requires `complete`. Nearest-rank p99 for n=50 = max (tested).
- Endpoints: `wake→emitted→send_bytes→admitted` and `received` after `recv_bytes` before parsing match PROTOCOL lines 60–64; `rc<ad` permitted.
- Transport parity: both modes run identical `scheduler`/`produce`, same `Connection` pipe, same relay-thread structure, `time.monotonic_ns` in both (system-wide on macOS).
- Spawn/pipe endpoints: parent closes transferred ends after `start()` in process mode; thread mode defers close until after bounded join; double `Connection.close()` is safe.
- CPU load: started in the consumer process after ready, before schedule send; stopped in `finally`.
- Freeze/authorization: `--prepare` writes `authorized:false`; `--authorization` requires exact plan + sha256 of all four frozen files + non-empty host declaration; test confirms no worker/output before rejection.
- Order: thread/process paired per rate/load/rep with identical offsets; shuffled group order with fixed seeds; disjoint seeds (tested).

## Scope limitations
- No code executed; tests not re-run. No test exercises real `scheduler`, `run_case`, spawn, or pipe behavior — those paths are reviewed statically only.
- Host facts (Python version, clock implementation, spawn latency vs. the ~26 s slack after ~53 s mean horizon) not verifiable here.
- Old serving calibration remains invalid; nothing here bears on it.

## Verdict
Findings. Fix #1 before freezing and re-prepare hashes; then thresholds/protocol must remain frozen through collection.
