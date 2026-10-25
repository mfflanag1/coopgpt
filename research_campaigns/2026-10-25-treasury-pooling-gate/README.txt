CoopGPT Treasury application gate — 25 October 2026
Open index.html for the full reviewed handoff; DECISION.txt gives the conclusion.

Result: both the primary material-separation screen and Gaussian-tail screen fail. The post-outcome available-quote diagnostic does not change that conclusion. No general theorem, novelty, prospective forecast, or actual institutional pooling claim.

INPUT
../2026-10-24-risk-geometry/data/gsw-vintage-2026-10-24.csv
SHA256 59a802aa6f1661c3beb37a7880706627db2913601920e3be3c3dcdd6b5321278
This sibling directory structure is expected by the scripts. Preserve the historical input; a new download is a different vintage. DATA_MANIFEST.json records source, variables, units and limitations. requirements.txt and runtime.json record the actual numerical environment.

VERIFY SAVED OUTPUTS
From this directory, run: python verify_results.py
This reads both result sets and raw input, performs independent numerical checks, and refreshes verification.json, data_audit.json. To preserve the sealed bundle byte-for-byte, use a working copy even for verification. The producer scripts are not imported by the verifier. The selected charge-coordinate full-lex audit takes longer than simply reading output.

FULL REGENERATION
Use a separate working copy, preserving the source and sibling raw-data path. Remove existing generated JSON outputs in the COPY only, including the copy's quote_interval_diagnostic directory (not its script). Then:
  python run_gate.py > run.log
  python run_quote_diagnostic.py > quote_diagnostic_run.log
  python verify_results.py > verification_run.log
  python build_report.py
The diagnostic wrapper refuses to overwrite its existing results. The primary script writes results.json, run_summary.json and daily_scores.json. Neither script changes the raw file, contract, protocol, amendment, original freeze records, or external systems. Regenerated completion timestamps and floating-point last digits may differ. Original design-freeze timestamps are historical provenance, not something to regenerate or backdate.

LOGIC
run_gate.py computes all63 coalition inequalities for each6-unit monthly game, full lexicographic selectors, credit caps, Euler/proportional comparators, static ownership sensitivities and rolling/static calibration. Split ownership uses7 units; merge uses5. The quote diagnostic shares this numerical implementation but changes only the observed-quote differencing convention. It is post-outcome, not a new primary.

verify_results.py independently reconstructs source transformations/covariances, checks all saved constraints and cap feasibility, recalculates tail quantities/bootstrap intervals, and certifies selected full-lex stages in charge coordinates. Both use SciPy/HiGHS. Finite floating-point verification is not a general proof or independent solver certificate.

PROVENANCE
CONTRACT.txt, PROTOCOL_V1.txt, design_freeze.json: frozen before headline outcomes.
PRE_OUTCOME_AMENDMENT.txt, amendment_freeze.json: estimator/interpretation clarifications before outcomes.
POST_OUTCOME_QA_PLAN.txt: declared missing-quote diagnostic after observing primary failure.
design_review*, implementation_review*: tool-free Fable snapshots, inputs/status, not executed tests.
REVIEW_DISPOSITION.txt: findings checked against actual code/data/results; unsupported reviewer conjectures rejected.
data_audit.json: complete additional dropped quote-change inventory.
verification.json and structural_diagnostics.json: executed QA and distinct Euler witnesses.
campaign_status.json and artifact_hashes.json: final local handoff record.

No manuscript or Git/GitHub mutation in this run. No financial activity or external human contact. For further work start with NEXT_CONTRACT_GATE.txt, not a retuned synthetic portfolio.
