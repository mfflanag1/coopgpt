#!/usr/bin/env bash
set -euo pipefail

python_bin="${1:-python3}"
repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/paper5-verify.XXXXXX")"
trap 'rm -rf "$scratch_dir"' EXIT
cd "$repo_root"

run_python() {
  echo "RUN $1"
  "$python_bin" "$@"
}

run_python coopgames/verifiers/s6/audit_lex_improvement_predicate.py \
  --output "$scratch_dir/lex.json"
cmp coopgames/verifiers/s6/lex_improvement_predicate_audit.json \
  "$scratch_dir/lex.json"

run_python coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
run_python coopgames/verifiers/s6/verify_independent_bound_two.py
run_python coopgames/verifiers/s6/verify_third_bound_two.py \
  --output "$scratch_dir/third.json"
cmp coopgames/verifiers/s6/third_bound_two/verification.json \
  "$scratch_dir/third.json"

run_python coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py \
  --output "$scratch_dir/formula-interface.json"
cmp coopgames/verifiers/s6/strict_exchange_formula_interface.json \
  "$scratch_dir/formula-interface.json"
run_python coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py \
  --output "$scratch_dir/semantic-interface.json"
cmp coopgames/verifiers/s6/strict_exchange_semantic_interface.json \
  "$scratch_dir/semantic-interface.json"

run_python coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py \
  --output "$scratch_dir/templates.json"
cmp coopgames/verifiers/s6/strict_exchange_large_case_templates.json \
  "$scratch_dir/templates.json"
run_python coopgames/verifiers/s6/audit_strict_exchange_large_case_activation_atlas.py \
  --output "$scratch_dir/activation-atlas.json"
cmp coopgames/verifiers/s6/strict_exchange_large_case_activation_atlas.json \
  "$scratch_dir/activation-atlas.json"
run_python coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py

run_python coopgames/verifiers/s6/reproduce_equality_exchange_classification.py
run_python coopgames/verifiers/s6/verify_g23_witness.py
run_python coopgames/verifiers/divergence/verify_ceiling_root_interpolation.py \
  --output "$scratch_dir/ceiling-root-interpolation.json"
cmp coopgames/verifiers/divergence/ceiling_root_interpolation.json \
  "$scratch_dir/ceiling-root-interpolation.json"
run_python coopgames/verifiers/divergence/verify_mixed_block_star_boundary.py \
  --output "$scratch_dir/mixed-block-star-boundary.json"
cmp coopgames/verifiers/divergence/mixed_block_star_boundary.json \
  "$scratch_dir/mixed-block-star-boundary.json"
run_python coopgames/verifiers/divergence/verify_tied_ceiling_two_spoke_repair.py \
  --output "$scratch_dir/tied-ceiling-two-spoke-repair.json"
cmp coopgames/verifiers/divergence/tied_ceiling_two_spoke_repair.json \
  "$scratch_dir/tied-ceiling-two-spoke-repair.json"
run_python coopgames/verifiers/divergence/verify_n6_three_packet_repair.py \
  --output "$scratch_dir/n6-three-packet-repair.json"
cmp coopgames/verifiers/divergence/n6_three_packet_repair.json \
  "$scratch_dir/n6-three-packet-repair.json"
run_python coopgames/verifiers/divergence/verify_n6_three_packet_facet_z3.py \
  --output "$scratch_dir/n6-three-packet-facet-z3.json"
cmp coopgames/verifiers/divergence/n6_three_packet_facet_z3.json \
  "$scratch_dir/n6-three-packet-facet-z3.json"
run_python coopgames/verifiers/divergence/verify_optimized_mixed_currency_certificate.py \
  --output "$scratch_dir/optimized-mixed-currency-certificate.json"
cmp coopgames/verifiers/divergence/optimized_mixed_currency_certificate.json \
  "$scratch_dir/optimized-mixed-currency-certificate.json"
run_python coopgames/verifiers/divergence/verify_two_stratum_direct_gluing.py \
  --output "$scratch_dir/two-stratum-direct-gluing.json"
cmp coopgames/verifiers/divergence/two_stratum_direct_gluing.json \
  "$scratch_dir/two-stratum-direct-gluing.json"
