# Mechanism-to-price program

Date: 2026-08-23

Starting checkpoint: `bd97ded7d0ebc1410305b9be8c01d01750524101`

Status: literal target falsified at n=5 (PXC141); corrected n>=6 target
falsified at the dimension-minimal n=7 checkpoint (PXC143); the sharp n=7
constant and structural classification remain open.

## 1. Frozen target and inputs

For the Lmin/Lmax selections `x,z` of an exact singleton-normalized game,
the target is

```text
O(x,z) = sum_i min(x_i,z_i) >= c_n T,
c_n = n/floor(n^2/4),  T=v(N).                         (MP0)
```

As literally written, `(MP0)` is false.  The already-proved five-player
extremal game has `T=4`, `O=3`, while `c_5*T=10/3`.  The proved n<=4
coincidence theorem makes n=5 the smallest failure.  PXC141 independently
replays all selector and certificate arithmetic and records that its Lmax
top stratum has size four, outside PXC112/PXC114.  The rest of this program
was therefore retained as the corrected **n>=6** target; PXC143 below now
falsifies that corrected target at seven players.

The following are frozen inputs for the corrected program.

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

## 10. PXC125: demand localizes to the two-rung chamber

The inequalities `3A<B` and `2A<B` used to display PXC122 are not actually
restrictions on its positive-demand problem.  On the full natural chamber

```text
0<A<B,
B+A/(t+1)<K0<B+2A/t,
M>max(K0,2A),
C=A+(t+1)B-tK0,
```

the same lower-envelope game, complete certificate, eight-row tight menu,
five extreme covers, forced-zero blocker, and common wrong Lmax persist.
PXC125 counts the residual opposite-pair layers without assuming an order
between `2A`, `B`, and `C`.  The declared subpacking is

```text
t=1:   P_C=(B-A)+(min(B,C)-2A)_+,
t>=2:  P_C=(B-A)+(B-2A)_+.
```

These are at most two disjoint, predeclared rectangles.  They are selected by
the two certificate rows, the active zero normal, and the blocker-separated
`K` block; they are not the complete canonical packing.

The sharp localization is:

```text
t>=2                         => D_H=0,
t=1 and A>=B/3              => D_H=0,
D_H>0                       => t=1 and B>3A.
```

In the last line `C>B-A>2A`, so the positive-part formula reduces exactly to
the PXC123 two-rung price and pays `D_H`.  Thus PXC123 was already the whole
positive-demand region of this maximal incidence chamber.  The independent
audit integrates the threshold counts directly through `t=64`; removing the
blocker/core-comparison upper endpoint gives a positive-demand seven-player
fail-open point.

This is a structural handover, not merely a larger parameter grid: the
blocker comparison forces every dimension above six onto the spectral side,
and the only residual price case has exactly two rungs.

## 11. Reciprocal affine no-go and the live theorem

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

PXC125--PXC126 sharpen that target to a concrete structural statement.  This
is **not** a player minor: PXC115 proves that restriction, contraction,
amalgamation, and even null extension do not preserve the quantified sparse
failure object.  Instead, take a retained common row `C` and an outside-union
blocker `Q`.  Their traces partition the non-top players into the four cells
`V11,V01,V10,V00`.  Choosing one player from each cell gives the
Boolean-square price

```text
P_square=(a_11-b_01)_+ + (a_10-b_00)_+,
a_i=min(x_i,z_i), b_i=max(x_i,z_i).
```

The two pairs are vertex-disjoint, so threshold counting proves
`P_square <= O-B_H` for every allocation pair.  In the only positive-demand
PXC125 case, `t=1`, use `C=rhbK`, `Q=rhaK`, and the four players
`(K,a,b,j)`; the price is exactly `(B-A)+(min(B,C)-2A)_+`.  For `t>=2`
this is merely a smaller valid subpacking than PXC125's two-distinct-`K`
price, but those dimensions already have `D_H=0`.

For fixed `C,Q`, optimization over the four representatives separates:

```text
max P_square
 = (max_V11 a - min_V01 b)_+ + (max_V10 a - min_V00 b)_+.
```

An empty cell means that row pair supplies no square.  Hence, after fixing
payoff orders and a certificate/blocker menu, square failure is an explicit
finite piecewise-linear system rather than a hidden combinatorial search.

> **Boolean-square price extraction (open).**  Every positive-demand PXC114
> common obstruction either has a retained common row, a basic staged
> outside-union blocker, and four incidence-cell representatives with
> `P_square >= D_H`, or its mixed singleton-witness projection supplies a
> target-reaching price.

