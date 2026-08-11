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