run_python coopgames/verifiers/divergence/audit_direct_ceiling_common_hinge_trichotomy.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/direct-ceiling-common-hinge-trichotomy.json"
cmp coopgames/verifiers/divergence/direct_ceiling_common_hinge_trichotomy.json \
  "$scratch_dir/direct-ceiling-common-hinge-trichotomy.json"
run_python coopgames/verifiers/divergence/audit_n6_positive_residual_facet_atlas.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/n6-positive-residual-facet-atlas.json"
cmp coopgames/verifiers/divergence/n6_positive_residual_facet_atlas.json \
  "$scratch_dir/n6-positive-residual-facet-atlas.json"
run_python coopgames/verifiers/divergence/audit_affordable_rooted_packing.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/affordable-rooted-packing.json"
cmp coopgames/verifiers/divergence/affordable_rooted_packing.json \
  "$scratch_dir/affordable-rooted-packing.json"
run_python coopgames/verifiers/divergence/audit_labelled_facet_cover_duality.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/labelled-facet-cover-duality.json"
cmp coopgames/verifiers/divergence/labelled_facet_cover_duality.json \
  "$scratch_dir/labelled-facet-cover-duality.json"
run_python coopgames/verifiers/divergence/audit_cover_to_direct_handover.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/cover-to-direct-handover.json"
cmp coopgames/verifiers/divergence/cover_to_direct_handover.json \
  "$scratch_dir/cover-to-direct-handover.json"
run_python coopgames/verifiers/divergence/audit_marked_packing_target_reserve.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/marked-packing-target-reserve.json"
cmp coopgames/verifiers/divergence/marked_packing_target_reserve.json \
  "$scratch_dir/marked-packing-target-reserve.json"
run_python coopgames/verifiers/divergence/audit_strict_carrier_minimum_deletion.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/strict-carrier-minimum-deletion-audit.json"
cmp coopgames/verifiers/divergence/strict_carrier_minimum_deletion_audit.json \
  "$scratch_dir/strict-carrier-minimum-deletion-audit.json"
run_python coopgames/verifiers/divergence/audit_marked_hinge_deficiency_transfer.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/marked-hinge-deficiency-transfer-audit.json"
cmp coopgames/verifiers/divergence/marked_hinge_deficiency_transfer_audit.json \
  "$scratch_dir/marked-hinge-deficiency-transfer-audit.json"
run_python coopgames/verifiers/divergence/verify_marked_hinge_mixed_facets_z3.py \
  --input "$scratch_dir/marked-hinge-deficiency-transfer-audit.json" \
  --output "$scratch_dir/marked-hinge-mixed-facets-z3.json"
cmp coopgames/verifiers/divergence/marked_hinge_mixed_facets_z3.json \
  "$scratch_dir/marked-hinge-mixed-facets-z3.json"
run_python coopgames/verifiers/divergence/audit_pxc51_handover_controls.py \
  --marked-audit "$scratch_dir/marked-hinge-deficiency-transfer-audit.json" \
  --neutral-control coopgames/verifiers/divergence/n7_neutral_rectangle_control.json \
  --output "$scratch_dir/pxc51-handover-controls.json"
cmp coopgames/verifiers/divergence/pxc51_handover_controls.json \
  "$scratch_dir/pxc51-handover-controls.json"
run_python coopgames/verifiers/divergence/audit_pxc52_coloured_charge.py \
  --six-player coopgames/verifiers/s6/harvest6_602.json \
  --neutral-control coopgames/verifiers/divergence/n7_neutral_rectangle_control.json \
  --output "$scratch_dir/pxc52-coloured-charge.json"
cmp coopgames/verifiers/divergence/pxc52_coloured_charge.json \
  "$scratch_dir/pxc52-coloured-charge.json"
run_python coopgames/verifiers/divergence/audit_two_spoke_alignment_bound.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --neutral-control coopgames/verifiers/divergence/n7_neutral_rectangle_control.json \
  --output "$scratch_dir/two-spoke-alignment-bound.json"
cmp coopgames/verifiers/divergence/two_spoke_alignment_bound.json \
  "$scratch_dir/two-spoke-alignment-bound.json"
