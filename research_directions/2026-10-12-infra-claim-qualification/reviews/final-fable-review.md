**Provisional verdict: no material bugs in reviewed scope; blind labels balance 8/8/8 and 4 per source. Most important item: two label-ambiguity notes (case 11 insufficient-vs-contradicted; case 9 two independent single-ID proofs) must match the author file before launch.**

## Blind label table (minimal sufficient sets; relevant IDs)

| # | request_id | Label | Min proof(s) | Relevant | Note |
|---|---|---|---|---|---|
| 1 | 7b008687 | contradicted | {D2} | D2 (D1 optional corroboration) | |
| 2 | 5545862a | supported | {D2} | D2, D1 | Premise "driver/plugin installed" is explicit in claim; D1 is not required for proof, only corroboration. D2 alone should be accepted. |
| 3 | f540b424 | supported | {D1} | D1 | |
| 4 | 78be88e8 | supported | {D3} | D3, D1 | Prefill-vs-decode is only in D3; D1 ("skip computation of shared part") is relevant but insufficient alone. |
| 5 | 333f65d9 | insufficient | — | — | Fractional GPU not addressed in excerpts. |
| 6 | bd05a86c | contradicted | {D3} | D3 | |
| 7 | 43ab6c82 | insufficient | — | — | |
| 8 | a894655c | contradicted | {D2} | D2 | |
| 9 | 1f522109 | contradicted | {D1} or {D3} | D1, D3 | Two independent single-ID proofs; both must be in acceptable_evidence. |
| 10 | 7ae6f123 | supported | {D1} | D1 | |
| 11 | 249821e6 | insufficient | — | — | **Ambiguity**: D1 states caching speeds allocation, but claim asserts a measured outcome on "our training job"; rubric line 14 makes this insufficient. If author labeled contradicted, reconcile. |
| 12 | cc5026c0 | supported | {D3} | D3 | |
| 13 | cf56d7ee | contradicted | {D4} | D4 | |
| 14 | 5fcd7666 | insufficient | — | — | |
| 15 | c846353a | supported | {D3,D4} | D3, D4 | Both required; neither alone is complete. |
| 16 | b6126a81 | contradicted | {D2} | D2 | |
| 17 | 0e8b4de4 | supported | {D1} | D1 | |
| 18 | 0cec5f44 | insufficient | — | — | |
| 19 | 8da5f614 | insufficient | — | — | |
| 20 | 20577571 | insufficient | — | — | |
| 21 | 21f7d9ba | insufficient | — | — | |
| 22 | 8efc7a43 | contradicted | {D2} | D2 | |
| 23 | 3e102eeb | contradicted | {D1} | D1 | D2 is about level 2; not relevant. |
| 24 | e9456337 | supported | {D3} | D3 | |

Counts: 8 supported / 8 contradicted / 8 insufficient; 4 per source section.

## Static check findings

No material bugs found. Verified:

- **Strict JSON** (`contract.py:18-26`, audit via `transport_audit.strict_json` outside packet): duplicate keys and NaN/Infinity rejected; exact key set, enum, ≤3 unique string IDs enforced (`contract.py:36-39`, `audit_runtime.py:34-39`).
- **Citation rule** (`contract.py:40-42`, `audit_runtime.py:44-49`): ids ⊆ valid ∩ relevant and ⊇ some acceptable proof; insufficient requires `[]`. Consistent between scorer and audit.
- **Gate** (`contract.py:45-59`, `audit_runtime.py:60-84`): ≥22, ≥7/≥7, ==8, zero false-support, all schemas valid, bool-typed flags with consistency checks. Both implementations agree on thresholds.
- **No gold leakage**: `wire_job` (`contract.py:28-30`) uses only passage id/text and claim; audit recomputes the prompt from the same fields (`audit_runtime.py:54-57, 211`).
- **No relabeling/reruns**: `cases.json` hashed in FREEZE (`collect.py:31-43`, audit `175-200`); `out.mkdir(exist_ok=False)` and `out.mkdir()` prevent overwriting; failures raise with no retry; all 24 are offered irrespective of quality (`collect.py:70-123`).

Minor (non-blocking): `collect.py` does not invoke `contract.validate_sources`, so offset/hash/evidence-contract validity of `cases.json` relies on it having been run separately plus the freeze hash. Suggested verification: run `python -I contract.py` before freezing.

## Scope limitations
`client.py`, `server_control.py`, `clock_bridge.py`, `transport_audit.py`, `cases.json`, `CONFIG.json`, `FREEZE.json`, and source files not in packet; I did not execute anything or verify source offsets/hashes. Labels are from excerpt text only.

## Verdict
Findings (label ambiguities to reconcile: cases 2, 9, 11, 15); no material code findings in reviewed scope.
