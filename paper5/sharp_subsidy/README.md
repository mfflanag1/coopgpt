# Sharp subsidies for protecting core maxima

**Working manuscript, 3 October 2026.** [Read the ten-page PDF](output/pdf/manuscript.pdf) or [edit the standalone LaTeX source](manuscript.tex).

In a strict three-sector assignment market, how much external money is needed to give every player one third of their best original stable payoff? The sharp worst-case subsidy is one third of the original surplus, as a supremum over finite markets. Every individual finite market needs strictly less.

The assumptions are equal finite sector sizes, nonnegative pair-additive full-team values, integral matching worth, positive grand worth, and a nonempty original entire core. Only full triples are productive. The individual maxima are frozen before intervention. The manuscript includes the direct fractional upper proof, the all-parameter sharpness construction, the sharp bound for integral partial-matching obstructions, and exact slack identities.

## Review and scope

- [Coordinator self-audit and adjudication](review/SELF_AUDIT.md): every load-bearing step, boundary case, and independently checked reviewer finding.
- [Fresh Fable 5.1 manuscript review](review/fable_review.md): no mathematical error found; low-severity exposition, notation, and attribution findings were addressed. This review executed no code and did not assess novelty.
- [Source comparison update](review/SOURCE_SCOPE.md): established ingredients, original passages checked, and unresolved comparisons.
- [Verification report](review/VERIFICATION.json) and [build and visual-inspection record](review/BUILD_QA.json).

Human specialist validation and historical priority remain pending. This is not a claim of a field-level breakthrough, formal verification, or publication readiness following journal review. No outreach or submission was made. The original theorem package remains a [historical proof archive](../../research_campaigns/2026-10-03-core-witness/sharp_result/SHARP_ONE_THIRD.md); this manuscript supersedes its presentation, not its mathematical claims.

## Reproduce the checks

Python 3, standard library only; no solver or network is needed. From this directory:

```sh
python3 -B -O verification/verify.py --output /tmp/coopgt-sharp-verification.json
```

The runner also works from an arbitrary directory using an absolute script path. It verifies hashes, runs the checks with Python assertions disabled, and writes intermediate files only to a temporary directory. It checks 27 ordered label triples, four per-label identities, two global identities, 48 rational packing cases, four enriched diagnostic points, and 3,603,804 full-team inequalities across twelve construction sizes. It rejects 28 altered symbolic identities, twelve damaged allocations, and two false relaxed points; a further scope control disproves applying the integral formula to fractional residual mass.

The enriched points are necessary-condition diagnostics; their inclusion does not certify that every stored vector is realizable as a market's core maxima. All-size validity comes from the written proofs.

The two mathematical checkers and six fixtures are unchanged copies of earlier project files. Their origins and hashes are in [verification/PROVENANCE.json](verification/PROVENANCE.json). In those historical scripts, `B` means the manuscript's scalar `beta`, and their construction parameter `q` means the manuscript's `ell`; neither is a player residual weight there.

## Build the PDF

Open `manuscript.tex` in the Codex LaTeX editor, or use an existing TeX installation:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir=/tmp/coopgt-sharp-build \
  -pdflatex='pdflatex -no-shell-escape %O %S' manuscript.tex
```

The source is standalone and requires no bibliography file. The release PDF was also rendered and visually inspected page by page. The package's file hashes are in [MANIFEST.json](MANIFEST.json).