The first exact falsification gate is the stronger square-only implication:
enumerate every complete-certificate tangent class, every common direction,
every outside-union blocker that occurs in a basic staged certificate, and
every four-cell choice, and require `max P_square < D_H`.  A SAT witness must
be reconstructed as an exact game and then tested against the mixed rooted
packet projection; it is not automatically a counterexample to overlap.
This is now the shortest route to a full common-branch theorem.  Do not call
the Boolean square an oriented-matroid or player minor, and do not replace
the blocker-generated family by all canonical rectangles, which would
collapse back to the label-currency identity.

### PXC127 correction: square failure and the common-row cut

The square-only implication is false.  The exact total-25 lower envelope

```text
rh>=12, rhj>=69/5, rhak>=89/5, rhbk>=23, rhajk>=99/5
```

has

```text
x=(32/5,32/5,1,51/10,1,51/10),
z=(6,6,1/5,26/5,9/5,29/5).
```

Its unique complete proper-row certificate is `{rhj,rhbk}`, its sole extreme
top cover is `{rh}`, and the reduced Lmax is
`(6,6,1/5,11/2,9/5,11/2)`.  The common direction moves `b` up and `k` down;
the two omitted negative blockers are `rhk,rhajk`.  Every certificate/blocker
pair has an empty Boolean cell, so the maximum square price is zero although
`D_H=2/3`.

The same witness exposes the stronger price.  For a common row `C`, split the
residual players into `I=C cap R` and `J=R minus C`.  Give every cross edge
`ij` weight `max((a_i-b_j)_+,(a_j-b_i)_+)` and take a maximum-weight matching.
This permits edgewise mixed orientations; every active edge still consumes a
different high-high and low-low endpoint.  Hence
`P_cut(C)<=O-B_H` by the same threshold count.  In PXC127, `C=rhbk` separates
`{b,k}` from `{a,j}` and

```text
P_cut=(51/10-1)+(51/10-9/5)=37/5=O-B_H>D_H.
```

The next falsifiable common-branch target is therefore:

> **Common-row cut-or-witness theorem (open).** Every positive-demand PXC114
> common obstruction either has a retained common certificate row `C` with
> `P_cut(C)>=D_H`, or an explicitly selected mixed singleton-attainment
> packet satisfying (MCP)--(MWP) pays the residual demand.

The pure cut implication must be attacked first.  A counterexample must have
`max_C P_cut(C)<D_H`, not merely an empty Boolean cell.  If it exists, retain
the smallest exact witness and derive the mixed packet from the actual
outside-union blocker and its staged Farkas support.  Do not use the full
unrestricted rectangle matching, since that is just the label-currency
identity in disguise.

### PXC128 fractional cut-cover reduction

Let `E` be the positive canonical rank carriers from (CS), with lengths
`ell_e`, and let `delta_Ce` record whether common row `C` separates the two
endpoints of carrier `e`.  The fractional set-cover number

```text
chi = min sum_C theta_C
      s.t. theta>=0 and sum_C theta_C delta_Ce >= 1 for every e
```

gives the dimension-free lower bound

```text
max_C P_cut(C) >= (O-B_H)/chi.
```

This follows because the canonical edges crossing any fixed row are already
a feasible matching for that row.  If the pure cut implication fails, then
either one positive carrier is unseparated by every common row, or the exact
dual produces rational weights `y_e` with

```text
sum_e y_e > (O-B_H)/D_H,
sum_{e cut by C} y_e <= 1  for every common row C.
```

This is the next packet input: a carrier measure which is sparse across every
common-certificate cut.  The live lemma is to combine that measure with the
actual outside-union blocker and its basic staged Farkas support to construct
one rooted tagged packet satisfying (MCP)--(MWP).  PXC128 does not yet prove
that extension.  PXC122 and PXC127 both have `chi=1`; a separate triangle
control has `chi=3/2`, so the reduction is not secretly integral.

### PXC129 carrier-to-cover price dichotomy

PXC129 supplies the local bridge for the unseparated-carrier outcome of
PXC128.  For a positive carrier `i -> j`, put `d=e_j-e_i`.  If no row tight
at both selectors separates its endpoints, staged optimality separately
forces an `x`-tight and a `z`-tight oriented blocker, and every open point of
the segment from `x` to `z` admits a small Pigou--Dalton transfer in direction
`d`.

For any normalized `z`-tight top cover, equal non-top loads imply that the
total cover weight on rows containing `i` but not `j` equals the total weight
in the reverse orientation.  Hence either both are positive, in which case
the separated rows pay strictly positive comparison slack inside the exact
top-selection identity, or both vanish, in which case `d` is tangent to the
lift and full-game Lmax optimality forces an omitted oriented outside
blocker.  Thus the PXC128 residue always yields one of the two permitted
currencies.

