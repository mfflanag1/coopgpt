**Provisional verdict: no material findings in reviewed scope** (one unverifiable config dependency; several scope gaps).

## Findings

**1. Medium (unverifiable) — hard-required CONFIG keys differ from server_control's optional treatment.**
`calibrate.py:24,34,44` index `config['model']`, `config['options']`, `config['context']` directly, while `server_control._check_lock` (lines 129–137) treats `context`/`options` as optional via `.get(...)`. If `CONFIG.json` omits `context`, every stage raises `KeyError` at line 44 *after* the owned server is started and warmup completes, aborting the campaign. This is fail-closed (no false promotion), but it would waste the single confirmation opportunity's budget. CONFIG.json is not in the packet. Verification: confirm CONFIG.json contains `model`, `options`, `context: 4096`, or change calibrate.py to assert them in `check_freeze`/`main` before any server start.

**2. Low — context-margin check is optimistic under Ollama prompt caching (acknowledged).**
`calibrate.py:44` uses `prompt_eval_count`, which Ollama reports after prefix-cache reuse; with `keep_alive=120s` and an identical instruction+schema prefix on every serial request, the reported count may undercount the true prompt length. PROTOCOL lines 33–35 already disclaim this. No code change required for the gate (the server's own truncation log check at lines 53–54 and `verify_loaded` is the real guard), but the `observed_context_margin` field should not be reported as a bound.

**3. Low — budget headroom excludes non-request phases.**
`calibrate.py:28` checks `deadline-110` only before each request; server startup (≤30 s), warmup (≤35 s), and `_finish` cleanup (unload 10 s + terminate ≤12 s) are not budgeted. A budget stop is an explicit abort, so this cannot produce false promotion; it only means the 1800 s figure is a request-loop budget, not an end-to-end bound.

**Checked and found consistent (no finding):**
- Gold leakage: `wire_job` sends only prompt/cap/format; `expected` never serialized; example IDs R9001–R9003 cannot collide with `R0001–R0192`; schema carries no enum/minItems/maxItems.
- Scoring: duplicate-key hook, NaN/Infinity rejection, type/pattern checks, strict `obj==expected`, order-sensitive list equality; `done_reason=length` with valid JSON passes as PROTOCOL specifies.
- Stopping rule: `run_gate` returns after A's confirmation regardless of result; stage abort raises through; tests cover all four branches.
- Dropped/misclassified requests: incomplete row or `TimeoutError` aborts before `quality_pass` can be set; `planned` vs `requests` length exposes missing cases.
- Watchdog: 100 s > 95 s collector hard bound, so it is a backstop; `triggered` flag closes the cancel/fire race; `stop_owned` signals only the verified session-leader PGID.
- Clock arithmetic: stamps appended in monotonic order; `duration_bounds_s` and `bridge_diagnostics` subtract ints before one float conversion; `_require_tolerance` fix excludes `numbers.Rational` from `isfinite` and the 10**1000 regression test exercises it.

## Scope limitations
- Not supplied: `CONFIG.json`, `FREEZE.json`, `CLOCK_CONTRACT.txt`, `test_client.py` fixture, `development.json`/`confirmation.json`, old traces (freshness vs. prior study unverified).
- Cannot verify Ollama 0.20.0 accepts `pattern`/`additionalProperties` in `format`; a rejection would surface as HTTP error → abort, not false promotion.
- No tests were run; host AC is absent so `_host_state('before')` will refuse to launch until connected (by design).

## Verdict
No concrete defects in the reviewed logic that could yield gold leakage, silent request loss, false promotion, wrong clock arithmetic, unsafe signaling, or a stopping-rule mismatch. Resolve Finding 1 against the real CONFIG.json before the run.