run_python coopgames/verifiers/divergence/audit_multigainer_common_spoke_star.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --neutral-control coopgames/verifiers/divergence/n7_neutral_rectangle_control.json \
  --output "$scratch_dir/multigainer-common-spoke-star.json"
cmp coopgames/verifiers/divergence/multigainer_common_spoke_star.json \
  "$scratch_dir/multigainer-common-spoke-star.json"
run_python coopgames/verifiers/divergence/audit_ordered_costar_bound.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/ordered-costar-bound.json"
cmp coopgames/verifiers/divergence/ordered_costar_bound.json \
  "$scratch_dir/ordered-costar-bound.json"
run_python coopgames/verifiers/divergence/audit_ceiling_root_gainer_exclusion.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/ceiling-root-gainer-exclusion.json"
cmp coopgames/verifiers/divergence/ceiling_root_gainer_exclusion.json \
  "$scratch_dir/ceiling-root-gainer-exclusion.json"
run_python coopgames/verifiers/divergence/audit_multiomission_direct_base.py \
  --output "$scratch_dir/multiomission-direct-base.json"
cmp coopgames/verifiers/divergence/multiomission_direct_base.json \
  "$scratch_dir/multiomission-direct-base.json"
run_python coopgames/verifiers/divergence/audit_generalized_packet_deficit_quota.py \
  --max-n 96 \
  --output "$scratch_dir/generalized-packet-deficit-quota.json"
cmp coopgames/verifiers/divergence/generalized_packet_deficit_quota.json \
  "$scratch_dir/generalized-packet-deficit-quota.json"
run_python coopgames/verifiers/divergence/audit_priced_decorated_costar.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/priced-decorated-costar.json"
cmp coopgames/verifiers/divergence/priced_decorated_costar.json \
  "$scratch_dir/priced-decorated-costar.json"
run_python coopgames/verifiers/divergence/audit_costar_saturation_dichotomy.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/costar-saturation-dichotomy.json"
cmp coopgames/verifiers/divergence/costar_saturation_dichotomy.json \
  "$scratch_dir/costar-saturation-dichotomy.json"
run_python coopgames/verifiers/divergence/audit_menu_relaxed_root_exchange.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/menu-relaxed-root-exchange.json"
cmp coopgames/verifiers/divergence/menu_relaxed_root_exchange.json \
  "$scratch_dir/menu-relaxed-root-exchange.json"
run_python coopgames/verifiers/divergence/audit_saturated_unit_exchange_boundary.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/saturated-unit-exchange-boundary.json"
cmp coopgames/verifiers/divergence/saturated_unit_exchange_boundary.json \
  "$scratch_dir/saturated-unit-exchange-boundary.json"
run_python coopgames/verifiers/divergence/audit_spectral_or_reserve.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/spectral-or-reserve.json"
cmp coopgames/verifiers/divergence/spectral_or_reserve.json \
  "$scratch_dir/spectral-or-reserve.json"
run_python coopgames/verifiers/divergence/audit_two_stratum_spectral_closure.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/two-stratum-spectral-closure.json"
cmp coopgames/verifiers/divergence/two_stratum_spectral_closure.json \
  "$scratch_dir/two-stratum-spectral-closure.json"
run_python coopgames/verifiers/divergence/audit_chosen_family_costar_closure.py \
  --output "$scratch_dir/chosen-family-costar-closure.json"
cmp coopgames/verifiers/divergence/chosen_family_costar_closure.json \
  "$scratch_dir/chosen-family-costar-closure.json"
run_python coopgames/verifiers/divergence/audit_split_top_spectral_structure.py \
  --output "$scratch_dir/split-top-spectral-structure.json"
cmp coopgames/verifiers/divergence/split_top_spectral_structure.json \
  "$scratch_dir/split-top-spectral-structure.json"
run_python coopgames/verifiers/divergence/verify_class_b_pair_row_handover.py \
  --output "$scratch_dir/class-b-pair-row-handover.json"
cmp coopgames/verifiers/divergence/class_b_pair_row_handover.json \
  "$scratch_dir/class-b-pair-row-handover.json"
