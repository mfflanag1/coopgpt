# Exact core-witness compatibility campaign

Completed 3 October 2026 under the [frozen contract](CONTRACT.md), with a 40-hour ceiling and an 8-hour calibration gate. [Phase 1 passed](PHASE1_GATE.md); see [STATUS.json](STATUS.json). **The mathematical target is resolved internally: S3=1/3, strictly unattained at finite size.** See the [complete proof and sharp examples](sharp_result/SHARP_ONE_THIRD.md), [review packet](sharp_result/SPECIALIST_PACKET.md), and [source comparison](sharp_result/SOURCE_COMPARISON.md). Novelty and human specialist review remain unresolved. Gates are maximum effort allowances, not minimum waiting periods. See the [completion audit](COMPLETION_AUDIT.md).

## Calibration checkpoint

Six retained exact checks pass, including the current one-third lower family. The independently authored standard-library checker passes 38 unit tests, 380 adversarial cases and 380 corrupted-upper rejections, plus replay of 34 retained frontier certificates covering 2,678,055 full-team inequalities. Five end-to-end numerical-generator/exact-checker calibrations pass. Perfect P requires a dummy core witness; witnesses for different ideals remain separate.

The known eight-label diagnostic is reproduced: the insufficient relaxation permits 3/8, while the full-witness fixed-support optimum is 1/4. These numbers concern different optimization formulations; they do not alter the known zero subsidy of the retained particular eight-label market.

## Frozen registry and scope

[Six supports](registry/supports.json) were frozen before optimization: four one-cycle supports and two cycle-rank-three supports, all 12 labels; CW-05 and CW-06 were reserved and then tested only after a candidate conjecture was written and hashed. [Provenance limits](registry/PROVENANCE_GAPS.md) qualify historical newness. All incidence trees were conservatively excluded by this bounded selection, not proved universally safe. The full-witness LP itself already exists in September work; the intended new contribution must be a reusable compatibility constraint, counterexample or precise obstruction.

## Paired results and live obligation

All six supports now have exact rational full-model upper certificates below1/3; CW-01,CW-04,CW-06 have matching primal/dual values. See [initial results](PAIRED_RESULTS.md) and [reserved-support results](HELDOUT_RESULTS.md). These historical finite results are now supplemented by the universal proof linked above.

Two elementary explanations of the relaxation gap were proved, checked and reviewed. They remain consequences of established deletion/path tools. The [proof-state ledger](PROOF_STATE.md) records the successful all-size aggregation of these constraints; the relaxation-sufficiency conjecture is proved and the substantive mechanism gate passes. The generic sector-projection route remains stopped. No further supports may be added.

The independent diagnostic checker verifies33 coordinate maxima and132negative controls. Its [output](interpretation/DIAGNOSTIC_QA.json) distinguishes actual fixed-market objectives from the all-weight support optimization and from full subsidy values. Reproduce using `python3 -B -O research_campaigns/2026-10-03-core-witness/src/check_diagnostic_ideals.py` in the recorded checkout; the source retains the explicit audited project path.

The final [reproduction guide](sharp_result/REPRODUCE.md) includes symbolic identities, exact dual checks and the sharp family. The [approach ledger](APPROACH_LEDGER.md) records stopped routes.

## Reproduce

Use Python 3.14.3 for the recorded environment; install requirements.txt only for numerical discovery/registry work. The exact full-witness checker and its tests use the standard library alone.

    python3 -O -m unittest discover -s research_campaigns/2026-10-03-core-witness/src -p test_check_certificate.py
    python3 -O research_campaigns/2026-10-03-core-witness/src/checker_adversarial_qa.py
    python3 -O research_campaigns/2026-10-03-core-witness/src/replay_frontier.py
    python3 -O research_campaigns/2026-10-03-core-witness/src/check_certificate.py research_campaigns/2026-10-03-core-witness/calibration/false_relaxation_support_candidate.json

Run from repository root. Registry self-test needs networkx; it reads source artifacts and runs no optimizer:

    python3 -O research_campaigns/2026-10-03-core-witness/src/support_registry.py --repo . --self-test

[Model routing](MODEL_ROUTING.json), [review adjudication](reviews/checker/ADJUDICATION.md), [formulation](FORMULATION.md), and [initial free-source ledger](SOURCE_LEDGER.md) separate executed checks from model opinions and unresolved source comparisons. The standalone CLI could not run Astra; native Astra xhigh performed the opposite-model QA. No accepted CLI routing score was fabricated.
