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

## 7. Immediate frontier

The immediate theorem target is now the faithful branch, not another blocker
census:

> **Faithful polar-to-threshold lemma (open).**  On every exact
> singleton-normalized selector pair with `D_H>0`, if a qualifying extreme
> cover is faithful for a fixed complete `Cx`, then a proper, predeclared
> subset of the joint staged-polar transports carried by `Cx union R` has
> threshold value at least `D_H`.

If this fails, the counterexample will determine which additional exactness
witness or facet row is indispensable.  Once branch F is settled, the same
currency interface can be used for the common and reciprocal branches rather
than attempting incompatible blocker-specific scalar formulas.
