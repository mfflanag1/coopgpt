BOUNDED CONVENTION / NAV / TREASURY GATE — COMPLETE, STOP EXPANSION
25 October2026. Public/free sources. This is a post-result diagnostic, not a holdout.

Current browser handoff (updated in place):
http://127.0.0.1:52140/research-campaigns/2026-10-25-public-risk-feasibility/index.html#convention-gate

RESULT
All29 NAV exclusions match original SEC fields (87 numbers), including discrepancies. No documented tolerance established; none restored. The parent1791-record provisional panel is unchanged. Exclusion is a researcher protocol decision, not a finding of violation or material error.

Frozen ZROZ case:20 ordinary zero-coupon UST holdings,99.9967227983% assets, unmatched$52,298.67 exactly disclosed cash. Original face/mark/maturity/coupon/rate inputs all match; original radio selections were not independently verified. Model uses filed marks to infer yields. It is not independent market-price validation.

Model A allocates full-shock losses by maturity; B weights shocks before repricing. Both bases365.25/365 were declared before target holdings extraction. All four combinations miss the1NAVbp diagnostic screen at both active nodes. This screen is not statistical uncertainty or documented internal precision. Denomination compatibility of USD-group responses is assumed in dollar/NAV comparisons. No actual filer convention identified.

Six new synthetic tests passed. Seventy-digit Decimal calculations independently check90 aggregate outputs, including all A/B, up/down1/100bp, tangent and two day-count scenarios. Maximum difference below8.11e-8 dollars. Exact holdings-plus-cash and NAV identities pass. Prior22 tests and8955 panel node checks were not rerun in this follow-up. A separate extraction exactly reproduced the saved1/20/20 data rows from the original archive.

REPLAY (from this directory, use fresh output paths)
python3 extract_target.py /Users/maxf/Downloads/2025q2_nport.zip --output /private/tmp/new_treasury_extract.json
python3 -m unittest -v test_treasury
python3 verify_benchmark.py --output /private/tmp/new_treasury_validation.json

verify_benchmark.py replays both declared models and compares the complete structured outputs with treasury_result.json, then computes separate Decimal node totals. It refuses output overwrite. treasury_benchmark.py also refuses to overwrite the original result. No dependency beyond Python standard library. Raw archive SHA256 is enforced by extract_target.py.

record_observations.py reconstructs browser-observation ledgers from transcribed numbers. It does NOT re-fetch originals, and reconstructed comparisons are not new independent browser evidence. Full original filings were not locally downloaded. Live reinspection needs public access.

FILES
SCOPE.txt + scope_hash.json: fixed diagnostic specification; parent protocol unchanged.
extract_target.py, target_holdings_raw.json: selected raw rows and reproducible extraction.
treasury_benchmark.py, treasury_result.json: original conditional calculation, unchanged after review.
verify_benchmark.py, numerical_validation.json: executed independent numerical checks.
nav_source_audit.json, holdings_source_audit.json: original rendered values, scope and limits.
verified_sources.json: only narrow root-verified regulatory findings.
BENCHMARK_REVIEW_DISPOSITION.txt: independently checked Fable findings and rejected extrapolations.
SOURCE_REVIEW_DISPOSITION.txt: Fable source draft rejected as written after Codex QA; only supported findings integrated.
review_provenance.json: review run paths and hashes. No reviewer opinion counted as an executed test.
before_*: prior report/status versions preserved.
update_handoff.py: builds the existing report from preserved prior version and saved results; does not rerun research.

STOP / RE-ENTRY
Do not expand an error-prevalence study from arithmetic residuals. Resume only with a documented public shock definition, compatible denomination and independently matched valuation, or deliberately redesign around an explicitly defined stress model and a consequential economic outcome. Applicable technical precision rules and latest full competing-paper comparison remain unverified/incomplete. No confirmed novelty, true valuation error, margin obligation, causal estimate or pooling gain. No automatic follow-up, manuscript/Git change, human outreach or purchase.
