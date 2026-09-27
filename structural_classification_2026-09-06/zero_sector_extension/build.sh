#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
transfer_python="${COOPGT_PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
if [[ "${1:-}" == "--smt" ]]; then
  "$transfer_python" -O check_extension.py --smt
elif [[ -z "${1:-}" ]]; then
  "$transfer_python" -O check_extension.py
else
  exit 2
fi