run_python coopgames/verifiers/divergence/audit_class_b_support_alternative.py \
  --output "$scratch_dir/class-b-support-alternative.json"
cmp coopgames/verifiers/divergence/class_b_support_alternative.json \
  "$scratch_dir/class-b-support-alternative.json"
run_python coopgames/verifiers/divergence/verify_class_b_matching_counterexample_independent.py \
  --output "$scratch_dir/class-b-matching-counterexample-independent.json"
cmp coopgames/verifiers/divergence/class_b_matching_counterexample_independent.json \
  "$scratch_dir/class-b-matching-counterexample-independent.json"
run_python coopgames/verifiers/divergence/audit_class_b_three_row_supports.py \
  --output "$scratch_dir/class-b-three-row-supports.json"
cmp coopgames/verifiers/divergence/class_b_three_row_supports.json \
  "$scratch_dir/class-b-three-row-supports.json"
run_python coopgames/verifiers/divergence/verify_pxc87_necessity_independent.py \
  --output "$scratch_dir/pxc87-necessity-independent.json"
cmp coopgames/verifiers/divergence/pxc87_necessity_independent.json \
  "$scratch_dir/pxc87-necessity-independent.json"
run_python coopgames/verifiers/divergence/audit_pxc89_classification_counterexample.py \
  --output "$scratch_dir/pxc89-classification-counterexample.json"
cmp coopgames/verifiers/divergence/pxc89_classification_counterexample.json \
  "$scratch_dir/pxc89-classification-counterexample.json"
run_python coopgames/verifiers/divergence/verify_pxc89_classification_counterexample_independent.py \
  --output "$scratch_dir/pxc89-classification-counterexample-independent.json"
cmp coopgames/verifiers/divergence/pxc89_classification_counterexample_independent.json \
  "$scratch_dir/pxc89-classification-counterexample-independent.json"
run_python coopgames/verifiers/divergence/audit_faithful_sparse_lift_counterexample.py \
  --output "$scratch_dir/faithful-sparse-lift-counterexample.json"
cmp coopgames/verifiers/divergence/faithful_sparse_lift_counterexample.json \
  "$scratch_dir/faithful-sparse-lift-counterexample.json"
run_python coopgames/verifiers/divergence/verify_faithful_sparse_lift_counterexample_independent.py \
  --output "$scratch_dir/faithful-sparse-lift-counterexample-independent.json"
cmp coopgames/verifiers/divergence/faithful_sparse_lift_counterexample_independent.json \
  "$scratch_dir/faithful-sparse-lift-counterexample-independent.json"
run_python coopgames/verifiers/divergence/verify_n6_two_outsider_repair_obstruction.py \
  --output "$scratch_dir/n6-two-outsider-repair-obstruction.json"
cmp coopgames/verifiers/divergence/n6_two_outsider_repair_obstruction.json \
  "$scratch_dir/n6-two-outsider-repair-obstruction.json"
run_python coopgames/verifiers/divergence/verify_n6_split_cover_blocker_no_go.py \
  --output "$scratch_dir/n6-split-cover-blocker-no-go.json"
cmp coopgames/verifiers/divergence/n6_split_cover_blocker_no_go.json \
  "$scratch_dir/n6-split-cover-blocker-no-go.json"
run_python coopgames/verifiers/divergence/verify_n6_extreme_cover_rank_fidelity.py \
  --output "$scratch_dir/n6-extreme-cover-rank-fidelity.json"
cmp coopgames/verifiers/divergence/n6_extreme_cover_rank_fidelity.json \
  "$scratch_dir/n6-extreme-cover-rank-fidelity.json"
run_python coopgames/verifiers/divergence/verify_n6_zero_loss_cover_boundaries.py \
  --output "$scratch_dir/n6-zero-loss-cover-boundaries.json"
cmp coopgames/verifiers/divergence/n6_zero_loss_cover_boundaries.json \
  "$scratch_dir/n6-zero-loss-cover-boundaries.json"
run_python coopgames/verifiers/divergence/verify_n6_top_pair_blocker_no_go.py \
  --output "$scratch_dir/n6-top-pair-blocker-no-go.json"
