## Provisional verdict
**Findings (non-blocking).** No reproducible false-PASS path found in the reviewed code. The strongest concrete issue: `reproduce_campaign.py:64` records `'assertions_enabled': True` as a report fact, but that value is hardcoded and is never measured in any child process — the only thing actually enforced is the parent's `sys.flags.optimize` (line 31) plus stripping one env var (line 73). The remediation is correct for the known vector (children are spawned as `[sys.executable, source.name, ...]`, so `-O` cannot be inherited through argv, and `PYTHONOPTIMIZE` is removed), but the recorded claim is an unverified assertion, not evidence.

## Findings

**1. Unmeasured `assertions_enabled` claim — medium, non-blocking**
`reproduce_campaign.py:64`, vs. enforcement at lines 31 and 72–73. Nothing in the report distinguishes "child verified unoptimized" from "parent assumed it." *Verification:* add a one-line probe subprocess under the same `checker_environment` emitting `sys.flags.optimize`, and record the observed value per job; or record whether `PYTHONOPTIMIZE` was present and removed. Then `assertions_enabled` is derived, not asserted.

**2. Child environment is not hermetic — medium, non-blocking**
`reproduce_campaign.py:72` copies all of `os.environ` and removes only `PYTHONOPTIMIZE`. `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP`, `sitecustomize` on the path all persist. This is a deliberate trade for the existing NumPy/SciPy install (consistent with `reviews/portable_delivery_final_audit/REPAIR_DISPOSITION.txt:21-22`), but it means replay results are environment-dependent; the report should log the retained `PYTHONPATH`.

**3. No binding of copied checkers to expected hashes — low/medium**
Lines 93–98 verify copy fidelity (source↔copy) but never compare against `PORTABLE_MANIFEST.json`. A mutated checker that prints `{"status":"PASS"}` would be recorded and accepted. `REPRODUCTION_GUIDE.txt:44` is honest ("records their SHA256 hashes"), so this is scope-accurate, not misleading — but the evidence is self-attesting.

**4. `generated_files` conflates fixtures with outputs — low**
Lines 125–126 exclude only `source.name`, so copied fixtures (`PROFILE_TABLE.json`, etc., line 57) and `stdout/stderr.txt` are labeled generated. Matches the acknowledged "nonblocking provenance wording" item.

**5. `--out` is not constrained to lie outside `ROOT` — low**
Lines 42–44 only require nonexistence. A new subdirectory inside the sealed campaign tree would satisfy this, contradicting the docstring's "isolated from sealed research records" and polluting later index/manifest regeneration.

**6. Non-dict JSON result crashes instead of failing cleanly — low**
Line 120: `json.loads('"PASS"')` → `str`, `.get` raises `AttributeError`; report is left `status: 'RUNNING'` with a traceback (exit ≠ 0, so no false PASS). Same class: missing-key lookups in `verify_portable_metadata.py:74,81,106,110` raise `KeyError`, bypassing `require`'s diagnostic.

**7. `by_range` discards the source ledger/folder — low**
`verify_portable_metadata.py:51,61`: keys are `(kind,start,length)` and saved paths omit `kind`. Placement checks (lines 85, 115) therefore cannot confirm a required range came from the May ledger rather than another folder. Currently constrained by the shared `archive_bytes` check (line 117), so no present defect.

**8. Footer/tar verification is internal consistency only** — correctly disclosed at lines 126–127; no overstatement found. Guide lines 89–92 accurately match the code (all 334 bodies hashed, header and footer ranges fully accounted).

## Scope limitations
I could not execute anything or inspect the checkers, fixtures, ledgers, or manifests. Unverifiable from this packet: the SHA256 values in both dispositions; "fresh extracted-input replay and corrupted-byte rejection were executed" (guide:95); whether checkers resolve paths relative to `__file__` (if any resolve to repo-absolute paths, the "runs on copies" claim weakens); the guide's "seven fixed-partition fixtures" and M4/M64 coverage claims; no mathematics reviewed.