This is not the final price theorem.  The live arrow is now quantitative and
aggregate: couple the PXC128 dual carrier measure to the coverwise selection
charges and the staged Farkas/singleton-witness values of the forced blockers,
without reusing a cover's total top currency, and prove the combined payment
is at least `D_H`.  PXC104 and PXC118 have zero positive canonical carrier
length; they calibrate the incidence boundary but their reciprocal
cross-cover price remains a separate obligation.

### PXC130 exceptional-set slack transport

The exact-facet experiments reduce to a conventional dimension-free packet
identity.  If an exactness witness attains `v(E)` and

```text
sum_S lambda_S 1_S = rho 1 + beta 1_E,
```

then every core allocation `y` satisfies

```text
sum_S lambda_S [y(S)-v(S)] >= beta [y(E)-v(E)].
```

This is obtained by evaluating the incidence identity first at the witness
and then at `y`; indecomposability is unnecessary.  For a singleton
exceptional set it prices the positive coordinate `beta*y_r` using explicit
coalition slacks.  Catalogue type 41 is the first carrier-search control: one
such packet alone excludes a relaxed no-common-separator selector point by
`609/178`.

For a partition-star cover on exceptional top pair `T`, the transport becomes

```text
sum_s slack_y(T union B_s) >= (m-1) slack_y(T).
```

After normalized equal-top scaling, every such cover has exactly
`Phi_R=(x(T)-z(T))/2`.  Hence the two PXC104 cross covers and PXC118's added
two-block cover all expose the same `5/6` pair-shear budget.  Their facet
inequalities cannot be summed as independent reciprocal payment without a
new disjoint label-layer or witness argument.  This is a useful no-go: the
cross-cover facets explain the dependency cycle but do not themselves create
post-top currency.

The six-player PXC101--PXC102 anchor gives the separate value `1/2`; the
full PXC101 chamber retains the formula rather than that fixed number.

### PXC131 nontrivial completion criterion and route no-go

For a nonsingleton row `E`, delete only its inequality from the full core
description. LP duality says that an active exceptional-set packet supported
away from `E` exists exactly when the deleted inequality remains implied:

```text
min_(y in K_-E) y(E)=v(E)
iff
sum_(S!=E) lambda_S 1_S = rho 1 + 1_E,
sum_(S!=E) lambda_S v(S) = rho T+v(E).
```

The tautological coefficient `lambda_E=1` is excluded. The canonical
blockers are strict negative controls:

- PXC101 `rj>=6`: deleted-row minimum `3`, gap `3`;
- PXC104 `rhaj>=18`: deleted-row minimum `16`, gap `2`;
- PXC104 `rhak>=18`: deleted-row minimum `16`, gap `2`.

These minima satisfy every other proper core row and have independent dual
lower-bound packets. Thus exactness does **not** automatically complete an
outside or cross blocker into a useful packet. A successful price must keep
the blocker as a tagged row in a mixed witness packet, change the exceptional
coalition, or extract genuinely disjoint staged-label currency. This closes
the naive direct-facet route without weakening the global objective.

The live PXC130--PXC131 continuation is an **existence and congestion theorem**:
derive, from the PXC128 carrier measure and actual staged blockers, a family
of exceptional-set packets whose transported slacks can be assigned to
disjoint threshold layers.  The packet identity is now solved; universal
packet selection and aggregate payment remain open.

### PXC132 forced-zero active-packet escape

The mixed-packet route has a sharp support restriction. Let Q be the only
proper z-tight row on which a staged direction d has nonzero derivative,
with d(Q)<0 and d(N)=0. A reduced active exceptional packet containing Q
cannot have all of its positive rows z-tight. If it did, activity at z
would make the exceptional row z-tight as well; dotting the incidence
identity with d would then read lambda_Q d(Q)=0.

This applies in every dimension to both forced-zero common families:

- PXC101 uses d_j=-(k-1) and d_o=1 on the other outsiders;
- PXC125 uses d_b=t and d_k=-1 on the K block.

Thus the common-direction proof cannot remain inside the active z-tight
facet menu. It must import a non-z-tight row and price that row's actual
core slack, or use staged threshold-label currency directly. PXC104 is the
correct reciprocal fail-open control: its larger z-tight menu supplies the
missing derivative, and each type-33 cross-cover facet is entirely
z-tight.

The six-player catalogue audit is only a calibration: PXC101 has 35 active
blocker-containing catalogue facets and PXC125 has three, but zero in either
common game have all positive rows z-tight. Each PXC104 blocker has one
all-z-tight active cross-cover facet. The conventional dot-product theorem,
not those counts, establishes the all-dimensional support escape.

The live selection problem is now narrower: choose the imported non-tight
rows so their slack decomposes across disjoint canonical threshold layers.
An active-facet theorem confined to the z-tight menu cannot solve the
common branch.

