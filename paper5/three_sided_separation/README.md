# Three-sided assignment: maximal selector separation

Internal result, 2026-09-04. The sharp supremum of full leximin versus full leximax-min normalized L1 distance over standard three-sided assignment games with nonempty entire cores is **2**, even with equally sized sectors and triple weights in {0,1,2,3}. No positive dimension-independent fraction of a player's maximum core payoff is guaranteed by leximin.

For L>=1 and R>=0, the explicit family has

    n = 9(L+R)+12, T = 3(L+R+2),
    rho = 2[((R+2)2^L-1)] / [(2^L+2)(L+R+2)].

Taking R=L² gives rho→2. Padding the optimized parameters proves 2-S_n=O(log n/n) for every sufficiently large total player count. A top V player has maximum core payoff 1 and leximin payoff 2/(2^L+2). A separate unshifted family gives an exponentially small fraction 1/(2^L+1) while both selectors coincide.

The main construction uses only 12(L+R)+9 positive triples, linear in player count. Every dummy is counted. An explicit integral matching and equal-value feasible cover certify the optimum and core nonemptiness. The proof identifies the **entire** core and both **full** selectors. These are nonempty-core games, not exact TU games in the technical cooperative-game sense.

## Reading

- `three_sided_separation.tex` and `output/pdf/three_sided_separation.pdf`: four-page theorem-first note.
- `CONSTRUCTION_PROOF.md`: expanded construction proof and controls.
- `coordinate_amplification.md`: companion coincident-selector family.
- `distance_family_independent_audit.md`, `final_independent_audit.md`: independent structural and verifier audits.
- `PRIMARY_SOURCE_AUDIT.md`, `SOURCE_HASHES.json`: dated primary-source and bounded novelty audit.
- `REVIEW_PACKET.md`: specialist review materials, prepared locally and not sent.

## Reproduce

Requires Python 3.10+ and z3-solver 5.1.0.0. The main sparse generator uses the standard library only.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run_checks.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=output/pdf three_sided_separation.tex
shasum -a 256 -c SHA256SUMS
```

The shipped results are exact rational output. Source hashes identify downloaded primary PDFs, which are not redistributed here. The manifest covers frozen delivered files; regenerated solver witnesses or PDF metadata may change bytes without changing the mathematics. Checks raise on solver failure or UNKNOWN and do not rely on Python assertions.

## Verification scope

- All 256 binary 2x2x2 arrays: full coalition worths computed by integral matching recursion; Lucas conditions checked after relabeling an optimal matching. There are 237 positive nonempty-core markets, 18 empty-core markets and one zero-value control. The 237 have coincident full selectors; their smallest observed individual fraction is 1/3.
- Published nonbinary empty-core example: independently enumerated integral optimum 7, Lucas failure 11<14, fractional obstruction 17/2.
- Twelve fixed-seed nonadditive 3x3x3 samples with weights 0..5: eight nonempty cores; not an exhaustive classification.
- Additive calibration m=2,3,4: entire-core selectors and rho=4m/[3(m+2)].
- Parent raw-generator checks: unshifted depths 0,1,2,3,5 and six shifted/replicated cases through 165 players.
- Separate raw construction: four full-selector and entire-core-inclusion checks through 192 players, including rho=287/198>4/3. Separate unshifted generator: four cases and integer matching optimization.
- Negative controls: deleting complementary triples permits off-recurrence core points; removing root anchors enlarges the core; removing recurrence gives coincident selectors. Root-anchor removal is a characterization control, not an asserted distance change.

Independent generators and conventional proofs are checked against raw inequalities. The exact optimizer helper is shared; these are not independent solver implementations. The all-parameter result rests on the proof. The final PDF was built and all four rendered pages inspected.

## Status and limits

The active mathematical target is resolved internally. The two-sided predecessor has supremum 1 and a half-of-core-maximum guarantee; three-sided games permit supremum 2 and no positive guarantee. This is a structural change in the natural market class.

The bounded audit found no matching prior theorem, but original Quint and Lucas full texts were not inspected. External correctness, priority and significance remain unverified. No sharp finite-n formula or optimal deficit coefficient is claimed. No external messages, publication or remote push occurred.

Protected earlier checkpoints: 99e6e08499b945c97c8533dc526abcc8065ff80b and 2466be6fe9237e5c9ab64a047de2aa5de05ea01e. Their research artifacts remain unchanged.
