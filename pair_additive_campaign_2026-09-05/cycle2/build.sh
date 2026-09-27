#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -O verify_family_integer.py
python3 -O experiment/verify_finite_coupler.py
python3 -O experiment/verify_family_finite_types.py
python3 -O audit/symbolic_cover_certificate.py