### PXC133 two-allocation packet conservation

Every exceptional packet has a constant exactness gap:

    sum lambda_S sigma_y(S) = beta sigma_y(E) + g,
    g = rho T + beta v(E) - sum lambda_S v(S) >= 0.

Therefore comparison between the two selectors cancels the gap exactly:

    sum lambda_S [x(S)-z(S)] = beta [x(E)-z(E)].

Raw core slack is not automatically overlap currency. PXC101's active
rooted mixed packet has slack 9 at x but 8 already at z, leaving comparison
currency 1. More decisively, the positive-demand PXC125 mixed packet has
raw slack 22/5 at x but slack 4 at z; its net comparison shear is only
2/5, below D_H=2/3. PXC104 is the clean fail-open control: every row of its
cross packet, including the exceptional pair, is z-tight, so all raw 10/3
survives as comparison currency, or 5/6 after cover normalization.

The surviving amount is **cover-selection shear**, not automatically either
term in the spectral decomposition. Exact controls give

```text
          B*     BH     O     BH-B*   O-BH   packet shear
PXC101    15     15     15      0       0         1
PXC104    56/3   56/3   56/3    0       0        10/3
PXC125    16     16     23      0       7         2/5
```

Thus a positive shear can be entirely surplus when `D_H=0`, and even at
positive demand it need not be the currency that closes the target. Any
next theorem must construct an admissible map from selected shears or staged
labels into the actual threshold layers; nomenclature cannot supply that
map.

Together PXC132 and PXC133 rule out counting imported facet slack directly.
The next theorem must assign exceptional comparison shears—or the staged
labels that generate them—to vertex-disjoint threshold rectangles. Exactness
slack already present at z is not spendable a second time.

### PXC134 endpoint-congested threshold transport

For any predeclared family of high--low residual pairs `i -> j`, give the
edge length

    ell_ij = min(x_i,z_i) - max(x_j,z_j) > 0.

Choose nonnegative edge weights with outgoing weight at most one and
incoming weight at most one at every player. Layer-cake counting proves, in
every dimension,

    max sum ell_ij rho_ij <= O-B_H.

The exact dual is a bipartite source/sink cover:

    min sum_i (p_i+q_i)  subject to p_i+q_j >= ell_ij, p,q>=0.

For the complete clipped graph, the canonical opposite-rank edges from
`(CS)` are feasible and attain equality. Hence the LP loses value only when
the structural mechanism rule omits needed edges.

Hence a blocker/Farkas rule that generates an allowed graph with transport
value at least `D_H` closes the target. If it fails, the dual potentials with
total below `D_H` are the precise obstruction that the singleton witnesses
must contradict. A player has separate high-source and low-sink capacities:
using it once in each role is safe because the two threshold ranges are
disjoint. This enforces cross-packet congestion without imposing the false
stronger requirement that a player appear only once in total.

PXC125's two predeclared rungs give value `7=O-B_H`; PXC127's common-cut
graph gives `37/5=O-B_H`; both exceed `D_H=2/3`. PXC101, PXC104, and PXC90
have no positive label layer and zero demand, so their positive packet
shears do not enter this transport LP.
An allocation-only chain control confirms that the split capacities retain
two consecutive half-unit edges through the same physical player; merging
the capacities would incorrectly lose one. Its restricted value is `1`;
the complete clipped graph restores all `3/2` of its label currency.

The remaining theorem is now exact: from a positive-demand PXC114 common
blocker or reciprocal blocker pair, construct an allowed edge graph whose
fractional matching value reaches `D_H`, or use the dual source/sink potentials
to derive a contradiction from the staged Farkas identities and singleton-
attainment witnesses.

### PXC135 mechanism-labelled canonical saturation

PXC129 and PXC134 remove the qualitative construction/congestion issue.
Take every positive canonical rank carrier from `(CS)`. If a common tight
row separates its endpoints, use that row as its label. Otherwise PXC129,
applied to any qualifying cover, supplies either a separating positive cover
row or the staged-Lmax blocker forced when the cover sees the endpoints
identically. Thus every canonical carrier has a tight-row/polar mechanism
label.

The canonical carriers use each player at most once as source and once as
sink, so all can be assigned weight one simultaneously in PXC134. Their
value is exactly `O-B_H`. This proves a dimension-free mechanism attribution
of all label currency in both PXC114 branches, without spending packet shear.
A row label may repeat because it certifies incidence only; no row slack is
being charged once per carrier.

What remains is quantitative, not combinatorial selection: prove from the
singleton-attainment and staged Farkas inequalities attached to those labels
that no PXC134 source/sink dual cover of total below `D_H` can exist. In
other words, the missing lemma must lower-bound the lengths of the already
labelled canonical carriers; adding more labels or more packet catalogues
cannot solve it.

