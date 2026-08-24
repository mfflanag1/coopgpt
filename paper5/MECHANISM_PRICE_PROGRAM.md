# Mechanism-to-price program

Date: 2026-08-23

Starting checkpoint: `bd97ded7d0ebc1410305b9be8c01d01750524101`

Status: active proof/counterexample program; no novelty claim.

## 1. Frozen target and inputs

For the Lmin/Lmax selections `x,z` of an exact singleton-normalized game,
the target is

```text
O(x,z) = sum_i min(x_i,z_i) >= c_n T,
c_n = n/floor(n^2/4),  T=v(N).                         (MP0)
```

The following are frozen inputs.

1. PXC112: complete Lmin certificates are quotiented by equality of their
   staged tangent cones at `x,z`.
2. PXC114: if every qualifying extreme-cover lift fails, then either all
   covers share a later Lmax descent, in which case a z-tight blocker lies
   outside the cover union, or two covers cross-block one another.
3. The exact currency identity

   ```text
   O = B_* + C_top + C_label,
   C_top=B_H-B_*,  C_label=O-B_H.                      (MP1)
   ```

The missing quantitative assertion is

```text
C_top + C_label >= D_* := max(0,c_n T-B_*).            (MP2)
```

Neither `C_label` itself nor the complete canonical-rectangle identity may
be cited as an unexplained payment for `(MP2)`.

## 2. First correction: PXC114 is not an all-game dichotomy

For a fixed complete `Cx`, there are three mutually exclusive structural
branches:

```text
F: at least one qualifying extreme cover is selector-faithful;
C: every cover fails and their staged descent sets have nonempty intersection;
R: every cover fails, the intersection is empty, and a reciprocal pair exists.
                                                               (MP3)
```

The second and third alternatives are PXC114.  The first is their omitted
complement.  Thus a global mechanism-to-price theorem must price **all three**
branches.  PXC90 is not merely a benign regression control; it represents a
logically necessary branch.

This is load-bearing, not cosmetic.  The exact audit

```bash
python3 verifiers/divergence/search_archive/audit_pxc119_spectral_deficit_mechanisms.py \
  --case optimized_label_free_spectral_failure \
  --case actual_top_fixed_failure \
  --output verifiers/divergence/search_archive/pxc119_spectral_deficit_mechanisms.json
```

reconstructs both lower-envelope games, exhausts the full proper z-tight
menu and every normalized extreme top cover, and recomputes the invariant
staged descent graph.

* The optimized-label-free control has spectral deficit `5/216`.  Its unique
  extreme cover has full outsider rank and is faithful.  Its top-selection
  currency already removes the post-top deficit.
* The actual-top-fixed control has **positive post-top deficit `1/24`** and
  label currency `5/12`.  It has twelve qualifying extreme covers and every
  one is faithful.  There is no common outside-union blocker and no reciprocal
  pair to charge.

Consequently the proposed blocker-only implication

```text
positive post-top deficit => common blocker or reciprocal pair             (X)
```

is false.  More strongly, any formula assigning all non-top payment only to
PXC114 blockers returns zero on the second control while the demanded payment
is positive.  The correct program is a faithful/common/reciprocal trichotomy.
This bounded audit falsifies `(X)`; it is not evidence for `(MP0)`.

## 3. Exact singleton-witness inequality for the common branch

The first reusable conventional inequality is as follows.  Let a normalized
z-tight top cover be

```text
sum_(S in R) lambda_S 1_S = eta 1_N + sum_(h in H) alpha_h e_h,
lambda_S>0, alpha_h>0, sum_h alpha_h=1, z_h=M.          (MP4)
```

For `r in H`, let `w^r` be an exactness witness with `w^r_r=0`.  Evaluating
the tight cover rows at `w^r` and at `z` gives

```text
sum_(h in H\{r}) alpha_h w^r_h >= M.                  (MP5)
```

Put `theta_r=max_(h != r) alpha_h`.  Then

```text
sum_(h in H\{r}) w^r_h >= M/theta_r.                 (MP6)
```

If a z-tight blocker `Q` contains `r` and no other top player, exactness also
gives `w^r(Q\{r})>=z(Q)`.  The two coordinate sets are disjoint, hence

```text
M/theta_r + z(Q) <= T.                                (MP7)
```

This is scale invariant: it prices the actual blocker row and cover weights,
not the arbitrarily scaled tangent value `-d(Q)`.  The general overlap case
is a small packing statement.  If nonnegative coefficients `mu_Q,nu_C`
on z-tight blocker rows and x-tight retained rows obey, for every `i != r`,

```text
alpha_i/theta_r
 + sum_(Q contains i) mu_Q
 + sum_(C contains i) nu_C <= 1,                      (MP8)
```

where `alpha_i=0` off `H`, then

