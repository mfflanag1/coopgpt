#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
route_python="${COOPGT_PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
if [[ "${1:-}" == "--smt" ]]; then
  "$route_python" -O check_route.py --smt
elif [[ -z "${1:-}" ]]; then
  "$route_python" -O check_route.py
else
  exit 2
fi
