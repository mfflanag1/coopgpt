# Pairs and triples: consolidated research checkpoint

5 September 2026. This package consolidates the two-sided and three-sided campaigns into one eight-page proof note and investigates priority at the level of individual claims.

**Main change in assessment:** the bipartite half-payoff guarantee follows from Vazirani v6's algorithmic invariants. The sharper candidate contribution is the finite graph distance bound together with the explicit three-sided construction approaching maximum disagreement. Novelty and field significance remain unconfirmed.

## Results under common definitions

Let x be full ascending leximin, z full descending lexicographic minimum, H_i the player's maximum over the entire core, T the integral matching value, and rho=||x-z||_1/T. Count all players, including fixed zeros. All models have unit capacity and a nonempty entire core.

| Market class | Individual guarantee | Sharp distance statement |
|---|---|---|
| Graph matching, including nonbipartite graphs | x_i>=H_i/2 | Exact n-player maximum floor(n/2)/(floor(n/2)+1) for n>=4; zero for n=2,3 |
| Complete additive triples, equal sector sizes | x_i>=H_i/3 | Supremum 4/3 |
| Arbitrary three-sided assignment | No positive uniform fraction | Supremum 2; all-n deficit O(log n/n) |

Half rho is the minimum fraction of surplus that changes recipients between rules. This is not a welfare loss. The triple construction has values in {0,1,2,3}, linear positive-triple count and a three-dimensional core. Explicit obstructions separate it from pair-additive and ordered-supermodular/local-monotonicity subclasses.

## Files

- `pairs_and_triples.tex`, `output/pdf/pairs_and_triples.pdf`: unified definitions, statements, complete proofs and qualified attribution.
- `PRIORITY_MATRIX.md`: claim-level verdict, significance assessment, limitations and direction.
- `TWO_SIDED_PRIORITY_AUDIT_2026-09-05.md`, `THREE_SIDED_PRIORITY_ADDENDUM.md`: exact primary-source anchors and access boundaries.
- `consolidated_theorem_audit.md`: independent mathematical and integration audit. Its m>=2 correction is incorporated in the manuscript.
- `REVIEW_REQUEST.md`: local specialist-review draft; not sent.
- `verify_extensions.py`, `extension_checks.json`: six graph and eight additive cases, including negative controls, full selectors, entire-core maxima and any-minimax violation checks.
- `verify_priority_exclusions.py`, `priority_exclusion_checks.json`: raw cube and positive recurrence certificates at four depths.
- `pdf_manifest.json`, `source_downloads.json`, catalog records and retrieval log: source versions, hashes and inaccessible-original evidence. Downloaded source PDFs remain in research scratch; they are not redistributed here.
- `exact_three.py`, `triple_recurrence_family.py`: unchanged support files copied from the protected three-sided checkpoint, with provenance in `BASELINE_HASHES.json`.

## Reproduce new checks and build

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python verify_extensions.py
.venv/bin/python verify_priority_exclusions.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf pairs_and_triples.tex
shasum -a 256 -c SHA256SUMS
```

Checks require z3-solver 5.1.0.0 and fail on UNKNOWN. They test the new consolidation claims; the previous exhaustive campaign suites were not needlessly repeated. Source manifests and stored outputs were inspected for scope before use. Regenerated PDF metadata or solver witnesses may change file hashes without changing the mathematics.

The consolidated PDF build passed and all eight rendered pages were inspected. Prior work at checkpoints 99e6e084, 2466be6f and de315e8f is preserved. New material is saved separately and the recovery summary records the revised priority judgment.

No external messages, publication, purchase or remote push occurred. Investigating priority is complete to the documented evidence boundary; proving first discovery and external significance is not claimed. Original Quint and Lucas full texts remain the most concrete source gap.
