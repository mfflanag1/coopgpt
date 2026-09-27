#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
"${COOPGT_PYTHON:-python3}" -O verify.py "$@"
"${COOPGT_PYTHON:-python3}" -O tree_certificate.py
"${COOPGT_PYTHON:-python3}" -O verify_replication.py
"${COOPGT_PYTHON:-python3}" -O verify_two_label.py
"${COOPGT_PYTHON:-python3}" -O verify_rejected_root.py
"${COOPGT_PYTHON:-python3}" -O verify_deletion.py
"${COOPGT_PYTHON:-python3}" -O uniform_template.py
"${COOPGT_PYTHON:-python3}" -O verify_uniform.py
"${COOPGT_PYTHON:-python3}" -O verify_double_junction.py
"${COOPGT_PYTHON:-python3}" -O universal_template.py
"${COOPGT_PYTHON:-python3}" -O verify_universal.py
"${COOPGT_PYTHON:-python3}" -O verify_upper_lemma.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_pair_budget.py
"${COOPGT_PYTHON:-python3}" -O verify_sparse_graft.py
"${COOPGT_PYTHON:-python3}" -O surplus_template.py
"${COOPGT_PYTHON:-python3}" -O verify_surplus.py
"${COOPGT_PYTHON:-python3}" -O mixed_donor_template.py
"${COOPGT_PYTHON:-python3}" -O verify_mixed_donor.py
"${COOPGT_PYTHON:-python3}" -O verify_mixed_budget.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_variable_p.py
"${COOPGT_PYTHON:-python3}" -O verify_marginal_extraction.py
"${COOPGT_PYTHON:-python3}" -O verify_local_rule_dual.py
"${COOPGT_PYTHON:-python3}" -O cut_transport.py
"${COOPGT_PYTHON:-python3}" -O verify_cut_transport.py
"${COOPGT_PYTHON:-python3}" -O ring_zero.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_cyclic_patterns.py
"${COOPGT_PYTHON:-python3}" -O verify_harmonic_sector.py
"${COOPGT_PYTHON:-python3}" -O verify_tree_slack.py
"${COOPGT_PYTHON:-python3}" -O verify_tree_integrality.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_tree_convex_hull.py
"${COOPGT_PYTHON:-python3}" -O one_hub.py
"${COOPGT_PYTHON:-python3}" -O verify_one_hub.py
"${COOPGT_PYTHON:-python3}" -O leaf_dilation.py
"${COOPGT_PYTHON:-python3}" -O verify_leaf_dilation.py
"${COOPGT_PYTHON:-python3}" -O two_hub_block_certificate.py
"${COOPGT_PYTHON:-python3}" -O verify_two_hub_blocks.py
"${COOPGT_PYTHON:-python3}" -O verify_affine_block_barrier.py
"${COOPGT_PYTHON:-python3}" -O root_mass_certificate.py
"${COOPGT_PYTHON:-python3}" -O verify_root_mass.py
"${COOPGT_PYTHON:-python3}" -O hub_rebalancing_certificate.py
"${COOPGT_PYTHON:-python3}" -O verify_hub_rebalancing.py
"${COOPGT_PYTHON:-python3}" -O compound_cut_certificate.py
"${COOPGT_PYTHON:-python3}" -O verify_compound_cut.py
"${COOPGT_PYTHON:-python3}" -O verify_broken_ring.py
"${COOPGT_PYTHON:-python3}" -O verify_cyclic_frontier.py
"${COOPGT_PYTHON:-python3}" -O verify_cyclic_necessity.py
"${COOPGT_PYTHON:-python3}" -O verify_sector_min_core.py
"${COOPGT_PYTHON:-python3}" -O verify_ideal_difference.py
"${COOPGT_PYTHON:-python3}" -O verify_coattainability.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_repeated_unicycle.py
"${COOPGT_PYTHON:-python3}" -O verify_cycle_boundary.py
"${COOPGT_PYTHON:-python3}" -O verify_adaptive_boundary.py
"${COOPGT_PYTHON:-python3}" -O finite_mixed_donor.py
"${COOPGT_PYTHON:-python3}" -O verify_finite_mixed_donor.py "$@"
"${COOPGT_PYTHON:-python3}" -O localization_certificates.py --generate
"${COOPGT_PYTHON:-python3}" -O verify_extremal_localization.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_shortfall_identity.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_finite_budget_direct.py "$@"
"${COOPGT_PYTHON:-python3}" -O verify_bounded_unicycle.py
"${COOPGT_PYTHON:-python3}" -O verify_core_slack.py
"${COOPGT_PYTHON:-python3}" -O verify_zero_hub_module.py
"${COOPGT_PYTHON:-python3}" -O verify_full_affine_module.py
"${COOPGT_PYTHON:-python3}" -O verify_internal_cloning.py
"${COOPGT_PYTHON:-python3}" -O verify_core_compatibility_upper.py "$@"
"${COOPGT_PYTHON:-python3}" -O audit_20260920/verify_affine_refinement.py
