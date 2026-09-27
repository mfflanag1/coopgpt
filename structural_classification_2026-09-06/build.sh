#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
graph_python="${COOPGT_PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
"$graph_python" -O check_cycle.py
"$graph_python" -O check_negative.py
if [[ "${1:-}" == "--smt" ]]; then
  "$graph_python" -O verify.py
elif [[ -n "${1:-}" ]]; then
  exit 2
fi

bash tree_extension/build.sh "${1:-}"

bash zero_sector_extension/build.sh "${1:-}"

bash diagonal_subdivision/build.sh "${1:-}"

bash subdivision_uniform_bound/build.sh "${1:-}"

bash selective_c4/build.sh "${1:-}"

bash graph_dichotomy/build.sh "${1:-}"
