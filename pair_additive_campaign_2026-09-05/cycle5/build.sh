#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
coopgt_python="${COOPGT_PYTHON:-python3}"
if [[ -n "${1:-}" && "${1:-}" != "--full" ]]; then
    printf '%s\n' 'Usage: bash build.sh [--full]' >&2
    exit 2
fi
"$coopgt_python" -O root/verify_scope_witness.py
"$coopgt_python" -O recurrence/verify_saved.py
if [[ "${1:-}" == "--full" ]]; then
    "$coopgt_python" -O independent/verify_family.py --smt
else
    "$coopgt_python" -O independent/verify_family.py
fi
