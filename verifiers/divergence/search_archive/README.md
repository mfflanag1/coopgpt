# Design-search archive for the saturated-arm campaign

Raw drivers and progress logs behind the finite search counts quoted in
`divergence.tex` for (PXC72), (PXC73), and (PXC76).  The drivers use the
exact certified selectors and are seeded; each log line is a JSON stats
snapshot every 25 rounds, and each finding line is a complete exact
witness.  Runs were stopped manually once their purpose was served, so
the quoted counts refer to the final logged snapshot of each run, not to
the full round budget.

| Artifact | Seed / scope | Quoted in print |
|---|---|---|
| `ds_pxc63b.log` | seed 20260816, n=7, stopped at round 4,650 | the (PXC72) search totals: 4,624 games, 2,034 divergent, 4,269 candidate roots, 109 ordered saturated roots, 99 aligned/equality, 7 `(PXC63b)` violations, 0 ordered-unsaturated |
| `ds_combined.log` | seed 20260817, n=7, total 14, stopped at round 6,300 | 151 roots, 141 packet-closed, 10 spectral-rescued, 0 combined failures |
| `ds_pxc76.log` | seed 20260819, n=7, stopped at round 1,450 | split-top uncovered violations (3), 1 PXC75-covered violation, 0 target violations |
| `ds_n8.log` | seed 20260818, n=8, total 16, stopped at round 875 | 10 ordered saturated roots, 0 failures |
| `ds_n8b.log` | seed 20260820, n=8, total 16, stopped at round 2,375 | 38 ordered saturated roots, all packet-closed; 0 combined failures, 0 target violations, 0 ordered-unsaturated |
| `split_top_extended_grid.json` | full split-family grid (12-minute run) | 75 split-top roots, sharpened bound closes all 75 |
| `hillclimb_combined.log` | seeds = five violation shapes | the both-sided plateau at the exact double boundary |
| `family_scan.log` | fixed parameter grid, n=7..9 | packet-violation growth and equality members quoted before the pinned grid replaced them |

The pinned, release-replayed evidence lives in the adjacent `audit_*`
verifiers; this directory only archives the discovery runs so that every
printed count has a recorded artifact.

## Violation classification

`classify_violations.py` recomputes exact selectors for every distinct
generator set among the archived finding lines and classifies each packet
violation against the `(PXC75)` hypotheses.  Result (2026-08-16): the ten
archived violation classes split as eight split-top-and-unfed and two
top-uniform-and-fed; together with the sixteen audited grid violations
(top-uniform and fed by construction), top-uniformity and co-star feeding
coincide on every audited packet violation.

`probe_top_uniform_feeding.py` mutates the known top-uniform violation
shapes one unit at a time: twenty more top-uniform packet violations, all
co-star fed (38/38 total with the audited classes); the feeding
implication remains a conjecture.

`wide_probe_run1.log` (seed 20260822, stopped near round 2,400): the
first many-generator run --- 185 feeding counterexamples and fourteen
`(PXC79)` escapes, all on one selector profile, repaired by `(PXC80)`.
The driver's disjunct list was then upgraded to the partially fed
hypotheses for subsequent runs.

- `probe_uncovered_outsider.py` + `probe_uncovered_outsider_run1.log` -- full two-generator grid sweep for the bipartite-pairing angle: 102 uniform-top violations, 18 pair-condition failures, 18/18 direct- and family-closed, every uncovered outsider at or below the Lmin floor (grid-wide).

- `ds_split_partial.py`/`.json` + `ds_split_b.py`/`.json` (logs gzipped) -- split-top design searches (seeds 20260825/20260827, 8000+6000 rounds): 810 split-top violations, 285 with a slack heavy-block row (class B), 285/285 with the top pair Lmax-tight, dispersion under the class-A bound and chain closed everywhere; zero partially fed, zero unfed, zero multi-heavy violations -- caveat: every observed violation has s=2, where partial feeding is impossible, so the partial-feeding absence is scope-limited.

- `wide_probe_v2.py`/`.json` (log gzipped, seed 20260824, 20000 rounds complete) -- PXC81-disjunct wide probe with pair-graph atlas: 5513 roots, 1724 violations, 1721 covered by the five pre-PXC83 mechanisms, 3 escapes (all rooted-triple menus, all closed by PXC83), 22 graph shapes.
- `wide_probe_n8.py`/`.json` (log gzipped, seed 20260826, 8000 rounds, n=8, seeded on the condition-failure shapes) -- 2337 roots, 998 violations, 996 covered + 2 PXC83-closed escapes; 705 gated feeding-counterexample logs (unfed neighborhoods by design); 32 graph shapes, 14 condition-failing; SEVEN ordered-but-unsaturated ceiling roots (nu = 5/4 < 4/3), first ever observed, one pinned as a verifier scope control; every one target-safe (overlap 50/3 vs 10).
- `ds_triple.py`/`.json` (log gzipped, seed 20260828, 8000 rounds around the triple-menu escape) -- 5642 roots, 4695 violations: 4666 rooted menus ALL closed by the PXC83 chain, 26 pair menus, 3 mixed menus (pair-condition covered, rootless rows present).
- `wide_probe_run2_partial.log.gz` -- PXC80-disjunct probe run 2 (seed 20260823), stopped at 11,200/20,000 rounds to free cores: 1162 violations, all covered, zero escapes.
- `ds_split_s3.py` -- s=3-seeded split search (running at archive time; results land separately).

