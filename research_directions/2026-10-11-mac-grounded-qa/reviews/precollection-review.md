**Provisional verdict: no blocking findings in reviewed scope.** Most important item: pre-launch risks are environmental (grammar support for `["string","null"]`, runtime-parallel log pattern for Qwen3:32b on 0.20.0, unpinned official scorer copy in tests), not code bugs.

## Findings

**1. Low — official scorer used for the isolated comparison is not hash-pinned** (`test_design.py:18-37`). `source_dir()` accepts any `official_evaluate.py` from three locations (including `/tmp/coop-qwen32-build/sources`) without a SHA check. The "matches original scorer" claim therefore depends on an unverified file. Verification: record and assert the SHA256 of the official `evaluate-v2.0.py` in the test and in FREEZE.json. (I manually compared `normalize_answer`/`token_f1`/empty-gold handling against the official order lower→punct→articles→whitespace and the `[''] ` fallback; they agree.)

**2. Low — scoring can abort the stage instead of marking schema failure on exotic parser errors** (`design.py:177-180`, `calibrate.py:107-108`). `score` catches only `ValueError/TypeError/UnicodeError`; `RecursionError` from deeply nested output, or a non-string `response` chunk causing `''.join` to raise `TypeError` *outside* `score`, would be classified as infrastructure abort. With grammar-constrained `format` this is practically unreachable, but the semantic/infrastructure boundary should be explicit. Verification: add a test with 1100 nested `[` and a `response: null` chunk.

**3. Low — unverified assumptions that will surface only at warmup** (`design.py:24`, `server_control.py:218-220`):
- Ollama 0.20.0 must accept `type: ["string","null"]` + `additionalProperties:false` in `format`; a 400 would abort as transport failure (acceptable, but confirm before scheduling battery time).
- `verify_loaded` requires exactly `[1]` from `n_seq_max|Parallel|--parallel` log patterns. If Qwen3:32b runs on the newer engine with different log wording, `parallel == []` fails closed at warmup. Protocol does not mention a pre-launch dry check of this regex for this model.

**4. Info — single 1800 s budget spans both stages** (`calibrate.py:160`, `:41,62`). Dev (12 + warmup + ~60 s load) and confirmation (36 + load) share one deadline with 300 s headroom; at ≥35 s/request confirmation would abort mid-stage as "unobserved". Consistent with protocol, but worth a timing dry-run on the 32B model.

**5. Info — FREEZE.json coverage not visible.** `check_freeze` only verifies files listed in FREEZE.json; `development.json`/`confirmation.json` must be included and should equal `build_dataset()` output. Cannot confirm from packet.

Checked and found correct: duplicate-key/NaN/Infinity/extra-key/trailing-text rejection; literal-null requirement with `''`/`'the'`/`'.'` rejected; empty-normalized gold exclusion; article-disjoint 12/23 partition matching SELECTION.json; no paragraph or ID reuse across phases; `wire_job` excludes gold/label/title (test canary); top-level `think:false` sent and retained, any non-empty `thinking` aborts; gate thresholds (11/5/3; 33/16/10/5) match PROTOCOL; `exact_match` requires `schema_valid`; killpg only on verified new-session pgid ≠ own pgrp, bounded escalation, unload verified before terminate; original 11434 idle, AC/battery≥60 with ioreg cross-check, thermal check before/after each request.

## Scope limitations
No FREEZE.json, clock_bridge.py, test_client.py, development/confirmation.json, or official evaluate script in packet; no tool execution; Ollama 0.20.0 API behavior asserted from code, not tested.

## Verdict
No blocking findings in reviewed scope; items 1 and 3 should be resolved before dispatch.