cmp coopgames/verifiers/divergence/n6_top_pair_blocker_no_go.json \
  "$scratch_dir/n6-top-pair-blocker-no-go.json"
run_python coopgames/verifiers/divergence/verify_faithful_sparse_lift_resolution.py \
  --output "$scratch_dir/faithful-sparse-lift-resolution.json"
cmp coopgames/verifiers/divergence/faithful_sparse_lift_resolution.json \
  "$scratch_dir/faithful-sparse-lift-resolution.json"
run_python coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_exact_search.py \
  --output "$scratch_dir/unrestricted-pxc91c-exact-search.json"
cmp coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_exact_search.json \
  "$scratch_dir/unrestricted-pxc91c-exact-search.json"
run_python coopgames/verifiers/divergence/verify_unrestricted_pxc91c_pxc98_independent.py \
  --output "$scratch_dir/unrestricted-pxc91c-pxc98-independent.json"
cmp coopgames/verifiers/divergence/unrestricted_pxc91c_pxc98_independent.json \
  "$scratch_dir/unrestricted-pxc91c-pxc98-independent.json"
run_python coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_n5_archive.py \
  --output "$scratch_dir/unrestricted-pxc91c-n5-archive.json"
cmp coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_n5_archive.json \
  "$scratch_dir/unrestricted-pxc91c-n5-archive.json"
run_python coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells.py \
  --workers 4 --cell-timeout-ms 120000 \
  --output "$scratch_dir/unrestricted-pxc91c-n5-all-cells.json"
cmp coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells.json \
  "$scratch_dir/unrestricted-pxc91c-n5-all-cells.json"
run_python coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells.py \
  --workers 4 --cell-timeout-ms 120000 \
  --cell-driver coopgames/verifiers/divergence/search_archive/verify_unrestricted_pxc91c_n5_cell_ni.py \
  --encoding-label independent-NI \
  --output "$scratch_dir/unrestricted-pxc91c-n5-all-cells-ni.json"
cmp coopgames/verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells_ni.json \
  "$scratch_dir/unrestricted-pxc91c-n5-all-cells-ni.json"
run_python coopgames/verifiers/divergence/search_archive/faithful_sparse_lift_n6_search_v2.py \
  --total-max 11 --random-rounds 1000 --seed 20260821 \
  --output "$scratch_dir/faithful-sparse-lift-n6-run-v2.json"
cmp coopgames/verifiers/divergence/search_archive/faithful_sparse_lift_n6_run_v2.json \
  "$scratch_dir/faithful-sparse-lift-n6-run-v2.json"
run_python coopgames/verifiers/divergence/audit_control_branch_projection.py \
  --output "$scratch_dir/control-branch-projection.json"
cmp coopgames/verifiers/divergence/control_branch_projection.json \
  "$scratch_dir/control-branch-projection.json"
run_python coopgames/verifiers/divergence/audit_partially_fed_spectral_closure.py \
  --output "$scratch_dir/partially-fed-spectral-closure.json"
cmp coopgames/verifiers/divergence/partially_fed_spectral_closure.json \
  "$scratch_dir/partially-fed-spectral-closure.json"
run_python coopgames/verifiers/divergence/audit_carrier_separator_payment.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/carrier-separator-payment.json"
cmp coopgames/verifiers/divergence/carrier_separator_payment.json \
  "$scratch_dir/carrier-separator-payment.json"
run_python coopgames/verifiers/divergence/verify_n7_root_block_budget_counterexample.py \
  --output "$scratch_dir/n7-root-block-budget-counterexample.json"
cmp coopgames/verifiers/divergence/n7_root_block_budget_counterexample.json \
  "$scratch_dir/n7-root-block-budget-counterexample.json"
run_python coopgames/verifiers/divergence/verify_cardinality_ranked_support.py \
  --output "$scratch_dir/cardinality-ranked-support.json"
cmp coopgames/verifiers/divergence/cardinality_ranked_support.json \
  "$scratch_dir/cardinality-ranked-support.json"
