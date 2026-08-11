#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
release_dir="$script_dir/arxiv_release"
scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/paper5-arxiv.XXXXXX")"
trap 'rm -rf "$scratch_dir"' EXIT

mkdir -p "$release_dir"
cp "$script_dir/divergence.tex" "$scratch_dir/main.tex"

(
  cd "$scratch_dir"
  pdflatex -file-line-error -halt-on-error -interaction=nonstopmode main.tex >/dev/null
  pdflatex -file-line-error -halt-on-error -interaction=nonstopmode main.tex >/dev/null
  pdflatex -file-line-error -halt-on-error -interaction=nonstopmode main.tex >/dev/null
)

if rg -n "LaTeX Warning|Package .* Warning|undefined|multiply defined|Overfull|Underfull" \
  "$scratch_dir/main.log"; then
  echo "release build produced a warning; inspect the lines above" >&2
  exit 1
fi

cp "$scratch_dir/main.pdf" "$script_dir/divergence.pdf"
cp "$scratch_dir/main.pdf" "$release_dir/divergence-arxiv.pdf"
(
  cd "$scratch_dir"
  tar -czf "$release_dir/divergence-arxiv-source.tar.gz" main.tex
)

tar -tzf "$release_dir/divergence-arxiv-source.tar.gz"
pdfinfo "$release_dir/divergence-arxiv.pdf" | sed -n '1,24p'
echo "PASS: arXiv source and PDF rebuilt from a clean one-file source tree"