```text
M/theta_r + sum_Q mu_Q z(Q) + sum_C nu_C x(C) <= T.  (MP9)
```

Proof: multiply the cover evaluation `(MP5)` by `1/theta_r`, add the retained
core inequalities at `w^r`, and use `(MP8)` plus `w^r>=0` and `w^r(N)=T`.
This is a genuine exactness/cover/blocker inequality.  It is **not yet** an
overlap theorem: the missing step is to convert a demand-sensitive part of
`(MP9)` into threshold currency without charging baseline mass twice.

For PXC101, `alpha_r=alpha_h=1/2` and `Q=rj`, so `(MP7)` specializes to

```text
2M+(M+J) <= T.
```

The stronger chamber inequality comes from packing the two common `Cx` rows
as well.  This verifies that the witness constraint sees the forced-zero
blocker, while correctly allowing its overlap charge to be zero whenever
`B_H` already clears the target.

## 4. Correct quantitative subgoals

Define the post-top demand

```text
D_H=max(0,c_n T-B_H).                                  (MP10)
```

The three branch lemmas now required are:

### F. Faithful staged-polar pricing

If `Cx union R` preserves both selectors, extract basic staged Farkas supports
for both selections and prove that an explicit restricted family of their
labelled transports has value at least `D_H`.  The restriction must be stated
before optimization and must not be the complete rectangle family, whose
optimum is identically `C_label`.  PXC90 is the full-rank calibration; the
actual-top-fixed control is the mandatory positive-demand calibration.

### C. Common-blocker incremental pricing

Normalize the common descent at its first improved Lmax stratum.  Use an
outside-union blocker from a basic full-game staged Farkas certificate, the
singleton-witness packing `(MP5)--(MP9)`, and common `Cx` rows to construct an
incremental threshold charge `P_C` satisfying

```text
P_C <= C_label,   P_C >= D_H.                          (MP11)
```

The first inequality prevents invented currency; the second pays the target.
PXC101 and PXC116 are incidence calibrations but have zero demand after the
spectral/actual-top term, so a sound theorem may assign `P_C=0` there.

### R. Reciprocal aggregate pricing

For reciprocal covers `R,R'`, choose basic cross-blocking staged polars and
combine the two cross rows (or their partition-star semi-balanced facets) into
a scale-invariant aggregate `P_R`.  Required gates are

```text
P_R <= C_label,   P_R >= D_H,                          (MP12)
```

with no separate charge of the same threshold layer by both directions.
PXC104 and PXC118 are structural calibrations; sharp equality families must
return zero slack.

## 5. No-go ledger

The following routes are closed and must not be restarted without a new
hypothesis.

1. The stronger effective-bipartition/CEB scalar bridge is false by the exact
   seven-player counterexample; its main-overlap margin remains positive.
2. The complete high-low rectangle packing equals `C_label` identically, so
   asking it to cover `D_H` is `(MP0)` in disguise.
3. Staged-certificate coefficient magnitudes have unbounded amplification;
   only support/incidence information survives.
4. A universal common blocker is false: reciprocal PXC104/PXC118 have empty
   common descent intersection.
5. Common/reciprocal blockers are not present in every positive-deficit game:
   the faithful controls above refute that implication.
6. A bounded game census, additional six-player primitives, or an incidence
   catalogue is not a dimension-free proof.

## 6. Two-sided promotion gates

A proposed branch price is promoted only after:

1. a conventional derivation of both inequalities in `(MP11)` or `(MP12)`;
2. exact tests on PXC90, PXC101, PXC104, PXC116, PXC118, both sharp equality
   orientations, the three named spectral deficits, and the CEB falsifier;
3. a fail-open control obtained by dropping the exactness/blocker hypothesis;
4. an independently formulated exact replay;
5. an adversarial search that optimizes `price-D_H` in both directions.

If a branch lemma is false, the deliverable is its smallest exact rational
counterexample with independently recomputed selectors, complete `Cx`
exhaustion, full extreme-cover census, and the exact missing threshold layer.

## 7. First promoted quantitative cell: PXC119

The actual-top-fixed faithful control generalizes to a dimension-free
two-top ladder theorem.  For the notation and complete proof see PXC119 in
the manuscript.  Its exact price identity is

```text
D=n+1+2(s-1)/g,
O-(1-s/D)T=(s/D)[2(m-ell)+(g+2)(B-A)+nq]>=0,
1-s/D >= n/floor(n^2/4)  (n>=6).                     (MP13)
```

The two affine equalities used to eliminate the selector levels are exactly
the common tight rows `{u,v,c}` and `{c,q0}`.  The payment on the right is
made entirely of explicit stratum gaps and the bottom level.  Thus `(MP13)`
is non-tautological and dimension-free.  It proves the target on the whole
labelled profile cell, not on the whole faithful branch.

