# PXC151 goal-completion audit

Audit date: 2026-08-30

Frozen mathematical commit:
`8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564`

Starting commit required by the campaign:
`d57b6a22bae7d3f6ca747a1b38cdc9e9a743cec9`

This file audits the original two-growing-block objective requirement by
requirement. It does not strengthen any theorem and is not a substitute for
external review. “Proved” below means proved internally at the frozen commit;
it does not mean externally accepted or novel.

## Completion verdict

The mathematical construction deliverable (outcome 1) is internally
complete: PXC151 is an all-parameter infinite exact family with conventional
selector proofs, an infinite strict benchmark improvement, independent exact
selector replay, negative controls, and the required PXC146 boundary
calibrations. The full objective is **not yet complete** because no external
cooperative-game specialist has returned a correctness and prior-art verdict.
No field-level claim is currently permitted.

## Requirement map

| Original requirement | Authoritative evidence | Verdict |
|---|---|---|
| Start from PXC146 commit `d57b6a2` | Git ancestry `d57b6a2 -> 4b4f271 -> 1956134 -> 5747ba3 -> c693137 -> 8d5947f` | Proved |
| Both the `m`-player floor-gainer block and an `r`-player loser block grow | `K_{m,r}` has roles `U^m,b,c,d,E^r,g`, for every `m>=2,r>=3`; `divergence.tex` (PXC151a) | Proved |
| Require `H_{m,2}=H_m` | The campaign defines `Hhat_{m,2}:=H_m` and `Hhat_{m,r}:=K_{m,r}` for `r>=3`; the manuscript explicitly calls this a structural handover, not algebraic continuation | Proved as a piecewise boundary calibration; external reviewer must assess whether this satisfies the intended meaning of “extending” |
| Reproduce `H_7,H_8,H_9,H_10` and all PXC146 formulas | PXC151 primary verifier checks PXC146 `m=1..8`; the release suite separately replays PXC144 and both PXC146 verifiers | Proved |
| Begin with the PXC146 four-generator incidence mechanism | PXC147 (`4b4f271`) derives the incidence-faithful two-block formulas and both selector chambers | Proved |
| If that template fails, explain the obstruction structurally | PXC147 proves `rho<8/5` for the complete incidence-faithful class and identifies the forced linear total scale; PXC148 classifies the one-row repairs; PXC149 and PXC150 prove stronger exactness-witness bottlenecks for split-block and complete-pair menus | Proved for the explicitly stated template classes, not for arbitrary four-generator games |
| Identify a minimal viable escape mechanism | PXC151 drops the complete pair-menu floor proof and replaces it by sequential whole-gainer then loser pinning. It uses three lower-envelope generators and a three-row minimax dual | Constructive escape proved; literal global minimality among every conceivable mechanism is not claimed or required once outcome 1 is achieved |
| Exactness for all parameters | `K_{m,r}` is the lower envelope of three efficient nonnegative allocations; every coalition minimum is attained by a displayed allocation | Proved conventionally |
| Singleton normalization for all parameters | The zero sets of `B_0,C_0` cover every player, so every singleton minimum is zero | Proved conventionally |
| Closed `Lmin` | (PXC151b)--(PXC151d) pin `U,g,b,d,E,c` using core inequalities and efficiency | Proved conventionally |
| Closed `Lmax` | (PXC151e)--(PXC151f) give a normalized minimax dual, prove the ceiling, and use equality rows to pin all later strata | Proved conventionally |
| Closed overlap and `rho(m,r)` | (PXC151g): `O=2m+r+2`, `rho=2(2mr-m-1)/(2mr+m+r+1)` | Proved algebraically |
| Infinite strict improvement over balanced `G` | (PXC151h) gives the exact diagonal margin `2(k^2-4k-2)/((k+2)(2k^2+2k+1))`, positive exactly for integers `k>=5` | Proved |
| A ray with deficit coefficient below 8 | (PXC151i): for `m/r->a`, `n(2-rho)->C(a)=2a+3+1/a`; minimum `3+2sqrt(2)<8` at `a=1/sqrt(2)`; diagonal gives 6 | Proved |
| Exact rational discovery/checking only | Primary verifier uses `Fraction` and SymPy exact identities; artifacts contain rational strings; no floating-point inference is used | Proved for the pinned audit |
| Human inequalities, not bounded-grid evidence as proof | The manuscript gives the lower-envelope, row-pinning, minimax-dual, overlap, and asymptotic arguments symbolically for all parameters; finite grids are explicitly regression-only | Proved |
| No null padding or direct sums | Every player is active in the displayed three-generator family and the proof uses no product/direct-sum construction | Proved |
| Do not return to failed PXC138/PXC140 route | PXC151 uses a new lower-envelope incidence construction and sparse minimax dual; PXC138/PXC140 are not dependencies | Proved |
| Independent selector implementation | `verify_pxc151_quadratic_two_block_breakthrough_independent.py` imports no project or primary selector code and solves directly generated role-orbit cores with standalone Z3 QF_LRA; permutation averaging justifies the exact role reduction at every staged face | Proved as an independent implementation; still computational evidence, not the all-parameter proof |
| Negative controls | Moving one unit in `B_0` from `g` to `d` undercuts the load-bearing row; the independent implementation recomputes a different `Lmin` | Proved |
| Hostile-review packet | `PXC151_QUADRATIC_TWO_BLOCK_REVIEW_PACKET.md` contains the claim, dependency map, reproduction commands, limitations, and eight hostile questions | Complete |
| Prior-art audit | `PXC151_PRIOR_ART_AUDIT_20260830.md` screens primary adjacent sources and explicitly disclaims a novelty conclusion | Complete as author-side screen only |
| Seek external specialist correctness/prior-art assessment | `PXC151_SPECIALIST_OUTREACH.md` identifies complementary expertise, pins review to `8d5947f`, and supplies a structured request and verdict form | Prepared, but no outreach or external verdict is evidenced; incomplete |
| Do not call the outcome field-level before external assessment | Manuscript, ledger, review packet, prior-art audit, and outreach file all state that correctness, novelty, and significance remain externally unreviewed | Satisfied |

