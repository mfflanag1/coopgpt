#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -O verify_rational.py
python3 -O experiment/verify_saved_rationals.py
python3 -O literature/audit_checks.py
