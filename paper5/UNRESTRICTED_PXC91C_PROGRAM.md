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

## 2026-08-22 structural continuation: PXC101--PXC103

PXC98 is now embedded in a positive-dimensional rational family for every
`n>=6`; see `paper5/FORCED_ZERO_BLOCKER_PROGRAM.md`. The construction grows a
genuine outsider block rather than adjoining null players. Its proper x-tight
pool remains the unique complete pair `{rha,rhb}`, its z-tight menu remains the
five incidence types `{rh,rha,rhb,rj,rhO}`, and outsider balance forces `rj`
to coefficient zero in every top cover. Both extreme covers equalize the
outsider block and therefore fail Lmax.

PXC103 gives the exact iff criterion for a direction shared by every failing
cover: after respecting common Cx and zero-coordinate normals, the direction
must vanish on the union of all cover-eligible rows. Full-game Lmax then
supplies a blocker outside that union.

## 2026-08-22 second mechanism: PXC104

The universal extension is false. PXC104 gives a total-23 exact
singleton-normalized game with selectors
`x=((41/6)^2,(7/3)^4)` and `z=(6,6,5,4,1,1)`, unique complete
`Cx={rha,rhb}`, and three extreme covers `{rh}`, `{rhb,rhj,rhak}`, and
`{rhb,rhaj,rhk}`. Every lift fails. The first positive cover leaves the
`a -> k` descent, blocked by `rhaj` in the second cover; the second leaves the
`a -> j` descent, blocked by `rhak` in the first. Their support union has full
outsider rank, so there is no common forbidden direction and no load-bearing
row forced zero in every cover. The revised classification problem is a
dichotomy problem: common forced-zero blockers versus directed cycles of
cross-cover blockers.

## 2026-08-22 parametric cross-cover family: PXC105

PXC104 is the `A=5` member of a rational open chamber `4<A<11/2`.  At total
`18+A`, retain bounds `rha,rhb>=16`, `rhj,rhk>=13`, and
`rhaj,rhak>=13+A`.  The selectors are
`x=(((46-A)/6)^2,((A+2)/3)^4)` and `z=(6,6,A,4,1,1)`.  The unique complete
Cx, six-row z-tight menu, and three-cover triangle stay constant.  Every
cover still fails, with the same two-cycle and zero common kernel.  Exact
endpoint interpolation certificates plus five interior rational audits are
replayed by two separately formulated verifiers.  This proves positive
dimension for the second mechanism; PXC106 below supplies its all-`n` lift.

## 2026-08-22 all-dimension cross-cover lift: PXC106

The low outsiders may be replaced by nonempty blocks `J,K`.  The two
positive covers partition all non-top players as `{b}|J|({a} union K)` and
`{b}|({a} union J)|K`.  The full game pins both block sums, whereas deleting
one cross row moves the lost `a` mass uniformly into the opposite block.
The specialization `p=1,q=n-5,A=4+1/(n-3)` satisfies the strict chamber for
every `n>=6`; every added player has payoff one and lies in a load-bearing
row.  Thus both the forced-zero mechanism and the cross-cover mechanism now
have positive-dimensional and genuine all-dimension realizations.

## 2026-08-22 exact obstruction dichotomy: PXC107

For every qualifying extreme cover, form its full staged descent cone. All
cover lifts fail exactly when every such cone is nonempty. PXC107 then gives
an exhaustive dichotomy: a shared direction (PXC103), or a directed
cross-cover blocker cycle. A direction nonnegative on the entire cover union
would vanish on every positive cover by its dual identity and would therefore
be shared; the apparent third branch is impossible. PXC98 and PXC104 realize
the two cases.