run_python coopgames/verifiers/divergence/verify_excluded_block_deficit_quota.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output "$scratch_dir/excluded-block-deficit-quota.json"
cmp coopgames/verifiers/divergence/excluded_block_deficit_quota.json \
  "$scratch_dir/excluded-block-deficit-quota.json"
run_python coopgames/verifiers/divergence/verify_n7_quota_reserve_facet_boundary.py \
  --output "$scratch_dir/n7-quota-reserve-facet-boundary.json"
cmp coopgames/verifiers/divergence/n7_quota_reserve_facet_boundary.json \
  "$scratch_dir/n7-quota-reserve-facet-boundary.json"
run_python coopgames/verifiers/divergence/verify_weighted_three_role_coincidence.py \
  --output "$scratch_dir/weighted-three-role-coincidence.json"
cmp coopgames/verifiers/divergence/weighted_three_role_coincidence.json \
  "$scratch_dir/weighted-three-role-coincidence.json"
run_python coopgames/verifiers/divergence/verify_weighted_four_role_obstruction.py \
  --output "$scratch_dir/weighted-four-role-obstruction.json"
cmp coopgames/verifiers/divergence/weighted_four_role_obstruction.json \
  "$scratch_dir/weighted-four-role-obstruction.json"
run_python coopgames/verifiers/divergence/verify_weighted_four_role_family.py \
  --output "$scratch_dir/weighted-four-role-family.json"
cmp coopgames/verifiers/divergence/weighted_four_role_family.json \
  "$scratch_dir/weighted-four-role-family.json"
run_python coopgames/verifiers/divergence/verify_weighted_four_role_normalized_obstruction.py \
  --output "$scratch_dir/weighted-four-role-normalized-obstruction.json"
cmp coopgames/verifiers/divergence/weighted_four_role_normalized_obstruction.json \
  "$scratch_dir/weighted-four-role-normalized-obstruction.json"
run_python coopgames/verifiers/divergence/verify_weighted_balanced_seesaw.py \
  --output "$scratch_dir/weighted-balanced-seesaw.json"
cmp coopgames/verifiers/divergence/weighted_balanced_seesaw.json \
  "$scratch_dir/weighted-balanced-seesaw.json"
run_python coopgames/verifiers/divergence/verify_weighted_endowed_seesaw.py \
  --output "$scratch_dir/weighted-endowed-seesaw.json"
cmp coopgames/verifiers/divergence/weighted_endowed_seesaw.json \
  "$scratch_dir/weighted-endowed-seesaw.json"
run_python coopgames/verifiers/divergence/verify_common_face_endowment_scope.py \
  --output "$scratch_dir/common-face-endowment-scope.json"
cmp coopgames/verifiers/divergence/common_face_endowment_scope.json \
  "$scratch_dir/common-face-endowment-scope.json"
run_python coopgames/verifiers/divergence/verify_common_two_finite_z3.py \
  --output "$scratch_dir/common-two-finite-z3.json"
cmp coopgames/verifiers/divergence/common_two_finite_z3.json \
  "$scratch_dir/common-two-finite-z3.json"
run_python coopgames/verifiers/divergence/verify_weighted_fairness_selector.py \
  --output "$scratch_dir/weighted-fairness-selector.json"
cmp coopgames/verifiers/divergence/weighted_fairness_selector.json \
  "$scratch_dir/weighted-fairness-selector.json"
run_python coopgames/verifiers/divergence/verify_weighted_common_face_rigidity.py \
  --output "$scratch_dir/weighted-common-face-rigidity.json"
cmp coopgames/verifiers/divergence/weighted_common_face_rigidity.json \
  "$scratch_dir/weighted-common-face-rigidity.json"
run_python coopgames/verifiers/divergence/verify_carrier_cycle_cardinality.py \
  --output "$scratch_dir/carrier-cycle-cardinality.json"
cmp coopgames/verifiers/divergence/carrier_cycle_cardinality.json \
  "$scratch_dir/carrier-cycle-cardinality.json"
run_python coopgames/verifiers/divergence/verify_complement_star_facets.py \
  --output "$scratch_dir/complement-star-facets.json"
cmp coopgames/verifiers/divergence/complement_star_facets.json \
  "$scratch_dir/complement-star-facets.json"
