#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
paper_python="${COOPGT_PYTHON:-python3}"
case "${1:-}" in
  '') "$paper_python" -O certificates/check_all.py ;;
  --smt) "$paper_python" -O certificates/check_all.py --smt ;;
  --full)
    "$paper_python" -O certificates/check_all.py --smt
    latexmk -pdf -interaction=nonstopmode -halt-on-error -cd paper/manuscript.tex
    latexmk -pdf -interaction=nonstopmode -halt-on-error -cd review/specialist_packet.tex
    ;;
  *) printf '%s\n' 'Usage: bash build.sh [--smt|--full]' >&2; exit 2 ;;
esac
