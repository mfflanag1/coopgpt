# Subsidies for truthful cooperation

A consolidated review manuscript by Maxwell Flanagan, 6 October 2026.

- [Manuscript PDF](output/pdf/manuscript.pdf) · [LaTeX source](manuscript.tex).
- [Two-page specialist brief](output/pdf/specialist_brief.pdf) · [Source](specialist_brief.tex).
- [Portable review and verification archive](truthful_cooperation_review.zip).
- [Source comparisons](SOURCE_COMPARISON.txt), [reviewer recommendations](REVIEWERS.txt), and [unsent outreach drafts](OUTREACH_DRAFTS.txt).
- [Internal audit](review/RESOLUTION.txt) and [validation record](validation/VALIDATION.json).

The paper combines the all-profile capped continuous-Banzhaf upper bound,
the unrestricted necessary total factor two, the sharp floor-free proportional
asymptotic, and nonlinear escapes on restricted profile families. It includes
complete proofs and the two-altered-binary-pool extension in an appendix.
The established game, Banzhaf functional, and strategic-report convention are
credited. This is a candidate contribution: historical novelty, significance,
and human specialist validation remain unresolved. The unrestricted constant-
budget question remains open.

Run from this directory with Python 3.9 or later (standard library only):

```sh
python3 -B -O verification/run_all.py
```

The runner checks copied-source hashes, executes all six verifiers in temporary
directories, requires fresh PASS reports, and compares their canonical hashes
against the archived results. Only Python-version metadata is excluded from
report identity. Reports and logs go to `validation/replay` by default; use
`--output /tmp/coopgt-replay` to choose another destination. Checks remain active
under `-O`. Hashes and finite tests are reproducibility evidence, not formal
proofs of the universal theorems or priority.

Build each standalone `.tex` source with the Codex LaTeX editor or two passes
of `pdflatex`. The supplied PDFs were compiled and visually inspected. No
third-party articles are redistributed. The archive contains the manuscript,
brief, source ledger and exact verifiers; internal model-review transcripts
and contact drafts remain separately available in the repository.

This package consolidates the relevant October 4–5 research campaigns. It is
one manuscript candidate, not a separate paper for each extension. Earlier
two-pool exponential-payment and random-order results remain in the campaign
archive and are not claimed as included here. External outreach is unsent.