### PXC136 stationary singleton-witness bridge

The carrier dual factorizes because the canonical carriers form a matching.
The first coefficient-bearing object that does not factor is instead the
stationary circulation of all singleton-attainment witnesses.  With total
`T`, use variables `pi_r,F_ri` satisfying

```text
sum_i F_ri = pi_r = sum_i F_ir,     F_rr=0,
T F_r(S) >= pi_r v(S),              sum_r pi_r=1.
```

Exactness makes this system nonempty: normalize one zero-at-`r` core witness
per row and take a stationary distribution of the resulting zero-diagonal
Markov matrix.  Conversely every positive flow row is exactly such a core
witness after rescaling.  The stationary core allocation `y=T*pi` satisfies
`y_i<=T/2`.

For any allocations `x,z`, define

```text
Psi_stat=max sum_i[min(x_i,y_i)+min(z_i,y_i)]-T.
```

Then

```text
Psi_stat
 = O(x,z)-min sum_i dist(y_i,[min(x_i,z_i),max(x_i,z_i)])
 <= O(x,z).
```

This is a conventional all-dimensional theorem, not a census.  Its LP dual
has one family of exact-game row coefficients for every root, coupled by
shared row/column potentials; it is the first candidate price that cannot be
spent independently edge-by-edge.

The live conjecture is the exact disjunction

```text
max(B_star,Psi_stat) >= c_n T.                         (PXC136?)
```

It passes the two six-player archive banks exactly: among 374 raw records
(373 distinct selector triples), 321 are closed first by `B_star` and the
other 52 have a target-reaching stationary bridge.  It also closes the
positive-demand PXC125 control and every balanced `G(p,k)`; on the latter a
two-witness bipartite stationary chain puts `T*pi` coordinatewise between
the two selectors and hence recovers overlap exactly.  PXC101, PXC104 and
PXC118 are positive controls; PXC90 is already a spectral/full-rank boundary.

The arms are genuinely complementary.  A sharp total-four equality control
has exact stationary optimum `45/17<8/3`, while its spectral bound equals
`8/3`.  Exact primal/dual certificates use the six irredundant core rows;
deleting the witness-core constraints raises the relaxed bridge to `8/3`.

The next goal is no longer to construct more transport labels.  It is:

> **Spectral-deficit stationary-dual theorem (open).**  Assume
> `B_star<c_n T`.  Combine the complete staged Lmin/Lmax Farkas identities
> with an arbitrary dual certificate for `Psi_stat` to prove that its dual
> objective is at least `(1+c_n)T`.

Falsification must search directly for an exact selector pair with both
`B_star<c_nT` and `Psi_stat<c_nT`, then independently replay the selectors,
the spectral certificate, and matched stationary primal/dual optima.  A
six-player catalogue extension is not a substitute for this two-sided test.

### PXC137 product midpoint and forced-diagonal price

The stationary relaxation is now exact.  Drop only `F_rr=0` from PXC136 and
put

```text
pi_r=(x_r+z_r)/(2T),
F_ri=(x_r z_i+z_r x_i)/(2T^2),
y=(x+z)/2.
```

Row and column marginals are `pi`, and every root-labelled core row has the
exact slack

```text
T F_r(S)-pi_r v(S)
 = [x_r(z(S)-v(S))+z_r(x(S)-v(S))]/(2T) >= 0.
```

Because `y` lies in the coordinate box between the selectors, the relaxed
bridge equals `O` exactly.  Thus the entire PXC136 loss is caused by the
single structural constraint `F_rr=0`; it is not caused by aggregate core
feasibility, row/column balance, or cap linearization.

A fixed-midpoint repair is a matrix `R` with zero row/column sums,
`R_rr=-x_r z_r/T^2`, `F+R>=0`, and each core-row derivative bounded below by
the negative displayed slack.  Common-tight selector rows have zero slack,
so the repair directions lie in the PXC112 common tangent.  This is the
first exact algebraic interface from the stationary bridge to PXC114:
PXC114 independently supplies common outside-union blockers or reciprocal
cross-cover pairs on the universal-cover-failure branch.  Proving that those
labels control the coupled diagonal repair is the next theorem; it is not
claimed by PXC137.

In the PXC136 dual define

```text
L_r(i)=sum_(S contains i) lambda_rS,
Delta_r=T L_r(r)-A_r-B_r.
```

The diagonal-relaxed dual simply adds `Delta_r<=0`.  Weighting the existing
dual by the product flow proves

```text
dual objective >= T+O-sum_r (x_r z_r/T^2)[Delta_r]_+.
```

