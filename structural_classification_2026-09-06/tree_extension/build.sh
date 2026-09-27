#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tree_python="${COOPGT_PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
"$tree_python" -O check_synthesis.py C4_INTEGER_CERTIFICATE.json
"$tree_python" -O check_synthesis.py cycle_m3_sector0_above8.json
"$tree_python" -O check_negative.py
if [[ "${1:-}" == "--smt" ]]; then
  "$tree_python" -O check_clipping.py
elif [[ -n "${1:-}" ]]; then
  exit 2
fi