run_python coopgames/verifiers/divergence/verify_n6_positive_residual_facets_z3.py \
  --output "$scratch_dir/n6-positive-residual-facets-z3.json"
cmp coopgames/verifiers/divergence/n6_positive_residual_facets_z3.json \
  "$scratch_dir/n6-positive-residual-facets-z3.json"
run_python coopgames/verifiers/divergence/verify_clone_expanded_rooted_star_facets.py \
  --output "$scratch_dir/clone-expanded-rooted-star-facets.json"
cmp coopgames/verifiers/divergence/clone_expanded_rooted_star_facets.json \
  "$scratch_dir/clone-expanded-rooted-star-facets.json"
run_python coopgames/verifiers/divergence/verify_complete_graph_rooted_pair_facets.py \
  --output "$scratch_dir/complete-graph-rooted-pair-facets.json"
cmp coopgames/verifiers/divergence/complete_graph_rooted_pair_facets.json \
  "$scratch_dir/complete-graph-rooted-pair-facets.json"
run_python coopgames/verifiers/divergence/verify_k4_edge_rooted_facet_z3.py \
  --output "$scratch_dir/k4-edge-rooted-facet-z3.json"
cmp coopgames/verifiers/divergence/k4_edge_rooted_facet_z3.json \
  "$scratch_dir/k4-edge-rooted-facet-z3.json"
run_python coopgames/verifiers/divergence/verify_pxc101_forced_zero_family.py \
  --output "$scratch_dir/pxc101-forced-zero-family.json"
cmp coopgames/verifiers/divergence/pxc101_forced_zero_family.json \
  "$scratch_dir/pxc101-forced-zero-family.json"
run_python coopgames/verifiers/divergence/verify_pxc101_forced_zero_family_independent.py \
  --output "$scratch_dir/pxc101-forced-zero-family-independent.json"
cmp coopgames/verifiers/divergence/pxc101_forced_zero_family_independent.json \
  "$scratch_dir/pxc101-forced-zero-family-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc104_cover_dependent_counterexample.py \
  --output "$scratch_dir/pxc104-cover-dependent-counterexample.json"
cmp coopgames/verifiers/divergence/pxc104_cover_dependent_counterexample.json \
  "$scratch_dir/pxc104-cover-dependent-counterexample.json"
run_python coopgames/verifiers/divergence/verify_pxc104_cover_dependent_counterexample_independent.py \
  --output "$scratch_dir/pxc104-cover-dependent-counterexample-independent.json"
cmp coopgames/verifiers/divergence/pxc104_cover_dependent_counterexample_independent.json \
  "$scratch_dir/pxc104-cover-dependent-counterexample-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc105_cross_cover_family.py \
  --output "$scratch_dir/pxc105-cross-cover-family.json"
cmp coopgames/verifiers/divergence/pxc105_cross_cover_family.json \
  "$scratch_dir/pxc105-cross-cover-family.json"
run_python coopgames/verifiers/divergence/verify_pxc105_cross_cover_family_independent.py \
  --output "$scratch_dir/pxc105-cross-cover-family-independent.json"
cmp coopgames/verifiers/divergence/pxc105_cross_cover_family_independent.json \
  "$scratch_dir/pxc105-cross-cover-family-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc106_cross_cover_dimension_lift.py \
  --output "$scratch_dir/pxc106-cross-cover-dimension-lift.json"
cmp coopgames/verifiers/divergence/pxc106_cross_cover_dimension_lift.json \
  "$scratch_dir/pxc106-cross-cover-dimension-lift.json"
run_python coopgames/verifiers/divergence/verify_pxc106_cross_cover_dimension_lift_independent.py \
  --output "$scratch_dir/pxc106-cross-cover-dimension-lift-independent.json"
cmp coopgames/verifiers/divergence/pxc106_cross_cover_dimension_lift_independent.json \
  "$scratch_dir/pxc106-cross-cover-dimension-lift-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc107_obstruction_alternative.py \
  --output "$scratch_dir/pxc107-obstruction-alternative.json"
