# arXiv and reviewer release checklist

Date: 2026-08-10

This checklist covers the public manuscript in `divergence.tex`.  It does not
authorize submission through the author's arXiv account and does not convert
an internal reconstruction into external peer review.

## Canonical artifacts

```text
coopgames/paper5/divergence.tex
coopgames/paper5/divergence.pdf
coopgames/paper5/arxiv_release/divergence-arxiv-source.tar.gz
coopgames/paper5/arxiv_release/divergence-arxiv.pdf
```

The upload archive contains exactly one top-level file, `main.tex`.  The paper
has an inline bibliography and no figures, custom styles, hidden files,
external documents, shell escapes, generated bibliography, or auxiliary-file
dependency.  This follows arXiv's current TeX guidance: compilation occurs
from the submission root, necessary sources should be included, and auxiliary
outputs such as `.aux`, `.log`, and `.pdf` should not be placed in the TeX
source archive.

## Rebuild

Run from the repository root:

```bash
bash coopgames/paper5/build_arxiv_release.sh
```

The builder copies the source to a fresh temporary directory as `main.tex`,
runs PDFLaTeX three times with `-halt-on-error`, rejects LaTeX/package,
reference, box, and rerun warnings, writes the final PDF and source archive,
and prints the archive inventory and PDF metadata.  It intentionally excludes
the repository's 273 MB verification corpus from the arXiv upload; the paper
links to that public corpus instead.

## Mathematical release gates

- [ ] The coefficient-two reviewer report accepts both complete traces, or
      every identified gap has been repaired and re-reviewed.
- [ ] `(2,3,1):a72` has all 24 negative cuts and seven comparisons per cut.
- [ ] `(3,3,0):a74` has all 26 negative cuts and seven comparisons per cut.
- [ ] The independent and third coefficient-two verifiers pass from a
      Z3-enabled Python; base systems are SAT and full systems are UNSAT.
- [ ] The fifteen strict formulas byte-regenerate and all stored proof records
      verify.
- [ ] The exact `G(2,3)` lower-bound witness recomputes.
- [ ] The manuscript calls the six-player upper bound computer-assisted and
      does not treat solver agreement as proof of the human interface.
- [ ] Novelty is phrased as a targeted negative search pending specialist
      opinion, not as an established “first.”

## Typesetting and archive gates

- [ ] Clean PDFLaTeX build has no warnings, undefined references, box
      overflow, or missing glyphs.
- [ ] The PDF has 30 or more nonblank pages, letter-size portrait pages, no
      encryption, no forms, and no JavaScript.
- [ ] Every font is embedded.
- [ ] All pages have been rendered to PNG and visually inspected for clipping,
      overlap, broken equations, malformed tables, and unreadable references.
- [ ] The arXiv source tar contains only `main.tex` and rebuilds to the same
      manuscript from an otherwise empty directory.
- [ ] The reviewer PDF and arXiv PDF are byte-identical, or any harmless
      metadata difference is recorded.

## Suggested submission metadata

```text
Title: Maximal divergence of the leximin and leximax core selections in exact games
Author: Maxwell Flanagan
Primary category: econ.TH
Possible cross-list: math.OC
MSC 2020: 91A12; 90C05; 52B12
```

The author should confirm the category, license, abstract, and any affiliation
or ORCID in the arXiv interface.  The generated PDF must be viewed in arXiv's
submission preview before final submission, as required by arXiv.

## Reviewer packet

Send the PDF together with:

```text
coopgames/paper5/EXTERNAL_REVIEW_S6_DIRECT_BOUND.md
coopgames/paper5/S6_EXTERNAL_RECONSTRUCTION_PACKET.md
coopgames/paper5/S6_INTERFACE_REVIEW_WORKSHEET.md
coopgames/paper5/S6_SPECIALIST_NOVELTY_SIGNOFF.md
```

Ask reviewers to return correctness, formula-interface, coefficient-two,
novelty, and significance verdicts separately.  An affirmative novelty answer
does not validate the proof, and a passing proof-object replay does not
establish novelty.
