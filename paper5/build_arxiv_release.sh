#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
release_dir="$script_dir/arxiv_release"
scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/paper5-arxiv.XXXXXX")"
trap 'rm -rf "$scratch_dir"' EXIT

# Freeze all time-sensitive build metadata so that two clean builds of the
# same source are byte-identical.  This is 2026-08-10 00:00:00 UTC, the paper
# date recorded in divergence.tex.
SOURCE_DATE_EPOCH=1786320000
FORCE_SOURCE_DATE=1
TZ=UTC
COPYFILE_DISABLE=1
export SOURCE_DATE_EPOCH FORCE_SOURCE_DATE TZ COPYFILE_DISABLE

mkdir -p "$release_dir"
cp "$script_dir/divergence.tex" "$scratch_dir/main.tex"
touch -t 202608100000.00 "$scratch_dir/main.tex"

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
  tar --format ustar -cf "$release_dir/divergence-arxiv-source.tar" main.tex
)
gzip -n -f "$release_dir/divergence-arxiv-source.tar"

tar -tzf "$release_dir/divergence-arxiv-source.tar.gz"
pdfinfo "$release_dir/divergence-arxiv.pdf" | sed -n '1,24p'
echo "PASS: arXiv source and PDF rebuilt from a clean one-file source tree"
