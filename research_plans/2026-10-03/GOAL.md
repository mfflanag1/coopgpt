# Proposed long research goal: exact core-witness compatibility

Prepared 3 October 2026. **Execution completed:** see the [campaign audit](../../research_campaigns/2026-10-03-core-witness/COMPLETION_AUDIT.md). The text below records the original plan; its unchanged launch snapshot is `CONTRACT.md` in that campaign. Suggested budget: at most 40 active research hours, with a hard continuation gate at hour 8. This is a proposed execution budget, not a claim that a theorem can be completed in that time. Count elapsed campaign work, including solver waits and delegated work, against the 40-hour ceiling; parallel work does not extend a phase. Use at most two local solver processes. No paid sources, cloud compute, outreach or scheduled runs are authorized by this plan.

## Objective and frozen statement

Resolve a structurally meaningful part of the sharp protected-subsidy problem by retaining actual coordinate-attaining original-core witnesses. Seek a proof, a certified counterexample, or a precise bounded obstruction; do not assume the conjecture is true.

Three equally sized finite sectors; nonnegative pair matrices; only full triples productive; original coalition worth is the maximum integral matching value; original grand worth T>0 and original entire core C nonempty. Freeze H_i=max{x_i:x in C} before intervention. Let s be the minimum extra grand-coalition budget permitting all original coalition inequalities and y_i>=H_i/3. S3 is the supremum s/T over this class. Current bounds are 1/3<=S3<=39999/100000.

Via the existing replication, sparsification and component reductions, the universal target is

    3 w(P) + sum_{i unmatched by P} H_i <= 4T

for every connected market supported on pairs of a diagonal optimal matching and one integral partial matching P. An all-size integral-P theorem suffices by replication; a finite-size census does not. The sector graph of the graph-protection paper and this label/P incidence graph are different objects.

## Exact finite formulation to build and verify

For a fixed labeled support (m,P), normalize the diagonal matching sum to T=1. Use nonnegative pair-weight variables only on pairs belonging to the diagonal or P. For each unmatched player i introduce a separate payoff vector x^(i)>=0 with sum x^(i)=1 and full-team cover inequalities for all m^3 triples. Let h_i=x^(i)_i. Optimize the linear objective

    J=w(P)+(1/3) sum_i h_i-1.

The shared weights define one original market; different players use different core vectors. A total-one core cover plus the value-one diagonal certifies ordinary grand worth 1. There is no common-attainment requirement. For fixed weights, each coordinate is positively weighted in the objective and its witness is independent, so its maximum is the true ideal. This exact formulation and its compactness/duality obligations must be independently checked before relying on it.

An exact feasible point with J>1/3 already gives a valid obstruction using lower witnesses for H; a disproof needs only verified lower witnesses, not exact ideals or the exact subsidy. Require full ideal primal/dual certificates and protected-allocation/subsidy-dual verification before reporting exact values. Any J>39999/100000 contradicts the retained upper bound and must be treated as a bug or unresolved proof conflict until independently resolved. An exact optimal dual J<=1/3 proves only that fixed support's all-coefficient inequality. Infeasibility of an extra restricted template is not a counterexample to S3=1/3.

## Phase 1: calibration and support registry (hours 0-8)

Reproduce the two-label zero-subsidy calibration; one lower-bound family instance; the eight-label false 3/8 relaxation example whose actual subsidy is zero; the m=11 market of exact subsidy 76/303; and the local affine certificate with coefficient 13/18. Use existing exact verifiers, not their saved PASS labels.

Implement the full-witness fixed-support LP and an independent rational primal/dual checker. Negative controls must corrupt a core inequality, a diagonal normalization, an objective/dual coefficient, a witness total, P player-disjointness, an off-support weight, and the unmatched-player set; each must be rejected under python -O. Unknown or timeout is unresolved.

Freeze a machine-readable registry of at most 6 genuinely untested supports before optimization. Start from connected incidence supports with 6 or 7 P-teams, m between 9 and 12, and cycle rank at least 1 or at least two degree-three diagonal labels. Generate deterministic within-sector swaps/reconnections of retained supports, preserving actual-player disjointness; include repeated-label P-teams where admissible. Check connectedness, counts and graph symmetries explicitly. Exclude every previously examined support, whether certified or inconclusive, and proven safe classes. Define equivalence by simultaneous diagonal-label relabelling, P-team reordering and sector permutation, preserving the sector-coloured incidence structure and repeated incidences. Reject known records with the same canonical form; test the filter against all 34 retained records. Freeze a deterministic priority ordering and identify held-out supports before solves. The existing 34 CYCLIC_FRONTIER records and IDEAL_DIFFERENCE example are calibration/provenance, not new discoveries.

No claim of exhaustive coverage of these sizes is permitted. If fewer than 6 new supports survive, use fewer. Gate: do not continue until the formulation, checker and registry pass; do not spend the whole campaign rebuilding an unchecked solver.

