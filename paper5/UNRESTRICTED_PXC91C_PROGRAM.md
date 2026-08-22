# Unrestricted PXC91c minimum-dimension campaign

Status updated: 2026-08-21. The formal target is `(PXC97a)--(PXC97b)` in
`divergence.tex`. PXC98 refutes both certificate quantifiers at `n=6`, and
PXC100 proves the canonical pair cover faithful for every fixed certificate
at `n=5`. The unrestricted minimum failure dimension is therefore exactly
six.

## Exact target

For each `n in {4,5,6}`, quantify over every tuple `(v,x,z,Cx)` where:

- `v` is an exact singleton-normalized game;
- `x=Lmin(v) != z=Lmax(v)` and `Top(z)={r,h}`;
- `Cx` is fixed data consisting of original `x`-tight nonempty proper-
  coalition rows whose retained polytope, with efficiency and nonnegativity,
  has Lmin `x`. Collections defining the same retained polytope are identified;
  repetitions and efficiency/nonnegativity duplicates are immaterial.

The strong statement is universal over every qualifying fixed `Cx`. The
weaker statement is `for all (v,x,z), there exists Cx and R`. A qualifying
`R` is a normalized extreme cover of original `z`-tight proper-coalition rows
with positive support weights, positive coefficients on both top players,
ambient load `eta>=0`, and `|R|<=n-2`. Its `Cx union R` lift must have both
selectors exactly `x,z`.

No orderedness, saturation, single-heavy shape, `s=2`, outsider lower bound,
reserve/direct condition, named cover family, or later-stratum tie pattern is
admissible as a hidden premise.

## Evidence tiers and calibrations

- PXC88: exact `n=7` failure; unique positive extreme cover; `0126,0136`
  indispensable; every proper subset of its only `x`-tight row pool changes
  Lmin.
- PXC90: exact positive faithful calibration.
- PXC94--PXC96: positive control only for the stated restricted `n=6` cell.
- PXC92b: exact staged tangent/Farkas fidelity criterion for every Lmax
  stratum; first-ceiling duality alone is insufficient.

Every promoted witness must be a full exact game with independently replayed
coalition minima, selectors, complete-certificate status, extreme-cover
census, and every later-stage fidelity test. Allocation profiles and
necessary relaxations are controls, not counterexamples.

## Resolved dimension cells

1. `n=5`, including `eta=0` and zero-coordinate singleton boundaries, is
   closed by the 3,840-cell, two-encoding exact-cone theorem PXC100.

PXC98 closes the former general `n=6` pair-tight and rank-deficient
positive-ambient cells negatively with one exact game. It has arbitrary
later strata and lies outside the restricted single-heavy program.

The existing coincidence theorem makes `n<=4` vacuous for divergent
instances; it remains a mandatory calibration of the implementation.

The exact five-player bank contains 165 distinct exact games, 36
with a two-player Lmax top stratum. Across those 36 games the exhaustive
audit tests every x-tight row subset, 37 complete certificates, and all 146
qualifying extreme covers; no strong fixed-Cx or existential-Cx failure
occurs. This bank is a positive calibration rather than the proof; PXC100
classifies the full five-player exact cone. One exceptional game has an x-tight row that is slack
at z, but its two common-tight rows already form a complete subcertificate;
therefore a proof cannot assume every Cx row is common.

## Current structural reductions

- `n<=4`: no divergent instances, by the proved Lmin--Lmax coincidence.
- Any positive-ambient cover whose non-top incidence matrix has full row rank
  is faithful at every later stage (`PXC97c`).
- Ambient load zero is equivalent to the tight top-pair cover: positive row
  weights force every support row to omit every non-top player, and positive
  top singletons cannot be tight in a singleton-normalized game.
- At `n=5`, the one-coalition ceiling theorem and anchor localization force
  the two-player top coalition itself to be tight. The remaining problem is
  therefore a three-coordinate staged-polar question for the fixed
  common-tight part of `Cx`; the first ceiling is not the missing step.
- At `n=6`, PXC98 has the unique complete `Cx={rha,rhb}` and exactly two
  qualifying extreme covers: the eta-zero top pair and the rank-three
  positive-ambient support `{rha,rhb,rhjk}`. Both omit the forced-zero later
  blocker `rj` and change Lmax from `(4,4,3,3,2,1)` to
  `(4,4,3,3,3/2,3/2)`. Thus both strong and existential-Cx formulations fail.

The former four-outsider cover-compatible staged-basis conjecture is false by
PXC98. Its exact obstruction is the later exchange
`(0,0,0,0,-1/2,1/2)`: the row `rj` blocks it in the original game but is
forced to coefficient zero in every top cover. The remaining sharp assertion
was the three-outsider, five-player pair-tight version, now resolved by PXC100.

For a fixed candidate cover, put `U=N\{r,h}`,
`C0={C in Cx:x(C)=z(C)}`, and `Z0={i:z_i=0}`. After the first top stratum is
pinned, positive cover weights turn its active inequalities into equalities,
so the exact later-stage tangent system is

```text
1_U·d_U=0,
A_R^T d_U=0,
d(C)>=0       (C in C0),
d_i>=0        (i in Z0),
d|E_(t-1)=0,
d_j<=0        (j in B_t), with one designated strict decrease.
```

Fidelity is equivalent to infeasibility of this system for every later
stratum/player. Its projected Farkas polar may use the free cover-column
span, efficiency and earlier-coordinate normals, nonnegative `C0` and `Z0`
normals, and the current-block sign normals. This is the exact proof/search
interface; first-ceiling rank or a second-stratum check alone is insufficient.

For `|U|=3`, put
`K=cone({1_(C cap U):C in C0} union {e_u:u in Z0})`. The full criterion
collapses to four residual-stratum shapes:

- all three tied: automatic;
- unique high `a`: `e_a in span{1}+K`;
- tied high pair `{a,b}`: some strict convex combination
  `theta e_a+(1-theta)e_b`, `0<theta<1`, lies in `span{1}+K`;
- strict `a>b>c`: `e_a in span{1}+K` and
  `e_b in span{1,e_a}+K`.

These are necessary and sufficient PXC92b polars, including zero-coordinate
normals. PXC100 proves that the 280-facet five-player exact cone plus
completeness of every fixed Cx forces the applicable membership. It
sorts x increasingly without loss, then enumerates all 16 x compositions,
10 top pairs, six outsider orders, and four outsider tie compositions:
`16*10*6*4=3,840` exact QF-LRA cells. All are UNSAT with no unknown/error in
both the raw PXC92b Farkas encoding and an independently normalized
nonnegative-incidence encoding.

## Promotion gates passed

The exhaustive exact-cone partition and its independent algebraic replay are
complete. The result retains both drivers, all 3,840 cell verdicts and keys,
exact-cone catalogue hashes, reproduction commands, and exact fail-open
controls. PXC98 retains primary and independent selector/cover
implementations. The remaining research opportunity is a short human proof
of the three-outsider common-polar implication, not a missing correctness
condition for the computer-assisted threshold theorem.