- Second-wave hunts (seeds 20260830-32, logs gzipped): `ds_pairgap` -- 4,172 class-B instances mutated from archived witnesses, zero with a slack top pair (the class-B closure conjecture survives a dedicated refutation hunt); `ds_rootless` -- 1,008 violations, rootless rows never load-bearing; `ds_unsat` -- 10 more ordered-unsaturated roots, all one rigid species (nu=5/4); `probe_uncovered_big` -- extended family grid (g<=5, a<=8, n<=9): 508 uniform-top violations, 89 condition failures, 11 without direct, 3 with neither direct nor family (rooted-triple menus, PXC83-closed, one pinned), and the uncovered-outsider floor law refuted.

- `ds_exotic.py`/`.json` (log gzipped, seed 20260833) -- engineered attack on the class-B closure conjecture: a generator concentrated on {h, sub-gainer, outsider} is added to archived class-B witnesses to manufacture mixed tight rows through the heavy gainer that could block the egalitarian descent without the heavy block or the top pair.  8,000 engineered instances, 474 surviving class-B split violations, zero with a slack top pair: the engineered rows never displace the pair row as the descent blocker.

- `search_pxc89_profile_variants.py` + `pxc89_profile_variants.json` (seed 20260821, 2,000 rounds, symmetry-reduced 835-cover support list, 541 denominator-seven profiles within distance 12 of PXC88) -- calibrated profile-varying attack on the corrected pair/PXC78/PXC87/direct classification.  Three qualified packet violations were found: two pair-closed and one exact escape.  The escape is the PXC90 forked-cover counterexample, separately pinned by project-exact and independent 84-vertex verifiers.  The search JSON is discovery provenance, not proof evidence.  Reproduce with `python3 verifiers/divergence/search_archive/search_pxc89_profile_variants.py --rounds 2000 --max-profile-distance 12 --symmetry-reduced --output verifiers/divergence/search_archive/pxc89_profile_variants.json`.

- `faithful_sparse_lift_exact_search.py` + `faithful_sparse_lift_calibrations.json` -- exhaustive exact support census on the PXC88 and PXC90 calibrations.  PXC88 has one positive extreme top cover through the PXC89 bound; its minimal lift preserves Lmin but changes Lmax, while PXC90 remains faithful.  This is discovery/reproduction provenance; the adjacent primary and independent PXC92 verifiers are the proof artifacts.
- `faithful_sparse_lift_n6_probe.py` + `faithful_sparse_lift_n6_probe_run.json` (seed 20260821, 300 exact integer-envelope games) -- corrected dimension-six hostile probe: 26 divergent games, one ordered saturated root, no `g=3,k=2` root and therefore no strict single-heavy `s=2` root or reserve failure.  The topology predicate explicitly requires top `{r,h}`, exactly one top gainer, two tied sub-top gainers, and both outsiders strictly below them.  This is finite evidence only.
- `faithful_sparse_lift_n6_search_v2.py` + `faithful_sparse_lift_n6_run_v2.json` (seed 20260821) -- archive-calibrated n=6 campaign.  The complete replay of both pinned archives gives 374 games, 89 ordered saturated roots, 35 corrected `g=3,k=2` roots, zero strict single-heavy/top-size-two roots, and zero reserve failures.  The designed run contains 1,975 exact games: an exhaustive symmetry-reduced two-block integer grid through total 11 plus 1,000 seeded multigenerator envelopes.  It gives 592 divergent games, 104 `g=3,k=2` roots, four strict single-heavy roots, and zero reserve failures.  The driver fails closed if a reserve-plus-direct candidate reaches the unrun fidelity gate.  This is exhaustive only for the stated bounded grid and is not an all-six-player exclusion theorem.  Reproduce with `python3 verifiers/divergence/search_archive/faithful_sparse_lift_n6_search_v2.py --total-max 11 --random-rounds 1000 --seed 20260821 --output verifiers/divergence/search_archive/faithful_sparse_lift_n6_run_v2.json`.
- `faithful_sparse_lift_n6_profile_v3.py` + `faithful_sparse_lift_n6_profile_run_v3.json` -- exact profile/menu stress test with PXC88 and PXC90 selector calibrations.  For fixed `Cx={012>=12,013>=12,023>=10}` and `x=(6,4,2,2,2,2)`, all 186 denominator-seven symmetric-outsider profiles with their maximal comparison-compatible menus fail singleton normalization.  In the central 18 profiles (top numerator 29--31), all 501 positive extreme covers through size four and all 17,832 distinct unions of one or two covers were enumerated; every minimal Cx lift again fails singleton normalization.  This is exhaustive only for the two stated profile/menu cells, not for all games.  Reproduce with `python3 verifiers/divergence/search_archive/faithful_sparse_lift_n6_profile_v3.py --output verifiers/divergence/search_archive/faithful_sparse_lift_n6_profile_run_v3.json`.