## Verification evidence

Primary files:

```text
paper5/divergence.tex                                      PXC151a--PXC151i
verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough.py
verifiers/divergence/pxc151_quadratic_two_block_breakthrough.json
verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough_independent.py
verifiers/divergence/pxc151_quadratic_two_block_breakthrough_independent.json
```

The primary verifier checks symbolic identities and 110 exact parameter
cells. The independent verifier recomputes both staged selectors on twelve
calibration cases, including diagonal and asymmetric block sizes, and runs a
fail-open negative control. The all-parameter claim rests on the manuscript's
conventional proof, not those finite cases.

The complete `paper5/verify_release.sh` replay passed at `8d5947f`, including:

- PXC147--PXC150 primary and independent controls;
- PXC151 primary artifact byte comparison;
- PXC151 independent artifact byte comparison;
- a clean one-file arXiv build;
- a second byte-identical PDF and source-archive build; and
- the terminal `PASS: paper5 reviewer/arXiv release suite` gate.

The resulting PDF has 183 pages and is 1,166,212 bytes. The mathematical
commit is published at:
<https://github.com/mfflanag1/counterexample-hunt/commit/8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564>.

## Remaining external gate

At least one specialist in egalitarian/Lorenz core selectors and exact or
exact-partition games must return a written verdict tied to the frozen SHA.
The verdict must independently separate:

1. correctness of (PXC151a)--(PXC151i), including the full later-stage
   `Lmax` pinning and the `r=2` handover;
2. novelty under exact-game, exact-partition, egalitarian, Lorenz,
   semi-balanced, majorization, and coherent-lower-probability terminology;
3. significance of an infinite construction improvement without a matching
   global upper bound.

An exact-cone specialist is the preferred second reader. Until the first
written external verdict is archived, the active goal must remain open and
the result must not be described as a field-level breakthrough.
