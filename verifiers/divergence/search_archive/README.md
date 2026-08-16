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
