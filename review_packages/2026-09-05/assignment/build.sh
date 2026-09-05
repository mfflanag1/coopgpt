#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p output/pdf
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf manuscript.tex
