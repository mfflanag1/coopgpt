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