cmp coopgames/verifiers/divergence/pxc107_obstruction_alternative.json \
  "$scratch_dir/pxc107-obstruction-alternative.json"
run_python coopgames/verifiers/divergence/verify_pxc108_invariant_cover_blocker_circuits.py \
  --output "$scratch_dir/pxc108-invariant-cover-blocker-circuits.json"
cmp coopgames/verifiers/divergence/pxc108_invariant_cover_blocker_circuits.json \
  "$scratch_dir/pxc108-invariant-cover-blocker-circuits.json"
run_python coopgames/verifiers/divergence/verify_pxc108_invariant_cover_blocker_circuits_independent.py \
  --output "$scratch_dir/pxc108-invariant-cover-blocker-circuits-independent.json"
cmp coopgames/verifiers/divergence/pxc108_invariant_cover_blocker_circuits_independent.json \
  "$scratch_dir/pxc108-invariant-cover-blocker-circuits-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc109_exact_cone_projection.py \
  --output "$scratch_dir/pxc109-exact-cone-projection.json"
cmp coopgames/verifiers/divergence/pxc109_exact_cone_projection.json \
  "$scratch_dir/pxc109-exact-cone-projection.json"
run_python coopgames/verifiers/divergence/verify_pxc109_exact_cone_projection_independent.py \
  --output "$scratch_dir/pxc109-exact-cone-projection-independent.json"
cmp coopgames/verifiers/divergence/pxc109_exact_cone_projection_independent.json \
  "$scratch_dir/pxc109-exact-cone-projection-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc112_certificate_dependence.py \
  --output "$scratch_dir/pxc112-certificate-dependence.json"
cmp coopgames/verifiers/divergence/pxc112_certificate_dependence.json \
  "$scratch_dir/pxc112-certificate-dependence.json"
run_python coopgames/verifiers/divergence/verify_pxc112_certificate_dependence_independent.py \
  --output "$scratch_dir/pxc112-certificate-dependence-independent.json"
cmp coopgames/verifiers/divergence/pxc112_certificate_dependence_independent.json \
  "$scratch_dir/pxc112-certificate-dependence-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc113_rank_potential_cycles.py \
  --output "$scratch_dir/pxc113-rank-potential-cycles.json"
cmp coopgames/verifiers/divergence/pxc113_rank_potential_cycles.json \
  "$scratch_dir/pxc113-rank-potential-cycles.json"
run_python coopgames/verifiers/divergence/verify_pxc113_rank_potential_cycles_independent.py \
  --output "$scratch_dir/pxc113-rank-potential-cycles-independent.json"
cmp coopgames/verifiers/divergence/pxc113_rank_potential_cycles_independent.json \
  "$scratch_dir/pxc113-rank-potential-cycles-independent.json"
run_python coopgames/verifiers/divergence/verify_pxc114_descent_set_potential.py \
  --output "$scratch_dir/pxc114-descent-set-potential.json"
cmp coopgames/verifiers/divergence/pxc114_descent_set_potential.json \
  "$scratch_dir/pxc114-descent-set-potential.json"
run_python coopgames/verifiers/divergence/verify_pxc114_descent_set_potential_independent.py \
  --output "$scratch_dir/pxc114-descent-set-potential-independent.json"
cmp coopgames/verifiers/divergence/pxc114_descent_set_potential_independent.json \
  "$scratch_dir/pxc114-descent-set-potential-independent.json"

bash coopgames/paper5/build_arxiv_release.sh
cmp coopgames/paper5/divergence.pdf \
  coopgames/paper5/arxiv_release/divergence-arxiv.pdf
cp coopgames/paper5/divergence.pdf "$scratch_dir/first-build.pdf"
cp coopgames/paper5/arxiv_release/divergence-arxiv-source.tar.gz \
  "$scratch_dir/first-build-source.tar.gz"
bash coopgames/paper5/build_arxiv_release.sh
cmp "$scratch_dir/first-build.pdf" coopgames/paper5/divergence.pdf
cmp "$scratch_dir/first-build-source.tar.gz" \
  coopgames/paper5/arxiv_release/divergence-arxiv-source.tar.gz

echo "PASS: paper5 reviewer/arXiv release suite"
