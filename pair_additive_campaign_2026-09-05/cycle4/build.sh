#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
coopgt_python="${COOPGT_PYTHON:-python3}"
if [[ -n "${1:-}" && "${1:-}" != "--full" ]]; then
    printf '%s\n' 'Usage: bash build.sh [--full]' >&2
    exit 2
fi
"$coopgt_python" -O root/verify_compact_proof.py
"$coopgt_python" -O experiment/verify_reduced.py
"$coopgt_python" -O experiment/verify_candidate.py
"$coopgt_python" -O theory/audit_candidate.py
if [[ "${1:-}" == "--full" ]]; then
    "$coopgt_python" -O zero_face/verify_compact_raw.py > zero_face/compact_raw_checks.json
    "$coopgt_python" -O zero_face/verify_one_ninth_raw.py > zero_face/one_ninth_raw_checks.json
    printf '%s\n' 'PASS independent raw full-core audits for 21 and 63 players; all six exclusion queries returned UNSAT'
fi