Hence every strict stationary loss has explicit root-labelled diagonal
currency.  PXC138 below shows that one optimal dual's defect is not equal to
the total price: the sharp equality control misses by a factor of 27.  Since
that control has `B_star=c_nT`, it does not refute a theorem under the strict
hypothesis `B_star<c_nT`; it makes that hypothesis quantitatively
load-bearing.  The integrated shadow-price target is the exact formulation
that remains valid on both sides of the boundary.

### PXC138 diagonal-release curve

The positive defect in PXC137d is only a marginal price.  For

```text
d_r=x_r z_r/T^2,  0<=t<=1,
```

replace the forbidden diagonal by `0<=F_rr<=t*d_r`, and call the bridge
optimum `Psi_t`.  Eliminating the new diagonal-cap multipliers in the dual
gives the exact envelope

```text
T+Psi_t = min_(q in D) { D(q)+t E(q) },
E(q) = sum_r d_r [Delta_r(q)]_+.
```

Therefore `Psi_t` is nondecreasing, concave, and piecewise linear, with
`Psi_0=Psi_stat` and `Psi_1=O`.  If `D_t` is the minimizing dual face, its
right slope is `e_+(t)=min_(q in D_t) E(q)`, and

```text
O-Psi_stat = integral_0^1 e_+(t) dt.
```

This kills the unconditional identification of the integral with one defect
at `t=0`.  On the sharp total-four equality control,

```text
Psi_t = 45/17 + min(9t/17,1/51).
```

The curve reaches overlap already at `t=1/27`; its initial optimal-face
exposure is `9/17`, while its total price is only `1/51`.  The ratio is 27.
Because this control has `B_star=c_nT`, it is not a counterexample to a
strict-spectral-failure theorem; such a theorem must use the strict deficit
and cannot follow from parametric LP duality alone.

Under `B_star<c_nT`, the live theorem is now exactly

```text
integral_0^1 e_+(t) dt
 <= C_top + C_label - (c_nT-B_star).
```

The left side is explicit root-labelled diagonal load.  The right side is
the already-proved spectral top-selection and label currency.  PXC112/PXC114
must control the *whole decreasing shadow-price curve*, not an arbitrary
dual at `t=0`.  This is the next common/reciprocal mechanism-to-price
theorem.  Parametric LP sensitivity itself is standard and is not claimed as
novel.

### PXC139 strict-spectral single-dual no-go

Strict spectral failure does not make the initial diagonal shadow price
small enough.  The exact singleton-normalized total-eight game defined by

```text
0123>=4, 0234>=6, 1234>=6,
025>=2, 125>=2, 245>=2, 01345>=8
```

has

```text
x=(1,1,0,5/2,5/2,1),
z=(2,2,0,2,2,0),
B_star=5 < 16/3=c_6*T,
O=6,
Psi_stat=191/34 > 16/3.
```

Thus the main spectral--stationary disjunction succeeds.  Nevertheless the
minimum product-weighted diagonal exposure on the optimal zero-diagonal
dual face is exactly

```text
E_0=54/17 > 2/3=O-c_6*T.
```

The upper certificate is an explicit optimal dual of exposure `54/17`.  An
exact released primal at `t=1/20` attains

```text
Psi_(1/20)=491/85=Psi_0+(1/20)(54/17),
```

which forces the matching lower bound on every optimal dual exposure by
PXC138a.  Hence the pointwise theorem

```text
B_star<c_n*T => exists optimal q with E(q)<=O-c_n*T
```

is false.  The next attack must control the integral of the changing dual
face, or an equivalent global release-curve quantity; optimizing one dual at
`t=0` is a closed route.

### PXC140 slope times saturation

The integrated price has an exact two-factor upper bound.  Let

```text
tau_star=min{t in [0,1]: Psi_t=O},
e0=Psi'_+(0).
```

Since the release curve is nondecreasing and concave, it is constant at
`O` after `tau_star`, and its right slope is nonincreasing.  Therefore

```text
O-Psi_stat = integral_0^tau_star e_+(t) dt
           <= tau_star*e0.                            (PXC140)
```

The threshold `tau_star` is itself a primal LP: minimize the common
normalized diagonal-cap factor needed by a bridge attaining the selector
box value `O`.  Thus `e0` is the initial staged-dual price and `tau_star` is
the amount of the forbidden resource that must actually be released.

This factorization is exact on the sharp equality control:

```text
tau_star=1/27, e0=9/17,
tau_star*e0=O-Psi_stat=1/51.
```

It also repairs the strict-spectral PXC139 obstruction:

```text
tau_star=14/81, e0=54/17,
O-Psi_stat=13/34 < tau_star*e0=28/51 < 2/3=O-c_6*T.
```

The exact upper bound on `tau_star` is a box-saturating primal.  A left
supporting dual with `D=469/34`, `E=81/68`, and
`D+(14/81)E=T+O=14` proves the matching lower bound.

