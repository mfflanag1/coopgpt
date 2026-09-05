# Startup lifecycle fixes for the three verification runners

All three patched runners now write their RUNNING result before importing scientific or package-local dependencies. Missing dependencies are caught by the existing failure path and replace an earlier PASS with FAIL while preserving a nonzero exit. All edits are confined to copies under this directory; the source packages were not modified.

Only these three files should be applied to the packages:

- [stable_core/verification/run_checks.py](stable_core/verification/run_checks.py)
- [asymptotic/verification/run_checks.py](asymptotic/verification/run_checks.py)
- [assignment/verification/run_checks.py](assignment/verification/run_checks.py)

The exact minimal diff is [runner_changes.patch](runner_changes.patch). Other copied verification files are dependencies for the replay, not proposed edits. Copied historical result files retain their historical meaning and should not be mistaken for new verification of the patched runners; the fresh results are explicitly identified below.

## Changes

Stable-core's four scientific imports now occur at the beginning of `_run_checks`, after `main` has written RUNNING to the result and log. Its mathematical checks and result schema are unchanged.

Asymptotic's `z3` import now occurs inside `main`'s try block after RUNNING is written. Solver-version metadata is populated after that import succeeds. Its argument parsing still precedes the run, so `--help` exits normally without importing Z3 or invalidating a scientific result. Helpers receive the module through the runner's global binding when `main` starts the scientific phase.

Assignment's initial result-directory setup uses pathlib directly, allowing the summary to be written before importing either `z3` or `verification_io`. Both imports are inside the existing try block. Successful summaries retain the solver-version field and eight-stage behavior, including optimized child processes. Failure summaries also identify the exception type.

## Fresh full scientific verification

The three normal invocations all exited zero and wrote PASS:

| Package | Fresh full replay | Behavior comparison |
|---|---|---|
| Stable core | Both 20,349-basis arrangements, symbolic ray certificate, claims, six negative controls | Scientific payload identical to shipped reference after excluding runtime, elapsed time, and input hashes |
| Asymptotic | All five raw-core cases, closure perturbation, Fibonacci and all-n arithmetic | Cases, arithmetic, and negative-control payloads identical to shipped reference |
| Assignment | All eight bounded verification stages | Every generated stage JSON payload identical to shipped reference |

The comparison supplements newly executed checks; stored PASS records were not accepted instead of a fresh replay. All three patched runners have zero removable Python assertions.

The full summary, result paths, and runner hashes are in [test_results/normal_replay_summary.json](test_results/normal_replay_summary.json). Fresh records are respectively `stable_core/verification/results/verification.json`, `asymptotic/verification/results/verification.json`, and `assignment/verification/results/verification_summary.json`.

## Lifecycle and scientific rejection tests

[test_lifecycle.py](test_lifecycle.py) creates separate disposable copies under this scratch directory and seeds their outputs with an old PASS marker. It is rerunnable: each invocation creates a new probes directory. It does not edit the three candidate runners or the source packages.

Twenty-four controls passed:

- **Six original startup regressions:** missing stable-core `verify_claims`, and missing third-party Z3 under `-S` for asymptotic and assignment; each normally and under `-O`. All now exit nonzero, persist FAIL, and remove the old PASS marker. [Results](test_results/startup_failure_after.json)
- **Four additional local-import failures:** missing stable-core `data` and assignment `verification_io`, each normally and under `-O`. [Results](test_results/extra_local_import_failures.json)
- **Six direct timing observations:** an import hook reads the result file at the first scientific import and explicitly verifies RUNNING is already persisted with the old marker removed, then raises a dependency exception. Each runner is tested normally and under `-O`. [Results](test_results/running_before_import.json)
- **Six actual scientific rejections:** a stored stable-core claim is changed to 999; the asymptotic expected leximin parameter is changed to 3/4; the first assignment stage is given the false requirement `rho <= -1`. Existing mathematical guards reject each mutation normally and under `-O`, leave FAIL, and propagate nonzero exits. The precise errors are `stored claims wrong`, `wrong maximin value`, and child-stage `generic bound failed`. [Results](test_results/scientific_exception_controls.json)
- **Two help controls:** asymptotic `--help` succeeds without Z3, normally and under `-O`, and leaves an existing scientific result untouched. Stable-core and assignment have no help parser, and their existing CLI contracts were not changed. [Results](test_results/help_behavior.json)

The aggregate record is [test_results/control_summary.json](test_results/control_summary.json). The original pre-fix six-case evidence remains in the coordinating audit at `/private/tmp/coopgt-deep-review-20260905/root/startup_failure_before.json`.

## Exact persistence boundary

The guarantee begins once Python has parsed the runner and the standard-library/bootstrap/output setup has succeeded. A syntax error in the entry-point runner, an interpreter/standard-library startup failure, argument parsing that exits before a scientific run, or an unwritable result destination can prevent RUNNING from being persisted. No in-process runner can promise to write FAIL when the destination itself cannot be written. A syntax error in an imported scientific module is different: it happens inside the protected phase and is caught after RUNNING.

An abrupt process termination such as SIGKILL after RUNNING can leave RUNNING instead of FAIL; it cannot be caught by Python. A later disk or filesystem failure can also prevent the final status write. Existing `write_text` behavior is preserved, so this patch does not claim atomic or crash-durable writes, nor coordination between simultaneous processes sharing one output path. Ordinary caught scientific/import errors with a writable destination are covered by the tests above.

These are verifier lifecycle fixes. They do not alter mathematical claims, scientific coverage, solver acceptance gates, or any manuscript.

Delivery note: the optional patch is rendered with zero context to avoid whitespace-only context records; apply with `git apply --unidiff-zero`. The corrected runner files are already integrated.
