# Response to the hostile review of the four-player Lmin--Lmax bridge

Review received 2026-08-03 for commit `5376a76`.  Verdict: **verified with
qualifications; major revision before submission**.  The reviewer reported no
critical finding and no mathematical error, independently recomputed the
eleven-case classification, all four witnesses, the five-player counterexample,
and the sharp dimension threshold.  This response does not turn that review
into a novelty certification or journal peer review.

**Post-review update.**  A later revision replaces the finite classification
as the theorem proof by a structural human argument based on the published
egalitarian-core transfer-blocking property, a fractional protector-packing
inequality, and exact singleton witnesses.  A second hostile review of commit
`163ad4c` returned **verified**, checked every proof step by hand, and ran
adversarial computational tests.  The reviewed encodings remain independent
audits.  The historical findings below describe the state of commit
`5376a76`.

## Resolution of the structural-proof review (`163ad4c`)

The second reviewer found no fatal or mathematical issue.  The revision after
that review:

1. strengthens the five-player proposition: all 541 ordered payoff partitions
   are checked in exact linear-rational arithmetic, proving that the base game
   is not an exact partition game at any core allocation;
2. records the corollary that the base core has no Lorenz-dominating element,
   since its Lmin and Lmax allocations differ;
3. confirms that large-core progress is emitted on standard error, leaving
   standard output as valid JSON;
4. replaces the standalone note's absolute "no enumeration" wording by the
   accurate claim of a human-scale, mechanism-driven case analysis;
5. explains that the protector face is indexed by final payoff strata, so
   degenerate algorithmic pinning substeps do not affect the proof;
6. states that pinned coordinates carry free multipliers in the LP dual and
   folds nonempty protector existence into the packing lemma; and
7. updates the PR and reviewer materials to point to the reviewed SHA.

The only substantive pre-submission gate left by that reviewer is a definitive
MathSciNet/zbMATH and expert citation-chain novelty check for the through-four
exact-partition classification.

## Central correction

The manuscript no longer presents richer-suffix tightness as an unnamed new
condition.  It is the exact-partition condition of Llerena--Mauri (2017), read
from richest to poorest, and its Lorenz-dominance consequence is prior art.
The contribution is now stated narrowly:

> Every singleton-normalized exact game with at most four players is an exact
> partition game witnessed at its Lmin allocation; this classification and
> Lmin coalitional monotonicity both fail sharply at five players.

The bibliography now cites:

- Llerena--Mauri (2017), *On the existence of the Dutta--Ray's egalitarian
  solution*, Mathematical Social Sciences 89, 92--99;
- Dietzenbacher--Yanovskaya (2020), *Antiduality in exact partition games*,
  Mathematical Social Sciences 108, 116--121.

## Resolution of findings

1. **Exact-partition attribution (high): resolved.**  The lemma is retitled as
   a finite exact-partition classification, the published definition and
   Lorenz result are cited, and novelty is limited to the through-four-player
   inclusion and sharpness.
2. **Five-player verifier did not recompute Lmin (high): resolved.**
   `src/verify_n5_exact_leximin_monotonicity_counterexample.py` now recomputes
   both allocations with the exact rational staged Maschler implementation and
   rejects disagreement with the displayed vectors.
3. **Stale bridge artifact (high): resolved.**  The primary verifier now
   supports `--output`; its JSON was regenerated.  The new
   `src/verify_n4_exact_lmin_pes_artifacts.py` regenerates all four bridge
   artifacts in a temporary directory and requires byte identity with the
   committed files and with each program's standard output.
4. **Incorrect interpolation wording (medium): resolved.**  The manuscript now
   uses concavity of decreasing-rearrangement partial sums against the affine
   partial sums of a tied Lmin block.
5. **Lmax identification elided (medium): resolved.**  The proof now states the
   sorted-vector equality and uniqueness step.
6. **Monotonicity domain unquantified (medium): resolved.**  The theorem now
   quantifies over exact pairs `v,v'` on the same `N` with
   `v'=v+d*1_S`, `d>0`.
7. **Encoding independence overstated (medium): resolved.**  The second
   verifier is described as independently formulating Lmin optimality only;
   both encodings explicitly share the exactness system, normalization, and Z3
   engine.
8. **Unsat-core evidentiary value overstated (medium): resolved.**  The cores
   are described as same-solver audit conveniences, not Farkas certificates,
   hand-checkable certificates, or independent evidence.
9. **Five-player large-core fact omitted (medium): resolved with a new exact
   proposition.**  `src/verify_n5_exact_lmin_lmax_large_core.py` exhausts all
   169,911 candidate bases of Sharkey's acceptable-payoff polyhedron in exact
   rational arithmetic, verifies all 12 base and 8 endpoint vertices are
   core-dominated, and computes
   `Lmax(base)=Lmax(endpoint)=(2,0,6,6,6)`.  It also checks the base suffix
   slack `Lmin({3,5})=13>12=v({3,5})`.
10. **Optimized-mode framing (low): resolved.**  The guards are described as
    defensive policy, not load-bearing logic.
11. **Affine path under-checked (low): clarified.**  Endpoint feasibility is
    used with affine constraints to prove segment feasibility; the endpoint
    counterexample is independently recomputed by exact LP.  No stronger claim
    is assigned to the path loop.
12. **Unique-richest observation mislabeled (low): resolved.**  It is now
    identified as a corollary of exact-partition tightness, not corroborating
    evidence.
13. **Dead locals and slow-run usability (low): resolved.**  The unused local
    in the primal direction test was removed, and per-composition progress is
    emitted to standard error during the exhaustive run.

## Remaining limitations

- At the first reviewed commit, no concise hand proof replaced the finite
  computer-assisted classification.  That limitation is now superseded by the
  externally verified structural proof noted above.
- The two exhaustive encodings share the definition-level exactness system and
  Z3, although their Lmin-optimality formulations differ.
- The finite-classification novelty claim still requires MathSciNet/zbMATH and
  expert citation-chain review focused on exact-partition and Lorenz-stable
  games.
- The result has two favorable hostile external reviews, not journal
  acceptance or a definitive novelty opinion.