The product estimate proposed at this checkpoint was

```text
tau_star*e0
 <= C_top+C_label-(c_n*T-B_star).                     (PXC140?)
```

It is a sufficient mechanism-to-price theorem, not an equivalent
reformulation of the main inequality: the product may overestimate the true
integrated price.  PXC142 now falsifies it even in the strict-spectral n=6
domain.  PXC139 closes the initial-slope-only route and PXC142 closes the
uniform slope-times-saturation route; the surviving object is the integrated
release price itself.

## 12. Faithful complement

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

## 13. PXC141 literal-target resolution and successor frontier

The literal all-n objective is resolved negatively by the existing n=5
two-generator game:

```text
x=(1/2,1/2,5/4,1/2,5/4), z=(1,0,1,1,1),
T=4, O=3 < (5/6)T=10/3.
```

Exact primary and standalone symbolic replays pin the 32 game values, both
staged selectors, all 16 subfamilies of the proper x-tight pool, every
complete subfamily, and the exhaustive spectral-top result.  Since n<=4 has
Lmin=Lmax, this is the smallest counterexample.  The corrected n>=6 theorem
was the successor goal, with PXC141 as its mandatory domain guard; PXC143
below now falsifies it at seven players.

## 14. PXC142 structural saturation bound and product-route no-go

Mixing any zero-diagonal stationary flow with the PXC137 product flow gives
the dimension-free bound

~~~text
tau_star <= inf_F0 max_i q_i/(q_i+a_i),
a_i=|x_i-z_i|/2,
q_i=dist(T*pi_i,[min(x_i,z_i),max(x_i,z_i)]).
~~~

Equivalently, if a zero-diagonal stationary center lies in the selector box
expanded by a factor kappa, then tau_star<=1-1/kappa.  This is a genuine
structural theorem, but a complement-tight equal-coordinate can force
tau_star=1.

The exact n=6 blend

~~~text
v=(1/35)v_sharp+(34/35)(v_139/2)
~~~

has

~~~text
B_star=559/210 < 8/3,
O=47/15,
x_2=z_2=1/35,
v(N\{2})=139/35.
~~~

The last two identities force the full product diagonal at player 2 in every
overlap-attaining stationary bridge, hence tau_star=1.  Exact rational
primal--dual certificates at t=1/4 and t=0 give

~~~text
e0 >= 1678344132/2126609611 > 7/15=O-c_6*T.
~~~

Thus PXC140e is false inside the corrected strict-spectral domain.  The game
is not a counterexample to the main overlap inequality.  The next proof
route must control the integrated shadow-price curve directly, exploiting
how its active dual face changes, rather than multiplying a worst initial
slope by a worst saturation time.

## 15. PXC143 exact seven-player counterexample

The corrected `n>=6` overlap conjecture is now false.  PXC143 defines an
exact singleton-normalized seven-player game as the lower envelope of nine
explicit integer core allocations of total `119376`.  Exact staged
certificates and an independently formulated Z3 selector replay give

```text
Lmin=(8507,24825,41719,17026,8555,8519,10225),
Lmax=(36,132,25137,25137,25125,25113,18696).
```

Their distance is `99492`, twelve above `5T/6`; equivalently the overlap is
`69630`, six below `7T/12`.  Sparse tight-row summations give a conventional
stage-by-stage proof of both selectors.  The example is dimension-minimal
inside the corrected domain because Theorem `s6` proves the six-player
bound.  It does not identify the sharp seven-player constant.  The live
frontier is now classification and sharpening of the seven-player failure,
not another universal bridge inequality.

## 16. PXC144: the four-generator game `H_7`

PXC143 was a threshold crossing, not the seven-player frontier.  Exact
hill-climbing on the true selector distance (integer transfer moves on the
generator entries, every step re-evaluated by staged exact LPs) climbs from
`5/6+1/9948` to about `0.8417` within minutes, and a tangent linear program
then jumps to a vertex of the combinatorial cell: freezing the attaining
generator of every coalition, the tight rows of both selectors, the payoff
weak orders and the zero pattern makes the selector pair an affine function
of the generator entries, the staged Farkas identities keep certifying both
selectors (they depend only on incidence), and maximizing the distance is a
linear program.  Its optimum is the integer game

```text
T=13:  A=(1,4,7,0,0,0,1), B=(0,0,0,5,3,3,2), C=(0,5,8,0,0,0,0), D=(0,0,4,1,3,3,2)
Lmin=(1,3,5,1,1,1,1),  Lmax=(1,3,13,13,13,13,9)/5,
rho=56/65=5/6+11/390,  O/T=37/65<7/12.
```

