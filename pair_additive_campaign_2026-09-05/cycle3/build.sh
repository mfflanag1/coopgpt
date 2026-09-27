#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
coopgt_python="${COOPGT_PYTHON:-python3}"
"$coopgt_python" -O root/verify_finite_attainment.py
"$coopgt_python" -O theory/verify_factorization.py
"$coopgt_python" -O experiment/verify_composition.py 201
"$coopgt_python" -O experiment/verify_composition.py 210
if [[ "${1:-}" == "--full" ]]; then
    "$coopgt_python" -O independent/check_completion_obstruction.py > independent/completion_checks.json
    "$coopgt_python" -O independent/check_finite_attainment.py > independent/finite_attainment_checks.json
    printf '%s\n' 'PASS independent exact embedding obstruction and full-selector audit'
elif [[ -n "${1:-}" ]]; then
    printf '%s\n' 'Usage: bash build.sh [--full]' >&2
    exit 2
fi
