#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
"${COOPGT_PYTHON:-python3}" verify.py "${1:-}"