## Phase 2: paired exact synthesis (hours 8-20)

For each registered support, compare the full-witness optimum with the previously rejected ideal-difference relaxation using identical normalization and support. Use one initial attempt per support. Cap each solve at 30 minutes and rational-certificate recovery at 30 minutes, and cap all paired solves, recovery and retries together at 8 elapsed hours within this 12-hour phase. Permit at most two retries total, in the frozen priority order, only within that aggregate cap. Reserve the remaining time for interpreting certificates; stop when the phase cap is reached even if the registry is unfinished. Never substitute numerical status for exact acceptance.

Select at most two cases where the weaker relaxation permits an obstruction above 1/3 and the full-witness formulation has a certified smaller upper bound. Extract the responsible dual combination of full-team constraints. Explain what original-core relation is lost by the relaxed ideal vector. If an actual J>1/3 witness appears, halt exploratory branching and move to independent certification.

Gate at hour 20: a certified counterexample, or at least one new parametrically stated constraint with explicit hypotheses, an exact derivation and either a checked held-out support application or separation of a named relaxation point. A routine fixed-support dual alone does not pass this gate. A list of more below-threshold examples is not enough to proceed.

## Phase 3: one reusable lemma (hours 20-32)

Try to turn one extracted dual into an all-parameter compatibility inequality or a support-class theorem. Keep at most two distinct formulations. State explicitly which labels, incidences and original witness allocations it uses. Validate on calibration and held-out supports before promotion. A full universal proof is welcome but not the required outcome.

Treat the p=z=tau=0 scalar point q=11/41, v=11/82 and value 29/82 only as a diagnostic for information loss in the specified aggregate face. It is not an actual market, not a global upper bound, and not necessarily the full relaxation optimum. A new inequality must be mapped to the same variables with valid hypotheses before claiming it excludes that point; failure to realize it at finite tested sizes is not a nonrealizability theorem. Do not impose arbitrary finite-size equalities merely because the point arose on an idealized face.

If no general lemma survives two formulations, deliver a bounded theorem about J for the specified labelled support (not a bound on the full subsidy or S3) or exact limitation of the attempted mechanism and stop. Do not replace the model, freeze different ideals, or generalize K to declare success.

## Phase 4: adversarial verification and release (hours 32-40)

Use a reviewer who did not write the candidate proof to challenge all quantifiers, normalization, entire-core preservation, fractional lifting and certificate reconstruction. Independently reconstruct finite witnesses from raw pair matrices. For any claimed universal upper bound, independently check the symbolic all-size argument and every reduction; finite matrix checks cannot establish universality. A support-class lemma alone does not improve the global upper bound. Run exact negative controls and preserve hashes, environment, source ledger and failures.

Check freely available primary sources for the exact new claim. Established ingredients include subsidy LP duality, weak-priority transformations, matching tightness and half-optimal cores. Priority gaps remain gaps, not evidence of novelty. No mathematical completion label may depend only on an AI review.

Deliver: proof or bounded-result note; immutable support registry; exact witnesses and verifier; approach/no-go ledger; independent-review adjudication; source comparison; and a final statement of what remains unresolved. Continue beyond 40 hours only after a new user decision based on a concrete surviving mechanism.

## Retired approaches and safeguards

- Do not retune the coefficient at fixed intercept 1/18: 13/18 is sharp.
- Other affine intercepts/non-affine envelopes are not ruled out, but they are not an automatic second campaign; reopen only with a specific new dual or structural argument.
- Do not use a difference-constrained ideal vector in place of actual original-core witnesses.
- Do not assume optimal subsidy duals can be forest-supported; an actual counterexample to that restriction is known.
- Do not repeat prescribed/adaptive cycle-edge zeroing, frozen old hub weights, or a common-denominator template already refuted.
- Known one-hub incidence trees are a calibration class. A two-hub template is sufficient, not proved equivalent to the original problem.
- Do not equate a fixed-P bound with the full subsidy optimum of that market.

## Evidence and source anchors

Read the current files before launch: SHARP_SUBSIDY.md, REDUCTIONS.md, IDEAL_DIFFERENCE_LIMITS.md, CORE_COMPATIBILITY_UPPER.md, CYCLIC_OPTIMA_REQUIRED.md, TWO_HUB_BLOCK_REDUCTION.md, and audit_20260920/AFFINE_REFINEMENT.md under structural_classification_2026-09-06/sharp_subsidy/. Historical 2/5 headers are superseded by the current STATUS.json.

Primary literature anchors: [cost of stability](https://arxiv.org/abs/0907.4385), [priority games](https://doi.org/10.1007/s00186-024-00876-x), [half-optimal core](https://www.bse.eu/sites/default/files/working_paper_pdfs/153.pdf), and [multisided graph model](https://doi.org/10.1007/s10479-019-03256-5). The plan is a research design, not an assertion that the target or proposed lemma is novel.
