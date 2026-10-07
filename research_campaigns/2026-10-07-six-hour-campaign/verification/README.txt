PORTABLE EXACT VERIFICATION — SIX-HOUR CAMPAIGN

Requirements: Python3.9+ standard library; preserve full repository layout.
No scipy, numpy, external solver, LaTeX compiler, or paid material is required.

From repository root:
 python3 -B -O research_campaigns/2026-10-07-six-hour-campaign/verification/run_all.py
Add --output /path/to/replay.json to retain its complete JSON record.
The runner prints compact progress to stderr and the full record to stdout.
Each of its 26 scripts runs separately. Any nonzero exit, timeout, missing success
marker, absent dependency, or Python assert in checked source makes the run fail.
Explicit require/check helpers continue working under optimization.

Repository-relative dependencies outside this directory:
 research_campaigns/2026-10-06-monotone-envelope/verification/verify.py
 research_campaigns/2026-10-06-series-parallel/verification/verify.py
 paper5/truthful_cooperation/verification/sharp/verify.py
 paper5/truthful_cooperation/verification/sharp/poisson_certificate.py
The finite profile-certificate input is ../discovery/network_profile_lp.json.
These dependencies and every invoked script are hashed in each run record.

Main theorem checks:
 general_production.py — exact independent primal/dual vertices, raw selected
 forms, whole bundles, rational coefficients/profits, cap/endpoint coverage,
 own-report comparisons, polynomial/integrated identities, finite-K bounds,
 uncapped counterexample and substantive corruptions.
 simple_dag_lower.py — actual shared-fan maxflows, complete small cut counts,
 weighted histogram transports and full small subdivision report grid. Most
 subdivision coalition values use the proved complete-pair projection; do not
 describe all 60 million comparisons as independent maxflow computations.
 concave_production.py — analytic supports for a nonpolyhedral harmonic
 function, a boundary-discontinuous concave function, linear and zero controls.
 owner_count_lower.py — new parameter conversion, exact large-K tail checks
 for two heights, actual small-pool weighted certificates and corruptions.
 It does not enumerate huge-K histogram spaces or prove the asymptotic inversion.
 core_projection.py — four fixed owners, full efficient-core Euclidean
 projection; 32 linear primal/dual and 32 nonlinear KKT coalition certificates,
 three projection certificates, and an exact strict own-payment decrease.
 Attribution to the complete ABV2016 domain remains conditional.
 resource_dimension.py — complete three-owner/two-resource grid, all increasing
 single-coordinate pairs, zero cases, cone refinements and negative controls.
 sampling.py — exact finite law/posteriors, analytic expectation agreement,
 fixed-mask incentives, cushions, query sets and corruptions.
 seed_certificate.py — exact all-real-profile face enumeration for tiny fixed
 technologies; includes tie faces, T=0 and actual rational violations. Frozen
 originating-face formulas are retained on closures. This is an exhaustive
 domain certificate for those fixtures, not a sampled report grid.

Other scripts preserve exact checks for the successful predecessors and failed
routes. They are valuable calibration/obstruction evidence, not additional
independent papers. Historical discovery scripts in ../discovery/ can depend on
temporary paths or numerical solvers; they are not needed for this replay.

Evidence files:
 working_replay.json records the earlier 24-script working-tree run.
 clean_archive_replay.json records the final 26-script archive run, all PASS.
 Individual *_result.json files retain their original scoped run metadata;
 consult the final replay hashes when checking later portability edits.
 review/portability_* records the AST-preserving conversion of 124 assertions
 and removal of user-specific fallback paths in 14 older scripts.

These are conventional-proof corroboration and finite exact certificates.
No finite grid proves an unrestricted theorem, and no test result confirms
historical novelty or replaces external specialist review.
