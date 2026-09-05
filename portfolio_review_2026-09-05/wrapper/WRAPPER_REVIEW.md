# Historical strict/equality/orbit record-wrapper review and scratch fix

5 September2026. Scope limited to the three currently used record wrappers. Original repository files were not changed. Proposed complete replacements and a unified patch are in this directory.

## Concrete findings

1. **Incomplete row sets are accepted in ordinary Python.** The strict and equality wrappers check only the reported case_count=15 and iterate whatever rows are present. They never prove that all15 distinct sign cases are actually present. Setting rows=[] while retaining the declared count emits a PASS with checked=[] in normal Python and under -O. Missing and duplicated rows also pass. The orbit wrapper likewise trusts aggregate constants and does not require its actual rows to cover all three SELECTED cases. This is a false-positive validation result in the default interpreter, not merely an unsupported -O invocation.
2. **Python -O removes material proof-record gates.** All three wrappers use assert for status, UNSAT and proof-hash checks. Under -O, altered CPC bytes or a recorded Ethos status of incorrect can pass. The strict and equality wrappers also accept altered SMT2 bytes under -O. The orbit wrapper's explicit formula byte-regeneration test survives -O, so its formula-tamper behavior is different and must not be overstated.
3. **Several metadata/completeness checks are absent even normally.** Examples include direction counts not matching the retained menu; reported proof byte counts not matching actual files; orbit row counts not matching rebuilt groups; and an empty orbit-ablation list satisfying all(...) vacuously. These omissions weaken what the PASS record establishes.

No evidence was found that the currently stored audit rows were actually missing: valid frozen records passed normal checks. The negative cases were created only in scratch to expose validation blind spots. These findings do not by themselves refute the six-player theorem or demonstrate that any stored CPC proof is invalid.

## Proposed repair

The three self-contained replacements use ordinary RuntimeError guards that remain active under -O. They check the exact set of15 sign cases with positive and negative blocks and total size6, or exactly the three selected orbit cases. Counts are computed from actual distinct rows, retained menus and rebuilt orbit groups. Case labels must agree with role counts. Zero-length retained menus remain allowed when the base constraints already suffice; their reported counts must still agree.

Proof-record checks retain and strengthen status/hash gates with actual byte-count consistency. The orbit wrapper continues exact formula regeneration, validates all three original rows against the complete source audit, checks selected-orbit lists and actual assertion/direction totals, and requires complete nonvacuous orbit/anchor/blocker-ablation metadata where applicable.

These are **record-integrity wrappers**, not fresh external CPC proof checkers. The replacements explicitly say that they do not rerun Ethos. If formula/proof files and every corresponding metadata record were coherently forged, hash consistency alone would not establish mathematical validity. The release must retain its actual solver/formula/CPC checking stages. Other assert-based tools in the legacy pipeline are outside this bounded patch and require their own assessment or an explicit release-interpreter guard.

## Artifacts and reproduction

- proposals/: complete replacements for the three wrappers.
- ordinary_guards_and_coverage.patch: unified patch against the original repository files; not applied to originals.
- worktree/: scratch copies of supporting modules, frozen records, formulas and CPC objects, with old_ versions of each original wrapper for comparisons.
- test_wrapper_controls.py: runs valid data and tampered copies under both normal and -O Python, comparing originals with proposals; it restores every mutated scratch file in a finally block.
- wrapper_control_results.json and control_test.log: machine-readable outcomes and readable progress/results.

Run with the supplied environment:

    /private/tmp/coopgt-research-20260904/.venv/bin/python test_wrapper_controls.py

The test suite requires every valid original/proposed baseline to pass, and every proposed negative control to fail in both interpreter modes. It records original behavior without assuming every original control is bypassed; notably orbit-formula regeneration is already fail-closed.

The final test outcome is recorded in wrapper_control_results.json and TEST_SUMMARY.json once the running suite completes.

## Completed test outcome

All six proposed valid baseline runs passed (three wrappers, normal and -O). All34 mutated inputs were rejected by every proposed wrapper in both applicable interpreter modes:68 required rejections. The original wrappers accepted19 of these corruptions in ordinary Python and33 under -O. An additional zero-byte CPC control was accepted by the original strict wrapper under -O and rejected by its replacement. The orbit wrapper correctly rejected formula-byte changes even before the patch, including under -O. All mutated scratch data were restored and compared by SHA256 with the unchanged source files. TEST_SUMMARY.json records the complete counts and proposal hashes.
