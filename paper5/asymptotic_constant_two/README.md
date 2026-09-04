# Sharp asymptotic separation: constant two

Internal research checkpoint, 2026-09-04. For singleton-normalized exact TU games with positive grand-coalition value, let s_n be the supremum of normalized L1 distance between the full leximin and leximax-min core selections. The conventional proof establishes

    lim n(2-s_n) = 2,
    2-s_n = 2/n + O(log(n)/n^2).

This determines c_* and replaces the earlier frontier 2 <= c_* <= 3+2sqrt(2). PXC151 remains a valid construction. Its frozen files are unchanged; its coefficient was not globally optimal.

## Read first

- `output/pdf/sharp_asymptotic_separation.pdf`: four-page theorem-first manuscript; source is `sharp_asymptotic_separation.tex`.
- `THREE_GENERATOR_PROOF.md`: independent all-parameter construction extending PXC151 by increasing the intermediate role's multiplicity.
- `COALITION_CLOSURE_CONTROL.md`: exact explanation of why the initial abstract convex-set example loses its separation after coalition closure.
- `REVIEW_PACKET.md`: precise claims, review questions, prior-art boundaries, and recommended next direction.

The main construction encodes a Fibonacci recurrence using complementary coalition equalities. An invertible zero-one incidence matrix forces the entire core to be a line segment. The unique first-stage maximin and minimax points are therefore the full selectors. This realization lemma is useful beyond the particular asymptotic constant.

## Reproduce the rational checks

From this directory, with Python 3.13 and package installation available:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verify_closure.py
.venv/bin/python verify_fibonacci_segment.py
.venv/bin/python -O verify_integer_family.py
```

The scripts need only the standard library and Z3; no floating-point solver is used. They reconstruct every proper nonempty coalition inequality directly from generator coordinates, and regenerate the three `*_calibration.json` files beside the scripts. Any failed claim, timeout, or UNKNOWN result raises an error. Arithmetic results and verdicts are exact; a solver-chosen negative-control witness may vary between solver versions.

Recorded environment: Python 3.13.5; z3-solver 5.1.0.0 (runtime reports 5.1.0). The integer-family replay was also run under Python optimization (`-O`), which cannot disable its explicit checks.

| Check | Coverage | What is independently checked |
|---|---|---|
| Coalition closure | 24 cases, n=4 through 9 | Proposed core equals the full coalition core in both directions; all lexicographic stages and overlap |
| Fibonacci family | 5 cases, n=8,9,11,12,14 | No core point lies off the segment; exact floor/ceiling values; both first-stage faces are singletons |
| Three-generator family | 4 cases, n=9,10,12,13 | 16 UNSAT queries exclude better objectives and other optimal-face allocations |
| Negative controls | 3 | Out-of-chamber closure formula fails; perturbing Fibonacci unit-sum weights enlarges the core; out-of-domain three-generator formula fails |
| Arithmetic calibration | m=2 through 64; six all-n parameter choices | Fibonacci identities, admissibility, and exact deficit formulas |

The universal result is proved symbolically in the manuscript. Finite exact replays corroborate the proof; they do not replace it or constitute formal proof-assistant verification.

## Build the manuscript

With a standard TeX Live installation including latexmk:

```sh
mkdir -p output/pdf
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf sharp_asymptotic_separation.tex
```

The release build used TeX Live 2026 and latexmk 4.88. Its log had no undefined references or overfull/underfull warnings; all four rendered pages were visually inspected. PDF metadata timestamps can differ on rebuild; byte-identical PDFs are not asserted. `SHA256SUMS` identifies the released source, evidence and PDF files, excluding itself and temporary build files.

## Status and provenance

The proof and construction were developed in the recovered CoopGT task. The main argument received independent adversarial checks, including the all-n threshold, normalization, exactness, matrix invertibility, and selector uniqueness. All 33 finite cases and all three negative controls passed the final portable replay. The historical 66-stage PXC151 suite was not rerun: no frozen PXC151 code or manuscript was changed, and this release has its own full-coalition verification.

This is a completed internal mathematical checkpoint. External correctness, prior-art and significance review are pending. No specialist endorsement or field-level importance is claimed, and no external messages were sent.
