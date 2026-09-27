#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
"${COOPGT_PYTHON:-python3}" -O verify.py "$@"
