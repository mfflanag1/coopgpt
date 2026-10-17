REPRODUCE — 17 OCTOBER 2026
Sharp subsidies for truthful production and network cooperation
Author identity and contact: pending confirmation for this paper.

Current typeset sources are manuscript.tex, supplement.tex, specialist_brief.tex
at package root. LATEX_SOURCES.zip contains those exact three standalone files.
A clean extracted-source latexmk build produced all final PDFs. ESM_1.pdf is an
exact-byte alias of supplement.pdf. Build logs and CLEAN_BUILD.json bind output.
Native desktop compilation also succeeded for all three on 17 October.

SOURCE BUILD
Extract LATEX_SOURCES.zip into a new empty folder. With TeX Live and latexmk:
  latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
  latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
  latexmk -pdf -interaction=nonstopmode -halt-on-error specialist_brief.tex
No external bibliography, figures or project inputs are required. The two
supplement hyperref warnings remove math delimiters from one bookmark only;
there are no unresolved references or overfull-box warnings in final logs.

SCOPED CHECKS — RUN ONLY IN A DISPOSABLE COPY
Python 3.10.14 standard library was used; no solver, network or GPU.
From verification/ in the extracted ESM_2.zip:
  python3 -B -O paper5/truthful_cooperation/submission_2026-10-14/verification/replay.py --output new-central-validation.json
  python3 -B -O update16/checks/portfolio/REPRODUCE.py
  python3 -B -O update16/checks/architecture/verify_transcription.py
Choose a central output name that does not already exist. The later runners
replace their adjacent reports, so do not run against the sealed package.
Fresh results are fresh-central-validation.json and the update16/checks JSONs.
All 5 central jobs, all 5 portfolio jobs and the architecture checker passed.
The transcription checker targets its frozen latex_fragment.txt, not a PDF
or the complete integrated supplement. Old dated checks under verification/
paper5 are provenance; they are not extra newly rerun suites.

Finite checks corroborate bounded identities/instances. They are not universal
proofs, a full replay of every historical result, or independent specialist review.
The full source-consistency and exact review-binding audit is separate.