The affine fail-open point obtained by deleting `m>=ell` has overlap `4/7`,
below the seven-player target.  This pins the load-bearing order price and
prevents the common-row equalities alone from being overpromoted.

## 8. PXC120 is false; PXC121 closes the old controls spectrally

The exact controls initially suggested a sharper disjunction than separate
positive prices for all three branches:

```text
D_H>0  ==>  for the fixed complete Cx, some qualifying
            extreme top cover is faithful.                   (MP14?)
```

PXC122 falsifies this implication: its six-player anchor has `D_H=2/3`, a
unique complete `Cx`, five qualifying extreme top covers, and every cover
fails in the same common direction.  The forced-zero row `rhaK` is the sole
negative staged blocker and has coefficient zero throughout the normalized
cover polytope.

The earlier zero-demand evidence does promote parametrically in two important
controls.  PXC121 proves by symbolic elimination that the entire PXC101
common chamber and the entire PXC106 reciprocal chamber satisfy the target
already at the actual-top spectral bound.  Thus their blocker prices are
genuinely zero, not merely unobserved in sample points.

## 9. PXC122--PXC123: the first positive common price in every dimension

For every `t>=1`, PXC122 defines an exact singleton-normalized lower-envelope
family on `n=t+5` players with unique complete certificate

```text
Cx={rhj,rhbK}.
```

The full typed z-tight menu has eight row types and exactly five normalized
extreme top covers.  Every cover fails along the same one-dimensional
exchange between `b` and the symmetric block `K`; the transverse row `rhaK`
has forced coefficient zero in every cover.  The family contains both the
old zero-demand PXC116 point and the positive-demand PXC122 anchor.

PXC123 gives the price explicitly.  With `beta=min(B,C)`,

```text
t=1:   P_C=(B-A)+(beta-2A),
t>=2:  P_C=(B-A)+(B-2A)=2B-3A.
```

These are the first two rank-paired stratum rectangles.  Their endpoints are
fixed by `rhj`, `rhbK`, active nonnegativity, and the omitted blocker; no
unexplained overlap term is used as currency.  For `t=1`, direct algebra
proves `P_C>=D_H` whenever demand is positive.  For `t=2` and `t>=3`, the
actual-top spectral bound itself is already above the hybrid target.  This is
a conventional all-dimensional theorem for one open rational common family,
not the universal common branch.

## 10. Reciprocal affine no-go and the live theorem

The most direct reciprocal deformation of PXC104 does not open a positive
demand chamber.  In the one-parameter asymmetric selector profile audited as
PXC124a, write

```text
x=(p,p,u+s,u,u,u),       z=(M,M,A,B,J,K),
M>A>B>max(J,K)>=0,       0<=s<A-B,
u=(A+J+K-s)/3,          2p+4u+s=T=2M+A+B+J+K,
```

and put `j=min(J,K)`, `k=max(J,K)`.  The three possible locations of `u`
give the exact expressions

```text
u>=k and u<=B:  2T/3-B_H=(2B-2M-3j-3k+2s)/3,
u<k:            2T/3-B_H=(-A+2B-2M-4j-k+3s)/3,
u>B:            2T/3-B_H=(A-B-2M-2j-2k+s)/3.
```

Substituting `s<A-B` makes the respective numerators smaller than
`2A-2M-3j-3k`, `2A-B-2M-4j-k`, and
`2A-2B-2M-2j-2k`, all strictly negative.  Thus `B_H>2T/3` throughout this
lane.  The exact grid of 5,004 profiles is a regression check, not the proof
and not an exhaustive reciprocal-incidence theorem.

The next common-branch target is therefore not another parametric family:

> **Forced-zero blocker price theorem (open).**  Given a PXC114 common
> direction with positive demand, derive from the outside-union blocker, its
> singleton-attainment witnesses, the fixed complete Lmin certificate, and
> the staged Farkas identity a predeclared collection of rank-paired
> rectangles whose total is at least `D_H`.

The theorem must specialize to PXC116 and PXC122/PXC123, and must either
explain why the two-rung payment is universal or produce a smaller exact
counterexample with a new payment mechanism.  Only after this common theorem
is proved or sharply falsified should the search return to positive-demand
reciprocal mechanisms; the naive PXC104 deformation is now a proved dead
lane.

## 11. Faithful complement

The immediate theorem target is now the faithful branch, not another blocker
census:

> **Faithful polar-to-threshold lemma (open).**  On every exact
> singleton-normalized selector pair with `D_H>0`, if a qualifying extreme
> cover is faithful for a fixed complete `Cx`, then a proper, predeclared
> subset of the joint staged-polar transports carried by `Cx union R` has
> threshold value at least `D_H`.

PXC120 is false, so this faithful lemma is one branch of a genuine
three-branch program rather than a consequence of a fidelity disjunction.
The common branch now has its first positive all-dimensional calibration;
the reciprocal positive-demand branch remains open.