The generator set is minimal.  Both selectors have an eight-value sparse
hand proof (`v(235)=v(236)=7`, `v(146)=v(156)=5`, `v(12345)=11`,
`v(2456)=8`, `v(0234)=v(0235)=8`).  The value `56/65` is stable under
repeated polish--climb alternation from `H_7`; alternation started from the
two-generator seeds `G(2,4)`, `G(3,3)`, `G(4,2)`, `G(1,5)` did not leave
their own values in the same budget.  `s(7)>=56/65`; nothing is claimed
about the sharp value.

Method laws recorded: a first-crossing witness from a threshold search is
never the supremum — polish it; freezing the cell is what makes the polish
exact, and every polished point must be re-verified from scratch because
the LP optimum may create new ties.

## 17. PXC145: eight and nine players, and the family `H_m`

Twin-splitting the floor gainer of `H_7` (halving its column into two
players preserves equal totals; duplicating a column does not) and
re-running polish--climb gives

```text
n=8, T=44: x=(2,12,20,2,2,2,2,2), B=(0,0,0,18,10,10,6,0), C=(0,16,28,0,0,0,0,0), D=(0,0,15,3,10,10,6,0)   rho=63/55
n=9, T=31: x=(1,9,15,1,1,1,1,1,1), B=(0,0,0,13,7,7,4,0,0), C=(0,11,20,0,0,0,0,0,0), D=(0,0,11,2,7,7,4,0,0)  rho=196/155
```

against formula values `1` and `11/10`.  The loser side `{d,e,e',g}` is
identical in all three games; only the number `m` of floor gainers grows.
Reading off the entries gives the family `H_m` of (PXC145a).  PXC146 now
proves conventionally, for every integer `m>=1`, that its displayed vectors
are the two selectors and
`rho(H_m)=14(5m-1)/(5(9m+4))`.  The proof uses eight affine coalition values:
a partition cap pins the `m` floor players, three incidence sums pin the
remaining Lmin floor, and two five-load inequalities pin the four-player
Lmax top; the candidate Lmax is an explicit positive convex combination of
three generators.  A stdlib affine-identity verifier audits the universal
algebra and an independent Z3 tangent implementation calibrates `m=1..4`.
The family beats balanced `G(p,k)` exactly for `m<=8` (`7<=n<=14`) and tends
to `14/9<2`.  Hence its fixed four-player loser side is the precise
obstruction to an asymptotic improvement; a two-parameter family growing
both sides is the next construction target.

Upper-bound status: the threshold form of the s6-style exchange relaxation
(x, z, seven singleton witnesses, anchors, full `{0,+1,-1}` menu, threshold
`56/65`, tangent-separator CEGAR) remained SAT after two rounds
(`3` and `10` minutes); no upper bound below `2` is known at `n=7` beyond
the trivial `rho<=2`.

Worked controls this round: the n=6 polish--climb alternation started from
`G(2,3)` stays exactly at `2/3` (as Theorem s6 requires), and the
two-generator n=7 seeds `G(2,4)`, `G(3,3)`, `G(4,2)`, `G(1,5)` stay at their
own values under the same budget.

## 18. PXC147: two growing blocks force a four-generator no-go

The incidence-faithful extension of `H_m` is now classified rather than
left as a search prompt.  Replacing `{e,e'}` by an `r`-player symmetric
block while retaining the PXC146 floor-pinning rows forces

```text
h=2m/(r-1),  p=rh+1,  q=h+1,  s=m+1,
T=m+2rh+r+2.
```

For every ordered transfer `p/2<=t<=p`, PXC147 proves both selectors in two
closed chambers (`h<=1` and `h>=1`).  Along `m/r -> a`, both chambers have

```text
rho -> 8a/(5a+1) < 8/5,
```

and the exact formula is below `8/5` throughout the `r>=3` class.  Thus the
obvious four-generator extension cannot beat balanced `G` infinitely often;
its failure is structural, not a failed coefficient search.

The algebra identifies the broken dependency.  The rows `bcdE`, `cdg`,
`be_i g`, and `cEg`, together with efficiency, force the linear total scale.
Replacing only `cEg` by `c(E\i)g` still gives `X_c<=3m`, and merely adding a
fifth point cannot repair an undercut already created by the unchanged
`B`-generator.  The smallest live construction ansatz must therefore split
the `B`-type load across two complementary growing loser subblocks and use a
cross-block d-pinning row.  This is the next five-generator experiment.

Evidence tier: conventional all-parameter proof plus a stdlib exact
transcription audit; standalone Z3 role-orbit selector recomputation on 25
calibration cases spanning both chambers and the PXC146 boundary; fail-open
control below `t=p/2`.  External correctness and prior-art review remain
required before treating the no-go mechanism as novel.
