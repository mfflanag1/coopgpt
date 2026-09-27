#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
paper_python="${COOPGT_PYTHON:-python3}"
case "${1:-}" in
  '') "$paper_python" verification/run_checks.py ;;
  --smt) "$paper_python" verification/run_checks.py --smt ;;
  --pdf) mkdir -p output/pdf; latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf paper/manuscript.tex ;;
  --full) "$paper_python" verification/run_checks.py --smt; mkdir -p output/pdf; latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf paper/manuscript.tex ;;
  *) exit 2 ;;
esac
