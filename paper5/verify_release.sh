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
