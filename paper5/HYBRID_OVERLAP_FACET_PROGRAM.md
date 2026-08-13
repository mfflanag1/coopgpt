# Hybrid overlap and rooted-facet program

Date: 2026-08-11

The protected theorem inventory, scope boundaries, disproved shortcuts, and
active dependency graph are maintained in
`paper5/PROTECTED_RESULTS_LEDGER.md`.  New attacks must preserve that ledger:
closing one branch is not permission to discard the other proved inputs or
the remaining carrier-selection and full-cone-facet obligations.

## 1. Status

The open target is

```text
O(x,z):=sum_i min(x_i,z_i)
       >= 4n T/[n^2-(n mod 2)]                         (H)
```

for `x=Lmin(v)`, `z=Lmax(v)`, and every singleton-normalized exact
`n`-player game with `n>=6`.  This note records a structural theorem for the
sharp family, a dimension-free sign-coherent staged-incidence theorem,
falsified strengthenings, and the exact boundary of what the one-packet
theory currently gives on the facet side.  It does not claim a proof of
`(H)`.

The newest theorem completely classifies the **scalar affordability** of a
labelled rooted row in every target dimension.  Two tight rooted pairs are
automatically affordable; one pair fails exactly when its partner is locked
into every larger rooted tight coalition; and a pair-free root fails exactly
when all its larger rooted tight coalitions share a common carrier.  An
empty-intersection family supplies a canonical minimal fractional packing,
whose balanced equality support is a saturated indecomposable
complement-star facet.  The all-dimensional overlap theorem is still open:
the remaining task is to turn the discrete carrier structure of price
failures into a direct upper-block packet, and to solve stratum alignment
when a scalar-affordable row is selected.

The price-failure branch now has a second dimension-free reduction.  A
descending carrier separator gives a strict direct-comparison payment after
complementation.  A carrier cycle is an exact module of the Lmin active
face; either the Lmax face separates it and gives the same strict payment,
or the block contracts to one integer-weighted role while preserving
exactness, both weighted lex selections, total payoff, and overlap.  This
falsifies “the cycle itself is always the direct block” on twelve exact
archive rows and replaces it with a separator-or-weighted-contraction
program.  Canonical block expansion proves that the weighted endowed quotient
is equivalent to a singleton-normalized exact block game, but does not yet
yield an induction because the weighted affordability/carrier theorems have
not been proved.  Weighted quotients with at most three roles are now closed
by a Lorenz-dominant clipped water-filling theorem.  Four-role quotients are
now also closed whenever both selectors share even one pair endpoint: a
weighted dispersion theorem forces a second shared endpoint, after which the
endowed crossing matrix has no diagonal gap, its adjacent gaps have an exact
atomic cost formula, and the unique target equality expands to the known
six-player `(4,2)`/`(2,4)` profile.  A connected positive-Lorenz continuation
then rules out every opposite-endpoint face change, completing the weighted
four-role quotient theorem.  The remaining theorem on the carrier arm is a normalized
separator/facet coupling together with that higher-dimensional quotient
classification, not a scalar lower bound on one separator slack.

The conclusion is that the correct missing object is a **fully labelled
fractional coupling with a distinguished singleton root**.  The one-witness
reduction in Section 8 turns it into a rooted two-tangent budget and gives a
linear-support certificate if the correct root can be selected.  The newest
premise ablation narrows the tested Lmax contribution further: among the
archived rows, only tight coalitions shared by a sparse ceiling over-cover
and the complete Lmin packet ever need be retained.  The newest sequential
census is sharper still.  After direct
gluing, ceiling interpolation, and null-player descent, only 16 positive-floor
six-player rows remain; 13 close with the complete Lmin packet and a ceiling
root alone, while exactly three need a common-hinge repair, all at tied
over-cover roots.  The common-hinge reduction is proved as a sufficient
implication and has a sharp exact negative control when all such hinges are
deleted, but the resulting root-price/common-repair disjunction remains
conjectural in general dimension.
A literal partition of the players is already false at six players, while
treating the Lmin packet itself as one exact-cone facet is also false in
general.

The newest positive result crosses that boundary on a dimension-free mixed
class.  A complete Lmin block-star packet plus a root-zero witness and only
one aligned Lmax-tight hinge already proves `(H)`; the other star hinges need
not be common.  Its witness projection is the same indecomposable rooted
block-star facet as in `G(p,k)`.  More generally, a rooted pair lift with
deficit/root price `P=Q/delta` proves
`O/T>=n_0/(P+n_0-1)` whenever its deficits lie on one lower loss stratum and
one mixed row pays the total gain.  Every extreme cut in the current hostile
suite has affordable price; multistage stratum/sign alignment is now the
precise unresolved facet interface.  The price is attached to the **marked
packing decomposition**, not to the completed exact-cone facet normal: the
rooted-pair gauge used for facet enumeration preserves the latter but can
destroy affordability.  Thus the missing selection object is a marked rooted
facet (normalized facet plus Lmin-tight pair labels), rather than an
unlabelled facet ray.
The compact hostile-review packet is
`MIXED_BLOCK_STAR_FACET_PRICE_THEOREM.md`.

The companion note `EFFECTIVE_BIPARTITION_BRIDGE.md` extracts a capped
fractional role of mass `a=min(1/theta_+,floor(n/2))` from the
minimum-dispersion ceiling over-cover.  The initially surviving candidate

```text
O/T>=1/a+1/(n-a)
```

would imply `(H)` and is exact on both balanced orientations of `G(p,k)`, but
is now refuted by an exact two-generator seven-player game.  The role
decomposition and exact dual formula for `theta_+` remain proved; their two
reciprocal masses are not a universal overlap floor.

### Theorem (zero-floor null-player descent)

Let `v` be any singleton-normalized exact game and put `x=Lmin(v)`.  If

```text
min_i x_i=0,                                            (NPD0)
```

then some player `r` is null:

```text
v(S union {r})=v(S)                  (S subset N\{r}). (NPD1)
```

Writing `v'` for the restriction to `N\{r}`, one has

```text
Core(v)=Core(v') times {0_r},
Lmin(v)=(Lmin(v'),0_r),
Lmax(v)=(Lmax(v'),0_r),
O(v)=O(v'),                         v(N)=v'(N).        (NPD2)
```

#### Proof

Singleton normalization makes the core nonnegative, and the first Lmin stage
is `max_(y in Core(v)) min_i y_i`.  If its value is zero, no core allocation
is strictly positive in every coordinate.  Were each player positive at some
core allocation `y^i`, the average of the finitely many `y^i` would be a core
allocation positive in every coordinate, a contradiction.  Hence some fixed
`r` is zero at every core allocation.  Exactness now gives

```text
v(S union {r})=min_(y in Core(v)) y(S union {r})
              =min_(y in Core(v)) y(S)=v(S),
```

proving nullity.

Because `v(N\{r})=v(N)`, efficiency and nonnegativity force every core point
to have coordinate `r` equal to zero.  Restriction therefore maps
`Core(v)` into `Core(v')`.  Conversely, extend any point of `Core(v')` by a
zero at `r`; nullity checks every coalition inequality containing `r`, so the
extension lies in `Core(v)`.  This proves the core product identity.  A
coordinate fixed at zero in the entire feasible set can simply be deleted
from both lexicographic comparisons, proving selection and overlap
preservation.  QED.

The target constants

```text
c_n=n/floor(n^2/4)=4n/[n^2-(n mod 2)]
```

are strictly decreasing.  For `n=2k`,

```text
c_(n-1)-c_n=(2k-1)/[k(k-1)]-2/k>0,
```

and for `n=2k+1`,

```text
c_(n-1)-c_n=2/k-(2k+1)/[k(k+1)]>0.                   (NPDC)
```

Therefore the zero-floor branch at dimension `n` follows from the theorem at
dimension `n-1`.  The proved five-player overlap floor `3/4` exceeds
`c_6=2/3`, so it seeds the six-player descent; the proved six-player theorem
then closes every zero-floor seven-player game.  More generally, any
minimal-dimensional counterexample to `(H)` has strictly positive Lmin floor
and no null player.  Thus the all-dimension program may restrict its hard
packet/gluing theorem to `mu>0` without loss under induction.

This elementary descent was used in earlier finite work but had not been
integrated into the all-dimension hybrid program.  It is not presented as a
novel null-player result.

Reproduce the target arithmetic and the existing exact null-padded control
with

```bash
python3 verifiers/divergence/verify_null_player_hybrid_descent.py \
  --output verifiers/divergence/null_player_hybrid_descent.json
```

## 2. Shared-hinge theorem for the sharp family

For the master family `G(p,k)`, write

```text
N={0} disjoint-union O disjoint-union B,
|O|=p, |B|=k, T=pk,
C_b={0} union (B\{b})       (b in B).
```

The known closed forms are

```text
x_0=p^2(k-1)/(p+1),       x_i=p/(p+1)       (i!=0),
z_0=z_b=p(k-1)/k          (b in B),
z_o=1/k                   (o in O).
```

### Theorem (common normal hinge)

The same `k` coalitions `C_b`, all tight at both `x` and `z`, support the
following three systems.

1. A first-stage Lmax over-cover:

   ```text
   sum_b (1/k^2) 1_(C_b) = alpha,
   alpha_0=1/k,
   alpha_b=(k-1)/k^2,
   alpha_o=0.
   ```

   Thus `eta=0`, `sum alpha_i=1`, and `alpha.x=max z`.

2. A first-stage Lmin under-cover:

   ```text
   sum_b 1/[k(p+1)] 1_(C_b) = xi 1_N-beta,
   xi=1/(p+1),
   beta_o=1/(p+1),
   beta_b=1/[k(p+1)],
   beta_0=0.
   ```

   Thus `sum beta_i=1` and `beta.z=min x`.

3. For every `b in B`, a rooted Lmin circuit:

   ```text
   1_(C_b)+sum_(o in O)1_({0,o})+1_({0,b})
     -(p+1)1_({0}) = 1_N.                              (R_b)
   ```

   This is the block-star system with root `{0}` and peripheral partition

   ```text
   B\{b}, {b}, and {o} for o in O.
   ```

   Hence it is indecomposable and defines an exact-cone facet by the standard
   semi-balanced facet criterion.  Its slack inequality is saturated at `x`.

### Proof

Every identity is coordinatewise.  In the first, player `0` belongs to all
`k` hinges, a player of `B` belongs to `k-1`, and a player of `O` belongs to
none.  In the second, the same loads are respectively
`1/(p+1)`, `(k-1)/[k(p+1)]`, and zero, which equal `xi-beta_i`.

For `(R_b)`, every non-root player belongs to exactly one positive coalition.
The root belongs to all `p+2` positive coalitions, and subtracting `p+1`
leaves load one.  The supported sets are exactly a block star, so the
dimension-free result in `paper3/BLOCK_STAR_FACET_THEOREM.md` supplies
indecomposability.  Finally, all singleton values vanish and direct
substitution gives

```text
sum_(o in O) s_x({0,o}) + s_x({0,b})
  = (p+1)s_x({0}),
```

so the facet budget is tight.  QED.

### Overlap factorization

Let `A={0} union O`, so `|A|=p+1` and `|B|=k`.  Coordinatewise minima give

```text
O(A)=T/k,             O(B)=T/(p+1).
```

Therefore

```text
O/T = 1/k+1/(p+1) = n/[k(p+1)].                       (F)
```

The sharp denominator is not accidental: the Lmin and Lmax normals share a
tight-coalition hinge, each hinge completes to an active rooted facet, and
the two carrier sizes enter reciprocally.  Balancing them minimizes `(F)`.

The solver-free verifier

```bash
python3 verifiers/divergence/verify_balanced_family_shared_hinge.py \
  --output verifiers/divergence/balanced_family_shared_hinge.json
```

checks both balanced seven-player orientations `(p,k)=(2,4),(3,3)`, every
incidence and objective identity, core membership, every rooted slack
equality, the deleted-load normalization `(OCP)`, both zero-slack pair-lift
evaluations, and the sharp overlap.  It uses the proved selection formulas;
generic staged recomputation is separate existing evidence.

## 3. A clean strengthening that is false

The factorization above suggests asking for a balanced carrier partition in
every game.  Put `w_i=min(x_i,z_i)`, `a=floor(n/2)`, and `b=ceil(n/2)`.
The tempting statement is that some `A`, `|A|=a`, satisfies

```text
w(A)>=T/b,             w(N\A)>=T/a.                   (IP)
```

Adding `(IP)` proves `(H)`.  However `(IP)` is false already at `n=6`.
Two archived exact pairs of total five have overlap multisets

```text
{1,1,1/2,1/2,1/2,0}.
```

Every three-element submultiset has sum at most `3/2` or at least `2`, so no
`3|3` split gives at least `5/3` on both sides.  Their total overlaps are
`7/2>10/3`; thus they do not challenge `(H)`.  They only refute the integral
carrier proof.

Reproduce the exact archive audit with

```bash
python3 verifiers/divergence/audit_hybrid_carrier_split.py verifiers \
  --output verifiers/divergence/hybrid_carrier_split_audit.json
```

It checks 375 archived six-player pairs and records exactly the two failures.
The audit finds no archived seven-player records in that data format, so the
closed-form seven-player hostile check is reported separately.

Allowing fractional player membership repairs the granularity defect, but by
itself merely convexifies the desired scalar inequality and supplies no new
game-theoretic restriction.  The fractional weights must therefore be
generated by the packet/over-cover incidence systems, not chosen after seeing
the overlap vector.

## 4. Hinge-surplus dichotomy and a sharper spectral theorem

The common hinge has an exact quantitative relaxation.  For any Lmax
over-cover

```text
sum_A lambda_A 1_A = eta 1_N+alpha,
```

supported on `z`-tight coalitions, define

```text
epsilon_+ = alpha.x-M.
```

### Lemma (Lmax hinge surplus)

```text
epsilon_+ = sum_A lambda_A [x(A)-v(A)] >= 0.           (S+)
```

It vanishes if and only if every positive-weight over-cover coalition is
also `x`-tight.

### Proof

Evaluate the incidence identity at `x` and `z` and subtract.  Efficiency
cancels the `eta` term, while `alpha.z=M` because `alpha` is a probability
on the Lmax top stratum.  Since every supported coalition is `z`-tight and
`x` is feasible,

```text
alpha.(x-z)=sum_A lambda_A[x(A)-z(A)]
           =sum_A lambda_A[x(A)-v(A)]>=0.
```

The summands and weights are nonnegative, giving the equality criterion.
QED.

The Lmin mirror is equally exact.  For

```text
sum_B gamma_B 1_B = xi 1_N-beta
```

supported on `x`-tight coalitions, with `beta` a probability on the Lmin
bottom stratum, put `epsilon_- = mu-beta.z`.  Then

```text
epsilon_- = sum_B gamma_B[z(B)-v(B)] >= 0,             (S-)
```

and equality is equivalent to common tightness on the positive support.

The surplus also strengthens the spectral-anchor theorem immediately.  If
`theta=max_i alpha_i` and `H` is the Lmax top block, then

```text
M+epsilon_+-mu
 = sum_(i in H) alpha_i(x_i-mu)
 <= theta sum_(i in H)(x_i-mu).                       (SA+)
```

Thus the subset requirement in `LMAX_OVERCOVER_COUPLING.md` can be sharpened
from

```text
sum_(i in J)(x_i-mu) >= (M-mu)/theta
```

to

```text
sum_(i in J)(x_i-mu) >= (M+epsilon_+-mu)/theta.        (SR)
```

The same rearrangement proof then gives a (weakly) larger certified overlap.
This is a dimension-free theorem.  It does not yet turn the surplus into the
closed numerical constant in `(H)`.

The exact archived-game audit

```bash
python3 verifiers/divergence/audit_hinge_surplus.py verifiers/s6 \
  --output verifiers/divergence/hinge_surplus_audit.json
```

finds 73 positive-surplus and 301 zero-surplus records among the 374 records
in that directory.  The sharpened discrete spectral minimum strictly
improves three records and creates no positive-floor target failure.  All
five archived equality records have zero surplus.  These counts are
discovery evidence only, but they support the correct dichotomy:

- positive surplus is quantitative overlap currency;
- zero surplus forces a common tight hinge and exposes the rooted-facet
  geometry of Section 2.

## 5. Paired dispersion: one false bridge and one surviving constraint

Let `theta_+` be the minimum Lmax over-cover dispersion and let `theta_-` be
the minimum of `max_i beta_i` over Lmin bottom under-covers.  The sharp family
and the exactified two-packet boundary both suggest

```text
O/T >= theta_+ + theta_-.                              (PD1)
```

This is false.  An exact audit finds 180 failures among 374 archived
six-player pairs.  Concentrated bottom certificates are the simplest issue:
`theta_-=1` can make the right side exceed one while the two selections are
distinct.  Full staged pinning cannot repair a scalar claim already false for
the actual selected pair, so `(PD1)` is discarded.

A different incidence-packing constraint is true in every dimension:

```text
1/theta_+ + 1/theta_- <= n.                            (PD2)
```

### Theorem (dispersion budget)

Suppose `x` and `z` are nonuniform, and put

```text
mu=min x,       M=max z,       Delta=M-mu>0.
```

Every pair of first-stage certificates with dispersions `theta_+` and
`theta_-` and hinge surpluses `epsilon_+,epsilon_-` satisfies

```text
1/theta_+ <= (T-n mu)/(Delta+epsilon_+),
1/theta_- <= (n M-T)/(Delta+epsilon_-).                (DB+)
```

Dropping the nonnegative surpluses gives

```text
1/theta_+ <= (T-n mu)/Delta,
1/theta_- <= (n M-T)/Delta,                            (DB)
```

and consequently `(PD2)`, including for the dispersion-optimal certificates.

### Proof

Put

```text
s_i=x_i-mu>=0,       r_i=M-z_i>=0.
```

Their totals are

```text
sum_i s_i=T-n mu,    sum_i r_i=n M-T,
sum_i(s_i+r_i)=n Delta.                                (T)
```

For an Lmax over-cover probability `alpha`, put
`u=alpha/theta_+`.  Then `0<=u_i<=1`, `u` is supported on the Lmax top block,
and `sum_i u_i=1/theta_+`.  On that block `z_i=M`, so

```text
x_i-z_i=s_i-Delta.
```

The exact hinge-surplus identity is `alpha.(x-z)=epsilon_+`.  Dividing by
`theta_+` therefore yields

```text
sum_i u_i s_i
 = (Delta+epsilon_+)sum_i u_i
 = (Delta+epsilon_+)/theta_+.
```

Since `u_i<=1` and `s_i>=0`, the left side is at most `sum_i s_i=T-n mu`.
This proves the first inequality in `(DB+)`.

For a bottom under-cover probability `beta`, put `w=beta/theta_-`.  On its
support `x_i=mu`, hence `x_i-z_i=r_i-Delta`, and the mirror hinge surplus is
`beta.(x-z)=mu-beta.z=epsilon_-`.  The same argument gives

```text
(Delta+epsilon_-)/theta_-
 <= sum_i w_i r_i <= sum_i r_i=n M-T.
```

This proves `(DB+)`.  Dropping both surpluses, adding `(DB)`, and using `(T)`
proves `(PD2)`.  QED.

If `M=mu`, efficiency forces `x=z=(T/n)1_N`; this is the trivial zero-gap
case and no proper extreme-stratum over-cover is needed.

### Corollary (rigidity at full dispersion budget)

If

```text
1/theta_+ + 1/theta_-=n,                               (DE)
```

then both hinge surpluses vanish and

```text
x_i>mu  =>  z_i=M and alpha_i=theta_+,
z_i<M   =>  x_i=mu and beta_i=theta_-.                 (DR)
```

### Proof

Write `a=1/theta_+`, `b=1/theta_-`.  The proof of `(DB+)` gives

```text
a(Delta+epsilon_+) <= T-nmu,
b(Delta+epsilon_-) <= nM-T.
```

Under `(DE)`, adding the left sides gives
`nDelta+a epsilon_++b epsilon_-`, while the right sides sum to `nDelta`.
Nonnegativity forces both surpluses to vanish and both separate inequalities
to be equalities.

In the Lmax proof, equality in

```text
sum_i u_i s_i <= sum_i s_i
```

with `0<=u_i<=1` and `s_i=x_i-mu>=0` forces `u_i=1` whenever `x_i>mu`.
Since `u` is supported on the Lmax top block, this gives the first implication
in `(DR)` and `alpha_i=theta_+`.  The mirror argument with
`r_i=M-z_i` gives the second.  QED.

Thus every tight-dispersion pair has only three possible payoff cells:

```text
R: x_i>mu, z_i=M;
L: x_i=mu, z_i<M;
C: x_i=mu, z_i=M.
```

Both `G(p,k)` and the nonuniform seven-player control have this geometry.
This characterizes equality in the dispersion budget, not yet equality in
the hybrid-overlap theorem.

For `G(p,k)`, the shared-hinge theorem gives

```text
theta_+=1/k,       theta_-=1/(p+1),
```

so `(PD2)` is tight because `k+(p+1)=n`.  All five archived six-player
overlap equalities also have `theta_+=theta_-=1/3`, hence equality in `(PD2)`.

This is not a stratum-cardinality observation.  In `G(p,k)`, the Lmax top
stratum has size `k+1`, the Lmin bottom stratum has size `n-1`, and they
overlap on all of `B`; their sizes sum far above `n`.  The reciprocals measure
effective incidence dispersion, not disjoint player supports.

There is a stronger formulation that explains `(PD2)`.  Let `A*` be the
polytope of Lmax over-cover probabilities attaining the optimal dispersion
`theta_+`, and let `B*` be the mirror polytope of optimal Lmin under-cover
probabilities.  The candidate theorem is

> **Fractional support-packing conjecture.**  There are `alpha in A*` and
> `beta in B*` such that
>
> ```text
> alpha_i/theta_+ + beta_i/theta_- <= 1    for every i. (FSP)
> ```

Summing `(FSP)` proves `(PD2)`.  On `G(p,k)`, the displayed shared-hinge
certificates satisfy equality at every player: the normalized Lmax load is
one at the head and `(k-1)/k` on each member of `B`; the normalized Lmin load
is one on `O` and `1/k` on `B`.

Independent dispersion LPs need not return a compatible pair.  In the
archived banks, 19 of 140 five-player records and 87 of 374 six-player
records initially have a coordinate of normalized load two.  A joint exact
rational LP, with both dispersions fixed at their separately proved optima,
repairs all 106 cases.  No jointly infeasible record was found.

### Exact separation reduction

The packing conjecture has a useful human-proof equivalent.  Put

```text
U={alpha/theta_+ : alpha in A*},
V={beta/theta_- : beta in B*}.
```

Then `(FSP)` holds if and only if, for every nonnegative price vector `c`,

```text
min_(u in U) c.u + min_(v in V)c.v <= sum_i c_i.       (SEP)
```

Indeed, `(FSP)` says `(U+V)` intersects the unit box `[0,1]^N`.  If the two
closed convex sets are disjoint, strong separation gives a vector `c` with

```text
min_(w in U+V)c.w > max_(y in [0,1]^N)c.y.
```

Negative coordinates of `c` may be replaced by zero: every `w` is
nonnegative, so the left side cannot decrease, while the box support becomes
`sum_i c_i`.  This gives a nonnegative violation of `(SEP)`.  The converse is
immediate by evaluating `(SEP)` at a packed pair.

This reduction is important for the facet program.  The two minima in
`(SEP)` are linear optimizations over projections of rational incidence
cones, so their pieces are attained on sparse extreme certificate rays.
Thus a proof of `(FSP)` can be sought on the rooted packet/over-cover extreme
rays rather than over games or payoff vectors.  Conversely, a failure has a
nonnegative rational price separator and exact sparse optimizing
certificates, a small checkable counterexample object.

The exact audit is

```bash
python3 verifiers/divergence/audit_paired_dispersion.py verifiers/s6 \
  --output verifiers/divergence/paired_dispersion_audit.json
```

and, for the second bank,

```bash
python3 verifiers/divergence/audit_paired_dispersion.py verifiers/s5close \
  --n 5 --output verifiers/divergence/paired_dispersion_n5_audit.json
```

They report all `(PD1)` counterexamples, numerically replay the proved
dispersion budget, find no joint `(FSP)` failure, and record the five
six-player equality rows.  The audit evidence for `(FSP)` remains finite;
`(PD2)` is the human theorem above.

The explicit nonuniform seven-player majorization counterexample supplies a
solver-free hostile control:

```bash
PYTHONPATH=verifiers/divergence \
python3 verifiers/divergence/verify_n7_dispersion_control.py \
  --output verifiers/divergence/n7_dispersion_control.json
```

Using the already proved selection formulas, it reconstructs
`theta_+=1/2`, `theta_-=1/5`, and a compatible normalized packing that tiles
all seven players exactly.  Both hinge surpluses vanish and `(PD2)` is tight.
This is qualitatively different from the balanced `G(p,k)` equality family,
although its overlap `9T/10` is far from extremal.

The proved `(PD2)` does not finish `(H)`: the false statement `(PD1)` was the
attempted conversion from certificate dispersion to actual overlap.  The role
of `(PD2)` is to control the two fractional carrier budgets, while hinge
surplus and later-stage rooted packets must supply the missing overlap
conversion.

## 6. Full-stage transport through pinning congestion

### General projected staged-circuit theorem

The complete staged packets have an exact dimension-free incidence form.
At a Lmin stage let `O` be the earlier pinned set, `B` the current block, and
`T_x` the proper coalitions tight at `x`.  Let

```text
pi:R^N -> R^N/span({1_N} union {e_j:j in O})
```

be the quotient map.

### Theorem (projected staged circuit)

A player `i in B` is pinned at the current Lmin stage if and only if the
projected configuration has a positive relation

```text
sum_(S in T_x)lambda_S pi(1_S)
 +sum_(k in B)r_k pi(e_k)+pi(e_i)=0,                   (PC-min)
```

with `lambda,r>=0`.  If the relation is infeasible, there is a rational
direction `d` satisfying

```text
d(N)=0,       d_j=0                  (j in O),
d(S)>=0       (S in T_x),
d_k>=0        (k in B),
d_i>0.                                                  (PA-min)
```

Thus `(PA-min)` is an explicit improvement on the recursively restricted
Lmin face.

The Lmax mirror replaces every current-block column by its negative:

```text
sum_(S in T_z)lambda_S pi(1_S)
 +sum_(k in B)r_k pi(-e_k)+pi(-e_i)=0.                 (PC-max)
```

Its infeasibility separator has `d_k<=0` on `B` and `d_i<0`, hence improves
the decreasing lexicographic objective on the pinned Lmax face.

Every support-minimal relation in either configuration uses at most

```text
n-|O|                                                     (PS)
```

projected columns, including the forced player column.

The bound is sharp.  If the current block is all `n-|O|` remaining players,
their projected unit columns satisfy

```text
sum_(k notin O)pi(e_k)=0,                               (PX)
```

and every proper subcollection is independent in the quotient.  Thus `(PX)`
is a circuit using exactly `n-|O|` columns.  The sign-reversed collection is
the Lmax sharp example.

The exact rank audit of this sharpness construction is reproduced by

```bash
python3 verifiers/divergence/verify_projected_staged_support_bound.py \
  --output verifiers/divergence/projected_staged_support_bound.json
```

It is only a finite audit of the displayed circuit; the rank argument below
is the proof for arbitrary `n` and `O`.

### Proof

The staged Farkas identity `(SP-min)` is exactly a lift of `(PC-min)`: the
free efficiency multiplier and free old-pin multipliers disappear in the
quotient.  Conversely, lifting a projected relation supplies those free
multipliers and reconstructs the staged incidence identity.  Dotting that
identity with `x` automatically gives the staged objective equation because
all supported coalitions are `x`-tight, old coordinates equal their pinned
values, and every current coordinate equals the stage level.  Hence no
separate objective restriction remains.

If the conic relation fails, exact separation in the quotient gives a dual
vector in the annihilator of `1_N` and every old unit column.  Its signs on
the remaining configuration are precisely `(PA-min)`.  The usual finite
short-step argument preserves all nontight core inequalities and strictly
improves player `i`.  This proves both directions.  The Lmax proof is the
sign mirror.

The quotient dimension is at most `n-|O|-1`.  A circuit in a configuration
of that rank uses at most one more column, proving `(PS)`.  QED.

### Exact enumeration algorithm and facet boundary

For a projected matrix `A`, the staged relation cone is

```text
K(A)={w>=0:A w=0}.
```

Its extreme rays are exactly the support-minimal nonnegative kernel vectors,
equivalently the conformal positive circuits of the projected configuration.
Indeed, a nonminimal support splits conformally into two nonproportional
kernel vectors, while a support-minimal kernel is one-dimensional and cannot
be so decomposed.  Thus circuit enumeration is not merely a support search:
it enumerates every irreducible staged-selection ray.

For a fixed staged face:

1. form the rational projected matrix with tight-coalition columns and the
   appropriately signed current-block unit columns;
2. enumerate conformal circuits containing the forced player column;
3. normalize that coefficient to one and lift the circuit to recover the
   efficiency and old-pin multipliers;
4. retain the sparse extreme relations, with at most `n-|O|` columns;
5. test any lifted semi-balanced system for indecomposability using the
   Studeny--Kratochvil criterion before calling it an exact-cone facet.

This is an exact facet/ray enumeration theorem for the **relative staged
normal configuration**.  It is not a one-to-one correspondence with facets
of the full exact-game cone: quotienting by pinned coordinates and retaining
the labels “tight protector” and “current-side column” are selection-specific
operations.  Some lifts are decomposable, as the three-trace example already
shows; indecomposable lifts are genuine exact-cone facets by the published
criterion.

The all-player staged certificates in
`verifiers/s6/two_packet_exactification_audit.json` and their separate replay
checker are finite bug audits of these identities, not proof dependencies.

### Rooted incidence Hall theorem for the first floor

Before introducing congestion, the individual first-stage certificates admit
an objective-free incidence characterization.  Let `T_x` be the proper
coalitions tight at `x` and let `P={j:x_j=mu}`.

### Theorem (first-floor incidence alternative)

A player `i in P` is individually pinned at the first Lmin stage if and only
if there are `lambda_S,q_j>=0` and a scalar `c` such that

```text
sum_(S in T_x)lambda_S 1_S + sum_(j in P)q_j e_j+e_i
 = c 1_N.                                               (IH)
```

Every solution automatically has `c>=0` and automatically satisfies the
usual certificate objective identity.  If `(IH)` is infeasible, there is a
rational direction `d` such that

```text
d(N)=0,
d(S)>=0       for every S in T_x,
d_j>=0        for every j in P,
d_i>0.                                                 (HD)
```

The direction `(HD)` is an explicit local Lmin improvement.  A
support-minimal certificate in `(IH)` uses at most `n` positive incidence
columns including the forced column `e_i`.

### Proof

The previously proved individual pinning certificate gives `(IH)`.  Conversely,
dot `(IH)` with any core point `y` satisfying `y_j>=mu` on `P`.  Tightness at
`x` and feasibility of `y` give

```text
cT
 = sum_S lambda_S y(S)+sum_j q_j y_j+y_i
 >= sum_S lambda_S v(S)+mu sum_j q_j+y_i.
```

Dotting `(IH)` with `x` shows

```text
cT=sum_S lambda_S v(S)+mu sum_j q_j+mu,
```

because `x(S)=v(S)` and `x_i=x_j=mu`.  Therefore `y_i<=mu`; together with
the first-stage lower bound this pins `i`.

For the alternative, project all incidence columns to
`R^N/span{1_N}`.  Failure of the conic membership in `(IH)` and exact
polyhedral separation give `d` with the signs in `(HD)`; conversely such a
`d` separates the forced column.  A short step `x+epsilon d` preserves every
tight core inequality, efficiency, and the bottom lower bounds while raising
player `i`.  Nontight inequalities remain feasible for sufficiently small
positive `epsilon`.  Finally, the quotient has dimension at most `n-1`, so a
support-minimal positive dependence has at most `n` columns.  QED.

This is a balanced incidence circuit on the full player set, not automatically
an indecomposable semi-balanced system or a facet of the exact-game cone.  It
does give an exact enumeration algorithm: enumerate conformal quotient
circuits containing `e_i`, or solve the rational cone-membership LP.  The
selection labels “tight protector” and “bottom completion” must be retained.

In the singleton-exactified two-packet boundary, `(IH)` is feasible exactly
for the actual first block `{0,1,2,5}` and infeasible for the false trial
player `3`.  Thus this incidence alternative is the precise Hall-type gate
that the aggregate under-cover omits.

The first rigorous use of information beyond the aggregate bottom under-cover
is a sign-aware congestion inequality.  Let `P={i:x_i=mu}` be the first Lmin
block and put

```text
I_+={i in P:z_i>mu},       I_-={j in P:z_j<mu},
P_+=sum_(i in I_+)(z_i-mu),
D_-=sum_(j in I_-)(mu-z_j).
```

For every `i in I_+`, choose an individual first-floor pinning certificate

```text
sum_S lambda^i_S 1_S + sum_(j in P)q^i_j e_j+e_i=c_i 1_N,
```

with `lambda,q,c` nonnegative and the supported coalitions `x`-tight.  Define
the minimum sign-aware column congestion

```text
kappa(P,z)=min max_(j in P) sum_(i in I_+)q^i_j,        (K)
```

where the minimum is over simultaneous choices of the exact pinning
certificates.

### Theorem (first-floor transport)

```text
P_+ <= kappa(P,z) D_-.                                 (FT)
```

### Proof

Evaluate player `i`'s incidence identity at `z`.  Core feasibility of `z`,
tightness of the supported coalitions at `x`, and the certificate objective
identity give

```text
z_i-mu <= sum_(j in P)q^i_j(mu-z_j).
```

Sum over `i in I_+`.  For a fixed column `j`, its coefficient is at most
`kappa(P,z)`.  Terms with `z_j>=mu` are nonpositive and may be deleted from
the upper bound.  The remaining terms sum to `D_-`, proving `(FT)`.  QED.

This directly controls the loss on the bottom block because

```text
sum_(i in P)min(mu,z_i)=mu|P|-D_-.
```

It does not yet upper-bound `D_-`; that is the next coupling needed from the
Lmax over-cover or later Lmin stages.

### Two sharp mechanisms

For `G(p,k)`, the targets are the `k` players of `B` and the deficit columns
are the `p` players of `O`.  For each `b in B`, the common hinge `C_b` gives
the individual certificate

```text
1_(C_b)+sum_(o in O)e_o+e_b=1_N.
```

Thus every deficit column has load `k`, so `kappa<=k`.  The closed-form
payoffs satisfy `P_+=kD_-`, proving `kappa=k` and equality in `(FT)`.

For the singleton-exactified two-packet boundary, the actual bottom block is
`{0,1,2,5}`, the surplus targets are `{1,5}`, and the deficit columns are
`{0,2}`.  Both target certificates use those two deficit columns with unit
weight, so `kappa=2` and again `P_+=2D_-`.

The exact joint certificate audit is

```bash
python3 verifiers/divergence/audit_first_floor_congestion.py \
  --output verifiers/divergence/first_floor_congestion_audit.json
```

It is an example replay, not evidence for a universal numerical bound on
`kappa`.

A tempting final shortcut is false: `D_-<=M-mu` holds in all 140 archived
five-player records and 372 of 374 six-player records, and is sharp in both
mechanisms above, but the remaining two exact pairs have, up to relabeling,

```text
x=(1,4/3,2/3,2/3,2/3,2/3),
z=(1,1,1,0,1,1).
```

Here `D_-=2/3=2(M-mu)`, while `O/T=4/5`.  The larger first-floor deficit is
more than compensated by overlap in the other strata.  Thus the correct
conversion must sum the stagewise transport inequalities; it cannot cap the
first floor in isolation.

### Complete staged transport identity

The exact form of that sum is now visible.  At Lmin stage `t`, let `O_t` be
the earlier pinned players, let `B_t` be the current block at level `ell_t`,
and choose the staged certificate for `i in B_t`:

```text
sum_S lambda_S 1_S + sum_(j in O_t)q_j e_j
 +sum_(k in B_t)r_k e_k+e_i=c 1_N,                    (SP)
```

where `lambda,r>=0` while the old-pin weights `q` are free.  Its objective
identity is

```text
cT-sum_S lambda_S v(S)-sum_(j in O_t)q_j x_j
 -ell_t sum_(k in B_t)r_k=ell_t.                      (SO)
```

Evaluating `(SP)` at `z`, using `z(S)>=v(S)` on the `x`-tight supported
coalitions, and substituting `(SO)` gives the exact stage inequality

```text
z_i-ell_t
 <= sum_(j in O_t)q_j(x_j-z_j)
   +sum_(k in B_t)r_k(ell_t-z_k).                     (ST)
```

For the first stage `O_t` is empty and `(ST)` reduces to the transport proof
above.  Although a raw later-stage dual has free old-pin weights, their signs
are not an intrinsic obstruction.

### Theorem (sign-coherent staged lifts)

Every Lmin staged pinning certificate can be chosen with

```text
q_j>=0                    (j in O_t).                  (SC-min)
```

Every Lmax staged pinning certificate can be chosen with the mirror
orientation

```text
q_j<=0                    (j in O_t).                  (SC-max)
```

Equivalently, put `P_t=B_1 union ... union B_t` for the cumulative Lmin lower
set.  A player `i in B_t` is pinned if and only if there is a pure
nonnegative incidence relation

```text
sum_(S in T_x)lambda_S 1_S + sum_(j in P_t)a_j e_j
 = c 1_N,                 lambda,a>=0, a_i>0.          (NI-min)
```

For Lmax, with cumulative upper set `Q_t`, the mirror relation is

```text
sum_(S in T_z)lambda_S 1_S - sum_(j in Q_t)a_j e_j
 = c 1_N,                 lambda,a>=0, a_i>0.          (NI-max)
```

Thus the free-coordinate quotient theorem has a globally sign-coherent lift:
the price is the weaker global support cap `n`, rather than the sharp relative
cap `n-|O_t|`.

### Proof

Proceed by induction over the Lmin stages.  The first-stage relation already
has no old-pin coefficient.  Suppose all earlier player certificates have
been made sign-coherent and start with any valid certificate at stage `t`.
Process the earlier blocks from latest to earliest.  If the current
coefficient of `e_j`, `j in B_s`, is negative, add a positive multiple of
the sign-coherent certificate that pinned `j` at stage `s`, choosing the
multiple to cancel that coefficient.  The coefficient of `e_j` in its own
certificate is `1+r_j>0`.  Every other unit coefficient it introduces in
`B_s` is nonnegative, and its coefficients on still earlier blocks are
nonnegative by induction.  Hence cancellation never creates a new negative
coefficient in a block already processed.  Coalition multipliers remain
nonnegative, and the supported coalitions remain `x`-tight.  After finitely
many cancellations all old coefficients are nonnegative, proving `(SC-min)`.

The Lmax relation has current-block coefficients `-(r_j+1_(j=i))`.  Starting
from the first stage and applying the same backward substitution cancels each
positive old coefficient by adding a positive multiple of the earlier
certificate.  It introduces only nonpositive unit coefficients, proving
`(SC-max)`.

Collecting the old and current unit coefficients gives `(NI-min)` and
`(NI-max)`.  Conversely, evaluate `(NI-min)` at a core point on the stage
face.  Earlier coordinates are fixed and current coordinates are at least
their stage level.  Equality at `x` forces every current coordinate with
positive `a_j` to equal that level; in particular it pins `i`.  The Lmax
argument is the sign mirror.  Finally, project `(NI-min)` or `(NI-max)`
modulo `1_N` and take a support-minimal positive subrelation containing the
forced unit column.  The quotient has dimension `n-1`, so it uses at most
`n` columns.  QED.

The qualitative hierarchical tight-coalition characterization is established
property I (Arin--Kuipers--Vermeulen, with Mauri's antidual Lmin form).  The
claim here is only the explicit backward-elimination/sign-coherent incidence
normal form and its transport consequence.  It should be treated as a
constructive reformulation pending specialist review, not advertised as a
new characterization of either selection.  See
`paper3/PROPERTY_I_STRICT_COVER_AUDIT.md` for the prior-art boundary.

### Corollary (two acyclic nonnegative transports)

Put `d=x-z` and `d_j^+=max(d_j,0)`.  For every Lmin-stage player `i`, a
sign-coherent certificate gives

```text
(z_i-x_i)^+
 <= sum_(j in O_t)q_j d_j^+ + sum_(k in B_t)r_k d_k^+,
 q,r>=0.                                                   (AT-min)
```

Every source on the right has `x_j<=x_i`.  The Lmax mirror gives

```text
(z_i-x_i)^+
 <= sum_(j in O_t)(-q_j)d_j^+ + sum_(k in B_t)r_k d_k^+,
 -q,r>=0,                                                  (AT-max)
```

where every source has `z_j>=z_i`.  Hence every player gaining from `x` to
`z` has both a poorer-in-`x` carrier packet and a richer-in-`z` carrier
packet supported on players losing from `x` to `z`.  This is stronger than
the former signed-flow conjecture, but it still leaves a quantitative issue:
recursive substitution can increase column congestion.

The exact regression audit

```bash
python3 verifiers/divergence/audit_sign_coherent_staged_lifts.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --n 6 --include-n7-control \
  --output verifiers/divergence/sign_coherent_staged_lifts_audit.json
```

finds sign-coherent lifts for all `4,488` stage/player certificates in the
`374` archived six-player pairs and all `14` certificates of the nonuniform
seven-player control.  This finite audit is not used in the proof.

Both known sharp all-dimension mechanisms have a two-stratum Lmin point, so
their nontrivial transport is already concentrated at the first stage.  The
remaining route is now precise: bound the congestion of the two acyclic
nonnegative transports jointly with the sparse Lmax over-cover, or show that
genuine multistage congestion purchases strict extra overlap.

### The individual unit-box and target-count bounds fail at seven players

The next conjecture is one-sided.  At Lmin stage `t`, let

```text
I_t={i in B_t:z_i>x_i},       P_t=O_t union B_t.
```

Choose one sign-coherent relation `(SP)` for every `i in I_t`.  Define its
joint auxiliary congestion as the largest, over `j in P_t`, of the sum of
the `q_j` and `r_j` coefficients across the chosen relations, and minimize
over all simultaneous choices.  Call the result `kappa_t`.

The six-player archive suggested the following strictly stronger route to
`(TC)`.
For every gaining target `i in I_t`, there is a normalized pinning relation
>
> ```text
> sum_(S in T_x) lambda_S 1_S + e_i + sum_(j in P_t)a_j e_j
>     = c 1_N,                 lambda>=0, 0<=a_j<=1.       (UB)
> ```

If `(UB)` held, choosing one bounded relation for each target and summing
would immediately give

```text
kappa_t <= |I_t|                         for every Lmin stage. (TC)
```

Its exact polar form is especially simple.  Let

```text
D_x={y:y(N)=0 and y(S)>=0 for every proper x-tight coalition S}
```

be the one-sided tangent cone of the core at `x`.  Finite-dimensional
polyhedral separation shows that `(UB)` is equivalent to

```text
y_i <= sum_(j in P_t) max(-y_j,0).                    (BM)
```

for every `y in D_x`.  Indeed `(UB)` fails exactly when a separator satisfies

```text
-y_i < min_(0<=a<=1) sum_(j in P_t)a_j y_j
     = -sum_(j in P_t)max(-y_j,0).
```

The tempting shortcut `y(P_t)<=0` is invalid: Lmin is lexicographically
maximin but need not Lorenz-dominate every core point once the exact-partition
property is lost.  Even the segment joining

```text
x=(1,2,7),                 w=(0,6,4)
```

has Lmin endpoint `x`, while its tangent `y=w-x=(-1,4,-3)` satisfies
`y({0,1})=3>0` and violates `(BM)` for target `1`.  This is not asserted to be
the core of a singleton-normalized exact game; it only proves that lex
optimality and general tangent-cone geometry are insufficient.

The stronger hope that exactness and `z_i>x_i` repair `(UB)` is also false.
Let `v` be the lower envelope of the two common-total allocations

```text
g=(1,1,0,5,0,4,1),             h=(0,0,8,0,4,0,0).
```

This is a singleton-normalized exact seven-player game of total `12`.  Sparse
staged incidence identities give

```text
x=Lmin(v)=(1,1,2,3,1,3,1),
z=Lmax(v)=(8/9,8/9,8/3,8/3,4/3,8/3,8/9).
```

At Lmin stage `1`,

```text
P_1=(0,1,4,6,2),          B_1={2},          I_1={2}.
```

The exact primal packet

```text
1_24+1_44+1_48+2e_0+2e_1+2e_6+e_2=2 1_N              (P7)
```

uses masks `24={3,4}`, `44={2,3,5}`, and `48={4,5}`, all
`x`-tight.  It has auxiliary congestion two.  This is optimal: put the entire
price on player `0` in `P_1` and take

```text
p=(1,0,0,0,0),
y=(-1,0,2,-1,1,-1,0).
```

Then `y(N)=0`, `y(S)>=0` for every proper `x`-tight coalition, and
`y_j>=-p_j` on `P_1`, while `y_2=2`.  Weak duality with `(TC-dual)` and `(P7)`
therefore gives

```text
kappa_1=2>|I_1|=1.                                    (N7-TC)
```

Thus both `(UB)` and `(TC)` are false, even for a two-generator exact game.
Its overlap is `11`, far above the conjectured seven-player floor `7`; this
is a counterexample to the proposed proof bridge, not to `(H)`.

The compensation mechanism is already visible.  Coalition `44={2,3,5}` is
tight at both selections, and

```text
(1/3)1_44=alpha,       alpha_2=alpha_3=alpha_5=1/3
```

is a zero-surplus Lmax over-cover with `theta=1/3`.  The sharpened spectral
anchor of Section 4 evaluates to `11`, exactly the true overlap.  Thus the
coefficient-two staged packet occurs only after the opposite certificate has
already purchased four units of slack above the target.  This suggests a
residual theorem: control congestion only on the regime not already closed by
the spectral anchor, rather than impose a universal target-count cap.

There is an exact price alternative.  Let `C_i` be the polytope of
sign-coherent certificates for target `i`, written with auxiliary vector
`a^i` on `P_t`.  Minimax and the individual incidence LP dual give

```text
kappa_t
 = max_(p in Delta(P_t)) sum_(i in I_t)
     max { y^i_i :
           y^i(N)=0,
           y^i(S)>=0       (S in T_x),
           y^i_j>=-p_j     (j in P_t) }.               (TC-dual)
```

The seven-player dual above attains value two with a single target, so no
termwise unit-Lipschitz proof of `(TC-dual)` is possible.  The remaining
interface must retain the actual Lmax over-cover and hinge surplus: a costly
Lmin tangent packet must be charged directly against overlap currency rather
than bounded by target count alone.  Support-minimal realizations still are
the rooted positive circuits of Section 7, but their coefficients cannot be
discarded.

The exact audit

```bash
python3 verifiers/divergence/audit_staged_target_congestion.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --n 6 --include-n7-control \
  --output verifiers/divergence/staged_target_congestion_audit.json
```

recomputes `(UB)` target by target and finds zero failures on `854` gaining
targets, as well as zero `(TC)` failures, in all `495` nontrivial Lmin stages
of the `374` archived six-player pairs; the largest
`kappa_t/|I_t|` is exactly one.  The older nonuniform seven-player control also
passes.  The new exact obstruction shows why neither finite observation had
dimension-free force.

Reproduce the obstruction, including all fourteen solver-free staged
selection identities and both sides of `kappa_1=2`, with

```bash
python3 verifiers/divergence/verify_n7_staged_congestion_obstruction.py \
  --output verifiers/divergence/n7_staged_congestion_obstruction.json
```

The coefficient growth is not a one-off normalization artifact.  A second
two-generator exact game on eight players has

```text
g=(0,0,7,4,3,2,0,0),          h=(4,1,0,0,0,0,6,5),
x=(8/3,2/3,7/3,4/3,1,2/3,4,10/3),
z=(28/13,7/13,42/13,24/13,18/13,12/13,42/13,35/13).
```

Sixteen sparse staged identities prove the two selections.  At Lmin stage
`3`, player `2` is the only member of its block and the only gaining target.
Its optimal packet is

```text
3 1_9+3 1_85+2 1_104+1_165+4 1_176+2 1_204
  +7e_1+e_2=7 1_N.                                  (P8)
```

The matching price is concentrated on player `1`, and the tangent

```text
y=g-h=(-4,-1,7,4,3,2,-6,-5)
```

is nonnegative on every `x`-tight coalition.  Hence primal and dual values
coincide at

```text
kappa_3=7>|I_3|=1.                                   (N8-TC)
```

After projection modulo `1_N`, the six coalition columns together with
`e_1,e_2` have rank seven.  Thus `(P8)` is a support-minimal positive circuit
on exactly `n` columns, and the coefficient seven is intrinsic to its
primitive circuit vector; it is not caused by a nonminimal certificate.

Again the opposite certificate pays for the local coefficient.  The exact
Lmax over-cover has `theta=7/13`, `eta=4/13`, zero hinge surplus, and spectral
bound `139/13`, while the required eight-player floor is only `8`.  The true
overlap is `544/39`.  Reproduce every identity with

```bash
python3 verifiers/divergence/verify_n8_coefficient_seven_obstruction.py \
  --output verifiers/divergence/n8_coefficient_seven_obstruction.json
```

Consequently neither bounded support nor circuit minimality bounds the
numerical congestion coefficients.  A future coupling may use the support
cap `n`, but it must retain the primitive circuit weights and charge them
against the opposite spectral certificate.

A tempting stronger collapse to one common box vector is false.  In
`verifiers/s6/harvest6_601.json`, record `0`, Lmin stage `1`,

```text
x=(3,3/2,5/2,3/2,3/2,0),
z=(7/3,2/3,7/3,7/3,7/3,0),
I_1={3,4},
```

there is no single relation with `0<=a<=1` and `a_3=a_4=1`, although separate
unit-box packets happen to exist and the sharp joint congestion is `2`.  This
older six-player negative control is now secondary to `(N7-TC)`.

The Lmax mirror is false and must not be imported into a proof.  The same
audit finds `27` failures among `494` nontrivial Lmax stages.  In
`verifiers/s6/harvest6_601.json`, record `21`,

```text
x=(1,1,1,1,2,1),
z=(4/5,4/5,7/5,8/5,8/5,4/5),
```

the first Lmax stage has the single gaining target `3` but minimum mirror
congestion `3/2`.  This exact negative control explains why the live program
uses the complete staged **Lmin** packet together with the sparse first-stage
Lmax over-cover rather than a symmetric pair of target-count bounds.

## 7. What one-packet theory gives on exact-cone facets

The strongest correct statement is a relative circuit theorem, not a global
facet correspondence.

The sign-coherent theorem adds a second exact enumeration layer.  For a fixed
tight menu and cumulative set `P_t`, project

```text
{1_S:S in T_x} union {e_j:j in P_t}
```

modulo `1_N`; use `-e_j` for Lmax.  The extreme rays of the nonnegative
kernel cone are exactly the positive circuits containing the forced signed
unit column, each with support at most `n`.  Enumerating those circuits
therefore enumerates every irreducible **nested selection certificate**, not
merely the certificates in the relative old-coordinate quotient.  This is a
finite exact algorithm for the rooted incidence systems selected by a given
lexicographic face.

The coefficient-seven circuit `(P8)` is a sharp warning about what this
algorithm returns.  The support theorem controls the **number** of columns,
not the size of the primitive rational kernel vector.  Exact circuit
enumeration must therefore output coefficients as well as supports; replacing
each selected circuit by a uniform or unit-load generator loses valid staged
geometry.

It still does not identify a new class of full exact-cone facets.  On the
Lmin side the added unit columns are ordinary singleton incidence columns,
so forgetting their selection role yields a balanced identity.  On the Lmax
side a circuit may contain several negative singleton roots, whereas the
published pure minimal semi-balanced facet correspondence has one
distinguished exceptional coalition.  Only a lift or factor having the
published indecomposability form may be called an exact-cone facet.  The
nested-circuit algorithm supplies candidates and their selection labels; the
Studeny--Kratochvil test remains a separate final filter.

At a slack Lmin richer suffix `H`, the one-packet theorem selects a rooted
signed incidence relation with at most `n` positive coalitions.  Projecting
incidence vectors modulo `1_N`, its support contains a conformal circuit with
`H` as its unique negative element.  Thus, for any fixed menus of tight
protectors and rooted completions, all candidate atoms can be enumerated by
exact rational circuit enumeration.  Each atom is a pure minimal
semi-balanced system and gives a valid exact-game inequality.

This yields an exact algorithm:

1. enumerate minimal balanced rich-trace packets (support at most `|H|`);
2. lift one tight protector per trace;
3. complete the poorer load by rooted spokes;
4. enumerate conformal circuits retaining the negative root;
5. apply the published indecomposability test to decide which circuits are
   exact-cone facets;
6. retain the labels “Lmin-tight protector” and “rooted completion” when
   coupling them to the opposite selection.

### Exact spectral-threshold oracle

There is also an exact finite algorithm on the Lmax side that removes the
apparent nonlinear optimization in `B_spec`.  Fix a rational game and its
rational selections `x,z`, and fix a rational threshold `b`.  Let `H` be the
Lmax top block, and precompute

```text
Bad_b={J subset N: |J|=|H| and B(J)<b}.
```

For a normalized over-cover, the sharpened eligibility condition `(SR)` for
`J` is

```text
theta sum_(j in J)(x_j-mu) >= alpha.x-mu,              (EJ)
```

because `M+epsilon_+=alpha.x`.  Thus that certificate proves spectral bound
at least `b` exactly when every `J in Bad_b` violates `(EJ)` strictly.

> **Theorem (exact threshold oracle).**  Choose in turn a player `r in H`
> that realizes `theta=max_i alpha_i`.  Add
>
> ```text
> alpha_r=theta,                 alpha_i<=theta (i in H),
> alpha.x-mu-theta E_J>=delta    (J in Bad_b)
> ```
>
> to the linear over-cover system `(OC)`, where
> `E_J=sum_(j in J)(x_j-mu)`, and maximize `delta`.  Some normalized Lmax
> over-cover certifies `B_spec>=b` if and only if one of these `|H|` exact
> rational LPs has optimum `delta>0`; if `Bad_b` is empty, any over-cover
> certifies the threshold.  The coalition part of a successful certificate
> can be reduced to support at most `n` without changing
> `(eta,alpha,theta,delta)`.

#### Proof

For a fixed maximizing coordinate, all displayed constraints are linear
because `x` and every `E_J` are input rationals.  If `delta>0`, every bad
subset fails `(EJ)`, so every eligible subset has `B(J)>=b`; the spectral
anchor gives `O>=b`.  Conversely, if a certificate gives `O>=b` through the
spectral minimum, each of the finitely many bad subsets fails `(EJ)`
strictly.  Their minimum positive exclusion margin is a feasible `delta>0`
for a player attaining `max alpha`.  Finally, with `(eta,alpha)` fixed, the
incidence load `eta 1_N+alpha` lies in the cone generated by the supported
`z`-tight incidence vectors.  Conic Caratheodory in `R^n` retains at most `n`
of them.  QED.

This is an exact algorithm for a fixed game's optimized spectral certificate,
not a proof of `(SRE)`.  It is nevertheless the needed interface to the
rooted-circuit enumeration: an alleged residual game comes with a checkable
LP alternative saying precisely which bad spectral subsets survive every
Lmax normal.

The oracle in fact collapses to one scalar radius.  Define

```text
R_*(v)=max_(normalized over-covers) (alpha.x-mu)/theta. (RAD)
```

Put `u=alpha/theta`, `s=1/theta`, and scale `(lambda,eta)` by the same factor.
After choosing a top coordinate `r` with `u_r=1`, `(RAD)` is the exact LP

```text
maximize     u.x-mu s
subject to   sum_A lambda'_A 1_A=eta' 1_N+u,
             sum_(i in H)u_i=s,
             u_r=1,            0<=u_i<=1.
```

Thus no fractional or bilinear optimization remains.

> **Corollary (spectral-radius formula).**  For every fixed rational game,
>
> ```text
> B_spec(v)=min {B(J): |J|=|H| and
>                       sum_(j in J)(x_j-mu)>=R_*(v)}.  (RF)
> ```
>
> In particular, if
>
> ```text
> E_bad(b)=max {sum_(j in J)(x_j-mu): |J|=|H|, B(J)<b},
> ```
>
> with the maximum over an empty set omitted, then a sparse spectral
> certificate proves threshold `b` exactly when the bad set is empty or
> `R_*(v)>E_bad(b)`.

To prove `(RF)`, observe that `(EJ)` says precisely `E_J>=R(alpha)` for a
given certificate.  Increasing `R(alpha)` can only delete eligible subsets,
so the best spectral minimum is attained at the maximum radius.  The scaled
LP proves that the maximum is exact and attained.  The threshold criterion is
then immediate, including the strict inequality required to exclude a subset
with `B(J)<b`.

Consequently the label-free spectral method succeeds at the sharp threshold
exactly when

```text
R_*(v)>E_bad(nT/floor(n^2/4))                           (SRE-R)
```

whenever the bad family is nonempty.  Its left side is an exact sparse Lmax
incidence optimization and its right side is a finite statistic of the two
spectra.  The formula is correct, but the inequality is not universal: the
label-relaxation controls below refute it at seven players.

The verifier

```bash
python3 verifiers/divergence/audit_spectral_threshold_oracle.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json --n 6 \
  --output verifiers/divergence/spectral_threshold_oracle_audit.json
```

recomputes the two hostile controls.  At `n=7`, four below-target subsets are
all excluded by the one-coalition over-cover with exact margin `5/3`; the
radius is `R_*=5` while `E_bad=0`.  At `n=8`, `R_*=100/21` and `Bad_8` is
empty: even before using the over-cover eligibility filter, every spectral
matching exceeds the required floor.  These controls validate the oracle's
signs.  The same exact run covers `249` positive-floor pairs in the `374`-pair
six-player archive: `157` have no bad spectral subset, `92` have a nonempty
bad family, and all `92` satisfy `(SRE-R)`; the smallest positive radius gap
is exactly one.  These counts are finite regression evidence, not evidence
for all-`n` `(SRE)`.

### Exact boundary of every partial relabeling shortcut

The six-player archive suggested that optimized spectral relabeling might be
enough.  A targeted seven-player search found a two-generator exact game

```text
g=(0,0,3,17,0,9,1),       h=(14,4,0,0,12,0,0),
x=(25/4,3/2,3/2,37/4,21/4,21/4,1),
z=(64/9,32/9,2/9,64/9,19/3,49/9,2/9).
```

Exact staged incidence LPs certify both selections.  Here

```text
R_*=237/20,       B_spec=605/36<35/2,
O(x,z)=929/36>35/2.
```

The minimizing eligible subsets are `{3,4}` and `{3,5}`, with excess `25/2`.
They are hypothetical replacements for the actual Lmax top block `{0,3}`.
Keeping the actual top labels raises the rearrangement bound to `641/36`.
Thus `(SRE)` and `(SRE-R)` are false because the spectral minimum forgets
which Lmin coordinates actually carry the Lmax top normal.

Fixing the actual top block is still insufficient.  The exact game generated
by

```text
g=(18,17,0,0,1,0,0),       h=(0,0,24,10,0,1,1),
x=(9,8,19/2,8,1/2,1/2,1/2),
z=(9,17/2,9,17/2,1,0,0)
```

has actual-top-fixed rearrangement `39/2<21`, whereas its true overlap is
`69/2`.  Opposite sorting below the top block falsely assigns the two Lmax
zeros to rich Lmin coordinates; the staged labels assign them to floor
players.

Even fixing both Lmax extreme blocks is insufficient.  For

```text
g=(10,1,0,1,21,0,9),        h=(0,0,1,0,0,41,0),
x=(19/2,1/2,1/2,1/2,45/4,45/4,17/2),
z=(10,1,0,1,21/2,21/2,9),
```

the top-and-bottom-fixed middle rearrangement is `24<49/2`, while the true
overlap is `40`.

Reproduce exactness, core membership, all `42` staged rational certificate
LPs, every relaxation value, and every true overlap with

```bash
python3 verifiers/divergence/verify_n7_label_relaxation_obstructions.py \
  --output verifiers/divergence/n7_label_relaxation_obstructions.json
```

These examples do not threaten `(H)`; each has enormous positive slack.  They
prove a structural boundary: **no proof may freely permute any unprotected
Lmax strata.**  The full label-specific Lmin packet is not merely needed to
exclude a few bad top subsets.  It must be coupled directly to the actual
hybrid sign cut.

The last labels are essential and are not part of the ordinary exact cone.
There are two sharp obstructions to a stronger claim:

- the unrooted Lmin-selected atom is always decomposable, so it is never a
  facet (`paper3/ATOMIC_LMIN_OBSTRUCTION_REDUCTION.md`);
- rooting does not always make it indecomposable: the seven-player
  three-trace atom still decomposes, although it factors into two active
  indecomposable facets.

Accordingly the one-packet theory does **not** classify facets of the full
exact-game cone.  It gives a finite, dimension-free support reduction and an
algorithmic classification of a **relative rooted coupling cone**.  The
standard exact-cone facet catalogue can classify the factors after the Lmin
selection has produced them, but it cannot recover the staged selection
labels or prove hybrid overlap on its own.

## 8. The precise missing lemma

The first-stage aggregate pair is insufficient even at six players, by
`TWO_PACKET_EXACTIFICATION_BOUNDARY.md`.  The integral carrier theorem is
also false by Section 3.  A valid all-dimension bridge must use the complete
staged Lmin pinning data.

The minimal live target is therefore:

> **Fully labelled fractional-hinge coupling lemma.**  Put
> `A={i:z_i>x_i}`.  From one sparse Lmax top over-cover, the complete
> label-specific sign-coherent Lmin packet, and exactness witnesses, construct
> a nonnegative combination of their incidence and transport inequalities
> whose payoff side is
>
> ```text
> x(A)+z(N\A)>=nT/floor(n^2/4).                         (FLC)
> ```
>
> The construction must preserve the actual player labels in every Lmax
> stratum.  Large primitive packet coefficients must be charged against the
> same labelled over-cover loads, hinge surplus, or already-counted overlap;
> no residual group of coordinates may be oppositely rearranged.

Since `x(A)+z(N\A)=sum_i min(x_i,z_i)`, `(FLC)` is exactly `(H)`, not a
stronger label-free surrogate.  For a fixed sign pattern and fixed rooted
circuit supports, finding the combination is an exact rational LP; the
projected support theorem and the spectral-radius oracle make both sides
sparse.  The missing dimension-free theorem is existence of a feasible dual
combination for every exact labelled packet system.

### Theorem (complete fixed-n labelled alternative)

For every fixed `n`, the truth of `(H)` over singleton-normalized exact games
is decidable by finitely many exact rational linear programs.  More precisely,
exactly one of the following holds:

1. every combinatorial branch has a rational Farkas certificate either of
   infeasibility or, when feasible, proving `(FLC)` from its labelled
   staged-selection and exactness constraints; or
2. some branch has a rational model which lower-envelope exactification turns
   into a singleton-normalized exact game with the displayed `Lmin,Lmax` and
   strict violation of `(H)`.

Every staged-selection normal in the branch may be chosen as a rooted
positive circuit with at most `n` columns globally, or at most `n-|O_t|` in
the relative quotient.  Every Lmax top incidence load may likewise be
represented by at most `n` tight coalitions.

#### Exact algorithm

For fixed `n`:

1. enumerate ordered player partitions for the Lmin and Lmax strata and a
   hybrid sign cut `A`;
2. enumerate, for every player at every lexicographic stage, a conformal
   rooted circuit containing its forced signed unit column, retaining the
   actual player labels and its primitive rational coefficients;
3. introduce `x,z` and singleton-zero witnesses `w^1,...,w^n` of common total
   `T=1`;
4. for every coalition used by a selected Lmin (respectively Lmax) circuit,
   impose that `x` (respectively `z`) has no larger coalition sum than any of
   the other displayed generators; this is exactly tightness in the eventual
   lower envelope;
5. impose nonnegativity and common total, all selected stage-by-stage circuit
   identities, the stratum orders, the hybrid sign inequalities, and
   `w^i_i=0`;
6. maximize

   ```text
   n/floor(n^2/4)-x(A)-z(N\A).                         (V)
   ```

All rows are rational and linear after the finite combinatorial choices are
fixed.  Strict stratum and sign conditions are handled by maximizing a common
rational margin; boundary points occur in a coarser ordered partition.

#### Proof of completeness

Given a genuine counterexample, use its selections, singleton exactness
witnesses, ordered strata, and support-minimal staged certificates.  The
`n+2`-generator normal-form theorem in `CORE_CLOSURE_REDUCTION.md` assigns an
attaining displayed generator to every coalition and places the counterexample
in one enumerated branch.  Its strict overlap violation gives a positive
rational LP optimum after a sufficiently close rational choice in the same
polyhedral cell.

Conversely, a positive rational branch model defines

```text
v_G(S)=min{x(S),z(S),w^1(S),...,w^n(S)}.
```

Every displayed point lies in `Core(v_G)`, every coalition is attained, and
the zero witnesses give singleton normalization.  The retained primitive
circuit identities, one for every player at every stage, are the full Farkas
optimality certificates for the successive lexicographic programs.  Their
tight coalition inequalities therefore prove all stages of the two
selections after closure, so the model is an exact rational counterexample,
not merely a relaxation.

If no branch has positive optimum, rational Farkas duality supplies an
infeasibility certificate for every empty branch and a nonnegative row
combination proving `(FLC)` on every feasible branch.  Finitely many branches
cover the domain, proving `(H)`.  QED.

This theorem is a completeness and proof-object result, not a proposal to
make a large `n=7` census the research endpoint.  Its value is diagnostic: a
dimension-free proof must explain the recurring Farkas combination shared by
these finite branches, while any failed lemma can be challenged by extracting
one exact rational branch model.

The exact-cone relationship is now precise.  Rooted staged circuits classify
the **relative selection normals**.  When a lifted circuit has the published
indecomposable semi-balanced form, the Studeny--Kratochvil criterion identifies
it as a facet of the full exact-game cone and removes redundant exactness
rows.  Decomposable or multiply rooted selection circuits remain necessary
labels in the branch LP but must not be advertised as new exact-cone facets.

### Theorem (fully labelled branch-circuit dual)

Fix one **feasible** branch from the preceding algorithm, including all
ordered strata, the sign cut `A`, and one primitive staged circuit for each
player and stage.
Let

```text
Q=(x,z,w^1,...,w^n)
```

be the `(n+2)n` generator-coordinate vector.  In the affine subspace where
every generator has total one and `w^i_i=0`, form the following labelled row
system `R_B`:

1. `q^a(S)-x(S)>=0` for every Lmin-circuit coalition `S` and every generator
   `q^a` other than `x`;
2. `q^a(S)-z(S)>=0` for every Lmax-circuit coalition `S` and every generator
   `q^a` other than `z`;
3. generator-coordinate nonnegativity, the fixed Lmin/Lmax stratum orders,
   and the fixed inequalities `z_i-x_i>=0` on `A` and
   `x_i-z_i>=0` off `A`.

Equalities inside a stratum are put in the affine lineality space.  Write

```text
c_B(Q)=x(A)+z(N\A)-n/floor(n^2/4).
```

Then the branch implies `(FLC)` if and only if, modulo the affine equalities,
the affine functional `c_B` belongs to the nonnegative cone generated by
`R_B`.  Moreover every support-minimal proof of this implication is a
positive circuit of the augmented labelled row configuration

```text
R_B union {-c_B}
```

that contains `-c_B`.  If the affine dimension of the branch is `d_B`, such a
circuit uses at most `d_B+1` defining rows in addition to `-c_B`; in
particular `d_B<=n^2-2` before additional stratum equalities are counted.

#### Proof

Once the primitive staged circuits are fixed, their stationarity equations
contain no payoff variables.  The only payoff-dependent assertion needed to
reuse each circuit is that every coalition in its positive support is tight
at the selected generator.  In the finite lower-envelope normal form these
are exactly rows 1 and 2.  The remaining branch information is exactly row 3
and the stated affine equalities.  Thus the feasible generator tuples form a
rational polyhedron `P_B` cut out by `R_B` in that affine space.

The assertion `c_B(Q)>=0` on `P_B` is a linear implication.  Affine Farkas
duality says it holds exactly when `c_B` is a nonnegative combination of the
defining rows plus a linear combination of the affine equality rows.  After
homogenizing the constant coordinate, removing rows from a support-minimal
such combination gives a minimally dependent positive relation containing
`-c_B`; conversely every such positive circuit is an irreducible Farkas
proof.  Circuit support in a rank-`d_B+1` homogenized configuration is at
most `d_B+2`, giving the stated count after the target row is removed.

There are `(n+2)n` generator coordinates.  The `n+2` total equations and the
`n` distinct witness-zero equations are independent, leaving dimension
`n^2-2`; stratum equalities and any forced generator coincidences only lower
it.  QED.

This is the exact facet-enumeration interface supplied by the current work.
Enumerating positive circuits of the augmented configuration enumerates the
irreducible **fully labelled branch proofs**.  It does not by itself prove
that `c_B` belongs to the row cone for every branch and every `n`; that is the
dimension-free content still missing from `(FLC)`.

Nor are these circuits automatically facets of the exact-game cone.  Rows 1
and 2 live in separate labelled generator blocks, while stratum and hybrid
sign rows record selection data absent from an ordinary characteristic
function.  Only a projection or factor whose coalition coefficients form an
indecomposable semi-balanced system passes to a Studeny--Kratochvil
exact-cone facet.  The branch-circuit theorem therefore gives an exact
algorithm and a sharp relative notion of irreducibility without conflating
it with the published full-cone facet correspondence.

An infeasible branch instead has the usual positive circuit containing the
homogenized constant row `-1`.  Keeping these two circuit types separate
prevents a vacuous branch implication from being mistaken for a substantive
hybrid-overlap certificate.

### Theorem (one-witness threshold reduction)

Fix a genuine game, complete primitive staged circuits for its selections,
and a player `r`.  Let `w^r` be a core allocation with `w^r_r=0`.  Define the
three-generator relaxation `P_(B,r)` using only

```text
(x,z,w^r),
```

their three common-total equations, `w^r_r=0`, the actual stratum and hybrid
sign rows, and the following tightness comparisons:

```text
x(S)<=z(S),w^r(S)       (S in the selected Lmin supports),
z(S)<=x(S),w^r(S)       (S in the selected Lmax supports).              (OW)
```

If

```text
min_(P_(B,r)) {x(A)+z(N\A)} >= n/floor(n^2/4),          (OWC)
```

then the original game satisfies `(H)`.  Whenever `(OWC)` holds, it has an
exact rational fully labelled circuit certificate using at most `3n-3`
defining inequality rows in addition to the target row.

#### Proof

The actual triple `(x,z,w^r)` is feasible in `P_(B,r)`: every circuit-support
coalition is tight at its selected point, while the other two core points
have at least its game worth.  The objective is the actual hybrid overlap,
so `(OWC)` proves `(H)`.

The triple has `3n` coordinates.  Its three total equations and one witness
zero equation are independent, leaving affine dimension at most `3n-4`;
stratum equalities only lower it.  Apply the fully labelled branch-circuit
dual theorem in this affine space.  A target-containing positive circuit has
at most `3n-2` total rows, hence at most `3n-3` defining rows besides the
target.  QED.

#### Rooted two-tangent form

The reduction has a useful human formulation.  Put

```text
a=w^r-x,                 b=w^r-z.                       (RT)
```

Then

```text
a(N)=b(N)=0,
a(S)>=0                  on every selected x-tight support,
b(S)>=0                  on every selected z-tight support,
a_r=-x_r<=0,             b_r=-z_r<=0.                  (RTC)
```

Moreover `a-b=z-x`, so the actual hybrid cut is

```text
A={i:a_i>b_i}.
```

Coordinatewise,

```text
min(x_i,z_i)=w^r_i-max(a_i,b_i).
```

Summing gives the exact identity

```text
1-O(x,z)=sum_i max(a_i,b_i)
        =a(A)+b(N\A).                                  (RTD)
```

Thus `(OWC)` is equivalently the following rooted two-tangent budget:

```text
sum_i max(a_i,b_i) <= 1-n/floor(n^2/4).                (RTB)
```

The common witness is not an auxiliary exactness nuisance: it is the common
apex from which the two selection tangents are measured.  The support rows in
`(RTC)` are precisely the nonnegative coalition slacks of those tangents, and
the witness zero gives their shared negative root.  The Lmin/Lmax stratum rows
orient `a-b`, preventing the relabelings that invalidated `(SRE)`.

This also states the exact interface with rooted deficit completion.  On each
selected protector/deficit subpacket, its `w^r`-slacks are the corresponding
coordinates of `a` or `b`.  The two
applications must retain their common root and the labelwise maximum in
`(RTD)`.  What remains to be proved is that suitable rooted subpacket budgets
can be coupled so their shared charge is at most the right side of `(RTB)`.
Proving that shared-charge inequality would establish `(OWC)`; dropping the
common root or replacing the maximum by separate total congestion recovers
the already refuted relaxations.

This changes the most promising missing statement.  It is sufficient to
prove:

> **One-witness threshold conjecture.**  For every feasible fully labelled
> selection branch, some singleton root `r` satisfies `(OWC)`.

Equivalently, if

```text
B_B(r)=min_(P_(B,r)) {x(A)+z(N\A)},
```

the desired root-selection theorem is

```text
max_(r in N) B_B(r) >= n/floor(n^2/4).                 (RSEL)
```

Each `B_B(r)` is an exact rational LP in only `3n` variables, and a successful
root has a target certificate of linear support by the theorem above.

Unlike target-count congestion, this conjecture does not bound primitive
packet coefficients.  Unlike spectral or rearrangement bridges, it never
forgets a player label.  Unlike the full `(n+2)`-generator alternative, it
would give a linear-support target certificate and a genuinely rooted
incidence object.  Its one witness supplies the distinguished root needed for
a possible indecomposable semi-balanced factor, although the
Studeny--Kratochvil test would still be required after projection.

Five exact hostile branches now pass this stronger relaxation:

| source obstruction | `n` | full branch minimum | weakest one-witness minimum | target |
|---|---:|---:|---:|---:|
| optimized label-free spectral failure | 7 | `3/4` | `25/34` | `7/12` |
| actual-top-fixed failure | 7 | `7/10` | `7/10` | `7/12` |
| top-and-bottom-fixed failure | 7 | `2/3` | `2/3` | `7/12` |
| coefficient-two congestion failure | 7 | `9/11` | `16/25` | `7/12` |
| primitive coefficient-seven circuit | 8 | `34/39` | `11/19` | `1/2` |

Here "weakest" means the minimum over **every** choice of root `r`; thus all
available roots pass in these five branches, not merely a favorably selected
one.  Exact full-branch minimizers lower-envelope exactify and retain all
staged selections.  Exact dual coefficient identities certify their optima.
The one-witness numbers are minima of larger three-generator relaxations and
are used only as sufficient bounds, not advertised as exact games.

The equality family supplies the sharper root-selection test:

| balanced `G(p,k)` | distinguished head root `0` | every non-head root | target |
|---|---:|---:|---:|
| `(p,k)=(2,4)` | `7/12` | `7/15` | `7/12` |
| `(p,k)=(3,3)` | `7/12` | `7/16` | `7/12` |

Thus the stronger statement that every root works is false, even on the
sharp family.  The surviving existential conjecture selects exactly player
`0`, the common exceptional root of the active block-star facets `(R_b)`.
This is a structural, not numerical, indication of how the exact-cone side
must choose the singleton witness: the appropriate root is the exceptional
coalition shared by the indecomposable rooted factors.  With that root the
one-witness relaxation is sharp, so the reduction specializes correctly to
both balanced seven-player extremizers.

In fact the specialization is dimension-free over the entire master family.

> **Theorem (common-hinge one-witness sharpness).**  Normalize `G(p,k)` to
> total one.  In the stratum/sign branch of its displayed selections, retain
> only the `k` common hinge supports `C_b`, and choose the head-zero witness
> `w^0=h/T`.  The resulting one-witness relaxation has exact minimum
>
> ```text
> 1/k+1/(p+1)=n/[k(p+1)].                              (OWG)
> ```

#### Proof

Write the normalized Lmin strata as `(X,q,...,q)`, and write the Lmax high
and low levels as `M,l`; its high block is `{0} union B` and its low block is
`O`.  Since `w^0_0=0`, nonnegativity and total one give `w^0(B)<=1`.  Summing
the `k` Lmin hinge comparisons gives

```text
k[X+(k-1)q]
 <=sum_b w^0(C_b)=(k-1)w^0(B)<=k-1.
```

Using `X+(p+k)q=1` therefore yields

```text
(p+1)q>=1/k.                                           (Gq)
```

The same sum on the Lmax side gives

```text
k^2 M<=k-1.                                            (GM)
```

The hybrid sign cut assigns the head and `O` to `z`, and `B` to `x`.  Since
`(k+1)M+pl=1`, its overlap objective is

```text
M+pl+kq=1-kM+kq
          >=1/k+1/(p+1).                               (GO)
```

The displayed normalized `x,z` and `w^0=h/T` attain equality in every hinge
comparison and in `(Gq)--(GO)`.  Thus the relaxation minimum is exact.  QED.

This proof uses exactly the exceptional head root shared by all block-star
facets `(R_b)`.  Choosing a non-head zero witness destroys the summed-hinge
identity at the required constant, matching the failed `7/15` and `7/16`
relaxations above.  The distinguished-facet root is therefore necessary even
inside the sharp family, not merely a convenient normalization.

### Theorem (one-common-hinge mixed block-star bound)

The full common-hinge hypothesis in `(OWG)` can be weakened to one common
hinge, provided the complete Lmin star and its actual labels are retained.
Let

```text
N={r} disjoint-union O disjoint-union B,
|O|=p>=1,       |B|=k>=2,       n=p+k+1,
```

choose `b_0 in B` and `j in B\{b_0}`, and put
`C_b={r} union (B\{b})`.  Suppose `x,z,w` have common total `T`, `w>=0`,
`w_r=0`, and the labelled branch has

```text
x_r=c,
x_b=b                         (b in B\{b_0}),
x_i=a                         (i in O union {b_0}),
0<=a<=b<=c,                                             (MBS1)

z_r=z_b=A                     (b in B\{b_0}),
z_(b_0)=B_0,                  z(O)=L,                  (MBS2)
```

where `z(O)` denotes the sum over `O`.  Assume the hybrid sign cut assigns
`B` to `x` and `{r} union O` to `z`, and retain only

```text
x(C_b)<=w(C_b)                (b in B),
z(C_j)<=x(C_j).                                        (MBS3)
```

Then

```text
O(x,z)>=nT/[k(p+1)]>=nT/floor(n^2/4).                 (MBS4)
```

#### Proof

Sum the `k` witness comparisons.  Every block player occurs `k-1` times,
while `w_r=0` and `w(B)<=T`, so

```text
k c+(k-1)[(k-1)b+a]<=(k-1)T.
```

Subtract `(k-1)` times

```text
T=c+(k-1)b+(p+1)a
```

to obtain

```text
c<=p(k-1)a.                                           (MBS5)
```

Put `P=p(k-1)` and `D=k(p+1)`.  Direct expansion gives the nonnegative
identity

```text
(P-1)T-D(c-b)
 =[kP+p+1](b-a)+n(Pa-c)>=0.                           (MBS6)
```

Hence `c-b<=(P-1)T/D`.  On the Lmax side,

```text
T=kA+B_0+L,
z(C_j)=(k-1)A+B_0<=c+(k-2)b+a=x(C_j).
```

The fixed hybrid cut therefore has

```text
O=A+L+(k-1)b+a
 =T-[(k-1)A+B_0-(k-1)b-a]
 >=T-(c-b)
 >=[D-P+1]T/D=nT/D.
```

Finally the positive integers `k` and `p+1` sum to `n`, so
`D=k(p+1)<=floor(n^2/4)`.  QED.

### Theorem (tied-ceiling two-spoke repair)

There is a second dimension-free repair pattern, and it does not require a
strict over-cover leader.  Let

```text
N={r,u,j} disjoint-union Q,       |Q|=m>=1,       n=m+3,
```

and let nonnegative `x,z,w` have common total `T`, with `w_r=0`.  Suppose

```text
x_r=c,          x_u=x_j=b,        x_q<=b          (q in Q),
z_r=z_u=z_j=A,  z_q<=x_q          (q in Q),
b<=A<=c,                                                (TCS1)
```

and retain the two rooted spokes and one reverse common-pair comparison

```text
x({r,u})<=w({r,u}),   x({r,j})<=w({r,j}),
z({r,j})<=x({r,j}).                                  (TCS2)
```

Then

```text
O(x,z)/T>=n/[2(n-2)]>=n/floor(n^2/4).                (TCS3)
```

#### Proof

Put `X_Q=x(Q)`.  The two witness rows and `w_r=0` give

```text
2(c+b)<=w_u+w_j<=T=c+2b+X_Q,
```

so `X_Q>=c`; the Lmin order in `(TCS1)` also gives `c<=X_Q<=mb`.
The reverse common pair gives `2A<=c+b`.  On the displayed sign branch,

```text
O=A+2b+z(Q)=T-2A+2b>=T-(c-b).                        (TCS4)
```

More sharply, the entire bound is the exact three-slack identity

```text
O-[m+3]/[2(m+1)] T
 =[c+b-2A]
  +2[mb-c]/(m+1)
  +(m-1)[T-2(c+b)]/[2(m+1)] >=0.                     (TCS5)
```

Since `floor(n^2/4)>=2(n-2)` for every `n>=4`, `(TCS3)` follows.  QED.

The exact-cone mechanism is not new notation for the same arithmetic.  In
`K_r`, put unit weight on the two rooted spokes.  Then

```text
delta=1,       q_q=1 (q in Q),       q_u=q_j=0,
```

and its rooted pair lift is

```text
1_{r,u}+1_{r,j}+sum_(q in Q)1_{r,q}-(m+1)e_r=1_N.    (TCSF)
```

This is exactly `(GPL)` with `k=2` and `p=m`.  The dimension-free
sharp-family facet theorem therefore proves that `(TCSF)` is an
indecomposable purely min-semi-balanced system and a facet of the exact-game
cone.  Thus the two-spoke repair is the smallest block-star facet coupled to
one reverse Lmax comparison, rather than an unrelated branch inequality.

This theorem humanly closes the tied-repair templates
`harvest6_601.json $.records[103]` and
`harvest6_602.json $.records[129]`.  Their actual normalized overlaps are
`15/16` and `11/14`; the branch theorem supplies the uniform `3/4` floor.
The irregular `harvest6_602.json $.records[82]` template does not have this
two-spoke form.  This is a branch reduction, not an assertion that every
all-dimensional residual has two rooted spokes.

Reproduce the symbolic identity, 217,175 exact parameter controls through
dimension 20, and both archived mappings with

```bash
python3 verifiers/divergence/verify_tied_ceiling_two_spoke_repair.py \
  --output verifiers/divergence/tied_ceiling_two_spoke_repair.json
```

### Theorem (six-player three-packet repair)

The last common-hinge repair template has a different but still human
certificate.  Let

```text
N={r,u,g,j,l_1,l_2},
x=(c,b,a,a,a,a)              on (r,u,l_1,l_2,g,j),
z_r=z_u=z_g=A,   z_j=D,      z_l_1=z_l_2=E,
0<=E<=a<=D,       a<=b<=A<=c.                         (TP1)
```

Let `w>=0` have total `T=x(N)=z(N)` and `w_r=0`.  Suppose the complete Lmin
packet supplies

```text
x({r,u,g,l_2})<=w({r,u,g,l_2}),
x({r,u,j})<=w({r,u,j}),
x({r,g,j})<=w({r,g,j}),                                (TP2)
```

and the common-hinge reverse comparison is

```text
z({r,u,j})<=x({r,u,j}).                                (TP3)
```

Then `O(x,z)>=2T/3`.

#### Proof

Summing `(TP2)`, every off-root witness coordinate has load at most two, so

```text
3c+2b+5a<=2T=2c+2b+8a,
```

and hence `c<=3a`.  Put
`h=c+b+a-2A-D>=0`, the slack in `(TP3)`.  On the displayed sign branch,
`T=3A+D+2E` and `O=A+b+2a+2E`, so exact cancellation gives

```text
O-(2/3)T = h+(a+b)/3+(2/3)(3a-c)>=0.                  (TP4)
```

QED.

This proves the `harvest6_602.json $.records[82]` repair row, whose actual
overlap is `7/9`.  Together with the two-spoke theorem, all three common-
hinge repair templates isolated by the sequential census now have human
proofs.  What remains open is the structural selection theorem forcing an
arbitrary residual into the Lmin-root-price or repair branches.

This repair is also carried by a genuine exact-cone facet.  Normalize the
three witness rows in `(TP2)` with weight `1/2`.  Their nonroot loads are one
on `u,g,j`, one half on `l_2`, and zero on `l_1`; the root load is `3/2`.
The rooted pair lift, after multiplying by two, is

```text
1_{r,u,g,l_2}+1_{r,u,j}+1_{r,g,j}
 +1_{r,l_2}+2 1_{r,l_1}-4e_r=2 1_N.                 (TPF)
```

Its six support columns have rank six.  The Studeny--Kratochvil
exceptional-set test is closed-form here.  For a candidate coalition `E`
with indicators `(e_r,e_u,e_1,e_2,e_g,e_j)`, the unique support weights are
nonnegative for some common load `rho` exactly when

```text
L(E)<=rho<=U(E),
L(E)=max{-e_u-e_g+e_j, -e_u-e_j+e_g,
         -e_g-e_j+e_u, -2e_2+e_u+e_g-e_j, -e_1},
U(E)=(e_r-e_j-e_2-e_1)/2.                            (TPE)
```

Checking the binary indicators in `(TPE)` leaves only

```text
{r}, {r,l_1}, {r,l_2}, {r,u,g,l_2}, {r,u,j},
{r,g,j}, N.
```

Every proper set in this list is already in the support of `(TPF)`.  Hence
there is no new proper exceptional coalition; `(TPF)` is indecomposable and
defines a facet of the exact-game cone.  This proof uses exactly the
published exceptional-set criterion, not an unsat-core inference.

```bash
python3 verifiers/divergence/verify_n6_three_packet_repair.py \
  --output verifiers/divergence/n6_three_packet_repair.json

PYTHONPATH=verifiers/divergence /tmp/coop-paper5-review/bin/python \
  verifiers/divergence/verify_n6_three_packet_facet_z3.py \
  --output verifiers/divergence/n6_three_packet_facet_z3.json
```

The proof isolates a more general exact-cone price criterion.  Suppose a
labelled branch has one root at `c`, exactly `g` players at `b`, and exactly
`m` players at `a`, so `n=1+g+m`, and its cross row still gives
`O>=T-(c-b)`.  If a rooted pair-lift `(PFRDBx)` has root excess `delta>0`,
all deficit weights supported on the `a`-level loss players, and total
deficit weight `Q`, then nonnegativity of the pair premiums gives

```text
c<=(Q/delta)a=:P a.                                  (MFP1)
```

With `D_P=P+n-1`, the exact identity is

```text
(P-1)T-D_P(c-b)
 =[g(P-1)+D_P](b-a)+n(Pa-c)>=0.                       (MFP2)
```

Therefore

```text
O/T>=n/(P+n-1).                                       (MFP3)
```

In particular the rooted facet proves the universal target whenever

```text
P=Q/delta<=floor(n^2/4)-n+1.                          (MFP4)
```

This gives a scalar meaning to the rooted exact-cone coefficients: `Q/delta`
is the **effective facet price** paid by the lower loss block for one unit of
exceptional-root load.  For the block-star lift, `Q=p`,
`delta=1/(k-1)`, and `P=p(k-1)`, so `(MFP3)` is exactly `(MBS4)`.

There is a useful reserve version.  Let the displayed root, `g` middle
players, and `m` low players form only a structured subset `U` of size
`n_0=1+g+m`; allow every player outside `U` to be a nongainer.  Let the full
gain set consist of the `g` middle players and one low player, and suppose a
mixed cross row proves

```text
z(G)-x(G)<=c-b.                                       (MFR1)
```

The same identity applies to `T_U=x(U)<=T`, while
`O=T-[z(G)-x(G)]`.  Hence

```text
O/T>=n_0/(P+n_0-1).                                  (MFR2)
```

If `T_U=0`, the cross row gives `O=T` directly; otherwise
`c>=b>=a` and `c<=Pa` force `P>=1`, as used in the division.

It reaches the `n`-player target whenever

```text
P<=n_0 floor(n^2/4)/n-n_0+1.                         (MFR3)
```

Thus extra nongaining strata are a literal overlap reserve: they need not be
forced into the three-level block.  The two independent tasks in a general
branch are now explicit: find a low-loss-supported rooted facet of affordable
price `P`, and find one mixed row paying the total gain by `c-b`.

The failure of first-floor alignment has an exact price.  For an arbitrary
rooted pair lift define

```text
e_q=max(0, [sum_i q_i(x_i-a)-sum_i q_i v({r,i})]/delta). (MPE1)
```

Then `(PFRDBx)` gives `c<=Pa+e_q`.  Replacing `Pa-c` by
`Pa+e_q-c-e_q` in `(MFP2)` proves

```text
O/T>=n/(P+n-1)-n e_q/[(P+n-1)T].                     (MPE2)
```

For a reserve subset of size `n_0`, the same proof gives

```text
O/T>=n_0(T-e_q)/[(P+n_0-1)T].                        (MPE3)
```

Thus the missing multistage theorem has a numerical target: label, spectral,
or reserve currency must pay exactly the `e_q` term (or the pre-existing
denominator margin must absorb it).  When the full structured dimension is
`n` and `F=floor(n^2/4)`, `(MPE2)` reaches `(H)` whenever

```text
e_q/T<=1-(P+n-1)/F.                                  (MPE4)
```

This penalty is zero in every first-floor-aligned cut; nonnegative pair
premiums can only reduce it.

All nine extreme mixed-projection cuts in the hostile/sharp control suite
have effective price at most their dimensional threshold (`6` at `n=7`,
`9` at `n=8`).  This finite fact does not prove their required stratum/sign
alignment: eight of the nine have every deficit on a nongaining player, but
only five put every deficit on the first Lmin floor.  It shows that
coefficient size itself is not the remaining obstruction; the four
non-floor-aligned cuts require a genuinely multistage price theorem.

Equality at the universal target requires the balanced product
`k(p+1)=floor(n^2/4)`, equality in the cross-hinge row, and

```text
b=a,             c=p(k-1)a,             a=T/[k(p+1)]. (MBS7)
```

It also forces equality in the summed witness packet, hence `w(B)=T`.
These conditions recover the sharp Lmin and root-zero witness of `G(p,k)`;
the displayed sharp Lmax point is one realization, but `(MBS1)--(MBS3)`
alone need not make its remaining levels unique.

This is a genuinely mixed packet theorem.  Only `C_j` must be tight at both
selections; the other `k-1` star hinges need only be Lmin-tight and compared
to the root-zero witness.  Eliminating the witness's outside nonnegativity
columns produces the same rooted pair-spoke shear `(GPL)`.  Thus its
support-minimal exact-cone factor is the already classified indecomposable
block-star facet, even though the labelled proof uses two colours.

The theorem was exposed by a new three-generator seven-player exact control:

```text
g=(2,4,0,16,2,0,0),
h=(0,8,5,0,0,8,3),
k=(1,0,7,8,0,3,5),                                   (MBS8)
```

all of total `24`.  Its exact selections are

```text
x=(2,4,4,6,2,4,2),
z=(7/4,9/2,9/2,9/2,7/4,9/2,5/2),                    (MBS9)
```

with actual overlap `22=11T/12` and unique maximum-overlap root `r=3`.
Nevertheless its full rooted one-witness relaxation has exact optimum
`7/12`.  The minimizing relaxation point is precisely the normalized
`G(2,4)` sharp triple.  Fourteen explicit staged incidence identities certify
the displayed selections, and a hard-coded rational primal/dual identity
certifies the rooted optimum without invoking an optimizer.  This is a sharp
branch boundary, not a new extremal game and not a proof of universal root
selection.

Reproduce with

```bash
python3 verifiers/divergence/verify_mixed_block_star_boundary.py \
  --output verifiers/divergence/mixed_block_star_boundary.json
```

### Maximum-overlap root candidate

The tangent identity gives a payoff-visible candidate for the distinguished
root.  At a witness zero,

```text
max(a_r,b_r)=max(-x_r,-z_r)=-min(x_r,z_r).              (RC)
```

Thus a player maximizing its coordinatewise overlap supplies the largest
available negative root credit in `(RTD)`.  This suggests the stronger live
form of `(RSEL)`:

> **Theorem (ceiling root and root deletion).**  Let `H` be the Lmax top
> block, with common value `M`, and let
>
> ```text
> sum_S lambda_S 1_S=eta 1_N+alpha
> ```
>
> be any normalized Lmax over-cover.  Then some `r in H` satisfies
>
> ```text
> x_r>=M,             min(x_r,z_r)=M=max_i min(x_i,z_i). (CR)
> ```
>
> For every such `r`, every singleton witness `w^r` with `w^r_r=0` satisfies
>
> ```text
> M<=theta_(-r) T,       theta_(-r):=max_(i!=r) alpha_i. (RD)
> ```

#### Proof

The hinge-surplus identity gives `alpha.x=M+epsilon_+>=M`.  Since `alpha` is
a probability supported on `H`, some `r in H` has `x_r>=M`.  At that player
`z_r=M`, while `z_i<=M` everywhere, proving `(CR)`.

Every supported coalition is `z`-tight and `w^r` is a core point, so

```text
0<=sum_S lambda_S[w^r(S)-z(S)]
  =alpha.w^r-alpha.z=alpha.w^r-M.
```

Because `w^r>=0`, `w^r(N)=T`, and `w^r_r=0`,

```text
alpha.w^r<=theta_(-r) sum_(i!=r)w^r_i=theta_(-r)T.
```

This proves `(RD)`.  QED.

The theorem makes the root canonical up to the nonempty set

```text
R_M={r in H:x_r>=M}=argmax_i min(x_i,z_i).              (CRM)
```

### Theorem (ceiling-root interpolation floor)

Put `mu=min_i x_i>0`.  Every ceiling root `r in R_M` gives the
dimension-free lower bound

```text
O(x,z)>=M-mu+T mu/M.                                  (CRI)
```

Indeed, at the root `min(x_r,z_r)=M`.  Off the root, `x_i>=mu` and
`0<=z_i<=M`, so

```text
min(x_i,z_i)>=min(mu,z_i)>=(mu/M)z_i.
```

Summing and using `sum_(i!=r)z_i=T-M` proves `(CRI)`.  In normalized
variables `t=M/T` and `u=mu/T`,

```text
O/T>=t-u+u/t.                                         (CRIN)
```

Consequently the target `O/T>=c_n` is automatic if `t>=c_n`; when `t<c_n`
it is automatic if

```text
u>=t(c_n-t)/(1-t).                                    (CRIW)
```

Thus a remaining positive-floor counterexample must lie in the explicit
wedge

```text
1/n<=t<c_n,       0<u<t(c_n-t)/(1-t).                 (CRIX)
```

For seven players this reads `1/7<=M/T<7/12` and

```text
mu/T < (M/T)(7/12-M/T)/(1-M/T).
```

The inequality also has a rigid equality pattern.  If `0<mu<M`, equality in
`(CRI)` forces every nonroot `z_i` to lie in `{0,M}`, and every nonroot top
player to have `x_i=mu`.  Hence `T=qM` for the integer top-block size `q`.
This explains why the bound is generically strict, but it does not replace
the rooted packet facets: on the sharp seven-player orientations `G(2,4)`
and `G(3,3)`, its normalized values are respectively `79/144` and `37/72`,
both strictly below `7/12`.  The facet rows supply the missing charge.

The exact audit below verifies `(CRI)` on all eight archived hard controls
and three rational equality patterns.  It closes none of the eight hard
controls by itself, so it is a parameter-space reduction rather than the
open hybrid theorem.

```bash
python3 verifiers/divergence/verify_ceiling_root_interpolation.py \
  --output verifiers/divergence/ceiling_root_interpolation.json
```

It also couples root choice directly to the sparse over-cover: deleting a
large load `alpha_r` replaces the global dispersion by the largest surviving
load.  For `G(p,k)`, the exceptional head has `alpha_0=1/k` and every
surviving block load is `(k-1)/k^2`; `(RD)` is exactly `(GM)`.  The remaining
dimension-free task is to couple this deleted-load ceiling bound to the
complete rooted Lmin packet and recover the complementary `q`-type term.

The best deleted-load certificate is itself an exact sparse oracle.  For
`r in R_M`, define `theta^del_r` by the rational LP

```text
minimize theta
subject to sum_S lambda_S 1_S=eta 1_N+alpha,
           sum_(i in H)alpha_i=1,
           alpha_i<=theta              (i in H\{r}),
           lambda,eta,alpha,theta>=0,
```

with `lambda` supported on the `z`-tight coalitions.  Then

```text
M/T<=theta^del_r,                                        (RDO)
```

the optimum is rational and attained for rational input, and its coalition
support may be reduced to at most `n` without changing
`(eta,alpha,theta)`.  Indeed `(RD)` proves the lower bound for every feasible
certificate.  Rational LP duality gives attainment, and conic Caratheodory in
`R^n` gives the support reduction.  For `G(p,k)` at the head root,

```text
theta^del_0=(k-1)/k^2=M/T.
```

Thus the sparse Lmax side of the proposed proof is now an exact root-indexed
quantity.  The missing Lmin theorem can be stated without ambiguity: for at
least one ceiling root `r`, its complete staged packet must contribute the
complementary overlap needed beyond the root-deleted ceiling `(RDO)`.

This suggests the stronger live form of `(RSEL)`:

> **Maximum-overlap root conjecture.**  For
> `R=argmax_i min(x_i,z_i)`, every feasible labelled selection system has
> some `r in R` with
>
> ```text
> B_B(r)>=n/floor(n^2/4).                              (MOR)
> ```

The two sharp-family orientations select their unique head in exactly this
way.  A targeted audit of all five archived six-player equality records gives

| record | root bounds | maximum-overlap roots | passing roots |
|---|---|---|---|
| `601[37]` | `(2/3,1/2,1/2,1/2,1/2,1/2)` | `{0}` | `{0}` |
| `601[108]` | `(1/2,1/2,1/2,1/2,2/3,1/2)` | `{4}` | `{4}` |
| `601[125]` | all `2/3` | `{0,4}` | all |
| `602[168]` | all `2/3` | `{1,4}` | all |
| `602[170]` | all `2/3` | `{4,5}` | all |

So `(MOR)` selects the unique successful root in both rigid equality records
and remains valid in the three degenerate ones.  Together with the two sharp
orientations and five hostile branches, it has survived twelve deliberately
hard fixed supports.  This is still finite branch evidence, not a proof, and
the extracted basic staged circuits are one choice among potentially several.

Reproduce the complete staged support extraction and all thirty exact rooted
LPs with

```bash
python3 verifiers/divergence/audit_n6_equality_one_witness_roots.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/n6_equality_one_witness_roots.json
```

A broader exact regression audit then tested every maximum-overlap root in
all `374` archived six-player pairs: `703` exact rooted LPs, no failure, and
minimum bound exactly `2/3`.  Forty records have at least one root attaining
the floor, while in `108` records every tested root relaxation reproduces the
actual overlap.  Reproduce it with

```bash
python3 verifiers/divergence/audit_n6_maximum_overlap_roots.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/n6_maximum_overlap_roots.json
```

This larger run still fixes one extracted basic staged-support system per
record and covers only an archive.  It is a regression and falsification
result, not evidence that the six-player domain, much less all dimensions,
has been exhausted.

### Common-hinge premise reduction

The complete Lmax staged packet is not needed in the archived root tests.
More sharply, even the **z-only** part of a sparse first-stage Lmax
over-cover can be discarded.  Let `C_x` be the union of one complete staged
Lmin support, let `C_z` be the support of one sparse Lmax top over-cover, and
put

```text
C_cap=C_x intersect C_z.                              (CHI)
```

> **Theorem (common-hinge one-witness reduction).**  Fix a player `r` and
> retain the usual common-total, nonnegativity, witness-zero, stratum, and
> hybrid-sign rows for `(x,z,w^r)`.  Impose
>
> ```text
> x(S)<=z(S),w^r(S)                 (S in C_x),
> z(S)<=x(S),w^r(S)                 (S in C_cap),       (CHW)
> ```
>
> but impose no Lmax tightness comparison for `S in C_z\C_x`.  If the
> minimum hybrid overlap in this relaxation is at least
> `n/floor(n^2/4)`, then the original game satisfies `(H)`.  A
> support-minimal proof uses at most `3n-3` defining inequality rows besides
> the target.  Moreover `|C_cap|<=n` after sparse reduction of the selected
> over-cover.

#### Proof

Every coalition in `C_x` is tight at `x`, and every coalition in `C_cap` is
tight at both `x` and `z`.  The actual triple `(x,z,w^r)` therefore satisfies
`(CHW)`, so a lower bound on this larger relaxation bounds its actual hybrid
overlap.  Its affine ambient space is the same `3n-4` dimensional space as in
the one-witness threshold theorem, hence the same affine-Farkas circuit bound
applies.  Finally `C_cap` is a subset of the support of a sparse Lmax
over-cover, whose support has at most `n` coalitions.  QED.

On a common coalition, `(CHW)` says exactly

```text
x(S)=z(S)<=w^r(S),
a(S)=b(S)>=0.                                         (CHE)
```

Thus the only surviving Lmax rows **glue the two rooted tangents on common
tight coalitions**.  All other coalition-slack information comes from the
complete Lmin packet.  This is a smaller structural interface than `(OW)`:
the ceiling over-cover selects at most `n` possible gluing coalitions, and
the complete Lmin packet decides which of them actually transmit charge.

### Theorem (exact rooted-hinge witness projection)

The common singleton witness can be eliminated without losing its shared
root geometry.  Fix a root `r`, let `C_x` be the selected complete Lmin
support, and let `C_cap` be the common-hinge support.  Retain the direct rows

```text
x(S)<=z(S)                 (S in C_x),
z(S)<=x(S)                 (S in C_cap).               (RHP0)
```

On `C_cap`, `(RHP0)` already gives `x(S)=z(S)`, so the `z`-to-witness rows
are duplicates of the `x`-to-witness rows.  Therefore a nonnegative total-`T`
witness `w` with `w_r=0` and

```text
x(S)<=w(S)                 (S in C_x)                  (RHP1)
```

exists if and only if, for every weight family `u in R_+^(C_x)`, one has

```text
sum_(S in C_x)u_S x(S)
 <=T max_(i != r)
   sum_(S in C_x:i in S)u_S.                          (RHP2)
```

After normalizing the maximum load to at most one, it suffices to impose
`(RHP2)` at the extreme points of the rooted fractional packing polytope

```text
K_r={u>=0:
     sum_(S in C_x:i in S)u_S<=1
     for every i != r}.                                (RHP3)
```

Every extreme packing has at most `n-1` positive weights.  Thus eliminating
the witness replaces it by a finite family of rational inequalities with a
linear support bound.  If no selected coalition is contained in `{r}`, then
`K_r` is bounded; otherwise its extreme rays supply the corresponding
zero-right-hand-side inequalities.

#### Proof

Necessity follows by weighting `(RHP1)`.  If
`p_i=sum_(S:i in S)u_S`, then

```text
sum_S u_S x(S)<=p.w
 <=T max_(i != r)p_i,
```

because `w>=0`, `w(N)=T`, and `w_r=0`.

For sufficiency, the set of requirement vectors dominated by some
`(w(S))_(S in C_x)` with `w` in the rooted simplex is a closed convex
down-set.  If the vector of `x`-requirements lies outside it, strict
separation from a down-set has a nonnegative normal `u`.  The support
function of the rooted simplex in that direction is exactly
`T max_(i != r)p_i`, contradicting `(RHP2)`.

The normalized inequalities are precisely the points of `(RHP3)`, so its
vertices and rays suffice.  At a vertex, the columns indexed by positive
weights must be linearly independent on the at most `n-1` nonroot capacity
rows; otherwise a support-preserving perturbation contradicts extremality.
This proves the support bound.  Rationality and finiteness follow from the
rational packing matrix.  QED.

This is the non-tautological packing object that the label-rectangle route
was missing.  Its capacities live on **players excluding the root**, not on
payoff thresholds.  The complete Lmin support determines the packing; the
sparse Lmax over-cover determines the diagonal gluing rows `x(S)=z(S)` on
`C_cap`.  On the sharp family, one extreme packing is the uniform sum of the
`k` block-star hinges.  Formula `(RHP2)`, transferred across those gluing
rows, gives both `(Gq)` and `(GM)` exactly, hence the sharp hybrid-overlap
bound.

### Corollary (root-deficit balance)

For `u in K_r`, let `p_i=sum_(S:i in S)u_S`, put

```text
delta=p_r-1,                 q_i=1-p_i>=0  (i != r).
```

Then `(RHP2)` is exactly

```text
delta x_r<=sum_(i != r)q_i x_i.                       (RDBx)
```

If every coalition with `u_S>0` is a common hinge, then the gluing equalities
give the mirror inequality

```text
delta z_r<=sum_(i != r)q_i z_i.                       (RDBz)
```

Thus any packing with `delta>0` converts the shared negative root into an
explicit nonroot deficit budget.  Equality requires the witness mass to be
supported only on players whose packing load is one (besides its forced zero
at `r`) and every positively weighted coalition comparison to be tight.

For `G(p,k)`, the normalized uniform block-star packing has

```text
delta=1/(k-1),
q_i=0 on B,                  q_i=1 on O.
```

Consequently `(RDBx)--(RDBz)` are precisely
`X<=p(k-1)q` and `M<=p(k-1)l`.  Combining each with efficiency gives `(Gq)`
and `(GM)`.  This is the human structural explanation of why the exceptional
head, the `k` common hinges, and the `p` outside players produce the sharp
constant.

For later use, the definitions of `p,q,delta` give the coordinate identity

```text
sum_S u_S 1_S
 +sum_(i != r)q_i e_i-delta e_r=1_N.                 (RMS)
```

### Theorem (pair-floor rooted projection)

The previous projection deliberately discarded most core rows of the
singleton witness.  One exactness consequence can be retained at linear
cost.  In a singleton-normalized game put

```text
m_i=v({r,i})                 (i != r),
M_r=sum_(i != r)m_i.
```

Every core witness with `w_r=0` satisfies `w_i>=m_i`; existence of that
witness implies `M_r<=T`.  A nonnegative total-`T` vector with these pair
floors and the requirements `(RHP1)` exists if and only if, for every
`u>=0`,

```text
sum_S u_S x(S)
 <=sum_(i != r)p_i m_i
   +(T-M_r) max_(i != r)p_i.                         (PFP)
```

After normalizing `u in K_r`, this is

```text
sum_S u_S x(S)<=T-sum_(i != r)q_i m_i,               (PFP1)
```

and the incidence identity `(RMS)` turns it into the sharpened root-deficit
budget

```text
delta x_r+sum_(i != r)q_i v({r,i})
 <=sum_(i != r)q_i x_i.                              (PFRDBx)
```

If the packing uses only common hinges, the same argument gives

```text
delta z_r+sum_(i != r)q_i v({r,i})
 <=sum_(i != r)q_i z_i.                              (PFRDBz)
```

#### Proof

Write `w_i=m_i+y_i` off the root.  Then `y>=0` and
`sum y_i=T-M_r`.  The support function of this translated rooted simplex in
direction `p` is

```text
sum_i p_i m_i+(T-M_r)max_i p_i.
```

The same down-set separation used for `(RHP2)` proves necessity and
sufficiency.  Under `p_i<=1`, rearrangement gives `(PFP1)`.  Dotting `(RMS)`
with `x` gives

```text
sum_S u_S x(S)=T+delta x_r-sum_i q_i x_i;
```

substitution proves `(PFRDBx)`.  Common-hinge equality transfers the left
coalition sum from `x` to `z`, proving the mirror.  QED.

### Theorem (rooted pair lifts and exact-cone facets)

The pair-floor budget has a canonical full-cone lift different from the
decomposable singleton-slack completion.  Put `Q=sum_(i != r)q_i` and replace
each deficit singleton by its rooted pair:

```text
sum_S u_S 1_S
 +sum_(i != r)q_i 1_{r,i}-(delta+Q)e_r=1_N.          (RPL)
```

If `u` is a vertex of `K_r`, the nonzero support of `(RPL)` is a
min-semi-balanced system with at most `n` coalitions and exceptional
coalition `{r}` whenever `delta+Q>0`.  On an Lmin-tight support, its induced
exact-game inequality is precisely `(PFRDBx)`; on a common-hinge support the
same inequality gives `(PFRDBz)`.  For `n>=3`, `(RPL)` defines a facet of the
exact-game cone if and only if this pair-lifted system is indecomposable in
the sense of Studeny--Kratochvil.

#### Proof

Use `1_{r,i}=e_r+e_i` in `(RPL)`; it reduces coordinatewise to `(RMS)`.
In the standard-form vertex basis, replacing a positive slack column `e_i`
by `e_r+e_i` is an invertible column shear while retaining the exceptional
column `e_r`.  Hence linear independence and the support bound are
preserved.  Lemma 2(c) of Studeny--Kratochvil gives minimal
semi-balancedness, and their facet theorem gives the last equivalence.

For the induced inequality, singleton normalization and Lmin tightness give

```text
0<=T-sum_S u_S v(S)-sum_i q_i v({r,i})
  =sum_i q_i[x_i-v({r,i})]-delta x_r,
```

where the last equality is `(RMS)` dotted with `x`.  This is `(PFRDBx)`;
common-hinge tightness permits the identical calculation at `z`.  QED.

This yields the distinguished exact-cone class sought by the packet program:
**rooted pair lifts of extreme staged Lmin packings**.  The common-hinge
subclass evaluates at both selections.  For a fixed staged menu the full
class is enumerated exactly by the vertices of `K_r`; support rank proves
minimality, and the published exceptional-set test decides which are facets.
The exact hostile replay produces eight nontrivial pair lifts.  Six are
indecomposable full-cone facets, including both sharp seven-player
orientations, both coefficient-two roots, one primitive coefficient-seven
cut, and the neutral-endpoint cut.  The other two primitive
coefficient-seven lifts have respectively `3` and `20` decompositions.
An independently formulated Z3 enumeration agrees with every exact-LP facet
verdict.  These finite verdicts audit the classification algorithm; the
theorem itself is the incidence/shear argument above.

### Theorem (dimension-free sharp-family pair-lift facet)

For every `p>=1`, `k>=2`, let

```text
N={r} dot-union O dot-union B,       |O|=p, |B|=k,
C_b={r} union (B\{b}).
```

The pair lift of the uniform sharp-family packing is

```text
sum_(b in B)1_{C_b}
 +(k-1)sum_(o in O)1_{r,o}
 -[p(k-1)+1]e_r=(k-1)1_N.                         (GPL)
```

Its support is an indecomposable min-semi-balanced system and therefore
defines a facet of the exact-game cone for every `p,k`.  On `G(p,k)` this
facet is active at both `Lmin` and `Lmax`; its two evaluations are exactly
the hand inequalities `X<=p(k-1)q` and `M<=p(k-1)l`.

#### Proof

Identity and minimality follow from `(RPL)`.  For indecomposability, suppose
a new proper coalition `E` were exceptional after adjoining it to the
support.  Normalize its coefficient to `-1`.  Let `a_b,c_o,d>=0` be the
coefficients on `C_b,{r,o},{r}`, let `rho` be the common load, and write

```text
e_r=1_{r in E},       b=|E intersect B|,       o=|E intersect O|,
A=sum_b a_b.
```

The `B`, `O`, and root coordinates give

```text
A-a_b=rho+1_{b in E},
c_o=rho+1_{o in E},
A+(p-1)rho+o+d-e_r=0,
A=(k rho+b)/(k-1).                                  (GPD)
```

The last left side before `d-e_r` is strictly increasing in `rho`.
If `o<p`, nonnegativity of an excluded `O` coefficient gives `rho>=0`.
For `b=0`, `(GPD)` permits only `E=emptyset`, `{r}`, or one supported pair
`{r,o}`.  For `0<b<k`, nonnegativity gives
`rho>=k-1-b`; the left side is at most one only when
`b=k-1`, `o=0`, `rho=0`, yielding one supported `C_b`.  For `b=k` it already
exceeds one.

If `o=p`, then `rho>=-1`.  When `b=0`, the excluded `B` rows improve this to
`rho>=0`, leaving only the supported pair in the special case `p=1`.
For `0<b<k` the same bound `rho>=k-1-b` makes the root equation impossible.
For `b=k`, its minimum occurs at `rho=-1` and equals one, yielding only
`E=N`.  Thus no new nonempty proper exceptional coalition exists, proving
indecomposability.  Activity on `G(p,k)` follows from `v({r,o})=0` and the
two equality cases of `(PFRDB)` already computed symbolically in `(Gq)` and
`(GM)`.  QED.

This supplies a uniform exact-cone explanation of the whole extremal family,
not just its two seven-player orientations: equality is carried by one
rooted pair-lift facet whose `k` common hinges are selected simultaneously.

### Theorem (over-cover to rooted pair-lift coupling)

Let a normalized Lmax top over-cover, supported on coalitions also tight at
Lmin, be

```text
sum_S lambda_S 1_S=eta 1_N+alpha,
sum_i alpha_i=1,             alpha>=0.
```

Fix a top player `r`, put

```text
theta_-=max_(i != r)alpha_i,       theta=eta+theta_-,
u_S=lambda_S/theta.
```

Assume `theta>0`; if `theta=0`, the root-deletion inequality `(RD)` already
forces the top level `M` to vanish.

Then `u in K_r`, with

```text
delta=(alpha_r-theta_-)/theta,
q_i=(theta_--alpha_i)/theta       (i != r).           (OCP)
```

In particular a strict deleted-load leader `alpha_r>theta_-` produces a
positive-root pair lift.  Its exact-game inequality, simultaneously evaluated
at the two selections, is

```text
(alpha_r-theta_-)x_r
 +sum_(i != r)(theta_--alpha_i)v({r,i})
 <=sum_(i != r)(theta_--alpha_i)x_i,                 (OCPLx)

(alpha_r-theta_-)z_r
 +sum_(i != r)(theta_--alpha_i)v({r,i})
 <=sum_(i != r)(theta_--alpha_i)z_i.                 (OCPLz)
```

The two rows have the same nonnegative pair-lift slack

```text
sigma_r=sum_(i != r)(theta_--alpha_i)x_i
        -(alpha_r-theta_-)x_r
        -sum_(i != r)(theta_--alpha_i)v({r,i})

       =sum_(i != r)(theta_--alpha_i)z_i
        -(alpha_r-theta_-)z_r
        -sum_(i != r)(theta_--alpha_i)v({r,i}).       (OCS)
```

Equivalently,

```text
sum_(i != r)(theta_--alpha_i)(x_i-z_i)
 =(alpha_r-theta_-)(x_r-z_r).                        (OCD)
```

Thus the coupled pair-lift inequality is active at either selection if and only if
`sigma_r=0`; then it is active at both, and `(OCD)` is its tangent balance
law.

If `u` is a vertex, the associated system is an exact-cone facet exactly
when its rooted pair lift is indecomposable.  In the bounded positive-top
case, an extreme-point decomposition of `u` expresses `(OCPL)` as a
nonnegative combination of the vertex pair-lift inequalities.  Thus a
common sparse over-cover supplies an
explicit finite packet of full-cone facet candidates rather than an unnamed
rooted charge.

#### Proof

The over-cover load at player `i` is `eta+alpha_i`.  Therefore

```text
p_i=sum_(S:i in S)u_S=(eta+alpha_i)/(eta+theta_-).
```

This is at most one off the root, and subtracting one gives exactly `(OCP)`.
Apply `(RPL)` and multiply its induced inequalities by `theta`; the common
tightness of every positively weighted over-cover coalition permits
evaluation at both `x` and `z`, yielding `(OCPLx)--(OCPLz)`.  The facet and
decomposition statements are the vertex theorem and rational polytope
decomposition for `K_r`.  Finally common tightness gives
`alpha.x=alpha.z`; equal totals expand this as `(OCD)`, and subtracting the
two displayed facet slacks gives `(OCS)`.  QED.

For `G(p,k)`, the common over-cover has

```text
alpha_r=1/k,
theta_-=(k-1)/k^2,
alpha_b=theta_-          (b in B),
alpha_o=0                (o in O).
```

Hence `(OCP)` gives `q_b=0`, `q_o=1`, and
`delta=1/(k-1)` exactly.  The single coupled inequality is `(GPL)`, while
root deletion gives `M/T<=theta_-`; these are precisely the two structural
ingredients in the sharp hand proof.

### Lemma (rooted-pair gauge quotient)

Rooted-pair coalitions already present in a packing are redundant in `(RPL)`.
If `t<=u_{r,i}`, replace

```text
u'_{r,i}=u_{r,i}-t,       q'_i=q_i+t,       delta'=delta-t.   (RPG)
```

All other coordinates are unchanged.  Then `u' in K_r`, and the merged
coefficient system `(RPL)` is identical before and after `(RPG)`.  Indeed,
the coefficient of `1_{r,i}` remains `u_{r,i}+q_i`, while

```text
delta'+sum_j q'_j=delta+sum_j q_j.
```

Repeating this operation deletes every rooted-pair column from the packing
without changing either the exact-game inequality or its facet status.
Consequently rooted pair-lift enumeration should be performed on the
quotient menu

```text
C_x^red=C_x \ { {r,i}: i != r },
```

and only then should the deficit pair columns be restored.  Distinct packing
vertices can otherwise encode the same exact-cone row.  This is a
dimension-free reduction of the facet-enumeration problem, not merely a
control-specific simplification.

It is essential that this quotient is **not** used for the hybrid price.
Writing `Q=sum_i q_i` and `K=floor(n^2/4)-n+1`, a gauge move of mass `t`
sends

```text
delta'=delta-t,       Q'=Q+t,
K delta'-Q'=K delta-Q-(K+1)t.                       (RPGP)
```

Thus `(RPG)` preserves the completed exact-cone row and its facet status but
not `P=Q/delta`, nor even the sign of the target margin `K delta-Q`.  The
price is an invariant of a **marked lift**---the completed row together with
the packing/deficit origin of each rooted-pair coefficient---not of the facet
normal alone.  Any all-dimensional selection theorem must retain this mark.

The required mark can nevertheless be optimized without remembering a dual
solver's history.  Fix a rooted completed row whose positive nonpair columns
are `x`-tight, and write `a_S>0` for its positive coefficients.
For the rooted pair `{r,i}`, split

```text
a_{r,i}=t_i+q_i,       0<=t_i<=a_{r,i},              (RPM1)
```

where `t_i` is packing mass and `q_i` is deficit mass.  Admissibility requires
`t_i=0` unless `{r,i}` is `x`-tight.  Put

```text
delta(t)=sum_(|S|>=3) a_S+sum_i t_i-1,
Q(t)=sum_i(a_{r,i}-t_i).                             (RPM2)
```

> **Lemma (optimal tight-pair marking).**  Among all admissible markings of
> a fixed rooted row, `K delta(t)-Q(t)` is maximized by taking
> `t_i=a_{r,i}` on every `x`-tight rooted pair and `t_i=0` on every non-tight
> rooted pair.  Hence the existence of an affordable marking is determined
> exactly by the facet normal together with its `x`-tight pair labels.

Indeed, relative to `t=0`, equations `(RPM2)` give

```text
K delta(t)-Q(t)
 =K delta(0)-Q(0)+(K+1)sum_i t_i.                    (RPM3)
```

Every coefficient of `t_i` is positive, so each admissible coordinate is set
to its upper endpoint.  This proves the lemma.  Notice the distinction: an
unlabelled facet ray is insufficient, but a rooted row labelled by a
specified Lmin tight set has a canonical best marking.  The all-dimensional problem can
therefore be posed as finite labelled-facet selection, not as recovery of a
particular Farkas-dual vertex.

There is an even smaller scalar form.  Let `c` be the exceptional-root
coefficient of the normalized completed row and let

```text
Q_bad=sum_{i: {r,i} is not x-tight} a_{r,i}.          (RPM4)
```

Root balance gives `c=delta_*+Q_bad` for the canonical best marking.  Hence

```text
K delta_*-Q_bad=Kc-(K+1)Q_bad.                        (RPM5)
```

> **Corollary (bad-spoke fraction criterion).**  A normalized rooted row
> whose nonpair columns are `x`-tight has an affordable admissible marking
> exactly when
>
> ```text
> Q_bad/c <= K/(K+1),                                 (RPM6)
> ```
>
> together with the required positive root excess `Q_bad<c`.

Thus the selection problem no longer involves a continuum of gauges: after
enumerating a rectangular facet, sum only the weights of its rooted-pair
spokes that fail the Lmin tightness label.  This is an exact finite
labelled-facet test at each fixed dimension.

### Theorem (labelled rooted-row packing/cover duality)

The preceding test has a direct hypergraph dual.  Put `V=N\{r}` and let
`G subset V` be the players whose rooted pair `{r,i}` is Lmin-tight;
write `B=V\G`.  Let `H` consist of the offroot traces `A` of all
root-containing Lmin-tight coalitions `{r} union A` of size at least three.
For `a>=0` on `H`, impose the fractional-packing constraints

```text
sum_(A contains i) a_A <= 1                    (i in V),       (LPC1)
```

and complete the unused load by rooted pairs,

```text
q_i=1-sum_(A contains i)a_A.                                  (LPC2)
```

In the canonical marking, `q_i` is packing mass for `i in G` and deficit
mass for `i in B`.  Define

```text
K=floor(n^2/4)-n+1,
C=K(|G|-1)-|B|,
w(A)=K(1-|A intersect G|)+|A intersect B|.                    (LPC3)
```

> The maximum canonical marked margin over this menu is
>
> ```text
> C+max {sum_A w(A)a_A: a satisfies (LPC1)},                  (LPC4)
> ```
>
> and, by exact fractional packing/cover duality, equals
>
> ```text
> C+min {sum_(i in V)y_i:
>        y>=0, sum_(i in A)y_i>=w(A) for every A in H}.        (LPC5)
> ```
>
> An optimum may be chosen at a vertex.  In standard form `(a,q)`, that
> vertex has at most `n-1` positive columns; its rooted completion therefore
> has at most `n` support columns including the exceptional singleton.  It is
> a min-semi-balanced atom, and it is a full exact-cone facet precisely when
> it passes the Studeny--Kratochvil indecomposability criterion.

Indeed, `(LPC2)` gives

```text
delta=|G|-1+sum_A[1-|A intersect G|]a_A,
Q_bad=|B|-sum_A|A intersect B|a_A.                            (LPC6)
```

Expanding `K delta-Q_bad` gives `(LPC3)--(LPC4)`.  Ordinary rational LP
duality gives `(LPC5)`.  Adding the slack coordinates `q` turns `(LPC1)`
into `n-1` incidence equalities, so a basic feasible solution has at most
`n-1` positive packing/slack columns.  The rooted-pair shear theorem then
gives the semi-balanced and facet statements.  QED.

This yields a useful dimension-free sufficient condition.  If `|G|>=2`,
take `a=0`.  Then `delta=|G|-1>0`, and the worst case is `|G|=2`, where

```text
K delta-Q_bad >= K-(n-3)=floor(n^2/4)-2n+4.                   (LPC7)
```

For `n=2m` the right side is `(m-2)^2`; for `n=2m+1` it is
`(m-1)(m-2)`.  It is positive for every `n>=6`.  Thus **two Lmin-tight
rooted pairs automatically supply an affordable marked rooted row** in all
target dimensions.

The one-pair branch is equally rigid.  Suppose `|G|=1`, with unique partner
`j`.  For a single nonpair trace `A`, the feasible packing `a_A=1` has

```text
margin=K |G\A|-|B\A|.                                (LPC8)
```

For `n>=6`, `K>=n-2=|B|`.  Hence if `j notin A`, this margin is nonnegative
and the root excess is one, so the row is affordable.  Conversely, if every
nonpair trace contains `j`, its packing constraint gives `sum_A a_A<=1`,
and `(LPC6)` gives `delta=0` for every feasible packing.

> **Corollary (locked-pair alternative).**  For `n>=6`, a root with exactly
> one Lmin-tight rooted pair is affordable if and only if some larger rooted
> Lmin-tight coalition omits the pair partner.  An unaffordable one-pair root
> therefore has a locked partner contained in every rooted packing column;
> the scalar obstruction is identically zero root excess, not merely an
> unfavorable optimum.

This is a dimension-free structural handover.  It says that the direct arm
must absorb a locked partner together with the root, but it does not by
itself select the remaining upper nongainer block or a gainer packet.

The pair-free branch has an exact hypergraph alternative as well.  Put
`m=n-1`, so

```text
K=floor((m-1)^2/4)=max_(2<=t<=m)(t-1)(m-t),
floor(n^2/4)=K+m.                                    (LPC9)
```

Assume `G` is empty and the total intersection of the nonpair traces is
empty.  Choose an inclusion-minimal empty-intersection subfamily
`A_1,...,A_t`.  Minimality supplies

```text
v_j in intersection_(k!=j) A_k \ A_j.
```

The witnesses are distinct.  Every `A_j` contains the other `t-1`
witnesses, while every vertex occurs in at most `t-1` of the selected
traces.  Therefore `a_(A_j)=1/(t-1)` is a feasible fractional packing, with
root excess `1/(t-1)>0`, and

```text
sum_j [K+|A_j|]/(t-1)
 >=t[K+t-1]/(t-1)
 >=K+m=floor(n^2/4).                                 (LPC10)
```

The last difference, after multiplication by `t-1`, is exactly
`K-(t-1)(m-t)>=0`.

Conversely, if every nonpair trace contains a common player `c`, its packing
constraint gives `sum_A a_A<=1`; since `G` is empty, `(LPC6)` gives
`delta=sum_A a_A-1<=0` for every packing.

> **Theorem (pair-free common-carrier alternative).**  For `n>=6`, a
> pair-free root is affordably markable if and only if its larger rooted
> Lmin-tight coalitions have empty offroot intersection.  Thus a pair-free
> price failure is exactly a rooted star: some common carrier player belongs
> to every larger rooted tight coalition.

Equality in the constructed bound forces
`K=(t-1)(m-t)` and `|A_j|=t-1` for every `j`.  Hence, with
`W={v_1,...,v_t}`, the selected traces are exactly
`A_j=W\{v_j}`, and `t-1` and `m-t` are the two balanced parts maximizing
their product.  This is the complement-of-singletons block-star geometry of
the sharp family.  It characterizes equality for this canonical packing;
additional tight columns could still make the best marked margin positive.

The canonical equality completion is itself a dimension-free exact-cone
facet.  Write `p=m-t` (so `p>=1` in the target equality range),
`U=V\W`, and put

```text
C_j={r} union (W\{v_j}),       P_u={r,u}.
```

Then the scaled incidence identity is

```text
sum_j 1_(C_j)+(t-1)sum_(u in U)1_(P_u)
 -[p(t-1)+1]1_{r}=(t-1)1_N.                         (CSF)
```

> **Theorem (complement-star facet).**  For every `t>=2` and `p>=1`,
> `(CSF)` is a saturated indecomposable purely min-semi-balanced system and
> therefore defines a facet of the exact-game cone by the
> Studeny--Kratochvil criterion.

The support has exactly `1+t+p=n` columns.  On the nonroot coordinates its
positive incidence matrix is block diagonal with blocks `J_t-I_t` and
`I_p`, so it has full rank; the root singleton completes the rank to `n`.
For indecomposability, let `E` be another feasible exceptional set and let
`gamma` be its common load.  Write

```text
epsilon_r=1_{r in E},  q=|E intersect W|,  s=|E intersect U|.
```

Solving the witness and outside coordinate equations forces

```text
a_j=[gamma+q-(t-1)1_{v_j in E}]/(t-1),
b_u=gamma+1_{u in E},
lambda_r=epsilon_r-s-q/(t-1)
         -[1+p(t-1)]gamma/(t-1).                    (CSX)
```

All three coefficient families must be nonnegative.  If `gamma<0`, the
`b_u` and `a_j` inequalities force every nonroot player into `E`, and
`(CSX)` leaves only `E=N`.  If `gamma>=0`, either `E` is empty, or
`epsilon_r=1`.  For `q=0`, `(CSX)` permits only `{r}` and one pair `P_u`;
for `0<q<t`, positivity of an included-witness coefficient gives
`gamma>=t-1-q`, and `(CSX)` permits only `q=t-1`, `s=0`, `gamma=0`, namely
one `C_j`; `q=t` is impossible.  Thus the only feasible exceptional sets
are the displayed support, the empty set, and `N`, which is exactly the
indecomposability test.  The assumption `p>=1` is essential to this short
classification; the `p=0,t=3` system is decomposable.

This adds an exact-cone explanation to the scalar equality mechanism: the
minimal empty-intersection packing selects a distinguished saturated facet,
not merely an arbitrary Farkas row.  It is a member of the published
indecomposable semi-balanced framework; no literature-novelty claim is made
for the family before specialist comparison.

Together with `(LPC7)` and the locked-pair alternative, this completely
classifies **scalar** affordability for every root when `n>=6`:

1. two tight rooted pairs imply affordability;
2. one tight rooted pair fails exactly when its partner is a common carrier;
3. no tight rooted pairs fail exactly when some common carrier exists.

The next selection problem is therefore discrete.  If every candidate root
is unaffordable, choose a carrier for each root and show that the resulting
carrier graph exposes an upper nongainer block and an Lmin-tight gainer
packet satisfying `(UBD)` or the exact interval criterion.  No continuous
facet-price optimization remains in the failure branch.

### Theorem (carrier monotonicity)

Let `x=Lmin(v)` and suppose `x_r>0`.  If player `c` belongs to every
`x`-tight coalition containing `r`, then

```text
x_c>=x_r.                                             (CMO)
```

Indeed, `d=e_c-e_r` has `d(S)>=0` on every tight coalition: the only negative
case would contain `r` but omit `c`.  Since `x_r>0`, all slack coalition
constraints and nonnegativity remain feasible for sufficiently small
positive movement along `d`.  If `x_c<x_r`, choose the movement smaller than
the payoff gap and all adjacent stratum gaps.  The first changed coordinate
of the increasing rearrangement is then in the `x_c` stratum and increases;
the decrease at the strictly higher `x_r` stratum occurs later.  This
strictly improves the leximin vector, a contradiction.

By the complete affordability classification, every positive root that is
unaffordable on its **full tight menu** has such a carrier.  Thus full-menu
carrier arrows point weakly upward through the Lmin strata; every directed
carrier cycle lies in a single Lmin stratum.  This is the first general order
structure on the failure branch.  A carrier found only in one selected
staged support does not justify this tangent argument, because an omitted
tight coalition could separate the two players.

On the six-player archive there are 554 full-tight-menu unaffordable
maximum-overlap roots.  Every one has at least one full-menu carrier that is
itself another maximum-overlap root, so the finite carrier graph closes on
that root block; all carrier orders satisfy `(CMO)`.  The narrower selected
staged menus have 560 unaffordable roots and the same finite root-block
closure, but only the full-menu count supports the tangent interpretation.
Root-block closure remains discovery evidence.  Its dimension-free proof,
or a sharp counterexample, is now the minimal bridge needed to turn a carrier
cycle into the direct block `H`.

In fact one need not assume root-block closure.  The mirror tangent argument
for `z=Lmax(v)` says: if `z_c<z_r`, then some `z`-tight coalition contains
`r` and omits `c`; otherwise `e_c-e_r` would be feasible at `z` and would
strictly improve the decreasing lexicographic objective.

> **Theorem (carrier-cycle/separator alternative).**  Let
> `R=argmax_i min(x_i,z_i)`, assume its coordinates are positive, and suppose
> every `r in R` is unaffordable on its full Lmin-tight menu.  Then at least
> one of the following holds.
>
> 1. There is a full Lmin carrier arrow `r -> c` with `r in R` and
>    `z_c<z_r`, together with a `z`-tight separator `D` such that `r in D`
>    and `c notin D`.
> 2. There is a directed carrier cycle `H subset R`.  The coordinates `x_i`
>    and `z_i` are each constant on `H`, every `x`-tight coalition meeting
>    `H` contains all of `H`, and every member of `H` has the same
>    gainer/nongainer sign.

For the proof, if some root has no carrier in `R`, choose one outside.  By
`(CMO)`, `x_c>=x_r`.  Since `c notin R` while `r` has maximum overlap,

```text
z_c<min(x_r,z_r)<=z_r,
```

and the Lmax tangent argument supplies `D`.  Otherwise choose one carrier in
`R` for each root.  The resulting finite functional digraph has a directed
cycle.  Coordinate monotonicity around the cycle forces equality of all its
`x` coordinates.  If an `x`-tight coalition contains one cycle vertex, the
carrier implications successively force every other vertex into it.  If `z`
is not constant on the cycle, some carrier arrow descends strictly in `z`,
and the Lmax tangent argument gives branch 1.  Otherwise `z` is constant as
well.  Since every cycle vertex maximizes `min(x_i,z_i)`, the two common
levels make all vertices gainers when the `z` level is higher and all
nongainers when it is no higher.  QED.

This theorem is the first genuine coupling between the complete Lmin packet
and an Lmax row in the price-failure branch.  It still stops short of `(H)`:
the separator branch needs a quantitative payment identity, while the cycle
branch is already sign-coherent but must meet the cardinality and packet
conditions in `(UBD)` or the exact direct interval.

The separator actually carries a strict, orientation-correct comparison
after complementation.

> **Lemma (strict complement payment).**  Suppose `c` belongs to every
> `x`-tight coalition containing `r`.  If a `z`-tight coalition `D` contains
> `r` and omits `c`, then
>
> ```text
> x(D)>z(D),              z(N\D)-x(N\D)>0.           (SCP)
> ```

Indeed `z(D)=v(D)` and core feasibility gives `x(D)>=v(D)`.  Equality would
make `D` an `x`-tight coalition containing `r` and omitting its carrier.
The second inequality follows from `x(N)=z(N)`.  Thus the separator debt in
the original orientation is a strict direct-comparison payment on the
complement.  Its magnitude has no known dimension-free lower bound, so
`(SCP)` alone does not pay a deficient cardinality base or a negative order
residual in `(TDG)`.

There is a stronger structural description of the cycle arm.  Call a set
`H` a tight-face module at an allocation `y` if every `y`-tight proper
coalition contains either all of `H` or none of it.

> **Theorem (carrier modules and exact weighted contraction).**  A directed
> carrier cycle `H` is a tight-face module at `x`.  Consequently, if
>
> ```text
> U_H={d: supp(d) subset H, sum_(i in H)d_i=0},
> ```
>
> then every `d in U_H` is in the two-sided lineality space of the active
> core tangent cone at `x`; for sufficiently small `epsilon>0`, both
> `x+epsilon d` and `x-epsilon d` are core allocations.  Moreover exactly
> one of the following holds.
>
> 1. Some `z`-tight coalition separates `H`; every such partial coalition
>    and its complement give a strict payment as in `(SCP)`.
> 2. `H` is a tight-face module at both `x` and `z`.  Contracting `H` to one
>    role of integer weight `h=|H|` gives an exact weighted quotient game in
>    which the projections of `x` and `z` are respectively weighted Lmin and
>    weighted Lmax.  The total and hybrid overlap are preserved when the
>    quotient role's per-capita payoff is repeated `h` times.

For the tangent assertion, every active coalition has zero incidence or
full incidence on `H`, so `d(S)=0`; positivity of the cycle coordinates and
the positive slack of every inactive constraint permit both signs locally.
If a `z`-tight coalition contains a nonempty proper part of `H`, choose an
included cycle member `r` and an omitted member `c`.  Successive carrier
implications around the cycle say that every `x`-tight coalition containing
`r` contains `c`, so `(SCP)` applies.

For the contraction statement, replace `H` by a role `*` and expand a role
coalition by replacing `*` with all of `H`.  Define

```text
v/H(A)=v(expand(A)),       pi(y)_*=y(H),
```

with unit weights off `*` and weight `h` at `*`.  Projection sends every
core allocation of `v` into the quotient core.  Exactness also descends:
for each quotient coalition, project an original exactness witness for its
expansion.  If the projected `x` admitted a better weighted Lmin point,
distribute the quotient-role displacement equally over `H`.  The direction
is nonnegative on every active original constraint, while inactive
constraints tolerate a small step.  Lex improvement is preserved for a
small step by the concavity of the sums of the lowest repeated coordinates,
contradicting Lmin optimality.  The convex sums-of-largest argument gives
the Lmax mirror.  Finally

```text
pi(x)_*/h=x_i,  pi(z)_*/h=z_i  (i in H),
```

so repeating the role coordinate `h` times preserves both `T` and `O`.

The quotient need not be singleton-normalized: its singleton worth at `*`
is `v(H)`, which is positive on 377 of the 420 carrier cycles in the archived
six-player audit.  Subtracting that endowment can change the two lexicographic
selections, so it is not legitimate to invoke the original conjecture on a
naively normalized quotient.  However the weighted endowed formulation is
exactly equivalent to a block-symmetric singleton-normalized game, not a
larger ungrounded domain.

> **Theorem (canonical block expansion).**  Let `(R,w)` be a nonnegative
> exact role game with positive integer role weights `h_a`, total atomic
> weight `n=sum_a h_a`, and `w({a})=0` whenever `h_a=1`.  Replace role `a`
> by a clone block `B_a` of size `h_a` and define
>
> ```text
> w^uparrow(S)=w({a:B_a subset S}).                  (CBE)
> ```
>
> Then `w^uparrow` is a singleton-normalized exact `n`-player game.  Its
> core projects onto the role core by block summation; its Lmin and Lmax are
> constant on every block and are precisely the clone repetitions of the
> weighted Lmin and weighted Lmax of `w`.  Total payoff and overlap are
> preserved.

For core projection, a clone allocation `y` dominates `(CBE)` because every
coalition contains its complete blocks and all clone coordinates are
nonnegative.  Conversely split any nonnegative role-core allocation among
the clones.  To prove exactness for a clone coalition `S`, put
`A={a:B_a subset S}` and choose a role-core witness `q` with `q(A)=w(A)`.
For every partially met block put all of `q_a` on a clone outside `S`; split
the other role totals arbitrarily.  The resulting clone-core point has
`y(S)=q(A)=w^uparrow(S)`.  Singleton normalization follows because a clone
singleton contains a full block only when that block has weight one, where
the assumed singleton worth is zero.

The game is invariant under permutations inside each block.  Uniqueness of
both lex selections therefore forces block constancy.  On the block-constant
subspace, sorting clone coordinates is exactly sorting role per-capita
coordinates with multiplicities `h_a`, so the two selections correspond.
The overlap identity follows term by term.

Applying `(CBE)` to a common-module quotient produces a canonical
singleton-normalized exact game on the same `n` atomic players, with the same
two selections and overlap as the original, and with every coalition worth
determined by its complete role blocks.  This is an exact normal-form
replacement and proves that the weighted endowed quotient is not outside the
original domain.

The correct induction parameter is the number of roles, not the atomic
weight.  Let `P_r` be the target inequality for every nonnegative exact
weighted game on at most `r` roles, with positive integer weights of total
atomic weight `n>=6` and zero singleton worth on every unit-weight role.

> **Proposition (common-module induction).**  Assume `P_(r-1)`.  If an
> `r`-role instance has a nontrivial common tight-face module `H` whose
> per-capita coordinates are constant at each selector, then it satisfies
> the atomic target.  Consequently a counterexample minimal in its number of
> roles has no common selector module.

Contract `H` to one role of weight `sum_(i in H) h_i`.  Exactness and
nonnegativity descend, all remaining unit-role singleton worths stay zero,
and the new role may have positive singleton worth because its weight is at
least two.  The quotient has fewer roles and the same atomic weight `n`,
while weighted Lmin, weighted Lmax, total, and overlap are preserved.  Thus
`P_(r-1)` gives the original target.  Weighted coincidence through three
roles and the atomic weighted four-role theorem below establish `P_4`.

This closes the contraction arm in a strong-induction proof.  It does not
require running the carrier machinery again after contraction: the entire
smaller-role assertion is the induction hypothesis.  The selection step at
the current role count still needs its weighted formulation.  Whenever that
step supplies a carrier cycle, however, a role-minimal counterexample must
have an Lmax-tight coalition splitting it; otherwise it is a common module
and the proposition applies.

The coincidence part of the induction base is closed through three roles.

> **Theorem (weighted three-role coincidence).**  Every nonempty core of a
> TU game on at most three roles, with positive integer role weights, has the
> same weighted Lmin and weighted Lmax.  Repeating each role's per-capita
> payoff according to its weight, the common point Lorenz-dominates every
> feasible role-core allocation.

For three roles, every proper coalition is a singleton or the complement of
a singleton.  Efficiency therefore turns the role core into

```text
K={q: sum_a q_a=T, ell_a<=q_a<=u_a},
ell_a=w({a}),                 u_a=T-w(R\{a}).        (W3R1)
```

The one- and two-role cases are the same form.  There is a unique `lambda`
(up to a harmless interval when all roles are clipped) such that

```text
q_a^*=clip_[ell_a,u_a](h_a lambda),
sum_a q_a^*=T.                                      (W3R2)
```

Suppose a feasible point has two unclipped roles with per-capita payoffs
`q_a/h_a<q_b/h_b`.  Moving a sufficiently small amount from `b` to `a`
preserves `(W3R1)` and is a Robin Hood transfer on the repeated atomic vector,
strictly increasing at least one lower partial sum and decreasing no lower
partial sum.  Iterate until every unequal pair is blocked by the lower bound
of the higher role or the upper bound of the lower role.  The resulting
no-exchange conditions are exactly `(W3R2)`.  Hence `q^*` Lorenz-dominates
every feasible repeated vector.  A Lorenz-greatest point is simultaneously
leximin and leximax-min, proving the theorem.

For two roles of weights `h,k` this specializes to

```text
q_1^*=clip_[ell_1,u_1](hT/(h+k)).                   (TQR)
```

Canonical block expansion then makes the original clone selections coincide
and gives overlap `T`.  Thus any contraction branch leaving at most three
roles is completely harmless for `(H)`.  Four or more weighted roles remain
open; this matches the known four-player coincidence boundary but is a
separate weighted-role theorem.

The exact regression verifier enumerates 170,244 feasible integer-bound
weighted boxes, 311,364 vertices, and every role-weight composition through
atomic weight eight.  It checks all repeated-vector Lorenz partial sums:

```bash
python3 verifiers/divergence/verify_weighted_three_role_coincidence.py \
  --output verifiers/divergence/weighted_three_role_coincidence.json
```

The exchange proof is dimension-free in the integer weights; the grid is a
falsification audit only.

Three further four-role coincidence reductions follow from the same proof
and from the companion four-player theorem.

> **Theorem (elementary four-role reductions).**  Let `K` be the nonempty
> core of an exact game on four roles with positive integer role weights.
> Weighted Lmin and weighted Lmax coincide in each of the following cases.
>
> 1. all four role weights are equal **and every role singleton worth is
>    zero**;
> 2. one role total is constant on `K`;
> 3. after writing the core as singleton lower bounds, complementary upper
>    bounds, and three complementary pair-sum slabs, all pair slabs are
>    redundant.
> 4. at most one of the three complementary pair-sum slabs is
>    nonredundant.

For (1), repeating every role coordinate the same number of times preserves
both the increasing and decreasing lexicographic order of the four role
coordinates.  The two weighted selectors are therefore the ordinary
four-role selectors, and those coincide by the exact-partition/Lorenz theorem
for **singleton-normalized** exact games on at most four players.  The
singleton hypothesis in this clause cannot be dropped: positive singleton
endowments on nonunit contracted roles are permitted by `(CBE)`, and direct
two-crossing-slab controls with equal weights already have distinct weighted
selectors.  This is precisely why modularly normalizing a quotient is not a
valid shortcut.

For (2), suppose `q_r=c` throughout `K`.  Project away `r`.  The resulting
three-role feasible set has efficiency `T-c` and, for every coalition `A` of
the remaining roles, the lower bound

```text
q(A) >= max{w(A), w(A union {r})-c}.                (FRC1)
```

Thus the projection is a nonempty three-role TU core.  Its clipped weighted
equalizer Lorenz-dominates every feasible repeated vector by the weighted
three-role theorem.  Lorenz dominance is preserved when the same multiset of
`h_r` copies of `c/h_r` is adjoined to both vectors: this follows immediately
from the positive-part characterization of majorization, since the common
summand is added to both threshold functions.  Hence the lifted equalizer is
Lorenz-greatest in `K` and is both weighted selectors.

For (3), the core is simply

```text
K={q: sum_a q_a=T, ell_a<=q_a<=u_a}.                (FRC2)
```

The water-filling point `q_a=clip_[ell_a,u_a](h_a lambda)` and the Robin Hood
exchange proof of `(W3R2)` never used the number three once `(FRC2)` had been
obtained.  It Lorenz-dominates every feasible repeated vector and therefore
equals both selectors.

For (4), retain the only nonredundant slab as

```text
L <= q(A) <= U,              A={0,1}, B={2,3}.       (FRC3)
```

Together with the coordinate intervals and efficiency, `(FRC3)` is a
laminar weighted resource-allocation polytope: the constraint tree has root
`R`, children `A,B`, and the four role leaves.  Progressive water filling on
such a tree has a unique terminal point independent of whether it is run
upward from the lower bounds or downward from the upper bounds.  At a
feasible point, call a transfer from role `b` to role `a` a Robin Hood
transfer if `q_a/h_a<q_b/h_b`, it preserves all interval constraints, and
its amount is small enough not to reverse the two per-capita levels.  Within
`A` or `B`, such a transfer is blocked only by a leaf bound.  Across `A|B`,
it is blocked only by a leaf bound or by the active endpoint of `(FRC3)` in
the transfer's direction.  Raise the currently lowest unblocked per-capita
leaves together, freezing them when a leaf or group endpoint becomes tight.
Laminarity means that a newly tight node is nested in or disjoint from every
earlier node, so freezing never has to be undone.  Starting from the upper
bounds and lowering the currently highest unblocked leaves freezes the same
nested nodes in reverse order and reaches the same no-exchange point.

To see that this point is Lorenz-greatest, compare it with any feasible
`q`.  At the first repeated-coordinate partial sum where `q` could exceed
it, the difference has a lower receiver and a higher donor not separated by
a tight laminar node; otherwise summing the nested tight-node differences
gives the opposite partial-sum inequality.  A small feasible Robin Hood
transfer would result, contradicting termination.  Thus every lower partial
sum of the terminal repeated vector is maximal, so it is both weighted
selectors.

Consequently a minimal weighted four-role obstruction to coincidence must
have four nonconstant role totals and at least two **crossing** nonredundant
complementary pair slabs.  If all role singleton worths vanish, equal weights
are harmless; without that stronger normalization they need not be.  The
`2/3` family `(W4N1)` has exactly two crossing slabs, so the crossing
threshold is sharp.

The same argument localizes the crossing requirement at the selectors, not
merely in the global description of the core.

> **Lemma (two active crossing partitions).**  If the weighted Lmin and
> weighted Lmax of an exact four-role core are distinct, then each selector
> lies on endpoints of at least two independent complementary pair-sum
> slabs.

Indeed, let `q` be either selector and retain efficiency, all coordinate
intervals, and only the pair slabs active at `q`.  If at most one independent
pair slab remains, this active relaxation is the laminar polytope `(FRC3)`
and therefore has a Lorenz-greatest weighted water-filling point `g`.  Both
canonical selectors are Lorenz-undominated: strict Lorenz domination would
improve their defining increasing or decreasing lexicographic vector.  If
`g!=q`, the segment from `q` toward `g` strictly Lorenz-dominates `q`.
Every dropped pair inequality is strict at `q`, so a sufficiently short
initial segment is feasible in the original core, a contradiction.  Hence
`g=q`; since the original core is contained in the active relaxation, `q`
Lorenz-dominates the whole core and must be both selectors.

There are only three complementary pair partitions.  Thus two distinct
selectors necessarily have active two-flat edge systems with at least one
partition in common.  What is not yet proved is that they use the same
endpoint on two partitions.  The residual is now precise: opposite-endpoint
motion on a shared partition, or a transition between two edges having only
one common endpoint equality.  The common-two-endpoint case is closed by
`(EWS1)--(EWS18)` below.

There is an exact coordinate form for this residue.  Put

```text
y_0=q_0+q_1,       y_1=q_0+q_2,       y_2=q_0+q_3.             (FEC1)
```

The three complementary pair slabs are simply independent intervals for
`y_0,y_1,y_2`, while efficiency inverts `(FEC1)` as

```text
2q_0=y_0+y_1+y_2-T,       2q_1=T+y_0-y_1-y_2,
2q_2=T-y_0+y_1-y_2,       2q_3=T-y_0-y_1+y_2.                 (FEC2)
```

Thus every four-role core is a rectangular pair-slab box cut by four
diagonal coordinate slabs obtained by substituting `(FEC2)` into
`ell_i<=q_i<=u_i`.  A common-two-flat face is an edge of this box after
diagonal clipping; the unresolved cases move between different clipped
edges.

For two efficient allocations let `delta_j=y_j(x)-y_j(z)`.  The inverse
Hadamard transform `(FEC2)` gives the exact distance identity

```text
||x-z||_1
 =1/2 (|d0+d1+d2|+|d0-d1-d2|+|-d0+d1-d2|+|-d0-d1+d2|)
 =max{|d0|+|d1|+|d2|, 2 max_j |d_j|}.                         (FEC3)
```

For the last equality, order the absolute values as `a>=b>=c` and flip
signs by the Hadamard symmetries.  If `a>=b+c`, the four terms sum to `4a`;
otherwise they sum to `2(a+b+c)`.  Since
`O=T-||x-z||_1/2`, objective A on the edge-transition residue is exactly

```text
max{sum_j |d_j|, 2 max_j |d_j|}
 <=2[1-4n/(n^2-(n mod 2))]T.                                 (FEC4)
```

This is a reformulation, not yet the missing displacement bound.  It is
useful because it separates the selection problem (which clipped edges are
chosen) from the final overlap arithmetic and keeps the atomic weight `n`
visible.

The active-edge combinatorics are finite.  Choose two active endpoint labels
at each selector, relabel the three pair coordinates, reverse individual
interval orientations, and interchange the selectors when useful.  After
putting the first edge at `y_0=L_0,y_1=L_1`, the second edge has exactly one
of the following forms:

| type | second edge | common endpoint equalities | distance consequence |
|---|---|---:|---|
| C | `y_0=L_0,y_1=L_1` | two | common-two-flat theorem |
| I | `y_0=L_0,y_1=U_1` | one | `d_0=0` |
| II | `y_0=L_0,y_2=L_2` | one | `d_0=0` |
| III | `y_0=U_0,y_1=U_1` | zero | two shared partitions, opposite endpoints |
| IV | `y_0=U_0,y_2=L_2` | zero | one shared partition, opposite endpoint |

Extra active endpoints either put the row in type C or specialize one of
I--IV.  Types I and II lie in one common pair-slab face.  By `(FEC3)` they
satisfy the sharper identity

```text
||x-z||_1=2 max{|d_1|,|d_2|}.                              (FEC5)
```

The common-face rigidity theorem below closes both types without needing a
quantitative displacement estimate.
Types III and IV are the genuinely face-changing cases and require the full
three-coordinate expression `(FEC3)`.  This table is a complete
combinatorial classification of minimal active-edge incidences; it does not
yet classify the weighted payoff strata inside each row.

The pure type-I row is in fact impossible.

> **Lemma (parallel-edge exclusion).**  Suppose two distinct weighted
> canonical selectors share the endpoint equality `y_0=L_0`, have no active
> endpoint of the third pair slab, and their remaining active pair equalities
> are respectively `y_1=L_1` and `y_1=U_1`, with `L_1<U_1`.  This
> configuration cannot occur.

Restrict to the common face `y_0=L_0`, retain all coordinate intervals, and
drop the `y_1,y_2` slabs.  This is the laminar fixed-pair relaxation from
`(FRC3)` and has a Lorenz-greatest point `g`.  Let `x` be the selector on
`y_1=L_1`.  If `y_1(g)>=L_1`, then either `g=x` (which already forces selector
coincidence) or a short segment from `x` toward `g` strictly Lorenz-dominates
`x`.  It remains in the `y_1` interval, and it remains in the dropped `y_2`
slab because that slab is strict at `x`.  Both alternatives contradict the
hypotheses.  Hence `y_1(g)<L_1`.  At the other selector `z`, where
`y_1=U_1`, a short segment toward `g` moves strictly into the `y_1` interval;
the `y_2` slab is again strict.  It is therefore feasible and strictly
Lorenz-improves `z`, the final contradiction.  Reversing endpoints gives the
same proof.

Thus a genuine common-face transition is either type II or has a third pair
endpoint active at one of the selectors, in which case it specializes the
three-flat boundary of types II--IV.  The exclusion is qualitative; it does
not yet supply the type-II displacement price.

There is a stronger weighted argument that removes this entire common-face
residue.  Fix a common endpoint, relabel its two sides as `{0,1}` and
`{2,3}`, and write

```text
q_0=s,  q_1=W-s,  q_2=t,  q_3=T-W-t.                  (FEC6)
```

The weighted-equality splits of the two fixed-total pairs are

```text
s_* = h_0 W/(h_0+h_1),
t_* = h_2(T-W)/(h_2+h_3),                             (FEC7)
```

and put `d_1=|s-s_*|`, `d_2=|t-t_*|`.  Moving either split toward its
equality point is a Pigou--Dalton transfer between the corresponding clone
blocks.  Hence if both `d_1,d_2` weakly decrease, with one strict, the full
repeated payoff vector is strictly Lorenz improved: the two within-pair
doubly stochastic maps combine block diagonally.

> **Theorem (weighted common-face rigidity).**  Let `K` be a compact
> four-role core with positive integer role weights.  If two Lorenz-undominated
> points of `K` lie on the same endpoint of one complementary pair slab,
> then either they coincide or they lie on the same endpoint of a second
> independent complementary pair slab.  In particular, distinct weighted
> Lmin and weighted Lmax cannot form type I or type II in `(FEC4)`.

Work in the common face `(FEC6)`.  Two undominated points must lie in a
common closed orthant about `(s_*,t_*)`.  Otherwise their segment crosses,
say, `s=s_*`; there the first dispersion is zero and the second, by
convexity of absolute value, is at most the larger endpoint dispersion.
The crossing point therefore Lorenz-dominates whichever endpoint has that
larger second dispersion.

On a fixed orthant write

```text
s=s_*+epsilon_1 d_1,   t=t_*+epsilon_2 d_2,
d_1,d_2>=0.                                              (FEC8)
```

The singleton/complement bounds in the common face give independent
intervals for `d_1,d_2`.  The two remaining pair coordinates have normals

```text
(epsilon_1,epsilon_2),  (epsilon_1,-epsilon_2).          (FEC9)
```

Exactly one is a same-sign normal.  Two distinct coordinatewise-minimal
points are incomparable, so the lower convex boundary between them has
negative slope.  Coordinate boundaries are vertical or horizontal, and a
boundary of the opposite-sign strip has positive slope; each contains at
most one coordinatewise-minimal point.  The only available negative-slope
boundary is therefore the unique inward endpoint of the same-sign pair
strip, where `d_1+d_2` is fixed.  All negative-slope edges are parallel, so
convexity makes them one collinear boundary rather than separate efficient
pieces.  Every two distinct Lorenz-undominated points therefore share that
second pair endpoint.

Weighted Lmin and weighted Lmax are Lorenz-undominated, so every
common-one-endpoint incidence returns to the proved common-two theorem
`(EWS31)`.  The only quotient residue is now the opposite-endpoint
face-changing types III and IV.  A quantified-LRA hostile audit checks the
canonical noncommon cells for every ordered positive weight
row through atomic weight seven; that audit is a hostile control, while
`(FEC6)--(FEC9)` are the dimension-free proof for the common-face branch.

The opposite-endpoint residue disappears after connecting the two selectors
inside the Lorenz frontier.  For a role point `q`, repeat `q_i/h_i` exactly
`h_i` times and let `Lambda_k(q)` be the sum of its `k` smallest repeated
coordinates, `1<=k<n`.  Each `Lambda_k` is a continuous concave polyhedral
function: it is the minimum of the sums over all `k` clone coordinates.

> **Lemma (connected positive-Lorenz continuation).**  Any two uniquely
> specified lexicographic extremes of the Lorenz vector
> `(Lambda_1,...,Lambda_(n-1))` lie in one connected set of
> Lorenz-undominated core points.

Indeed, the lower-comprehensive Lorenz image

```text
{u : exists q in K, u_k<=Lambda_k(q), 1<=k<n}
```

is a convex polyhedron, as the projection of the common hypograph of the
concave polyhedral `Lambda_k`.  Its finite normal fan supplies strictly
positive hierarchical vectors `a^x,a^z` for which the two extremes uniquely
maximize

```text
F_a(q)=sum_(k=1)^(n-1) a_k Lambda_k(q).                 (FEC10)
```

For `a(t)=(1-t)a^x+t a^z`, let `A(t)=argmax_K F_(a(t))`.  Every `A(t)` is
nonempty, compact, and convex, because `F_(a(t))` is concave.  Its graph is
compact.  If that graph were the disjoint union of two nonempty closed sets,
their projections would be closed sets covering `[0,1]`, hence would meet at
some `t`; they would then disconnect the convex fiber `A(t)`, a contradiction.
The graph, and therefore its projection to `K`, is connected.  Every point
in the projection is Lorenz-undominated because every coefficient of `a(t)`
is positive.  (If two allocations had the same full Lorenz vector, their
midpoint would strictly Lorenz-improve them unless their repeated payoff
vectors agreed; the canonical role point is therefore unique.)

The two-active-crossing proof above applies verbatim to every
Lorenz-undominated point, not only to the two canonical selectors.  Unless
the core has a Lorenz-greatest point (which makes the selectors coincide),
every point of the connected continuation lies on endpoints of at least two
pair slabs.  It therefore lies in the one-skeleton of the three-dimensional
pair-slab box.

> **Theorem (weighted four-role edge confinement).**  In every compact
> four-role core with positive integer role weights, weighted Lmin and
> weighted Lmax either coincide or share endpoints of two independent
> complementary pair slabs.

If a pair slab has zero width, its endpoint is common to every point and
common-face rigidity supplies the second endpoint.  Otherwise consider the
connected continuation in the ordinary box one-skeleton.  A connected subset
that meets interiors of two different box edges must meet interiors of two
edges incident at some vertex.  Points on those incident edges share exactly
one endpoint equality, contradicting weighted common-face rigidity.  Hence
the continuation lies in one clipped box edge, and its endpoints share the
two pair equalities defining that edge.  This proves the theorem and excludes
types III and IV without enumerating weights or payoff strata.

Thus no edge-transition residue remains.  The quantitative atomic theorem
still uses the common-two cost argument and its finite exact audit below;
the present result is the dimension-free structural bridge that makes that
branch exhaustive.

The three-role boundary is sharp.  On four roles with weights `(3,1,1,1)`,
take the exact role game whose worths in binary coalition order are

```text
(0,11,0,14,0,14,0,16,0,12,0,15,0,15,0,18).        (W4O1)
```

Its weighted selections, in role totals, are

```text
q^min=(12,2,2,2),              q^max=(11,3,3,1).    (W4O2)
```

Thus weighted Lmin and Lmax already differ at four roles.  Canonical block
expansion gives the singleton-normalized exact six-player game with

```text
x=(4,4,4,2,2,2),
z=(11/3,11/3,11/3,3,3,1),
T=18, O=16, O/T=8/9.                                (W4O3)
```

The example is a boundary control, not a threat to `(H)`: its overlap is far
above `2/3`.  An exact verifier minimizes every one of the sixteen role
coalitions, lifts those witnesses to all 64 clone coalitions by the `(CBE)`
placement rule, and independently recomputes both complete lexicographic
traces:

```bash
PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/verify_weighted_four_role_obstruction.py \
  --output verifiers/divergence/weighted_four_role_obstruction.json
```

Accordingly the next contraction theorem must be an overlap bound for
four-or-more weighted roles; coincidence cannot be used beyond three.

The four-role obstruction extends to every atomic dimension.  For `m>=2`,
give the roles weights `(m,1,1,1)`, total `T=2m+4`, and take the lower
envelope of

```text
(2m+4,0,0,0),       (2m,2,2,0),
(2m+2,0,2,0),       (2m+2,2,0,0),
(2m+3,0,0,1).                                      (W4F1)
```

Every displayed vector has total `T`; defining the game as their lower
envelope makes it exact.  Its worth table is

```text
(0,2m,0,2m+2,0,2m+2,0,2m+3,
 0,2m,0,2m+2,0,2m+2,0,2m+4).                       (W4F2)
```

> **Theorem (weighted four-role divergence family).**  The weighted
> selections in role totals are
>
> ```text
> q^min=(2m+1,1,1,1),        q^max=(2m,2,2,0).      (W4F3)
> ```
>
> Their canonical clone expansion is singleton-normalized exact on
> `n=m+3` players and satisfies
>
> ```text
> O/T=(m+1)/(m+2),          ||x-z||_1/T=2/(m+2).    (W4F4)
> ```

For weighted Lmin, the complement of coalition `7` gives `q_3<=1`, so the
maximum minimum per-capita payoff is at most one.  At floor one, efficiency
gives `q_0+q_1+q_2=2m+3`, while the tight lower bounds
`q_0+q_1>=2m+2` and `q_0+q_2>=2m+2` imply `q_0>=2m+1`.  Hence
`q_1+q_2<=2`; their floor bounds force `q_1=q_2=1`, and efficiency gives
`q_0=2m+1`.  This pins all roles.

For weighted Lmax, the singleton bound `q_0>=2m` makes the per-capita ceiling
at least two.  At ceiling two, `q_0<=2m`, hence equality; the two pair bounds
force `q_1,q_2>=2`, and efficiency plus nonnegativity forces
`q_1=q_2=2,q_3=0`.  This again pins every role.  The overlap arithmetic is
immediate, and `(CBE)` proves the clone statement.

This family proves that the weighted four-role problem does not collapse to
coincidence even as the clone multiplicity grows.  It is not an extremal
family for `(H)`: `(m+1)/(m+2)` tends to one and lies far above the target.
Its role is to force a quantitative four-role overlap theorem rather than a
selector-equality theorem.

A natural stronger guess would be a universal `O/T>=3/4` theorem for exact
weighted games on four roles.  That guess is false even under the
normalization needed by `(CBE)`.  Give the roles weights `(m,1,1,1)`, where
`m>=5`, and take the lower envelope of

```text
(0,5,3,4), (1,3,3,5), (2,4,3,3), (5,0,7,0), (0,6,0,6).       (W4N1)
```

The binary-order worth table is

```text
(0,0,0,4,0,0,6,6,0,4,0,5,6,6,7,12).                         (W4N2)
```

Every singleton worth is zero and every coalition minimum is attained by a
displayed generator, so the game is nonnegative and exact.  For every
`m>=5`, exact staged elimination gives

```text
q^min=(5,1,5,1),              q^max=(3,3,3,3),
O=8,                           O/T=2/3.                        (W4N3)
```

For Lmin, complementing the triple worth `w(123)=7` gives `q_0<=5`, so the
first floor is at most `5/m`; the displayed candidate attains it.  On the
face `q_0=5`, efficiency gives `q_1+q_2+q_3=7`, while the pair bounds
`q_1+q_2>=6` and `q_2+q_3>=6` give `q_3<=1` and `q_1<=1`.
Thus the next floor is at most one; the candidate attains it and forces
`(q_1,q_2,q_3)=(1,5,1)`.  When `m=5` these equal levels merge into one
stage, without changing the selected point.

For Lmax, `q_1+q_2>=6` forces the ceiling of the unit roles to be at least
three.  The candidate `(3,3,3,3)` attains ceiling three because `m>=5`.
On that face the same bound forces `q_1=q_2=3`, and
`q_2+q_3>=6` then forces `q_3=3`; efficiency gives `q_0=3`.
The verifier independently encodes every exact stage and is useful for
hostilely auditing this short elimination.

Canonical block expansion gives singleton-normalized exact games on every
`n=m+3>=8`, with the same ratio.  These games do **not** challenge `(H)`:
the conjectured atomic target is `1/2` at `n=8` and decreases
thereafter.  They instead prove that contraction to four roles cannot be
closed by an atomic-size-independent `3/4` estimate.  Any useful weighted
four-role theorem must retain total atomic weight, largest-block weight, or
additional carrier/label data.  This is a precise failure of the proposed
local bridge, not a failure of the main conjecture.

Reproduce the lower envelope, independently encoded staged selections, the
parameter grid through `m=40`, and explicit attainment witnesses for all
2,048 coalitions of the `m=8` canonical expansion with

```bash
PYTHONPATH=src python3 \
  verifiers/divergence/verify_weighted_four_role_normalized_obstruction.py \
  --output verifiers/divergence/weighted_four_role_normalized_obstruction.json
```

The common crossing face of `(W4N1)` admits a complete atomic-weight-aware
analysis.  It is useful beyond that family.

> **Theorem (balanced weighted seesaw face).**  Let a weighted four-role
> core have weighted Lmin `x` and weighted Lmax `z` on the same face
>
> ```text
> q_0+q_1=W,             q_0+q_3=W,             T=2W.          (BWS1)
> ```
>
> Let the intersection of that face with the core be nonempty.  If the role
> weights are positive integers with sum `n`, then
>
> ```text
> O(x,z)/T >= 4n/[n^2-(n mod 2)].                              (BWS2)
> ```

Efficiency and `(BWS1)` give

```text
q(t)=(t,W-t,t,W-t),                 l<=t<=u.                   (BWS3)
```

Write

```text
P=max(h_0,h_2),  p=min(h_0,h_2),
Q=max(h_1,h_3),  q=min(h_1,h_3).                               (BWS4)
```

On the unrestricted line, the lowest rising per-capita coordinate is `t/P`
and the lowest falling coordinate is `(W-t)/Q`; hence weighted Lmin is at

```text
t_min=W P/(P+Q).
```

The highest rising and falling coordinates are `t/p` and `(W-t)/q`, so
weighted Lmax is at

```text
t_max=W p/(p+q).                                               (BWS5)
```

Restricting to `[l,u]` clips both displayed positions to the same interval,
which cannot increase their distance.  Since changing `t` by `Delta`
changes all four role totals by `|Delta|`,

```text
O/T = 1-|t_min-t_max|/W                                      (BWS6)
```

before clipping and is no smaller after clipping.  Orient the absolute
difference.  If `t_min>=t_max`, then

```text
O/T = Q/(P+Q)+p/(p+q)
    >= 1/(P+Q)+1/(p+q);                                      (BWS7)
```

the opposite orientation gives the same last bound using `P,q>=1`.  Put
`A=P+Q`, `B=p+q`.  These are positive integers with `A+B=n`, so

```text
1/A+1/B = n/(AB) >= 4n/[n^2-(n mod 2)],                       (BWS8)
```

because the largest integer product with sum `n` is
`floor(n^2/4)=[n^2-(n mod 2)]/4`.  This proves `(BWS2)`.

The harmonic/product bound is tight only when the two numerator weights used
in `(BWS7)` equal one and `A,B` are balanced.  The exact integer audit finds
equality only at atomic weights four and five; for every `n>=6` this balanced
seesaw branch has strict target slack.  In `(W4N1)`, both selectors lie on
the common upper crossing face with `W=6`, and the remaining bounds merely
clip the seesaw interval.  Thus its `2/3` ratio is explained by `(BWS3)--(BWS6)`
and is automatically safe for every atomic multiplicity.

At the exact-cone interface, each equality in `(BWS1)` is a tight endpoint of
a complementary pair slab.  It is an exact-partition equality
`w(A)+w(R\A)=T` only when the opposite slab endpoints coincide.  The
inequality `(BWS2)` is therefore selection-order arithmetic on the
intersection of two core faces; it does not define or require a new full
exact-game-cone facet.  Since its target margin is strict for `n>=6`, neither
the six-player equality orbits nor the two balanced seven-player equality
orientations can lie in this branch.  They must continue through the
labelled rooted/mixed facet arms retained in the protected dependency map.

Reproduce all 91,390 positive weight vectors through `n=40` and 4,112,550
exact common-interval clipping controls with

```bash
python3 verifiers/divergence/verify_weighted_balanced_seesaw.py \
  --output verifiers/divergence/weighted_balanced_seesaw.json
```

The balance assumption in `(BWS1)` is not needed to identify the selectors.
It is needed only for the harmonic lower bound.  On an arbitrary common
two-flat crossing face, choose the left endpoint and write the interval as

```text
q(t)=(e_0+t,e_1+s-t,e_2+t,e_3+s-t),      0<=t<=s,             (EWS1)
T=E+2s,                                  E=sum_i e_i.
```

The adjacent-gap theorem below assumes the stronger **face normalization**
`e_i=0` whenever `h_i=1`.  This condition is sufficient for canonical block
expansion but is not forced merely by zero singleton worth of a unit role:
the minimum of that coordinate on this particular two-flat line can exceed
its minimum on the full core.  Positive `e_i` is therefore prohibited on a
unit role as an explicit hypothesis of this branch.  For a rising role
`r in {0,2}` and a falling role `f in {1,3}`, define the per-capita crossing
time

```text
kappa_(rf)=[h_r(e_f+s)-h_f e_r]/(h_r+h_f).                    (EWS2)
```

> **Theorem (endowed two-flat selector reduction).**  On `(EWS1)`, the
> weighted selections have parameters
>
> ```text
> t_min=clip_[0,s](max_r min_f kappa_(rf)),
> t_max=clip_[0,s](max_f min_r kappa_(rf)).                    (EWS3)
> ```

For Lmin, the lower envelope of the two rising per-capita lines is
increasing and the lower envelope of the two falling lines is decreasing.
Their last crossing is the row-max/min value in `(EWS3)`; common interval
restriction clips it.  Dually, the upper rising envelope is increasing and
the upper falling envelope is decreasing, giving the column-max/min value
for Lmax.  The crossing geometry now supplies the extra order fact that is
false for a generic `2 by 2` matrix: the two low entries cannot be one
diagonal while the two high entries are
the other.  Otherwise, at any parameter strictly between the middle entries,
the four per-capita lines would satisfy, after orienting the diagonal,

```text
R_0>F_1>R_2>F_3>R_0,
```

an impossibility.  Thus the two middle entries are adjacent.  In that case
the row-max/min and column-max/min values in `(EWS3)` are exactly those two
entries.  If the four clipped crossings are
`kappa_1<=kappa_2<=kappa_3<=kappa_4`, then

```text
{t_min,t_max}={kappa_2,kappa_3},
O/T=1-2(kappa_3-kappa_2)/T.                                 (EWS4)
```

The overlap identity follows because a parameter displacement `Delta`
changes all four role totals by `|Delta|`.  It remains to bound this now
necessarily adjacent middle gap.  Swapping rows or columns and, for a
column gap, reversing `t`, reduces it to a low row.  Write `p` for the weight
of that low rising role, `r` for the other rising weight, and
`q<=b` for the two falling weights.

> **Theorem (exact endowed adjacent-gap cost).**  Normalize a positive
> adjacent middle gap to length one.  Among all nonnegative endowments
> satisfying `e_i=0` on unit-weight roles and all widths containing that
> gap, the minimum total is
>
> ```text
> S(p,r;q,b)=
>   2+p/q+(p+q+b)/r,                 p>1;
>   infinity,                        p=r=1;
>   2(2r+b+1)/(r-1),                 p=1<r, q=1;
>   (q+1)(2r+q+b)/[q(r-1)],          p=1<r, q>1.       (EWS5)
> ```
>
> Consequently every **face-normalized** endowed common-two-flat face with
> atomic weight `n=p+r+q+b>=6` satisfies
>
> ```text
> O/T >= c_n:=4n/[n^2-(n mod 2)].                         (EWS6)
> ```

Here is the gap-cost proof.  Let `l` and `l+1` be the two middle crossing
times after scaling, and put `z_f=e_f+s` for `f in {q,b}`.  Clipping gives
`l>=0` and `s>=l+1`, while the four crossing inequalities are

```text
p z_f-f e_p <=(p+f)l,
r z_f-f e_r >=(r+f)(l+1).                              (EWS7)
```

The total has the cancellation

```text
T=e_p+e_r+z_q+z_b.                                      (EWS8)
```

If `p>1`, add the two high-row inequalities and use the low-row inequality
in the smaller column `q`.  Exact simplification gives

```text
T >= 2+p/q+(p+q+b)/r + (n/r)(l+e_r).                    (EWS9)
```

Equality is attained at `l=e_r=0` by

```text
z_f=(r+f)/r,
e_p=p(r+q)/(qr),
s=z_q,
e_q=0,
e_b=(b-q)/r.                                           (EWS10)
```

Every positive endowment in `(EWS10)` lies on a nonunit role: `p>1`, and
`b>q` implies `b>1`.  This proves the first line of `(EWS5)` sharply.

If `p=1`, canonical normalization forces `e_p=0`.  When also `r=1`, the two
crossing rows are identical and no positive gap exists.  For `r>1`, comparing
the low and high inequalities in column `q` gives the sharper bound

```text
l >= [r+q+q e_r]/[q(r-1)].                              (EWS11)
```

When `q>1`, summing the two high inequalities and substituting `(EWS11)`
gives the last line of `(EWS5)` plus a nonnegative multiple of `e_r`; both
falling endowments are allowed, so the minimum has `e_r=0`.  It is attained
by
`l=(r+q)/[q(r-1)]`, `s=l+1`, and
`z_f=(r+f)(l+1)/r`.  When `q=1`, its endowment must also vanish, so
`z_q=s`.  Combining the low and high `q` inequalities gives

```text
l >= (r+1+e_r)/(r-1),
```

Adding the two high lower bounds to the total and substituting this inequality
leaves the third line plus a nonnegative multiple of `e_r`.  Equality is
attained at `e_r=0`, `l=(r+1)/(r-1)`, `s=2l`, and
`z_b=2(r+b)/(r-1)`; the only possibly positive falling endowment belongs to
`b>1`.  This proves all four sharp cost formulas.

It remains only integer arithmetic.  Put

```text
F=floor(n^2/4),       H_n=2/(1-c_n)=2+2n/(F-n).          (EWS12)
```

Because `(EWS4)` gives `O/T=1-2d/T`, a unit-gap cost `S` proves `(EWS6)`
exactly when `S>=H_n`.  For `p>1`, put `k=p+q+b=n-r`.  Since `q<=b` and
`p>=2`,

```text
S-2=p/q+k/(n-k)
   >=4/(k-2)+k/(n-k)
   >=(2+sqrt(k))^2/(n-2)
   >=16/(n-2).                                          (EWS13)
```

The last quantity is at least `2n/(F-n)`: for even `n` this is
`16/(n-2)>=8/(n-4)`, and for odd `n>=7` it reduces to
`n^2-6n-2>=0`.  If `p=q=1`, then

```text
S-2=2n/(r-1)>=2n/(n-4)>=2n/(F-n).                       (EWS14)
```

Finally take `p=1,q>1`.  Since `q<=b`, put
`d=n-2q-2>=r-1>0`.  Dropping only positive terms and applying Engel's
inequality gives

```text
S-2 >= 2/q+2(q+1)/d
     >= 2/q+6/d
     >= (sqrt(2)+sqrt(6))^2/(q+d)
     > 14/(n-4) > 2n/(F-n).                             (EWS15)
```

This proves `(EWS6)`.  Equality throughout is possible only in `(EWS13)`
at

```text
n=6,       (p,r,q,b)=(2,2,1,1),                         (EWS16)
```

up to row/column reversal.  The equality construction `(EWS10)`, scaled to
width `s=3/2`, is the exact role interval with endpoints

```text
(3,3/2,0,3/2),              (9/2,0,3/2,0).              (EWS17)
```

Its lower-envelope role game is nonnegative and exact.  In binary role
notation its worths satisfy
`w(01)=w(03)=9/2`, `w(23)=w(12)=3/2`, and `w(R)=6`.
Core feasibility therefore makes both complementary inequalities equalities;
they force the displayed line, while the zero singleton bounds on roles `1`
and `2` cut it to precisely `(EWS17)`.  Canonical block expansion at
weights `(2,1,2,1)` is a singleton-normalized exact six-player game with

```text
Lmin=(2,2,1/2,1/2,1/2,1/2),
Lmax=(3/2,3/2,3/2,0,0,3/2),
O/T=2/3.                                                  (EWS18)
```

After sorting and normalizing, `(EWS18)` is exactly six-player equality
survivor 1408, with strata `(4,2)` versus `(2,4)`.  Thus the endowed
two-flat theorem gives a human structural realization of one of the two
previously certified equality payoff profiles.  The other survivor and both
seven-player equality orientations remain on the rooted/mixed arms: the
sharp face-normalized common-two-flat minimum at `n=7` is `5/8>7/12`, so
neither seven-player equality orientation can enter this branch.

For comparison, at `n=5`, weights `(1,1,1,2)`, endowment `(0,0,0,2)`, and
`s=1` give overlap `3/4`; hence the restriction `n>=6` in `(EWS6)` is sharp.
The exact-cone interpretation must distinguish a common tight face from a
global exact-partition equality.  The two common endpoint equations are
tight-coalition faces; only when both complementary endpoints coincide are
they exact-partition equalities.  Thus `(EWS6)` is selection arithmetic on a
face-normalized line and is not, by itself, a new full-cone facet.

The face-normalization hypothesis is genuinely stronger than canonical
role-singleton normalization.  At weights `(3,1,1,1)`, the lower envelope of

```text
(0,5,3,4), (0,3,5,4), (2,4,3,3), (5,0,7,0), (0,5,0,7)
```

has zero worth on all four role singletons and weighted selectors

```text
q_min=(9/2,3/2,7/2,5/2),       q_max=(4,2,3,3).
```

Both lie on the common upper endpoints of pair partitions `01|23` and
`03|12`.  The maximal nonnegative extension of their common line has
direction `(1,-1,1,-1)`, width five, and endowment `(1,0,0,1)`.  Role `3`
has unit weight but positive face endowment.  Canonical expansion is an exact
singleton-normalized six-player game, independently recomputed as

```text
Lmin=(3/2,3/2,3/2,3/2,7/2,5/2),
Lmax=(4/3,4/3,4/3,2,3,3),       O/T=11/12>2/3.          (EWS19)
```

Thus `(EWS19)` refutes only the automatic face-normalization inference, not
the atomic target.  The unrestricted common-two-flat branch must charge a
positive unit-role face endowment to the off-face exactness witness attaining
that singleton.  This is now part of the open quotient theorem rather than
being hidden in `(EWS5)`.

One part of that charge is forced by exactness.  Let the two tight pair
coalitions defining the common line be

```text
C={h,a},                 D={h,b},                 o=R\(C union D),       (EWS20)
```

so that `h` is their common **hub** and `o` is the opposite role.  The hub
and opposite coordinates move in the same direction on the line.  For any
point `q` on the common face, exactify the singleton `{h}` at a core point
`y`, so `y_h=w(h)`.  Tightness at `q` and core feasibility of `y` give

```text
y(C)+y(D) >= q(C)+q(D).
```

Because both sums count the hub twice and omit the opposite role, this is

```text
T-y_o+w(h) >= T-q_o+q_h,
q_h-w(h) <= q_o-y_o <= q_o-w(o).                         (EWS21)
```

> **Lemma (common-face hub payment).**  On every exact common-two-flat
> face, the singleton slacks of the common hub and opposite role satisfy
> `(EWS21)` at every point of the face.  In particular, if the hub is a
> unit-weight role in the normalization of objective A, then the maximal
> nonnegative line extension has `e_h<=e_o`.

The last assertion follows by evaluating `(EWS21)` at the common endpoint
where the two same-direction coordinates are minimal, using `w(h)=0` and
nonnegativity `w(o)>=0`.  This is a human consequence of an off-face
exactness witness, not a sampled inequality.  It repairs the formerly hidden
endowment only when that unit role is the hub.  It does **not** imply an
analogous bound for either arm `a` or `b`; applying the singleton witness of
an arm counts that arm in only one of the two tight equations.  Those two
arm orientations are the remaining exactness-payment problem in the
unrestricted common-two-flat branch.

There is nevertheless no infinite-dimensional gap here.  If the restrictions
`e_i=0` on unit roles are dropped entirely, the same LP projection used in
the proof of `(EWS5)` has the exact cost

```text
S_0(p,r;q,b)=2+p/q+(p+q+b)/r,             q<=b.          (EWS22)
```

Indeed `(EWS9)` was derived without using `p>1` or any unit-endowment
equality, so it is a universal lower bound.  The point `(EWS10)` is
nonnegative for every `p>=1` and `q<=b` and attains it once unit endowments
are unrestricted.  Thus `(EWS22)` is exact, rather than a relaxation chosen
only for convenience.

> **Theorem (unrestricted large-atomic common-face bound).**  Every endowed
> common-two-flat weighted four-role face, with arbitrary nonnegative
> effective endowments, satisfies the atomic overlap target `(EWS6)` whenever
> `n>=10`.

For `p>=2`, the proof `(EWS13)` applies verbatim.  Let `p=1`.  Then

```text
S_0-2=1/q+(n-r)/r.                                      (EWS23)
```

If `q=1`, the ordering `q<=b` gives `r<=n-3`, hence

```text
S_0-2 >= n/(n-3).                                       (EWS24)
```

If `q>=2`, then `b>=q`, so `2q+r<=n-1`; Engel's inequality gives

```text
S_0-2 >= 1/q+(2q+1)/r
       >=(sqrt(2)+sqrt(2q+1))^2/(2q+r)
       >(13)/(n-1).                                     (EWS25)
```

For even `n`, `(EWS24)` and `(EWS25)` are at least `8/(n-4)` for
`n>=10`.  For odd `n`, comparison with
`2n/(F-n)=8n/(n^2-4n-1)` reduces respectively to
`n^2-12n+23>=0` and `5n^2-44n-13>=0`, again valid from `n=10` onward.
By `(EWS12)`, this proves the theorem.

Consequently exactness payment on common-two-flat faces is needed only in
the finite atomic window `n=6,7,8,9`.  Up to ordering the two side weights,
the unrestricted LP falls below the target only at

```text
n=6: (p,r;q,b)=(1,2;1,2),(1,3;1,1),
n=7:                 (1,3;1,2),(1,4;1,1),
n=8:                               (1,5;1,1),
n=9:                               (1,6;1,1).            (EWS26)
```

This list does not assert realizability by an exact game.  It is the complete
finite list on which hub/arm exactness and global selector optimality must be
used; all other common-two-flat weights are already closed by human
inequalities.

The hub lemma removes one orientation of every row in `(EWS26)` by human
algebra.  All six have `p=q=1`.  Suppose the unit low role `p` is the common
hub.  Put `d=e_r-e_p>=0` by `(EWS21)`.  Comparing the low and high crossing
inequalities in the unit side column gives

```text
e_p+l >=(r+1+d)/(r-1).                                  (EWS27)
```

Adding the two high crossing bounds to `(EWS8)` gives, with
`A=2r+b+1`,

```text
T >=(A/r)(e_p+l+1)+[(r+b+1)/r]d
  >=2A/(r-1).                                           (EWS28)
```

The last expression is exactly the face-normalized `p=q=1` cost in
`(EWS5)`, hence it reaches the target on every row of `(EWS26)`.  Equality is
feasible in this relaxation at `d=l=0`,
`e_p=e_r=(r+1)/(r-1)`, so the price is exact.  Therefore only orientations
in which the unit low role is **not the common hub** remain (it can be an arm
or the opposite role).
The exact seeded witness search described below retained divergence in only
`9` of `1,836` lower-envelope games and found no target violation; that is
discovery evidence, not the missing arm proof.

The finite residue has an exact selector encoding that avoids guessing any
payoff stratum.  On a compact convex weighted role core `K`, a point `x` is
weighted Lmin if and only if it is max--min fair:

```text
for every y in K and every i with y_i/h_i>x_i/h_i,
there is j with x_j/h_j<=x_i/h_i and y_j/h_j<x_j/h_j.    (EWS29)
```

Weighted Lmax has the reversed min--max condition: if
`y_i/h_i<z_i/h_i`, some `j` with `z_j/h_j>=z_i/h_i` must satisfy
`y_j/h_j>z_j/h_j`.  These conditions are equivalent to lexicographic
optimality of the per-capita values repeated `h_i` times.  For one direction,
a violating `y` gives, on a sufficiently short segment from the candidate
toward `y`, a strict improvement at the first affected repeated-payoff
level.  Conversely the direction from a candidate toward its lexicographic
optimizer violates the displayed condition at the first improved level.
The min--max statement follows by reversing signs.

Together with `(FEC1)--(FEC2)`, `(EWS29)` gives a quantified linear-real
formulation: four coordinate intervals and three pair slabs describe the
entire core; the unit-singleton exactness witnesses are four-dimensional
linear points; and both selector properties are universal linear
implications.  Splitting only the `12` choices of two common endpoint labels
and the `16` overlap sign cells removes every `min` and endpoint disjunction.
No active coordinate face, payoff stratum, or dual support is assumed.

The exact quantified-LRA audit is conclusive on the finite residue.  For each
of the six rows `(EWS26)`, it checks all `12` choices of two common pair-slab
endpoint labels and all `16` coordinatewise overlap sign cells.  All

```text
6*12*16=1,152                                             (EWS30)
```

linear-real sentences are unsatisfiable, with no unknown result.  The
encoding keeps a core witness attaining every zero unit-role singleton and
deliberately drops attainment of every other bound.  It is therefore a
relaxation of objective A: unsatisfiability proves the exact-game statement
without needing the omitted exactness witnesses.

An independently formulated rational regression checks `(EWS29)` itself.
On `118` deterministic exact lower-envelope games with atomic weights
`4..8`, it computes `236` selectors by the staged lexicographic algorithm and
then solves a separate LP for a violating no-repair direction at each role.
All `944` role implications pass.  This finite agreement audits the encoding;
the short convex argument above is the fairness proof.

> **Theorem (atomic common-two-flat quotient bound).**  Let an exact
> nonnegative weighted four-role game have positive integer weights of total
> `n>=6`, and suppose every unit-weight role has zero singleton worth.  If
> weighted Lmin and weighted Lmax lie on the same endpoints of two independent
> complementary pair slabs, then
>
> ```text
> O/T >=4n/[n^2-(n mod 2)].                              (EWS31)
> ```

For `n>=10`, this is the human unrestricted theorem `(EWS22)--(EWS25)`.
For `n=6,7,8,9`, every relaxed weight row outside `(EWS26)` is already safe
by the same formula, while `(EWS30)` excludes a strict violation on the six
remaining rows.  Since the audit asks exactly for a strict violation, its
unsatisfiability is the displayed weak bound.  This proves `(EWS31)`.
Equality identification in this branch remains as before:
the face-normalized human theorem supplies six-player survivor 1408, while
the finite audit proves a bound and does not by itself classify every
equality core.

> **Theorem (atomic weighted four-role quotient bound).**  Under the same
> hypotheses, `(EWS31)` holds without an active-face hypothesis.  If the
> selectors differ, weighted four-role edge confinement supplies two common
> pair endpoints and the common-two theorem applies.

This completes objective A.  It does not supply the carrier/separator
selection and gluing theorem in objective B, nor a complete equality/facet
classification in objective C.
The result is computer-assisted only in the finite window `(EWS26)` and has
not yet received external specialist review.

Reproduce all sixteen role minima, both exact weighted traces, all 64 clone
attainment witnesses, and both independently recomputed atomic traces with

```bash
PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/verify_common_face_endowment_scope.py \
  --output verifiers/divergence/common_face_endowment_scope.json
```

A constant half-overlap shortcut remains false at the abstract seesaw level.
For

```text
h=(6,41,263,23),   e=(31,9,2,6),   s=59,
```

the clipped crossings are `0,0,8901/152,59`, so
`O/T=3715/12616<1/2`.  All roles have weight greater than one, so this does
not violate the canonical unit-role condition.  This row is recorded only as
an abstract selector counterexample: no exact role-game realization is
claimed here.  Its atomic target at `n=333` is much smaller and is safely
satisfied.

The exact verifier checks all four oriented formulas on 1,950,536 positive
weight/orientation rows through `n=60`, recovers only `(EWS16)` at target
equality, and independently minimizes the original six-variable unit-gap LP
for all 4,844 positive weight vectors through `n=20`, recovering every
closed-form optimum or infeasible equal-unit-row case.  It also recomputes
`(EWS22)` on 14,665 independently formulated unrestricted rational LPs
through `n=30`, recovers exactly the six subtarget rows `(EWS26)`, and applies
the hub-payment inequality in every unit-hub orientation of those rows.  It
also recomputes
all 64 coalition exactness minima and both complete staged selectors of
`(EWS18)`, and formulates eight additional complete staged role LP controls.
Its bounded endowment grid covers
2,484,224 rational cases for `5<=n<=20`, coordinates `0..3`, and widths
`1..4`.  These finite rows audit the formulas; `(EWS7)--(EWS15)` are the
dimension-free proof.  Reproduce them with

```bash
python3 verifiers/divergence/verify_weighted_endowed_seesaw.py \
  --output verifiers/divergence/weighted_endowed_seesaw.json

python3 verifiers/divergence/verify_common_two_finite_z3.py \
  --output verifiers/divergence/common_two_finite_z3.json
```

Reproduce the lower envelope, pinning arithmetic, and parameter grid through
`m=40` with

```bash
python3 verifiers/divergence/verify_weighted_four_role_family.py \
  --output verifiers/divergence/weighted_four_role_family.json
```

At the exact-cone interface, contraction deletes duplicate player rows from
both active incidence matrices and records their multiplicity.  It is the
selection-face inverse of the clone expansion theorem below.  Hence a
block-symmetric rooted-star marking can be classified on the contracted
matrix and lifted through the already proved clone-expansion criterion.
Root-specific singleton or pair shears that distinguish members of `H` must
still be retained; the module theorem is not a claim that every marked facet
is automatically symmetric.

An exact archive audit now distinguishes the old qualitative alternative
from these stronger statements.  Among the 228 archived six-player rows in
which every maximum-overlap root is unaffordable on its full tight menu,
all 228 enter the cycle arm and all have a nongainer cycle.  Across their 420
directed cycles, 169 are separated by the Lmax face and 251 are common face
modules.  At the row level, 163 expose at least one inductively contractible
common module.  The other 65 are role-irreducible with respect to these
cycles, and every one has an Lmax-tight separator.  This is the exact finite
shadow of common-module induction, not proof that the payments close the
target.  Of the 65 role-irreducible rows, 62 are closed by the cycle itself.
In each of the remaining three, the unique splitting-row complement contains
every gainer and is therefore inadmissible for the proper-packet direct
identity; replacing at least one gainer by one additional upper nongainer
gives an Lmin-tight block with cardinality base `4/5`.  Every row has a
target-reaching Lmin-tight direct comparison whose
nongainer block contains a cycle.  The cycle itself suffices on 216 rows;
the remaining 12 require exactly one additional nongainer.  Full carrier
closure does not repair those 12, so “take the cycle” and “take its forced
closure” are both false universal selection rules.  This finite result
supports the separator-or-weighted-contraction program but proves no
unbounded-dimension inequality.

Nor can the separator arm be closed by inserting one arbitrary strict
complement into `(TDG)`.  Eighty-five of the 228 rows have an Lmax-tight
coalition splitting at least one cycle, but its complement satisfies the
target and the required order-residual sign in only one row.  Strict payment
is therefore qualitative currency; a dimension-free proof must aggregate
several separator rows, charge the negative residual elsewhere, or contract
a common module.  This exact negative control rules out a single-separator
local proof strategy.

On the six fixed seven-player hostile/sharp controls, five have an affordable
full-menu maximum-overlap root.  The sole all-unaffordable control is the
top-and-bottom-fixed branch: roots `4,5` form a nongainer common-face module,
and an independent direct packet reaches `7/12`.  Both sharp equality
orientations stay on the affordable rooted-facet arm, as required; the new
contraction branch is not being used to explain away sharp equality.

Reproduce it exactly with

```bash
PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/audit_carrier_separator_payment.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/carrier_separator_payment.json
```

The same audit independently constructs `(CBE)` and recomputes both complete
lexicographic selections with the separate exact-simplex implementation on
six representative common-module controls.  All twelve recomputations return
the archived `x,z` exactly.  This is a bounded regression check of the
translation, not a premise of the block-expansion proof.

### Aggregate separator budget from the Lmax staged packet

The individually weak strict payments are not the whole Lmax information.
Let `H subset R` be a nongainer carrier cycle with common coordinates

```text
x_i=a, z_i=b, d_i=x_i-z_i=L>=0       (i in H).
```

Let `Q` be the cumulative Lmax upper set through the stratum containing `H`.
For each `i in H`, the sign-coherent Lmax theorem supplies

```text
sum_S lambda^i_S 1_S-sum_(j in Q)c^i_j e_j=k_i 1_N,
lambda^i,c^i>=0,             c^i_i>0,              (ASB1)
```

with every supported `S` tight at `z`.  Dotting `(ASB1)` with `d=x-z`
gives the exact identity

```text
sum_S lambda^i_S [x(S)-z(S)]=sum_(j in Q)c^i_j d_j. (ASB2)
```

All coalition brackets on the left are nonnegative.  Sum the relations over
`i in H`, after arbitrary positive normalizations, and write
`Lambda_S=sum_i lambda^i_S`, `C_j=sum_i c^i_j`, and
`C_H=sum_(j in H)C_j>0`.  Then

```text
sum_S Lambda_S[x(S)-z(S)]
 =L C_H
  +sum_(j in Q\H,d_j>=0)C_j d_j
  -sum_(j in Q,d_j<0)C_j(z_j-x_j).                  (ASB3)
```

This is a quantitative aggregate-separator budget.  If a supported coalition
splits `H`, its bracket is strictly positive by `(SCP)`; whole-module rows
remain valid nonnegative payments.  The only debt in `(ASB3)` is on earlier
Lmax gainers.  For such a player `j`, `z_j>=b`; since every member of `H`
maximizes overlap,

```text
x_j=min(x_j,z_j)<=b<=a.                              (ASB4)
```

If the block loss `L=a-b` is positive, every negative debt edge `j -> i`,
`i in H`, is strict in the Lmin order and is available to the sign-coherent
Lmin **transport**.  But it is not a high--low overlap rectangle: for the
gainer `j`,

```text
max(x_j,z_j)=z_j>=b=min(x_i,z_i).
```

Thus the canonical label-currency family has no interval from `j` to `i`.
The algebraic split

```text
z_j-x_j=(z_j-b)+(b-x_j)                              (ASB5)
```

does not turn either summand into separately countable overlap currency.
When `L=0`, strict Lmin availability can also disappear at a tied
maximum-overlap gainer.

Consequently the carrier failure branch now has a fully identified two-colour
coupling problem: Lmax pinning exposes the common block loss through `(ASB3)`,
and the complete Lmin packet provides exactly the opposite-sign transport
edges on which its earlier-gainer debts can travel.  What remains is a
**triangular normalized gain--loss matching theorem** that combines those
two transports without reclassifying their mass as label currency or
charging a payoff layer twice.  Arbitrary circuit amplification cannot prove
this; the normalization must come from a joint acyclic packing/cover dual or
an indecomposable marked facet.  Thus `(ASB3)` is a real narrowing, not yet
the gluing theorem.

If no supported Lmax coalition in `(ASB1)` splits `H`, its coalition-incidence
part factors through the contracted role system and `(CBE)` gives the
canonical block normal form.  Common-module induction discharges that branch.
Hence, in a role-minimal counterexample, the aggregate packet may be
restricted to cycles with a splitting Lmax row.  The unit-column
normalization still has to be expressed in weighted-role pinning coordinates
in the current-role selection step; no general weighted affordability
theorem is being assumed.

The proper-gainer-packet condition can be removed in the strict-loss branch.
Suppose `L=a-b>0` and let `j` be any gainer.  Maximality of the overlap on
`H` gives `x_j<=b<a=x_i` for `i in H`.  If every `x`-tight coalition
containing `i` also contained `j`, carrier monotonicity would imply
`x_j>=x_i`, a contradiction.  Therefore some `x`-tight coalition contains
`i` and omits `j`; the module property makes it contain all of `H`.

> **Lemma (strict-loss proper-packet support).**  For a nongainer carrier
> cycle with `a-b>0`, every gainer is omitted by some Lmin-tight coalition
> containing the whole cycle.  Its gainer part is therefore proper and its
> comparison payment is nonnegative.

The coalition may depend on the omitted gainer.  This does not prove the
residual condition in `(CTS2)`, and the argument loses its strict Lmin order
when `L=0`.  The cardinality condition is automatic:

> **Lemma (carrier-cycle cardinality).**  Let `p,g,h` be the atomic
> multiplicities of the three direct-identity sign blocks, with
> `n=p+g+h>=6`, `p,g>=1`, and `h>=2` because the nongainer block contains a
> carrier cycle.  For every proper gainer packet of atomic multiplicity
> `0<=s<g`,
>
> ```text
> 1-gp/[(g+h)(p+g-s)] >= 4n/[n^2-(n mod 2)].        (CCC)
> ```
>
> Equality is possible only at `(n,p,g,h,s)=(6,2,2,2,1)`.

The left side decreases with `s`, so the worst case is `s=g-1`.  At fixed
`n,g`, the subtracted product `[g/(g+h)][p/(p+1)]`, with `p=n-g-h`,
decreases with `h`, so the worst case is `h=2`.  Substituting `g=n-p-2`
leaves `(n+p)/[(n-p)(p+1)]`.  For even `n`, its cross-product difference
from `4/n` is `n` times

```text
4p^2+(4-3n)p+n^2-4n,
```

whose discriminant is `-7n^2+40n+16<0` for `n>=8`; direct substitution at
`n=6` gives the unique zero `p=2`.  For odd `n`, the cross-product quadratic
has leading coefficient `4n` and discriminant

```text
-(n+1)(7n^3-47n^2+9n-1)<0                         (n>=7).
```

Thus every strict-loss carrier-cycle branch has only the normalized residual
matching left: contraction, packet properness, and cardinality are closed.

There is a parallel exact reduction on the direct side.  Let `C` be any
`x`-tight coalition meeting a carrier cycle.  The module property forces
`H subset C`.  Split

```text
C=H_C disjoint-union J_C,
H_C={i in C:z_i<=x_i},       J_C={i in C:z_i>x_i}.
```

Then `H subset H_C`, and core feasibility of `z` gives

```text
z(C)-x(C)>=0.                                      (CTS)
```

Thus every supported Lmin row meeting the cycle already supplies the
comparison premise of `(TDG)`, with `H=H_C` and `J=J_C`; no separate common
hinge is needed.  By `(CCC)`, a proper `J_C` automatically satisfies the
target cardinality condition.  The remaining conditions are

```text
J_C is a proper subset of all gainers,
R_x(C)+R_z(C)>=0,                                  (CTS2)
```

and in the strict-loss branch the first line is automatic by proper-packet
support.  This isolates the residual sum as a finite labelled score on the
actual Lmin-tight support.

> **Carrier-support selection lemma (open).**  In the all-unaffordable
> maximum-overlap-root branch, either a carrier cycle has an Lmax separator
> whose payments close the triangular gain--loss matching, or some Lmin-tight
> coalition meeting a carrier cycle satisfies `(CTS2)`; common-module cases
> may first be put in canonical block form `(CBE)`.

This formulation contains precisely the twelve archive repairs: the cycle
alone is not always the correct nongainer block, but adjoining the other
nongainers already present in a selected tight coalition is allowed.  On all
228 archived six-player all-unaffordable rows, some such coalition satisfies
`(CTS2)`; 216 use no extra nongainer and twelve use exactly one.  This is
still finite evidence.  The prospective human proof must average or separate
the support columns of a sign-coherent pinning relation while retaining the
exact residual sum.

Affordability is only the scalar price part of the hybrid proof.  Formula
`(MFP)` still needs the forced deficits to occupy the required loss strata,
or an Lmax comparison that pays the resulting multistratum defect.  The
duality theorem must not be cited as an overlap proof without that alignment.
Its value is to isolate the remaining obstruction: failure of price is
exactly a low-cost weighted cover `(LPC5)`; when price succeeds, only
stratum/sign alignment and the common-hinge repair remain.

For the coefficient-two strict common certificate, the normalized packing is

```text
u_24=u_44=u_79=1/2,       r=3.
```

Mask `24` is the rooted pair `{3,4}`.  Gauge deletion leaves
`u_44=u_79=1/2`, the midpoint of two reduced packing vertices.  The aggregate
pair-lift row is therefore the half-sum of the following two distinct active
rows:

```text
1_44+1_9+1_10+1_24+1_72-4e_3=1_N,                  (C2F1)
1_79+1_24+1_40-2e_3=1_N.                            (C2F2)
```

Both supports are linearly independent and indecomposable, of sizes `6` and
`4`; hence both are full exact-cone facets.  Exact-LP exceptional-set tests
and an independently formulated Z3 replay agree that each has zero
decompositions, and both game inequalities have zero slack.  Thus the
coefficient-two strict leader supplies genuine facet currency, not merely a
nonminimal aggregate inequality.

This theorem does not by itself prove `(H)`.  Three genuinely separate
failures remain possible: a sparse over-cover need not be entirely
Lmin-tight; its ceiling root need not be a strict deleted-load leader; and
even an indecomposable common pair lift controls only one weighted component
`(OCD)` of the hybrid difference.  The pair-lift gluing disjunction must show
that direct rows or additional staged facets compensate in exactly these
cases.  These are now explicit premises to falsify, rather than hidden steps
inside a generic Farkas certificate.

### Exact premise map on the hostile controls

Two root-specific optimizations must not be conflated.  The **deleted-load
oracle** minimizes `theta_-=max_(i != r) alpha_i` over every normalized Lmax
top over-cover.  The **common-leader oracle** restricts the coalition support
to `C_x intersect C_z` and maximizes

```text
alpha_r-max_(i != r)alpha_i.                         (CLO)
```

The first is the strongest root-deletion ceiling certificate; the second is
the correct feasibility test for a useful positive-root pair lift.  Exact
rational optimization gives the following maximum-overlap-root map.  A dash
means that no normalized top over-cover supported entirely on common hinges
exists.

| branch | root(s) | minimum deleted load; common? | maximum common leader gap |
|---|---:|---|---|
| optimized label-free | 3 | `5/9`; no | -- |
| actual-top-fixed | 0, 2 | `1/2`; no | -- |
| top-and-bottom-fixed | 4, 5 | `1/2`; no | -- |
| coefficient two | 3 | `1/3`; yes, tied | `1/3` |
| coefficient two | 5 | `1/3`; yes, tied | `0` |
| primitive coefficient seven | 6 | `6/13`; yes | `1/13` |
| sharp `G(2,4)` | 0 | `3/16`; yes | `1/16` |
| sharp `G(3,3)` | 0 | `2/9`; yes | `1/9` |
| neutral rectangle | 3 | `1/2`; yes, tied | `0` |

The coefficient-two root `3` is the important correction.  One
minimum-deleted-load optimum has no strict leader, but another common
over-cover has

```text
eta=1/3,
alpha=(0,0,1/3,2/3,0,0,0),
lambda_24=lambda_44=lambda_79=1/3.
```

It has common-leader gap `1/3`, yields `delta=1/2`, and its pair-lift row is
active at both `x` and `z`.  Thus minimizing deleted load first can hide a
useful exact-cone facet-candidate packet.  Conversely, the neutral control proves that
a common certificate can exist while every such certificate has nonpositive
leader gap.  The first three controls prove a different obstruction: they
have no common top over-cover at all.  The missing gluing result therefore
has at least three real branches:

1. a strict common leader, where `(OCPL)` supplies a positive-root packet;
2. a common but necessarily tied root, where direct common-hinge or later
   staged rows must close the target; and
3. no common over-cover, where noncommon Lmax mass must be paid for before
   pair-lift coupling is available.

This is a finite hostile classification, not a proof that these branches
close `(H)` in general.  It does, however, rule out a local maximum in which
one optimizes `theta_-` and inspects only the returned optimal support.

Reproduce the exact witnesses and the fixed-game common-leader exclusions by

```bash
python3 verifiers/divergence/audit_overcover_pair_lift_coupling.py \
  --output verifiers/divergence/overcover_pair_lift_coupling.json

PYTHONPATH=verifiers/divergence /tmp/coop-paper5-review/bin/python \
  verifiers/divergence/verify_overcover_pair_lift_coupling_z3.py \
  --output verifiers/divergence/overcover_pair_lift_coupling_z3.json
```

The second command independently reformulates every optimum and
infeasibility in exact Z3 linear arithmetic.  For an optimum it checks both
feasibility at the reported rational value and unsatisfiability of a strict
improvement; the two formulations agree on all eleven roots.  It also
independently confirms indecomposability of `(C2F1)--(C2F2)`.

### Theorem (common-support deficiency dual)

Let `C_z` be the proper coalitions tight at `z`, let `H` be the Lmax top
block, and put

```text
d_S=x(S)-v(S)>=0                 (S in C_z).
```

The least possible hinge surplus of a normalized top over-cover is

```text
epsilon_*=min sum_(S in C_z)d_S lambda_S             (CSD-P)

subject to
sum_S lambda_S 1_S=eta 1_N+alpha,
sum_(i in H)alpha_i=1,
lambda,eta,alpha>=0,             supp(alpha) subset H.
```

Its exact player-price dual is

```text
epsilon_*=max t                                         (CSD-D)

subject to
y(S)<=d_S                  (S in C_z),
y(N)>=0,
y_i>=t                     (i in H),
y in R^N, t in R.
```

Moreover

```text
epsilon_*=0  iff  a normalized top over-cover supported on
                   C_x intersect C_z exists.            (CSD0)
```

#### Proof

The first display is the ordinary normalized over-cover LP with objective
equal to its weighted Lmin slack.  Give the player incidence equalities dual
prices `y_i` and the normalization equality dual price `t`.  The `lambda_S`,
`eta`, and `alpha_i` columns respectively give

```text
y(S)<=d_S,       -y(N)<=0,       -y_i+t<=0,
```

which is `(CSD-D)`; rational LP strong duality applies because the primal is
feasible and has nonnegative objective.  Since every summand
`d_S lambda_S` is nonnegative, objective zero is equivalent to every
positive-weight coalition satisfying `d_S=0`, exactly common tightness.
QED.

Thus “no common over-cover” is not a qualitative support accident.  It has a
canonical nonnegative deficiency `epsilon_*` and an exact separating
player-price witness.

### Theorem (noncommon surplus defect of a pair lift)

Take any normalized top over-cover, not necessarily common, and write

```text
epsilon=alpha.x-M=sum_S lambda_S[x(S)-v(S)].
```

For a top root `r`, put

```text
theta_-=max_(i != r)alpha_i,
b_i=theta_--alpha_i              (i != r),
a_r=alpha_r-theta_-,

kappa_r=theta_- T-M-sum_(i != r)b_i v({r,i}).         (NSA)
```

Then `kappa_r>=0`; it is the scaled exact-game slack of the rooted pair lift.
Its two selection-visible expressions satisfy

```text
sum_(i != r)b_i z_i-a_r z_r-sum_(i != r)b_i v({r,i})
   =kappa_r,                                             (NSAz)

sum_(i != r)b_i x_i-a_r x_r-sum_(i != r)b_i v({r,i})
   =kappa_r-epsilon.                                     (NSAx)
```

Equivalently, the common tangent law `(OCD)` acquires exactly one defect:

```text
sum_(i != r)b_i(x_i-z_i)=a_r(x_r-z_r)-epsilon.          (NSAD)
```

Consequently this noncommon pair lift supplies the same valid rooted
pair-floor inequality at Lmin exactly when

```text
kappa_r>=epsilon.                                       (ABS)
```

#### Proof

Normalize by `theta=eta+theta_-` as in `(OCP)`.  No common-tightness premise is
needed to obtain a rooted packing.  Multiply its `(RPL)` exact-game slack by
`theta`.  Since every supported coalition is `z`-tight,

```text
sum_S lambda_S v(S)=eta T+M,
```

and the scaled slack reduces to `(NSA)`, proving nonnegativity and `(NSAz)`.
At `x`, the same support evaluation is larger by exactly `epsilon`, proving
`(NSAx)`.  Subtraction gives `(NSAD)`, and `(ABS)` is just nonnegativity of
the Lmin-side expression.  QED.

This theorem subsumes the common case `epsilon=0`, but it also pinpoints why
common support mattered: noncommon mass consumes exact-cone facet slack
one-for-one.  The remaining root-selection question is no longer “find a
common certificate”; it is “find a certificate/root whose pair-lift slack
absorbs its deficiency, or pay the unabsorbed defect with additional staged
rows.”

The unrestricted absorption claim is false.  Null-pad the exact five-player
control at `verifiers/s5close/completeness3.json`, `$[3].audit`.  The padded
six-player core forces the new payoff to zero and preserves

```text
x=(43/280,43/280,47/280,21/80,21/80,0),
z=(1/10,29/140,31/140,33/140,33/140,0).
```

Its minimum deficiency is `epsilon_*=3/112`; both top roots `3,4` have
`kappa_r=0`, so `(ABS)` fails at every top root.  Its overlap is `25/28`, well
above the six-player target `2/3`; the null-player descent sends it to the
proved five-player theorem.  Hence any absorption-root lemma needed for the
all-`n` proof must be stated only after the zero-floor/null-player branch is
removed.  Positive Lmin floor is not cosmetic.

On the 374 archived six-player games, the minimum-dispersion certificate is
also minimum-surplus in all 374 cases; 73 have positive `epsilon_*`, and some
top root satisfies `(ABS)` in all 374.  The three noncommon hostile controls
have

```text
epsilon_* = 17/36, 1/4, 3/4,
```

and each has at least one absorbing top root.  These are exact finite facts,
not a positive-floor absorption theorem.

### Proposition (best possible single capped spectral anchor)

The scalar spectral route can be optimized exactly, so it need not be left
as a choice of a convenient over-cover.  Apply the perspective scaling

```text
L=lambda/theta,       e=eta/theta,       u=alpha/theta,
theta=max_i alpha_i.
```

Then the largest sharpened spectral excess obtainable from any one top
over-cover is the linear-program value

```text
R_*=max sum_(i in H)u_i(x_i-mu)                       (BSA)

subject to
sum_S L_S 1_S=e 1_N+u,
0<=u_i<=1             (i in H),
L,e>=0,               supp(u) subset H.
```

For a positive optimum the cap is saturated, and conversely normalizing by
`sum_i u_i` recovers a top over-cover.  Hence

```text
R_*=max_over_overcovers (M+epsilon-mu)/theta.
```

This proves that `(BSA)` is the strongest possible input to the existing
single-anchor rearrangement theorem.  It still misses the hybrid target on
all three noncommon hostile controls:

| branch | best spectral bound | hybrid target | shortfall |
|---|---:|---:|---:|
| optimized label-free | `605/36` | `35/2` | `25/36` |
| actual-top-fixed | `39/2` | `21` | `3/2` |
| top-and-bottom-fixed | `47/2` | `49/2` | `1` |

It also misses the neutral tied-common control.  Thus neither choosing a
different over-cover nor optimizing surplus and dispersion jointly can
rescue a one-scalar spectral proof.  The required advance is genuinely a
multirow rooted/staged gluing theorem.

Reproduce the deficiency, absorption, negative-control, and best-anchor
audits by

```bash
PYTHONPATH=verifiers/divergence python3 \
  verifiers/divergence/audit_surplus_absorption.py verifiers/s6 \
  --output verifiers/divergence/surplus_absorption_audit.json

PYTHONPATH=verifiers/divergence /tmp/coop-paper5-review/bin/python \
  verifiers/divergence/verify_surplus_absorption_z3.py \
  --output verifiers/divergence/surplus_absorption_z3.json
```

The second formulation independently checks every fixed-control deficiency
optimum and every best-anchor optimum by feasibility at the reported rational
value plus unsatisfiability of a strict improvement.

This extra term is exactly the coalition premium lost when the exceptional
root is transported through a deficit singleton.  For any nonempty set `J`
of deficit players, add the zero incidence relation

```text
e_r+sum_(i in J)e_i-1_({r} union J)=0
```

to `(RMS)` with multiplier `delta`.  The exceptional set moves from `{r}`
to `{r} union J`, while the induced exact-game inequality weakens by

```text
delta [v({r} union J)-v({r})-sum_(i in J)v({i})].    (ETP)
```

The bracket is nonnegative by total balancedness and equals
`delta v({r} union J)` under singleton normalization.  Thus `(PFRDB)` retains
precisely the single-player transport premiums that the canonical
semi-balanced decomposition otherwise loses.  In all eight nontrivial
hostile/sharp cuts the exact replay verifies `(PFRDBx)`; seven are equalities
and the neutral-endpoint control has slack `9/9523`.  Both sharp orientations
remain equalities because every relevant root--outside pair has value zero.

### Theorem (rooted vertices are singleton-exceptional systems)

The rooted packing has an exact, rather than metaphorical, interface with
the exact-game cone.  Identity `(RMS)` holds coordinate by coordinate.  If
`u` is a vertex of
`K_r`, delete its zero coefficients and collect any repeated singleton
columns.  The remaining incidence columns are linearly independent.  Hence:

- if `delta>0`, their support is a purely min-semi-balanced system in the
  terminology of Studeny--Kratochvil, with unique exceptional coalition
  `{r}`;
- if `delta<=0`, after omitting the zero root coefficient when necessary,
  their support is min-balanced.

For `n>=3`, the system in the first case defines a facet of the full exact
game cone if and only if it passes the published indecomposability test.
Consequently vertex enumeration in `K_r`, singleton-slack completion by
`(RMS)`, and exceptional-set decomposition testing form an exact finite
algorithm for all singleton-exceptional facet candidates exposed by the
chosen Lmin menu.  This is a candidate-enumeration and facet-testing theorem,
not a claim that every rooted packing cut is a facet or that this menu sees
every exact-cone facet.

#### Proof

The root coordinate of `(RMS)` is `p_r-delta=1`; every other coordinate is
`p_i+q_i=1`.  Introduce the nonroot slack variables `q`.  The map
`u -> (u,q)` identifies `K_r` with the standard-form polyhedron

```text
A_(N\{r})u+q=1,                 u,q>=0.
```

At a vertex the columns belonging to positive variables are linearly
independent.  Adding `e_r` when `delta!=0` preserves independence because
its restriction to the nonroot rows is zero.  Thus all displayed nonzero
columns are linearly independent and their union is `N`, by `(RMS)`.
Lemma 2(c) of Studeny--Kratochvil therefore makes the support
min-semi-balanced.  A positive `delta` gives its sole negative coefficient
to `{r}`, so the system is purely min-semi-balanced; a nonpositive `delta`
leaves a conic identity and hence a min-balanced system.  The final facet
claim is exactly their indecomposability theorem.  QED.

The distinction in the last paragraph is active, not cosmetic.  The exact
replay currently produces eight nontrivial cuts across the hostile and sharp
controls.  Every completion satisfies `(RMS)`, has full support rank, and is
purely min-semi-balanced.  The published exceptional-set test nevertheless
finds a decomposition for all eight.  An independently formulated Z3 check
agrees with the exact-LP decomposition counts.  Thus the singleton-slack
versions explain the rooted budget without supplying full-cone facets; the
pair shear `(RPL)` is the essential change that produces the facet class.

### Corollary (positive-root cuts never lift to exact-cone facets)

Let `n>=3`, and suppose the projected witness inequalities hold at a point
with `x_r>0`.  No vertex of `K_r` has an indecomposable completion `(RMS)`.
Indeed, `delta<=0` gives a min-balanced system, whose inequality is not a
facet of the exact-game cone for `n>=3`.  If `delta>0`, `(RDBx)` and `x_r>0`
force `q_i>0` for some nonroot player `i`.  The completion then contains both
singletons `{r}` and `{i}`.  Linear independence excludes `{r,i}` from its
support, while

```text
e_r+e_i-1_{r,i}=0
```

makes `{r,i}` exceptional in the enlarged system.  This is a decomposition
in the exact sense of Studeny--Kratochvil.  QED.

Thus the rooted-packing construction yields a dimension-free relative
inequality theorem and an exact finite enumeration algorithm, but its
canonical singleton-slack lifts cannot be new exact-cone facets at the
positive roots relevant to hybrid overlap.  The rooted-pair shear `(RPL)`
supplies the required different coalition lift and its exact facet filter.
What remains is not to enumerate more singleton completions, but to prove
that sparse Lmax gluing selects enough of the pair-lift inequalities to pay
the universal hybrid target.

The remaining all-dimension problem is now more specific: prove a
spectral-or-rooted-packing disjunction whose packing branch supplies enough
`delta` and a sufficiently concentrated deficit vector `q`, or show that
direct common-hinge gluing already proves the target when no such
root-advantaged packing exists.  The actual-top-fixed hostile control is of
the latter type: its target follows before any witness-projection cut, so a
theorem demanding `delta>0` in every nonspectral branch would be false.

The theorem also sharpens the relative facet interface.  Each nonredundant
extreme packing gives a rooted two-selection inequality with at most `n-1`
coalition rows.  Exact rank tests decide whether it is a facet of the
projected common-hinge polytope, while `(RMS)` supplies its canonical
min-semi-balanced lift.  The separate indecomposability test decides whether
that lift is a facet of the full exact-game cone.

An independently formulated exact cutting-plane replay separates over
`K_r`, adds violated inequalities `(RHP2)`, and compares the resulting
two-generator minimum with the direct three-generator witness LP.  They agree
on every maximum-overlap root of six hostile branches (including the neutral
seven-player control) and both sharp orientations.  The neutral control needs
one two-coalition cut and returns `7/10`; the sharp orientations require
exactly one cut, supported on `4` and `3` block-star hinges respectively, and
recover `7/12` exactly.
Reproduce with

```bash
python3 verifiers/divergence/verify_rooted_hinge_projection.py \
  --output verifiers/divergence/rooted_hinge_projection.json
python3 verifiers/divergence/verify_rooted_hinge_decompositions_z3.py \
  --output verifiers/divergence/rooted_hinge_decompositions_z3.json
```

The replay also constructs `(RMS)`, verifies incidence rank and minimality,
and exhausts the exceptional-set decomposition test for every generated cut.
These are exact controls of the projection, support bound, and candidate
facet filter, not evidence that a target-proving extreme packing exists for
every game.

The reduction is sufficient, but deleting every Lmax row is false even in
the archive.  In `harvest6_602.json`, record `82`, the maximum-overlap-root
relaxation has exact minimum

```text
5/8<2/3
```

with no Lmax rows.  Its sparse over-cover support is `(23,27,35)`, its
complete Lmin support is `(24,27,35,40,49)`, and retaining only the common
coalitions `(27,35)` raises the exact minimum to `3/4`; the actual overlap is
`7/9`.  One support-minimal dual uses the common coalition
`35={0,1,5}`.  Hence the common-hinge gluing is not merely decorative: at
least one archived branch provably loses the target when it is removed.

An exact premise-ablation audit tested `(CHW)` at every maximum-overlap root
of all `374` archived six-player pairs.  All `703` rational LPs pass and the
minimum is exactly `2/3`.  The same script independently formulates the
specialized three-generator LP and cross-checks every full sparse-support
optimum against the general labelled-branch encoding.  Reproduce it with

```bash
python3 verifiers/divergence/audit_n6_sparse_lmax_complete_lmin_roots.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/n6_sparse_lmax_complete_lmin_roots.json
```

The common-hinge reduction also preserves the target on all five hostile
fixed branches and both sharp seven-player orientations.  In the two sharp
orientations it retains the exact root discrimination: the head root gives
`7/12`, while every non-head root gives `7/15` or `7/16`.  Reproduce those
exact controls with

```bash
python3 verifiers/divergence/verify_common_hinge_root_reduction.py \
  --output verifiers/divergence/common_hinge_root_reduction.json
```

These computations motivate the strictly smaller live target:

> **Common-hinge maximum-overlap conjecture.**  Every singleton-normalized
> exact game admits a complete staged Lmin support, a sparse Lmax top
> over-cover, and a root `r in argmax_i min(x_i,z_i)` for which the
> common-hinge relaxation `(CHW)` has minimum at least
> `n/floor(n^2/4)`.

In tangent variables, the missing human lemma is now a rooted common-hinge
charge theorem: derive `(RTB)` from `a(S)>=0` on the complete Lmin support,
the gluing equalities `a(S)=b(S)>=0` on `C_cap`, and the labelled
stratum/sign rows.  It must explain why the sparse ceiling support meets the
rooted pair-lift systems `(RPL)` with sufficient weighted pair premium.
One-sided pair lifts are available on all of `C_x`; precisely those supported
on `C_cap` transmit the same facet inequality to `z`.  The exact negative
control above shows that a theorem using the Lmin packet alone would be too
strong.

This gives a sharper exact-cone interface as well.  Common-hinge rows are
diagonal gluing rows between the two generator blocks.  Target-containing
positive circuits of the reduced rooted configuration enumerate irreducible
**relative common-hinge proofs**, still with linear support.  After projection
to characteristic-function coordinates, only factors whose coalition
coefficients are indecomposable semi-balanced systems are facets of the full
exact-game cone under the Studeny--Kratochvil criterion.  The reduction does
not prove that every relative circuit projects to a facet; it isolates the
small shared coalition set on which that projection and factorization must be
audited.

> **Theorem (relative common-hinge facet decision).**  Fix the ordered
> strata, hybrid sign cut, root, complete Lmin support, and sparse ceiling
> support.  The common-hinge feasible set `P_cap` defined by `(CHW)` is a
> rational polytope.  Validity of the target inequality on `P_cap`, its exact
> equality set, all equality vertices, and whether the target cuts a relative
> facet are decidable by finite exact rational linear algebra.  If `d_cap` is
> the affine dimension of `P_cap`, the target is a relative facet exactly
> when
>
> ```text
> min_(P_cap) c=0
> and dim(P_cap intersect {c=0})=d_cap-1.              (CHF)
> ```
>
> Every support-minimal validity proof is a target-containing positive
> circuit of the homogenized common-hinge row configuration.

#### Proof

All rows in `(CHW)` and all branch rows are rational.  Each of the three
generators is nonnegative with total one, so `P_cap` is a closed subset of a
product of simplices and is bounded.  Exact rational LP decides feasibility
and the target minimum.  On a zero minimum, append `c=0`; the affine hull of
the resulting rational face is obtained by exact row reduction after testing
which defining inequalities are equalities throughout the face.  The usual
polytope facet criterion is exactly `(CHF)`.  Its vertices are the basic
feasible solutions obtained from full-rank active-row subsets, hence are
rational and finitely enumerable.  Finally affine Farkas duality and support
minimality give the stated positive-circuit correspondence, exactly as in the
fully labelled branch-circuit theorem.  QED.

Consequently a fixed-`n` exact algorithm may enumerate common-hinge branches,
solve the target LP, enumerate the equality bases, and apply `(CHF)`.  For
each relative facet, eliminate the labelled generator coordinates and test
each resulting coalition system for semi-balanced indecomposability.  Only
the systems passing that last Studeny--Kratochvil test may be entered in the
full exact-cone facet catalogue.  This is an exact algorithmic/facet theorem;
it does not supply the missing dimension-free reason that every branch is
valid.

The next human step is therefore sharper than an unlabelled search for a
root.  For a maximum-overlap root, take the cone generated by the one-sided
pair-lift rows `(PFRDBx)` from vertices of `K_r`, their two-sided copies
`(PFRDBz)` when the support lies in `C_cap`, and the direct gluing,
stratum/sign and efficiency rows.  Prove that either the direct rows already
close `(RTB)`, or the target normal lies in this cone.  This **pair-lift
gluing disjunction** is now the minimal missing lemma: it names both the
full-cone facet atoms and their exact charge `q_i v({r,i})`.  The
actual-top-fixed control forces the direct branch; the two sharp families
force one indecomposable common-hinge pair lift at equality.

Reproduce the fixed-support staged checks, exact primal minima, exact Farkas
identities, and every one-witness relaxation with

```bash
python3 verifiers/divergence/verify_labelled_branch_duals.py \
  --output verifiers/divergence/labelled_branch_duals.json
```

This is strong falsification evidence for the new bridge, but only across
seven fixed circuit branches: five hostile obstructions and two equality
orientations.  It is not bounded-enumeration evidence for the all-`n`
conjecture.  The next mathematical task is to prove that every feasible
branch has a root distinguished by its indecomposable semi-balanced factors
for which `(OWC)` holds, or to find one exact labelled branch for which every
root has minimum below the sharp target.

The theorem must allow multiple rooted facets and fractional sharing of a
player between the two carrier roles.  It must specialize on `G(p,k)` to the
common-hinge systems in Section 2.  Any proposed version must first reject:

1. the exactified two-first-stage-packet obstruction (overlap `2/3`, trial
   overlap `1/2` before later-stage repair);
2. the two integral-carrier failures in Section 3;
3. the nonuniform seven-player majorization counterexample; and
4. both balanced seven-player orientations `(2,4)` and `(3,3)` at equality;
   and
5. the coefficient-two seven-player obstruction `(N7-TC)`, which the spectral
   anchor closes with four units of slack; and
6. the primitive coefficient-seven eight-player circuit `(N8-TC)`, whose
   spectral bound is `139/13>8`;
7. the optimized spectral-radius counterexample in Section 7;
8. the actual-top-fixed rearrangement counterexample; and
9. the top-and-bottom-fixed middle-rearrangement counterexample.

The program has advanced beyond a bare outcome D: the common-hinge theorem,
hinge-surplus spectral refinement, surplus dispersion budget, first-floor
transport theorem, projected staged-circuit classification, and sign-coherent
nested-incidence theorem are proved dimension-free.  The exact audit has now
disproved both `(UB)` and `(TC)`, then proved that even a support-minimal
eight-player circuit can force coefficient seven, and has now disproved every
partial relabeling shortcut through exact seven-player controls.  The final
all-`n` inequality remains open: the fully labelled dual coupling `(FLC)` is
not yet proved.  The one-witness reduction isolates a linear-support rooted
two-tangent budget `(RTB)`, and the common-hinge premise reduction now deletes
every Lmax row except shared tight coalitions.  That smaller system survives
all archived six-player roots, five hostile branches, and both sharp
seven-player equality orientations; an exact negative control proves that
deleting the common hinges entirely is invalid.  This is meaningful
structural progress and a substantially narrower missing lemma, but not yet
the requested central breakthrough.

## 9. Effective bipartition and its exact obstruction

The newest reduction separates the ceiling certificate into a primal
fractional role and a dual rooted price.  For a minimum-dispersion over-cover

```text
sum_S lambda_S 1_S=eta 1_N+alpha,
theta_+=max_i alpha_i,
a=min(1/theta_+,floor(n/2)),
u=a alpha,
```

one has the human incidence theorem

```text
0<=u<=1,  sum_i u_i=a,
a sum_S lambda_S 1_S+(1-u)=(1+a eta)1_N.              (EB1)
```

If `epsilon=sum_S lambda_S[x(S)-z(S)]`, evaluation at the two selections
gives

```text
u.x=a(M+epsilon),       u.z=aM,
(1-u).x=T-a(M+epsilon), (1-u).z=T-aM.                 (EB2)
```

The proposed scalar target was

```text
O/T>=1/a+1/(n-a).                                      (EB3)
```

Since `a<=floor(n/2)`, `(EB3)` would imply `(H)`.  It specializes to equality on
the balanced `G(p,k)` orientations, reproduces the starved-family failure at
five and equality at six, passes all `374` archived six-player pairs and the
named seven/eight-player hostile controls, and fails on `12` of `124`
distinct five-player pairs.  Those finite facts did not detect the following
exact seven-player counterexample.

Let

```text
g=(12/17,4/17,0,1/17,0,0,0),
h=(0,0,6/23,0,6/23,10/23,1/23),
v(S)=min(g(S),h(S)).                                  (EB6)
```

The two generators have common total one, are core points, attain every
coalition worth between them, and have coordinatewise minimum zero.  Thus
`v` is singleton-normalized and exact directly from the definition.  Fourteen
solver-free staged identities and an independent exact staged encoding give

```text
x=(227/782,48/391,48/391,1/34,48/391,13/46,1/34),
z=(91,12,90,12,90,91,5)/391.                         (EB7)
```

Exact primal and dual incidence witnesses give

```text
theta_+=3/5,   a=5/3,
alpha=(2/5,0,0,0,0,3/5,0),
y=(-3,-1,1,-1,1,2,1)/5,   q=e_5.                    (EB8)
```

Nevertheless

```text
O=613/782 < 63/80=1/a+1/(7-a)                       (EB9)
```

with exact margin `-113/31280`.  Player `5` is both the atomic dispersion
root and a ceiling root, so even root coalescence does not repair `(EB3)`.
The main target remains safe with margin `613/782-7/12=941/4692`.

The dispersion cap itself has the exact player-price dual

```text
theta_+=max t
y(S)>=0                 (S proper and z-tight),
y(N)<=0,
t+y_i<=q_i              (i in the Lmax top block),
q>=0, sum_i q_i<=1.                                    (EB4)
```

This follows directly by rational LP duality.  Complementary slackness makes
`y(S)=0` on every positively weighted over-cover coalition and supports `q`
on coordinates with `alpha_i=theta_+`.  Consequently `theta_+` is a
combinatorial invariant of the labelled Lmax top block and its complete
tight-coalition incidence hypergraph.  Adding a tight coalition can only
lower it.  This is the missing sensitivity datum in the earlier fixed-cap
one-witness relaxation.

The exact audit

```bash
python3 verifiers/divergence/audit_overcover_dispersion_dual.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/overcover_dispersion_dual_audit.json
```

checks strong duality and complementary slackness on all `374` archived
six-player records.  Although every record admits an atomic optimal price
`q=e_r`, three have no atomic price root which is also a ceiling root
`x_r>=M`; the optimized seven-player spectral obstruction has the same
separation.  Thus identifying the two distinguished roots is another false
shortcut.

The proposed **price-completed fractional-role coupling lemma** was to combine
`(EB1)--(EB2)`, the optimal dispersion prices `(EB4)`, and the complete
sign-coherent staged Lmin packet to prove

```text
a(n-a)O>=nT.                                           (EB5)
```

`(EB9)` refutes this lemma with every stated premise present.  The
record-13 boundary remains a separate warning that omitting dispersion
optimality is insufficient, but adding that optimality does not restore
`(EB5)`.

For fixed `n`, `(EB4)` still improves the exact diagnostic interface:
enumerate a
complete labelled tight hypergraph, solve one rational primal/dual incidence
pair for `theta_+`, and test any proposed linear inequality on each rooted
staged branch.  It now returns `(EB6)--(EB9)` as a substantive separating
model for `(EB5)`.

The live direction is weaker and genuinely disjunctive.  The positive hinge
surplus in `(EB6)` is `9/170`; the proved sharpened spectral theorem gives
overlap floor `234/391>7/12` and closes the example.  Conversely, the three
named seven-player spectral obstructions are closed by their labelled
common-hinge branches.  The next candidate is therefore:

> **Spectral-or-common-hinge conjecture.**  Failure of the sharpened spectral
> floor at the universal target forces a maximum-overlap rooted common-hinge
> branch whose exact minimum attains that target.

This conjecture asks only for `(H)`, not the false dispersion-dependent floor.
It must use the complete staged Lmin packet on the second branch and preserve
the actual labels.  Target-containing positive circuits still classify its
irreducible relative branch proofs.  Only projected coalition systems which
pass the published indecomposable semi-balanced criterion may be called
facets of the full exact-game cone.

Reproduce the exact counterexample with

```bash
python3 verifiers/divergence/verify_n7_effective_bipartition_counterexample.py \
  --output verifiers/divergence/n7_effective_bipartition_counterexample.json
```

## 10. Exact label currency and the surviving disjunction

The spectral relaxation forgets labels in two distinct steps.  Both losses
have exact nonnegative currencies.

Fix the actual Lmax top block `H`.  Let `B_*` be the sharpened spectral bound,
minimized over every top assignment allowed by the over-cover anchor, and let
`B_H` be the same expression with the actual block `H` fixed.  Then

```text
O = B_* + C_top + C_label,
C_top=B_H-B_*>=0,
C_label=O-B_H>=0.                                    (LC1)
```

The first currency is the price of forgetting which Lmin labels occupy the
actual ceiling block.  The second is the price of oppositely rearranging the
remaining labels.

### Theorem (threshold label currency)

Let `R=N\H`, `m=|R|`, and for `t>=0` put

```text
X_t={i in R:x_i>=t},       Z_t={i in R:z_i>=t}.
```

Then

```text
C_label = integral_0^infinity
  [ |X_t intersect Z_t|-max(0,|X_t|+|Z_t|-m) ] dt.   (LC2)
```

In particular the integrand is a nonnegative integer.  On a fixed pair of
ordered payoff partitions, `(LC2)` is a finite nonnegative linear form in
the consecutive merged Lmin/Lmax stratum gaps.

#### Proof

The layer-cake identity gives

```text
sum_(i in R) min(x_i,z_i)
 = integral_0^infinity |X_t intersect Z_t| dt.        (LC3)
```

At every threshold, two subsets of an `m`-element set with cardinalities
`|X_t|` and `|Z_t|` have intersection at least
`max(0,|X_t|+|Z_t|-m)`.  Opposite sorting attains these lower bounds
simultaneously at every threshold, so its overlap is the integral of that
Frechet minimum.  Subtracting gives `(LC2)`.  The upper sets change only at a
coordinate of `x` or `z`; splitting the integral at those finitely many
levels gives the final linear-gap statement.  QED.

There is a more revealing form of the integrand.  Partition `R` at threshold
`t` into

```text
A_t=X_t intersect Z_t                    (high in both),
D_t=R\(X_t union Z_t)                    (low in both),
```

and the two mixed cells.  Since

```text
|X_t|+|Z_t|-m=|A_t|-|D_t|,
```

one gets the exact capacity identity

```text
C_label=integral_0^infinity min(|A_t|,|D_t|) dt.      (LC5)
```

Thus label currency is literally the total threshold capacity for matching a
simultaneously high player to a simultaneously low player.

### Theorem (all high--low rectangles are staged-available)

For every residual player put

```text
a_i=min(x_i,z_i),              b_i=max(x_i,z_i).
```

Player `i` lies in `A_t` exactly when `t<=a_i`, and player `j` lies in `D_t`
exactly when `b_j<t`.  Hence whenever `b_j<a_i`,

```text
I_(i,j)=(b_j,a_i]                                      (HR)
```

is a unit high--low rectangle under the capacity integrand `(LC5)`.
Moreover `x_j<=b_j<a_i<=x_i`, so `x_j<x_i`.  The complete strict Lmin
support theorem below therefore supplies the ordered pair `(i,j)`.  Thus
neutral players (`x_j=z_j`) are legitimate rectangle endpoints; restricting
to opposite signs of `x-z` discards valid staged-available rectangles.

#### Proof

The threshold assertions follow directly from the definitions of `a_i` and
`b_j`.  The displayed chain proves strict Lmin order compatibility.  Applying
the complete-support theorem gives a normalized staged relation for `i` with
positive auxiliary coefficient on `j`; clipping the geometric carrier to
`(HR)` preserves the unit-rectangle property.  QED.

### Theorem (canonical rectangles saturate label currency)

Order the residual `a`-values downward and the residual `b`-values upward,
with arbitrary deterministic tie breaking:

```text
a_[1]>=...>=a_[m],              b_[1]<=...<=b_[m].
```

For each rank `k` with `b_[k]<a_[k]`, give the rectangle
`(b_[k],a_[k]]` weight one.  Then at every threshold `t` their occupancy is

```text
#{k:b_[k]<t<=a_[k]}=min(|A_t|,|D_t|).                (CS1)
```

Consequently

```text
sum_(k=1)^m (a_[k]-b_[k])_+ = C_label,               (CS2)
```

and the complete staged-available rectangle packing has optimum exactly
`C_label`.

#### Proof

Because both sorted conditions select initial rank segments,
`{k:a_[k]>=t}` has size `|A_t|`, `{k:b_[k]<t}` has size `|D_t|`, and their
intersection has the smaller of those two sizes.  This is `(CS1)`.
Integrating it proves `(CS2)`.  The rectangles are staged-available by the
preceding theorem and feasible because their occupancy equals the capacity
on every layer.  Conversely `(LC7)` bounds every feasible packing by
`C_label`.  QED.

This theorem is important but negative for the proof program: complete
carrier packing does not lower-bound label currency by a new quantity; it
reconstructs label currency identically for every pair `x,z`.  Therefore
`B_H+nu=B_H+C_label=O`, and asking the complete packing to pay the overlap
deficit is exactly `(H)` again.

### Corollary (fractional interval packing)

Let `E` be any collection of such residual carrier intervals and give
interval `e` weight `rho_e>=0`.  If at every threshold

```text
sum_(e:t in I_e) rho_e <= min(|A_t|,|D_t|),           (LC6)
```

then

```text
sum_e rho_e |I_e| <= C_label.                         (LC7)
```

This is immediate by integrating `(LC6)` and interchanging the finite sum
and integral.

### Theorem (exact interval-packing min--max and integrality)

Fix `x,z`, the residual player set `R`, and a finite family `E` of residual
carrier intervals.  Let

```text
0=beta_0<beta_1<...<beta_L
```

be the distinct residual coordinates of `x,z` (with zero adjoined), put
`J_l=(beta_(l-1),beta_l]`, `Delta_l=beta_l-beta_(l-1)`, and let

```text
A_(l,e)=1[J_l subset I_e],
c_l=min(|A_t|,|D_t|) on J_l.
```

Then the largest label-currency amount certifiable by `E` is exactly

```text
nu(E,c)
 = max  sum_e |I_e| rho_e
       A rho<=c, rho>=0

 = min  sum_l c_l p_l,                              (IPD)
       sum_(l:J_l subset I_e) p_l>=|I_e|  (e in E),
       p>=0.
```

Moreover:

1. `A` is totally unimodular.  Since `c` is integral, the packing problem
   has an integral optimal extreme point, and one may choose such an optimum
   with at most `rank(A)<=L` positive interval weights.
2. If all payoff coordinates are rational, both sides of `(IPD)` are
   computable by an exact rational linear program in time polynomial in the
   displayed input.  After clearing the common payoff denominator, the cover
   problem also has an integral optimal extreme point.
3. The layer-width vector `p_l=Delta_l` is always cover-feasible and has cost

   ```text
   sum_l c_l Delta_l=C_label.
   ```

   Hence `nu(E,c)<=C_label`, as required by `(LC7)`.  Equality holds exactly
   when some feasible packing saturates every positive-width layer with
   `c_l>0`.
4. If exogenous interval bounds `0<=rho_e<=b_e` are included, the augmented
   constraint matrix remains totally unimodular.  Integral `b,c` still give
   integral vertices; arbitrary rational bounds still give an exact
   polynomial-time primal--dual certificate.  The staged coefficients below
   do not produce such finite bounds: their normalized supply collapses to
   support.

#### Proof

Every column of `A` consists of one consecutive block of ones.  For any
subset of rows, order the selected rows by threshold and give them alternating
signs.  The signed sum in each interval column is `0`, `1`, or `-1`.
The Ghouila--Houri criterion therefore proves total unimodularity.  Appending
unit rows for supplies preserves total unimodularity.

Linear-programming duality gives `(IPD)`.  Total unimodularity and integral
right-hand sides give integral primal vertices.  After multiplying all
payoffs by a common denominator, every interval length is integral; total
unimodularity of the transposed cover matrix gives the dual integrality
claim.  An extreme packing with more than `rank(A)` positive variables would
have a nonzero support-preserving kernel perturbation and would not be
extreme.  Finally,

```text
|I_e|=sum_(l:J_l subset I_e)Delta_l,
```

so `p=Delta` is feasible.  Its cost is `(LC5)`.  Since every `Delta_l>0`,
equality with that cost holds precisely when no capacity is left unused on a
positive-capacity layer.  QED.

### Corollary (rooted threshold-potential form)

The cover in `(IPD)` is a network-potential problem.  Define

```text
P_k=sum_(l=1)^k p_l,       r_k=P_k-beta_k,       r_0=0.
```

If `I_e=(beta_s,beta_t]`, its cover constraint becomes

```text
r_t>=r_s.                                             (RP1)
```

Nonnegativity of the layer price becomes

```text
r_l-r_(l-1)>=-Delta_l.                                (RP2)
```

The cover objective is exactly

```text
C_label+sum_l c_l(r_l-r_(l-1)).                       (RP3)
```

Thus a failure to recover all label currency is witnessed by a rooted
potential satisfying `(RP1)--(RP2)` with a negative capacity-weighted
increment in `(RP3)`.  The zero potential is the canonical full-currency
cover.

A feasible cover is a vertex precisely when its tight-edge graph on the
threshold nodes `{0,...,L}` is connected, where a tight `(RP2)` is the path
edge `(l-1,l)` and a tight `(RP1)` is the carrier edge `(s,t)`.  Consequently
every extreme cover has a rooted spanning-tree certificate.  Conversely,
choose a spanning tree of path and carrier edges, impose its equalities,
solve for `r`, and retain the solution exactly when all remaining inequalities
hold; this enumerates all extreme covers (with possible duplicates from
degeneracy).

Indeed, after fixing `r_0=0`, the active constraint rows are reduced
node--arc incidence vectors.  They have rank `L` exactly when their
underlying graph is connected.  This proves the vertex criterion and gives a
second, network-matrix proof of integrality.  It also identifies the precise
rooted object produced by the interval theory: a threshold tree, not yet an
indecomposable semi-balanced coalition system.

### Exact fixed-stratum algorithm and facet boundary

For fixed payoff strata and any deliberately restricted rectangle family,
`(IPD)` is an exact diagnostic algorithm:

1. construct the merged threshold layers and their integer capacities;
2. construct the chosen clipped high--low rectangles;
3. solve the rational packing and cover pair and retain both checkable
   certificates;
4. compare the restricted optimum with the canonical full-currency packing;
5. lift the resulting incidence inequality and apply the published
   indecomposable semi-balanced-system test before calling it a facet of the
   exact-game cone.

The interval matrix proves integrality and sparsity only for the relative
threshold-packing problem.  Its threshold rows are not coalition-incidence
rows, and a support-minimal interval cover need not lift to an indecomposable
semi-balanced system.  Thus this is a fixed-stratum algorithmic theorem and a
facet-generation interface, not yet a facet characterization of the full
exact-game cone.  For the complete staged-available family, the canonical
rank pairing gives the optimum in sorting time and the interval LP adds no
inequality.  No polynomial full facet-enumeration claim follows.

### Theorem (cellwise pullback and an exact fixed-`n` decision algorithm)

Fix `n` and refine the singleton-normalized exact-game cone into rational
polyhedral cells on which all of the following data are fixed:

- active staged bases and tight-coalition hypergraphs for Lmin and Lmax;
- payoff orders and equality strata;
- the actual Lmax ceiling block and the minimizing spectral branch;
- the strict comparisons among the `a_i` and `b_j` endpoints.

On each such cell, `x`, `z`, every threshold endpoint `beta_l`, `B_H`, and
`delta` are rational linear functions of the game coordinates, while the
capacity vector and rectangle incidence matrix are constant.  For every
rooted spanning tree in a restricted threshold-potential graph,
solving its tight equalities makes `p` a rational linear function of those
coordinates.  The conditions that this tree solution is cover-feasible and
that

```text
sum_l c_l p_l>=delta
```

are therefore finitely many rational linear inequalities on the cell.
Enumerating the rooted trees and checking these inequalities by exact LP
decides the restricted interval-packing statement on that cell.  For the
complete family, canonical saturation reduces the displayed inequality to
`B_H+C_label>=nT/floor(n^2/4)`, the original hybrid-overlap target rather
than a new certificate.

Consequently, for every fixed `n`, universal validity of `(H)` is decidable
in principle by a finite rational polyhedral computation over selection
cells.  This is not advertised as an
efficient algorithm: the number of selection cells, staged circuits, and
trees can be exponential or worse.  Nor does a cellwise boundary inequality
automatically define a facet of the full exact-game cone.  A candidate full
facet must survive gluing across adjacent selection cells and its coalition
lift must be an indecomposable semi-balanced system.

#### Proof

Each egalitarian selection is obtained by a finite sequence of rational
linear programs.  Fixing their active bases makes their solutions rational
linear in the right-hand-side game coordinates; refining by the finitely many
order, sign, top-block, and spectral comparisons gives the asserted rational
polyhedral cells.  On a fixed cell all interval and capacity combinatorics are
constant.  The rooted-tree equalities are a nonsingular reduced incidence
system, so their solution is rational linear in the threshold endpoints.
All remaining feasibility and target tests are consequently linear.  There
are finitely many bases and trees at fixed `n`, and exact rational LP decides
each resulting implication on the cell.  QED.

This gives a finite exact fixed-`n` decision method, but the interval theory
does **not** answer the facet half.  Canonical saturation shows that its full
threshold-tree lift is only a decomposition of overlap.  Any distinguished
exact-cone inequality must instead use coalition information coupling the
sparse Lmax over-cover to the Lmin packet, then pass the usual gluing and
indecomposability tests.

For a restricted rectangle family `E`, the recoverable amount is equivalent
to either side of

```text
nu(E,c)>=delta

<=> every fractional threshold cover p has sum_l c_l p_l>=delta.  (IPC)
```

This is the sharp Hall-type gate for that restricted family.  For the full
family, canonical saturation gives `nu(E,c)=C_label`, so `(IPC)` supplies no
new gate for `(H)`.

This theorem puts the missing labelled information in the same coordinates
as the staged packets.  The sets `X_t` and `Z_t` are complements/unions of
their cumulative ordered strata, and common-hinge rows are the only retained
coalition rows which glue the two labelled tangent blocks.  On a fixed
branch, `C_top`, `C_label`, and the spectral deficit are all linear in payoff
stratum gaps.  Therefore the surviving target is exactly

```text
C_top+C_label >= max(0,nT/floor(n^2/4)-B_*).          (LC4)
```

Unlike the false `(EB5)`, `(LC4)` is not advertised as a theorem: it is an
identity-equivalent target.  Its value is structural.  It says precisely
what a common-hinge/rooted-circuit proof must purchase and removes the false
reciprocal-mass price.

The **complete-family** interval-packing lemma previously proposed here is
therefore closed as a tautological reformulation.  A deliberately restricted,
transport-oriented rectangle family could still yield a nontrivial sufficient
condition, but staged availability alone neither selects such a family nor
forces it to pay the deficit.  The minimal live lemma must use information
that the scalars `a_i,b_i` forget: a common tight-coalition/hinge constraint
linking the sparse Lmax over-cover weights to the complete staged Lmin
relations.  It must lower-bound `B_H+C_label` without merely naming its
canonical rectangle decomposition.

### Theorem (normalized coefficient supply collapses to support)

The word "from" in that lemma can be made exact.  Normalize each selected
sign-coherent staged relation by giving its forced player column coefficient
one.  Write either orientation uniformly as

```text
sum_S lambda_S 1_S
 +sigma(e_i+sum_(j in P)a_j e_j)=c 1_N,              (SCR)
```

where `sigma=1` for Lmin, `sigma=-1` for Lmax, and `lambda,a>=0`.  Call a
strict residual carrier `(i,j)` **available** if some normalized relation
`(SCR)` has `a_j>0`.  If interval weights are conservatively required to obey

```text
0<=rho_(i,j)<=a_(i,j),                                (SS1)
```

then, for any finite `rho>=0`, simultaneously chosen normalized relations
satisfying `(SS1)` exist if and only if every positive coordinate of `rho` is
an available carrier.  Thus the projection of the joint
staged-certificate/supply system onto the interval weights is exactly the
nonnegative orthant on the available-edge set.

#### Proof

Necessity is immediate.  For sufficiency, fix one target `i`, choose a
normalized relation witnessing each desired available carrier, and take a
strict convex combination of those finitely many relations.  The result is
still normalized and has positive coefficient on every desired carrier.  If
its coefficients are `(lambda,a,c)`, then for every `K>=1`

```text
lambda'_S=K lambda_S,
a'_j=K a_j                         (j != i),
a'_i=K a_i+(K-1),
c'=Kc
```

is again normalized: its left side is exactly `K` times the left side of
`(SCR)`.  Choose `K` large enough to dominate all desired weights and repeat
independently for every target.  QED.

The duplicate auxiliary copy of the forced player column absorbs the extra
`(K-1)e_i`.  This is a normalization trap with a useful conclusion: raw or
normalized circuit magnitudes cannot provide a universal congestion bound.
Only the zero/nonzero carrier-support pattern is invariant.

### Theorem (complete strict carrier support)

The available support itself is complete.  For every Lmin target `i` and
every player `j` with `x_j<x_i`, there is a normalized sign-coherent relation
for `i` whose auxiliary coefficient on `j` is positive.  For every Lmax
target `i` and every `j` with `z_j>z_i`, the mirror statement holds.

#### Proof

Suppose `x_j<x_i`.  Player `j` belongs to a strictly earlier Lmin block.
Take any normalized sign-coherent relation `R_i` that pins `i` and any such
relation `R_j` from the earlier stage.  Every coalition in both relations is
tight at the same point `x`, and all unit columns of `R_j` belong to the
cumulative lower set for `i`.  Hence

```text
R_i+tau R_j,       tau>0,
```

is a valid sign-coherent relation for `i`: its forced `e_i` coefficient
remains one, while the auxiliary coefficient of `e_j` is at least `tau`.
The Lmax relations have the common negative unit-column orientation, so the
same addition proves the mirror claim when `z_j>z_i`.  QED.

Consequently every clipped high--low rectangle is available through Lmin:

```text
E_full={(i,j): b_j<a_i},       I_(i,j)=(b_j,a_i].     (EFULL)
```

Indeed `x_j<=b_j<a_i<=x_i`.  Equality creates a zero-length rectangle and is
immaterial.  The opposite-sign carrier family used earlier is only a proper
subfamily in general: neutral players may be essential endpoints.

### Corollary (complete support packing is tautological)

Put

```text
delta=max(0, nT/floor(n^2/4)-B_H),
```

where `B_H=B_*+C_top` uses the actual Lmax ceiling block.  The proposed
remaining packet statement becomes

```text
nu(E_full,c)>=delta.                                  (SSP)
```

Canonical saturation gives `nu(E_full,c)=C_label`.  Therefore `(SSP)` is
equivalent to `B_H+C_label>=nT/floor(n^2/4)`, namely `(H)` itself.  It is not
a stronger intermediate lemma and cannot serve as its proof.

The full joint LP dual confirms the collapse.  Give capacity rows prices
`p_l>=0`, coefficient-supply rows prices `s_e>=0`, and the incidence equality
for target `q=(sigma,i)` a free vector `y^q`.  Its constraints are

```text
p(I_e)+s_e>=|I_e|,
y^q(N)=0,                    y^q(S)>=0  (S tight),
sigma y^q_j>=sum_(e=(q,j))s_e             (j in P),   (SSD)
```

and its objective is

```text
sum_l c_l p_l-sum_q sigma y^q_i.
```

Dot a normalized relation `(SCR)` with `y^q`.  All terms are nonnegative and
their sum is zero, so `sigma y^q_i=0`.  If `(q,j)` is available, use a
relation with `a_j>0`; then `sigma y^q_j=0` and hence `s_e=0`.  The dual
therefore reduces exactly to the ordinary threshold cover on `E_full`; its
canonical optimum is the width vector `p_l=Delta_l`.

The rooted incidence system and threshold tree interact **serially**, not by
a new continuous coefficient price: the complete staged theorem supplies all
high--low pairs and the canonical rank pairing exhausts every threshold
capacity.  There is no residual coefficient, support, or threshold-tree
pattern to classify as the missing facet.  This rules out that candidate
mechanism, not `(H)`.

The two hostile controls for which `delta>0` have exceptionally small exact
witnesses.  In the actual-top-fixed control, the Lmin relation

```text
1_{0,2,4}+1_{0,1,2,3,6}+1_{4,6}+2e_5+e_1+e_3=2 1_N
```

pins gainer `3` and supplies the interval `(x_5,x_3]=(1/2,8]`.  The old
opposite-sign packing already has exact optimum `15`, versus deficit `3/2`;
the corrected full rectangle optimum is also `15`.  In the
top-and-bottom-fixed control,

```text
1_{1,3,4,5,6}+e_2+e_0=1_N
```

supplies `(x_2,x_0]=(1/2,19/2]`; the old opposite-sign packing has optimum
`9`, versus deficit `1`, while the corrected full rectangle optimum is its
entire label currency `33/2`.  Every coalition displayed is tight at the
relevant Lmin point.  Exact packing/cover duals and staged-availability
witnesses are replayed by

```bash
python3 verifiers/divergence/verify_staged_interval_deficit_controls.py \
  --output verifiers/divergence/staged_interval_deficit_controls.json
```

These historical opposite-sign controls are retained as regression tests.
They do not prove `(H)`; the full canonical family saturates label currency
for every pair by the theorem above.

An exact seven-player neutral-stratum control shows why the correction is
necessary.  It has residual gainer `1`, loser `2`, and `x_1=x_2`, while
`z_1>z_2`; hence both old opposite-sign carrier intervals have length zero.
Nevertheless

```text
C_label=15167/38092,
```

and the canonical rectangles pair `(high 1,low 4)` and `(high 2,low 6)`,
with lengths `8081/38092` and `7086/38092`.  Their unit occupancy saturates
every nonzero threshold layer.  The displayed selections are certified by
fourteen solver-free staged identities and independently replayed by the
generic exact staged verifier.  Reproduce with

```bash
python3 verifiers/divergence/verify_n7_neutral_rectangle_control.py \
  --output verifiers/divergence/n7_neutral_rectangle_control.json
```

The control refutes only the opposite-sign restriction.  Its overlap exceeds
the main seven-player target by `43349/114276`.

### Multistage direct gluing

The direct-labelled arm of the surviving disjunction admits a clean
dimension-free master theorem.  Partition
`N=P disjoint-union G disjoint-union H`, with sizes `p,g,h>=1`, and put
`m=p+g`, `q=g+h`, `n=p+g+h`.  Let `P,H` be nongainers and `G` the gainers:

```text
z_i<=x_i on P union H,       x_i<=z_i on G.
```

Put `l=z(P)/p`, `b=z(G union H)/q`.  If `J` is a subset of `G`,
`s=|J|<g`, and `x(H union J)<=z(H union J)`, put

```text
B=g/(m-s),
R_x=x(J)+(1-B)x(G\J)-B x(P),
R_z=(1-B)[z(H)-hb]-B[z(J)-sb].
```

Direct substitution, with no stratum assumption on either selection, gives
the exact identity

```text
O-[1-gp/{q(m-s)}]T
 =[gpn/{q(m-s)}]l+B[z(H union J)-x(H union J)]
  +R_x+R_z.                                         (TDG)
```

Thus the weaker condition `R_x+R_z>=0` already implies

```text
O/T>=1-gp/[(g+h)(p+g-s)].                            (TDGB)
```

The comparison is automatic if `H union J` is Lmin-tight, since `z` is a
core allocation.  Equality in the bound requires `l=0`, a tight comparison,
and zero residual sum.  The bound reaches the target exactly when

```text
floor(n^2/4)gp
 <=[floor(n^2/4)-n](g+h)(p+g-s).
```

This criterion is a one-dimensional packet problem.  Put

```text
delta_i=z_i-x_i on G,       L_H=x(H)-z(H),
U_s={(p-s)x(G)-g x(P)+(p-s)[z(H)-hb]+gsb}/g.
```

Then exact cancellation gives

```text
z(H union J)-x(H union J)=delta(J)-L_H,
(m-s)(R_x+R_z)=g[U_s-delta(J)].
```

Hence the direct branch closes whenever some cardinality-`s` packet hits
`L_H<=delta(J)<=U_s`.  Arbitrary multistratum geometry has therefore reduced
to an explicit interval-hitting question on the gainer weights.

There is a useful ordinal sufficient condition for the residual signs:

```text
s<=p,
max x(P)<=min x(G),
max z(G)<=min z(H),
J consists of s lowest-z players of G.
```

Indeed `s<=p` gives `0<B<=1` and the Lmin order gives
`R_x>=[s+(1-B)(g-s)-Bp] average(x(P))=0`.  The Lmax order gives
`average(z(H))>=b>=average(z(G))`, while the lowest-`z` choice gives
`average(z(J))<=average(z(G))`; hence `R_z>=0`.  The exact residual criterion
is stronger: it can hold when `s>p` and without either displayed block order.

This gives a convenient upper-block corollary.  Let `L` be the nongainers,
choose a nonempty proper block `H subset L`, put `P=L\H`, and let `J` be the
`s` lowest-`z` gainers.  If

```text
s<=|P|,  max x(P)<=min x(G),  max z(G)<=min z(H),
H union J is Lmin-tight,
floor(n^2/4)|G||P|
 <=[floor(n^2/4)-n](|G|+|H|)(|P|+|G|-s),             (UBD)
```

then the target hybrid-overlap inequality holds.  Tightness makes the
comparison term nonnegative by core feasibility, the first line makes both
ordinal residuals nonnegative, and `(UBD)` is exactly the target cardinality
test.  This is a proved conditional handover, not a theorem that such an
upper block and packet must exist.

When `x` is constant on `P union G` and on `H`, and `z` is constant on `P`
and on `G union H`, both residuals vanish and `(TDG)` reduces to the earlier
two-stratum identity.  More importantly, the arbitrary-Lmax formula exactly
recovers both archived direct hostile certificates.  The actual-top-fixed
branch gives base `7/10`, `R_x=15/4`, and `R_z=111/20`.  The
top-and-bottom-fixed branch gives base `2/3`, `R_x=1`, and `R_z=11`; here
`s=3>p=1`, so only the exact residual criterion applies.

In interval form, the two packets are respectively `1/2` in
`[1/2,129/10]` and `3/2` in `[3/2,15/2]`; the fresh control is sharp at the
singleton interval `[1/2,1/2]`.

Exhausting all sign-compatible partitions and proper gainer packets on the
seven fixed hostile branch selections gives a clean finite atlas.  The five
nonsharp obstructions have direct bases `3/5`, `3/4`, `2/3`, `5/8`, and
`5/9` (the last at `n=8`); the first four comparisons are Lmin-tight, while
the last has direct slack `5/39`.  Neither sharp `G(2,4)` nor sharp `G(3,3)`
has any target-reaching direct packet.  Those are exactly the branches closed
at equality by the rooted block-star theorem.  The sum criterion matters:
the `3/4` certificate has `R_z=-15/2`, and the `5/9` certificate has
`R_x=-8/9`, although the respective residual sums are positive.  This finite
classification motivates the direct-or-rooted theorem but does not prove it.

A broader exact six-player census prevents a false extrapolation from those
seven rows.  Of 374 archived pairs, 296 admit a target-reaching direct packet
and 282 admit one whose comparison is Lmin-tight.  The other 78 have no
direct packet; 76 are strictly above `2/3`.  The first strict control is

```text
x=(1,2,1,1,1,1),
z=(3/2,3/2,3/2,5/6,5/6,5/6),
O/T=6/7.
```

Hence “nonsharp implies direct” is false.  The separately encoded
common-hinge/root audit closes all 374 archived pairs with minimum exactly
`2/3`.  The surviving candidate is genuinely disjunctive: direct packets
cover many branches, while rooted packets must also cover strict branches.

The ceiling-root interpolation theorem closes 28 of the 78 direct failures.
Of the 50 remaining rows, null-player descent removes all 34 zero-floor
cases.  The genuinely live archive region is only 14 strict positive-floor
cases in the interpolation wedge and two equality cases.  All 78 have a
ceiling root.  This finite decomposition identifies the live rooted-packet
region without pretending that the archive proves it exhaustive in general
dimension.

The sequential support audit sharpens this further.  Every one of those 50
pre-descent residual rows has a nonempty intersection between one complete
staged Lmin support and one sparse Lmax top over-cover, and its ceiling root
is the unique maximum-overlap root.  The common-support size is one on 45
rows, two on three, and three on two.  Every one of the 16 positive-floor
residuals has a common coalition containing that root, and the corresponding
rooted relaxation reaches `2/3`.  Deleting every Lmax row still leaves a
target-reaching complete-Lmin rooted packet on 13 of the 16.  Only three
rows require the common-hinge repair, and all three have a tied over-cover
root load; 15 of the 16 have a tied load in total.  Conversely, all 37
archive rows with empty common support were already closed by direct gluing
or ceiling interpolation.  This isolates the missing theorem as a
**root-price/common-repair lemma**: after null-player descent, failure of the
first two arms must force either a target-priced complete Lmin rooted packet
or a common root hinge whose reverse comparison repairs the deficit.  The
repair branch must cover tied roots.

The exact-cone audit is cleaner than the branch count suggests.  For each of
the 13 positive-floor rows closed by the complete Lmin packet alone, extract
one exact optimal one-witness Farkas dual, normalize its witness coefficients
to a point of `K_r`, and apply the rooted pair shear `(RPL)`.  Every resulting
system has full support rank and passes the Studeny--Kratochvil
indecomposability test: 13 facets and no decomposable row.  Up to relabeling
there are only five support orbits, with Lmin-only multiplicities
`3,4,3,2,1`.

The two-spoke repair facet belongs to the first orbit, and the irregular
three-packet facet belongs to the fourth.  Consequently all 16 live
positive-floor archive rows are carried by the same five indecomposable
rooted pair-lift support orbits, with combined multiplicities `5,4,3,3,1`.
An independently formulated exact-LRA replay proves all 282 unsupported
proper exceptional-set candidates infeasible across the five orbit
representatives.

This is finite structural evidence, not a six-player domain classification:
the archive is not exhaustive, and one extracted optimal dual does not prove
that every admissible branch selects one of the five supports.  It does
sharpen the missing theorem from an unnamed rooted packet to a
**marked-facet selection conjecture**: a positive-floor residual must expose
an indecomposable rooted pair lift together with Lmin-tight labels whose
canonical best marking is target-priced, with a common reverse row only when
its Lmin-only marked price is insufficient.  The facet normal by itself does
not retain this price.

The labelled packing/cover audit sharpens the finite diagnosis.  Every one
of the 16 positive-floor residual rows has an affordable canonical marked
row, including the three rows that still require common-hinge repair.
Therefore those three are not price failures: they are pure
stratum/sign-alignment failures.  Across the fixed seven-player
hostile/sharp suite, every branch either has a direct packet or an affordable
labelled row at a maximum-overlap root.  These are finite controls, not the
missing selection theorem.

A hostile audit tests the converse handover on the entire six-player
archive.  There are 233 rows for which **every** maximum-overlap root has an
unaffordable canonical labelled row; all 233 admit a target-reaching direct
packet.  The tempting deterministic rule `H=R`, with `R` the entire
maximum-overlap root block, is nevertheless false: it supplies an Lmin-tight
direct packet on 228 rows and fails on five.  In every one of the five exact
failures, adjoining one highest-`x` remaining nongainer to `R` leaves a
singleton lower block `P`; a one-gainer packet then has an Lmin-tight
comparison, zero `R_x`, positive `R_z`, and direct base `4/5`.  Thus the
finite handover is not a fixed-root-block theorem.  The surviving conjecture
must select an **upper nongainer block containing the roots**, and `(UBD)`
identifies the clean ordinal branch of that selection problem.  The 233-row
result remains archive evidence, not a six-player domain theorem.

The locked-pair theorem explains four of the five failures more sharply: in
those four rows the two maximum-overlap roots are each other's unique locked
partner.  They must enter `H` together, after which one further upper
nongainer completes the direct comparison.  The fifth failure has pair-free
roots.  Thus, after the dimension-free `|G|>=2` affordability theorem and the
one-pair locked-partner theorem, the genuinely unstructured price-failure
branch is the pair-free rooted hypergraph.

```bash
PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/audit_n6_positive_residual_facet_atlas.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/n6_positive_residual_facet_atlas.json

PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/audit_affordable_rooted_packing.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/affordable_rooted_packing.json

PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/audit_labelled_facet_cover_duality.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/labelled_facet_cover_duality.json

PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/audit_cover_to_direct_handover.py \
  verifiers/s6/harvest6_601.json verifiers/s6/harvest6_602.json \
  --output verifiers/divergence/cover_to_direct_handover.json

PYTHONPATH=verifiers/divergence:src python3 \
  verifiers/divergence/verify_complement_star_facets.py \
  --output verifiers/divergence/complement_star_facets.json

/tmp/coop-paper5-review/bin/python \
  verifiers/divergence/verify_n6_positive_residual_facets_z3.py \
  --output verifiers/divergence/n6_positive_residual_facets_z3.json
```

The rooted status of the sharp rows is nevertheless a theorem, not an atlas
inference.  If every Lmax coordinate is positive, then every nonempty `P`
has `l=z(P)/p>0`; hence `(TDG)` is strict whenever its comparison and
residual-sum payments are nonnegative.  Thus a game with `O=c_n T` and
strictly positive Lmax cannot admit a direct packet whose base reaches
`c_n`.  Balanced `G(p,k)` has `k(p+1)=floor(n^2/4)`, overlap `c_n T`, and
strictly positive Lmax.  Its rooted indecomposable block-star system is
therefore structurally necessary within the direct-or-rooted framework.

The handover extends to every `G(p,k)`, not only balanced equality.  In the
master theorem take `P=O`, `G=B`, `H={r}`, and `J=B\{b}`.  The comparison is
the common block-star hinge.  With
`d=[p(k-1)-1]/[k(p+1)]`, each gainer has gain `pd`, the root loss and packet
gain both equal `p(k-1)d`, and both residuals vanish.  Hence

```text
direct base=n/[(p+1)(k+1)],
rooted block-star base=n/[k(p+1)].
```

The direct arm reaches the target iff
`(p+1)(k+1)<=floor(n^2/4)`.  The rooted arm always reaches it because
`k(p+1)<=floor(n^2/4)`.  Thus the exact one-unit denominator shift explains
why sufficiently unbalanced parameters can be direct while near-balanced
parameters, including strict `G(3,2)` and sharp `G(2,4),G(3,3)`, require the
rooted facet.

In facet-price notation the two denominators are
`D_direct=(p+1)(k+1)` and
`D_root=p(k-1)+n-1=k(p+1)`, differing by exactly `p+1`.  The rooted
pair-spoke shear is the indecomposable semi-balanced atom that realizes the
smaller denominator; the direct identity retains the positive low-Lmax
payment on the outside block.  This makes the exact-cone role of the root
witness explicit rather than merely algorithmic.

This is not yet a selection theorem.  The remaining direct-arm gap is now
precise: prove that a complete staged Lmin packet supplies a target-reaching
cardinality-`s` gainer packet in `[L_H,U_s]`, or show that every interval miss
admits an affordable mixed-colour rooted packet.  No two-stratum Lmax premise
remains.

A fresh three-generator exact seven-player control with
`(p,g,h,s)=(3,2,2,1)` has

```text
(3,0,0,6,1,2,0),
(1,0,2,0,0,3,6),
(0,5,0,1,5,0,1),
x=(3/2,3/2,3/2,9/4,3/2,3/2,9/4),
z=(4/3,2,4/3,2,2,4/3,2).
```

Coalition `74={1,3,6}` is tight at both selections, so `(TDG)` reads

```text
O-(5/8)T=(21/8)z_0+(1/2)[z(74)-x(74)].
```

An exact verifier checks the arbitrary-Lmax identity on the two archived
branches, 1,080 two-stratum parameter rows, 680 nonuniform order rows, the
fresh lower envelope, fourteen staged selection certificates, and the fact
that every rooted branch relaxation has minimum `5/8`:

```bash
python3 verifiers/divergence/verify_two_stratum_direct_gluing.py \
  --output verifiers/divergence/two_stratum_direct_gluing.json
```

### Mixed-colour rooted packets: the first noncommon gluing theorem

The common-hinge projection is not the largest inequality obtainable from a
single singleton witness.  Its restriction to `C_x`, followed by transfer to
`z` only on `C_x intersect C_z`, unnecessarily discards packets containing
different coalitions tight at the two selections.  The following extension
is dimension-free.

> **Theorem (mixed-colour rooted packet).**  Let `v` be a
> singleton-normalized exact game, let `x,z` be core allocations, and fix a
> root `r`.  Exactness supplies a core allocation `w^r` with `w^r_r=0`.
> Let `D` be a finite multiset of tagged coalitions `(sigma,S)`, where
> `sigma` is `x` or `z` and `S` is tight at the tagged selection.  Suppose
> that nonnegative rational numbers `rho_(sigma,S)`, `q_i`, and scalars
> `xi,tau` satisfy
>
> ```text
> sum_((sigma,S) in D) rho_(sigma,S) 1_S + q
>     = xi 1_N + tau e_r.                            (MCP1)
> ```
>
> Then
>
> ```text
> sum_((sigma,S) in D) rho_(sigma,S) sigma(S) <= xi T. (MCP2)
> ```
>
> In particular, neither common support nor equality of `x(S)` and `z(S)`
> is required.

#### Proof

Dot `(MCP1)` with `w^r`.  Since `w^r(N)=T` and `w^r_r=0`, the right side is
`xi T`.  On the left, `q.w^r>=0` and

```text
w^r(S)>=v(S)=sigma(S)
```

for every tagged tight coalition.  Dropping the nonnegative singleton term
proves `(MCP2)`.  QED.

This is not a restatement of the common-hinge theorem.  A common hinge can
be tagged either colour and transfers the same coalition sum between the
selections.  A genuinely mixed packet may instead contain an `x`-only
coalition and a different `z`-only coalition; the common exactness witness,
not a common hinge, glues their values.

The packet family is complete for elimination of that witness.  Put

```text
p_i(rho)=sum_((sigma,S):i in S)rho_(sigma,S).
```

> **Theorem (exact mixed-witness projection).**  A vector `w>=0` with
> `w(N)=T`, `w_r=0`, and
>
> ```text
> sigma(S)<=w(S)                  ((sigma,S) in D)    (MWP1)
> ```
>
> exists if and only if, for every `rho>=0`,
>
> ```text
> sum_(sigma,S)rho_(sigma,S)sigma(S)
>   <=T max_(i != r)p_i(rho).                        (MWP2)
> ```

Necessity is the same weighted witness argument.  For sufficiency, the set
of tagged requirement vectors dominated by coalition sums of the rooted
simplex `{w>=0:w(N)=T,w_r=0}` is a closed convex down-set.  Separation of a
point outside a down-set has a nonnegative normal `rho`; the support function
of the rooted simplex is exactly the right side of `(MWP2)`, a contradiction.
Thus extreme points and rays of `(MCP3)` give a finite exact description of
the entire one-witness projection.

#### Projection, support, and exact-cone interface

Normalize the off-root load of a tagged weight vector by

```text
K_r^mix={rho>=0:
  sum_((sigma,S):i in S)rho_(sigma,S)<=1  (i != r)}. (MCP3)
```

Every vertex has at most `n-1` positive tagged coalitions.  Indeed, after
adjoining the off-root slack variables, `(MCP3)` is in standard form with
`n-1` equations, so the positive columns of a basic feasible solution are
linearly independent.  In particular, two differently tagged copies of the
same coalition cannot both be positive at a vertex.  Root-only columns give
the familiar rays and zero-right-hand-side inequalities.

For a normalized point put `p_i=sum_(sigma,S:i in S)rho_(sigma,S)`,
`q_i=1-p_i` off the root, and `delta=p_r-1`.  The incidence completion is

```text
sum_(sigma,S)rho_(sigma,S)1_S
 +sum_(i != r)q_i e_i-delta e_r=1_N.                (MCP4)
```

Thus the colour labels disappear under projection to characteristic-function
coordinates.  The same Studeny--Kratochvil classification applies to the
underlying coalition incidence system: `(MCP4)` gives a finite list of
min-balanced or singleton-exceptional min-semi-balanced candidates, and the
published indecomposability test decides which candidates are facets of the
full exact-game cone.  The rooted-pair shear can again replace singleton
slack by pair columns before that test.  What is new is the **relative
two-selection evaluation** of the same exact-game inequality: different
coalitions may be evaluated at different tight selections.

Consequently, for a fixed pair of staged supports, vertex/ray enumeration of
`K_r^mix`, exact branch gluing, and the indecomposability filter form an exact
finite algorithm for the whole one-witness mixed-packet projection.  This is
an algorithmic and support theorem; it does not assert that some root's
one-witness relaxation always proves the universal hybrid-overlap target.

#### The first noncommon packet

The optimized label-free spectral obstruction has a sparse one-witness proof
at root `r=3`.  Three of its tight coalitions obey

```text
1_26+1_57+1_75+2e_2+e_5+e_6=2 1_N+e_3,            (MCP5)
```

where `26` and `57` are tight at `x`, while `75` is tight at `z`; only `57`
is common.  The theorem gives the genuinely mixed inequality

```text
x(26)+x(57)+z(75)<=2T.                              (MCP6)
```

This is exactly the coalition part that the old common-hinge projection
misses: at this root that projection has minimum `25/34`, below the branch
minimum `3/4`, whereas the mixed packet together with direct `x`--`z`,
stratum, nonnegativity, and efficiency rows gives an exact Farkas identity
at `3/4`.

That Farkas identity has now been distilled into a human nonnegative-slack
proof.  Normalize `T=1` and write `w=w^3`.  On the fixed branch,

```text
O-3/4
 =z_2+(1/2)w_2+(1/4)w_5+(1/4)w_6
 +(1/4)[w(26)-x(26)]+(1/4)[w(57)-x(57)]
 +(5/4)[x(52)-z(52)]+(1/2)[x(57)-z(57)]
 +(1/4)[w(75)-z(75)]
 +(3/4)(x_0-x_4)+(1/2)(z_4-z_5)+(z_5-z_1).          (MCS)
```

Every summand is nonnegative by core/witness comparison, nonnegativity, or
the fixed Lmin/Lmax order.  At the actual control all five coalition
comparison brackets vanish.  Its margin `929/1080-3/4=119/1080` is exactly
the weighted sum of `z_2` and the three displayed stratum gaps.  Thus the
mixed packet buys the `3/4` baseline and ordered label currency pays all
strictness.  The verifier below checks `(MCS)` as an exact coefficient
identity and supplies a matching feasible primal, without calling an
optimizer.

```bash
python3 verifiers/divergence/verify_optimized_mixed_currency_certificate.py \
  --output verifiers/divergence/optimized_mixed_currency_certificate.json
```

The other two noncommon hostile spectral failures separate cleanly.  Their
sparse certificates attain `7/10` and `2/3` using only direct
`x`-to-`z`, stratum, nonnegativity, and efficiency rows; neither needs a
witness packet.  Hence a universal theorem demanding a nontrivial rooted
packet in every nonspectral branch would already be false.  The viable
disjunction has at least two nonspectral closures: direct labelled gluing,
or one or more mixed rooted packets.

The exact coefficient identities, including every multiplier, and the
integer incidence identity `(MCP5)` are replayed by

```bash
python3 verifiers/divergence/verify_mixed_packet_gluing.py \
  --output verifiers/divergence/mixed_packet_gluing.json
```

An independently formulated cutting-plane elimination finds an alternative,
facet-bearing mixed packet at the same root:

```text
(1/2)(1_26+1_57+1_15)+(1/2)e_2+(1/2)e_5+e_6
  =1_N+(1/2)e_3.                                    (MCP7)
```

Here `26,57` are `x`-tagged and `15` is `z`-tagged.  This single cut raises
the witness-free master from `25/34` to the direct one-witness optimum `3/4`.
The canonical singleton completion is purely min-semi-balanced but has `48`
exceptional-set decompositions, so it is not a full exact-cone facet.  Its
rooted-pair shear is

```text
(1/2)(1_12+1_15+1_26+1_40+1_57)+1_72-(5/2)e_3=1_N. (MCPF)
```

The seven incidence columns have rank seven.  The published
Studeny--Kratochvil exceptional-set test finds no decomposition, so `(MCPF)`
defines a facet of the seven-player exact-game cone.  Its game-inequality
slack is zero on the hostile control.  Thus the first genuinely noncommon
mixed-witness cut has an active indecomposable rooted-pair factor; the colour
labels explain its relative two-selection use, while the pair shear explains
its full-cone facet content.

Across the eight hostile/sharp controls, exact cutting planes reproduce every
direct one-witness minimum.  They generate nine cuts: only `(MCP7)` uses both
colours, no canonical singleton completion is a facet, and seven rooted-pair
shears are facets.  Eight pair-lift inequalities are active; the neutral
control has the sole positive slack `9/9523`.  A separately formulated Z3
exact-LRA replay agrees with every decomposition count and with all seven
facet decisions.  Reproduce with

```bash
python3 verifiers/divergence/verify_mixed_witness_projection.py \
  --output verifiers/divergence/mixed_witness_projection.json
python3 verifiers/divergence/verify_mixed_witness_projection_z3.py \
  --input verifiers/divergence/mixed_witness_projection.json \
  --output verifiers/divergence/mixed_witness_projection_z3.json
```

The two projection formulations share the labelled branch rows; only their
witness-feasibility components are independently formulated.  The facet
counts are finite controls, not evidence that a target-proving root exists in
every dimension.

#### Rectangular rooted-star classification

The pair-lift class admits a complete fixed-dimension description whenever
the exceptional coalition is a singleton.  Suppose a normalized purely
min-semi-balanced identity has positive common load and exceptional root
`{r}`:

```text
sum_(j=1)^k lambda_j 1_(S_j)-c e_r=1_N,
lambda_j,c>0.                                         (RRC1)
```

> **Theorem (singleton-root rectangular classification).**  If `(RRC1)` is
> indecomposable, every `S_j` contains `r`.  Write
> `S_j={r} union A_j`, and let `A` be the `(n-1)` by `k` zero-one matrix of
> the nonroot incidences.  Minimality is equivalent to `rank(A)=k`, and
>
> ```text
> A lambda=1,             c=1.lambda-1.               (RRC2)
> ```
>
> In particular `k<=n-1`.  For a proposed exceptional coalition with root
> indicator `beta` and nonroot incidence `b`, a decomposition exists exactly
> when there are `mu>=0` and a free common load `gamma` satisfying
>
> ```text
> A mu-b=gamma 1,       beta+gamma-1.mu>=0.            (RRC3)
> ```
>
> Thus `(RRC1)` defines an exact-cone facet exactly when `(RRC3)` is
> infeasible for every unsupported proper nonempty `(beta,b)`.

To prove rootedness, suppose a positive support coalition `S` omits `r`.
If `S union {r}` is proper and unsupported, then
`1_S+e_r-1_(S union {r})=0` is an exceptional-set decomposition.  If it is
supported, the same three columns form a semi-balanced subsystem, contrary
to minimality (and they cannot be the whole support because then no
positive-load identity covers a player outside their union).  If
`S union {r}=N`, the two columns `1_S,e_r` already form a proper balanced
subsystem; a two-column support cannot satisfy `(RRC1)`.  Hence every
positive coalition contains the root.

Now the support columns are independent exactly when `A` has full column
rank: a kernel vector of `A` can have its root load cancelled by `e_r`, and
the converse is immediate.  The nonroot and root coordinates of `(RRC1)`
give `(RRC2)`.  Finally a decomposition through `(beta,b)` has nonnegative
old-support coefficients `mu_0,mu` and satisfies

```text
mu_0 e_r+sum_j mu_j 1_(S_j)-1_(beta,b)=gamma 1_N.
```

Its nonroot coordinates give the first part of `(RRC3)` and its root
coordinate gives `mu_0=beta+gamma-1.mu`, proving the criterion.  The facet
equivalence is precisely the published Studeny--Kratochvil
indecomposability theorem.  QED.

This gives an exact enumeration algorithm for the **entire positive-load
singleton-exceptional class** at fixed `n`: enumerate full-column-rank
zero-one matrices `A` up to row and column permutations, retain the systems
with a positive solution of `(RRC2)` and `c>0`, and test every Boolean
`(beta,b)` by `(RRC3)`.  Repeated rows are clone blocks.  After clearing
denominators, each passing identity is a primitive extreme ray of the dual
exact-game cone, and equality under singleton normalization is
`sum_j lambda_j v(S_j)=v(N)`.

Applied to `(RPL)`, rootedness is a decisive filter: an extreme packing whose
positive support contains any coalition omitting `r` has a decomposable pair
lift and cannot define a full exact-cone facet.  Hence irreducible facet
selection may be restricted before enumeration to

```text
C_x^r={S in C_x: r in S},                            (RRC4)
```

together with the restored rooted pair columns.  The open hybrid theorem is
therefore sharper: after direct/interpolation/null branches fail, prove that
some ceiling root exposes a rectangular facet using only its root-containing
Lmin-tight submenu **and a marked pre-quotient packing of affordable price**,
with common Lmax rows supplying any needed reverse repair.  Quotienting is
valid for classifying the facet ray but not for testing that price.  No such
selection theorem is inferred here.

#### Saturated rooted-star matrix classification

The new facet and both sharp-family facets belong to one dimension-free
matrix class.  Put `V=N\{r}` and let `A` be a `|V|` by `|V|` nonsingular
zero-one matrix whose distinct columns are the incidences of proper nonempty
sets `A_j subset V`.  The corresponding positive coalitions are
`S_j={r} union A_j`.  Define

```text
lambda=A^(-1)1_V,              c=1.lambda-1.          (RSM1)
```

> **Theorem (saturated rooted-star facet criterion).**  Suppose
> `lambda>0` and `c>0`.  Then
>
> ```text
> sum_j lambda_j 1_(S_j)-c e_r=1_N                 (RSM2)
> ```
>
> is a purely min-semi-balanced system with linearly independent support.
> It is the completion of a saturated rooted-packing vertex and attains the
> `n-1` positive-coalition support bound.  Rooted-pair shears enter this class
> by treating their pair columns as members of the completed menu.  For a
> proposed new exceptional
> coalition `B`, write `beta=1_(r in B)`, let `b` be its incidence on `V`,
> and put `u=A^(-1)b`.  Define
>
> ```text
> L(B)=max_j {-u_j/lambda_j},
> U(B)=(beta-1.u)/c.                                  (RSM3)
> ```
>
> The system decomposes through `B` in the exact sense of
> Studeny--Kratochvil if and only if `L(B)<=U(B)`.  Consequently `(RSM2)`
> defines a facet of the exact-game cone exactly when
>
> ```text
> L(B)>U(B)                                           (RSM4)
> ```
>
> for every proper nonempty `B` outside its support.

#### Proof

The off-root coordinates of `(RSM2)` are `A lambda=1`; its root coordinate
is `1.lambda-c=1`.  Nonsingularity of `A` makes the `n` columns consisting of
`e_r` and the `1_(S_j)` independent.  Strict positivity and `c>0` give a
purely min-semi-balanced system with sole exceptional coalition `{r}`.  The
same equation says that `lambda` is the unique point at which all `n-1`
off-root packing capacities are tight, hence a saturated packing vertex.

For the published exceptional-set decomposition test, nonnegative
coefficients `mu_0,mu_j` and a free common load `gamma` must satisfy

```text
mu_0 e_r+sum_j mu_j 1_(S_j)-1_B=gamma 1_N.           (RSM5)
```

Off the root this forces

```text
mu=A^(-1)b+gamma lambda=u+gamma lambda,
```

so `mu>=0` exactly when `gamma>=L(B)`.  The root coordinate forces

```text
mu_0=beta-1.u-gamma c,
```

so `mu_0>=0` exactly when `gamma<=U(B)`.  A decomposition therefore exists
exactly when the interval `[L(B),U(B)]` is nonempty.  Applying the
Studeny--Kratochvil indecomposability theorem gives `(RSM4)` and the facet
claim.  QED.

This yields an exact enumeration algorithm for the entire saturated
rooted-star class: enumerate nonsingular zero-one matrices up to row and
column permutations, retain those satisfying `(RSM1)`, and test the finitely
many Boolean vectors `(beta,b)` by `(RSM3)--(RSM4)`.  Passing matrices give
primitive facet normals after clearing denominators; equivalently they give
extreme rays of the dual exact-game cone.  Equality in the associated game
inequality is exactly

```text
sum_j lambda_j v(S_j)=v(N),                           (RSME)
```

under singleton normalization.

#### Nonroot clone-expansion theorem

The saturated matrix class has a dimension-free unsaturated closure.  Start
from a purely min-semi-balanced rooted-star system on root `r` and nonroot
roles `V`,

```text
sum_j lambda_j 1_({r} union A_j)-c e_r=1_({r} union V).  (CL1)
```

Replace every role `v in V` by a nonempty, pairwise-disjoint clone block
`B_v`, and replace `A_j` by `union_(v in A_j) B_v`.

> **Theorem (nonroot clone expansion preserves exact-cone facets).**  The
> expanded system is purely min-semi-balanced and indecomposable if and only
> if `(CL1)` is.  Hence every clone expansion of a saturated rooted-star facet
> is again a facet of the exact-game cone.

The incidence identity is preserved coordinatewise.  Minimality is also
preserved: restricting a linear relation among expanded columns to one
representative of each clone block gives a relation among the base columns.
For indecomposability, players in one clone block have identical rows in the
positive-coalition incidence matrix.  Subtracting their two coordinates in
the Studeny--Kratochvil exceptional-set equations forces the candidate
exceptional coalition to contain either the whole block or none of it.
Every expanded decomposition therefore collapses to a base decomposition;
conversely, every base decomposition expands blockwise.  This proves the
equivalence and the facet assertion.  QED.

There is consequently an exact fixed-dimension enumeration algorithm for
this enlarged class: enumerate saturated rooted-star base matrices by
`(RSM1)--(RSM4)`, enumerate positive clone-block size compositions summing to
`n-1` modulo base automorphisms, and expand.  This is complete for the
clone-expanded class, not for all exact-cone facets.

The five support orbits in the six-player positive-residual atlas all belong
to this class.  Three are already saturated; the other two compress along a
single clone pair to four-role saturated bases.  Their compressed
determinants are `1` and `-2`, respectively.  Thus the finite five-orbit
regularity is explained by one dimension-free facet construction, although
the open selection lemma must still prove that a sufficiently priced member
is exposed for an arbitrary residual branch.  Reproduce the exact support
audit with

```bash
python3 verifiers/divergence/verify_clone_expanded_rooted_star_facets.py \
  --output verifiers/divergence/clone_expanded_rooted_star_facets.json
```

#### Complete-graph edge facets: sharp failure of clone saturation

Clone expansion is not the whole rectangular class.  The published
Studeny--Kratochvil catalogue shows that all 23 singleton-exceptional types
through six players are clone-saturated; the first failure therefore occurs
on seven players.  For integers `m>=4`, `p>=0`, take

```text
N={r} dot-union E(K_m) dot-union O,       |O|=p,
S_v={r} union {e in E(K_m): v in e}.      (KRF1)
```

Thus graph edges are players and `S_v` is the rooted vertex star.  Then

> **Theorem (complete-graph rooted pair facets).**  For every `m>=4,p>=0`,
>
> ```text
> sum_(v in K_m)1_(S_v)+2 sum_(o in O)1_{r,o}
>   -(m-2+2p)e_r=2 1_N                             (KRF2)
> ```
>
> is an indecomposable purely min-semi-balanced system and defines a facet
> of the exact-game cone.  None of these systems is a clone expansion of a
> saturated rooted-star system.  The first member is `(m,p)=(4,0)` on seven
> players.

Every edge belongs to two vertex stars, every outside player to its rooted
pair, and the root coordinate also has load two, proving `(KRF2)`.  The
unoriented vertex-edge incidence matrix of `K_m` has rank `m` because
`K_m` contains an odd cycle; adjoining the `p` pair columns and `e_r` gives
support rank `m+p+1`.

For indecomposability, label a candidate exceptional coalition by edge bits
`b_ij`, outside bits `o_a`, and root bit `beta`.  Its old-support
coefficients must satisfy

```text
mu_i+mu_j-b_ij=gamma,       c_a=gamma+o_a,
d=beta+gamma-sum_i mu_i-sum_a c_a>=0.                (KRF3)
```

The elementary additive-binary graph lemma says that, for `m>=4`, a
zero-one edge labelling of `K_m` of the form
`b_ij=mu_i+mu_j-gamma` is only the empty graph, the complete graph, a star,
or the complement of a star.  If all potentials agree, the labelling is
constant.  Otherwise choose `mu_j>mu_k`.  For every `i` outside `{j,k}`,

```text
b_ij-b_ik=mu_j-mu_k,
```

so the common difference must be one, `b_ij=1`, `b_ik=0`, and all remaining
potentials `mu_i` agree.  Taking two such remaining vertices shows that
their mutual edge bit and `b_jk` sum to one.  The two choices give exactly
the star at `j` and the complement of the star at `k`.

Add the gauge parameter `t` simultaneously to every `mu_i` and `2t` to
`gamma`.  For the four graph types, canonical coefficients are respectively

```text
empty:     mu_i=t,                              gamma=2t;
star v:    mu_v=1+t, mu_i=t (i!=v),             gamma=2t;
co-star v: mu_v=t-1, mu_i=t (i!=v),             gamma=2t-1;
complete:  mu_i=t,                              gamma=2t-1.
```

Put `o=sum_a o_a` and `D=m+2p-2`.  Substitution in the last line of `(KRF3)`
gives, in the same order,

```text
d=beta-o-Dt,
d=beta-o-1-Dt,
d=beta+p-o-Dt,
d=beta+p-o-1-Dt.                                    (KRF5)
```

The empty and star cases require `t>=0`, leaving only the empty coalition,
`{r}`, one supported pair `{r,o}`, or one supported star `S_v`.  The co-star
case requires `t>=1`, so `(KRF5)` is negative.  In the complete case, if any
outside bit is zero then `t>=1/2` and `(KRF5)` is negative; if all are one,
only `beta=1,t=0` survives, giving `N`.  There is therefore no new proper
exceptional set.

Finally, the nonroot row configuration consists of all distinct two-subset
incidence vectors of `[m]`, plus the pair-spoke unit rows.  Since
`binom(m,2)>m` for `m>=4`, no clone compression can make the star block
saturated.  This proves the strict enlargement.  In packing coordinates the
star weights are `1/2`, the spoke weights are one,

```text
delta=m/2-1,       Q=p,       P=Q/delta=2p/(m-2).     (KRF4)
```

The `p=0` member forces a zero root when evaluated through a root-zero Lmin
witness, so it belongs naturally to the null-floor branch.  Members with
`p>0` have finite rooted price and are legitimate positive-floor facet
candidates, but no selection theorem is claimed.  Reproduce the exact grid
and the independent seven-player exceptional-set replay with

```bash
python3 verifiers/divergence/verify_complete_graph_rooted_pair_facets.py \
  --output verifiers/divergence/complete_graph_rooted_pair_facets.json
python3 verifiers/divergence/verify_k4_edge_rooted_facet_z3.py \
  --output verifiers/divergence/k4_edge_rooted_facet_z3.json
```

For the mixed facet `(MCPF)`, the root-deleted matrix has determinant of
absolute value `2`,

```text
A=
[0 1 0 0 1 0
 0 1 1 0 0 0
 1 1 0 0 0 0
 0 0 1 0 1 0
 0 0 0 1 1 0
 0 0 0 0 0 1],
```

up to the displayed player/coalition order.  Formula `(RSM1)` gives weights
`(1/2,1/2,1/2,1/2,1/2,1)` and `c=5/2`.  Every unsupported Boolean coalition
has strict margin `L-U>=2/5`, giving a compact exact certificate of
indecomposability rather than an opaque unsat result.

For `G(p,k)`, the matrix is block diagonal with blocks `I_p` and `J_k-I_k`.
Thus `(RSM1)` gives pair weights one, hinge weights `1/(k-1)`, and
`c=p+1/(k-1)`, recovering the already proved sharp-family facet.  The matrix
criterion therefore contains both balanced orientations and the first
noncommon facet in one distinguished exact-cone class; it is a specialization
of the published general indecomposability theory, not a replacement for it.

The inverse formula and every Boolean margin are replayed exactly by

```bash
python3 verifiers/divergence/verify_rooted_star_matrix_facets.py \
  --input verifiers/divergence/mixed_witness_projection.json \
  --output verifiers/divergence/rooted_star_matrix_facets.json
```

The verifier agrees with the exact-LP counts for all four saturated systems
extracted from the controls and checks `25` additional sharp-family matrices.
Those finite rows audit the formulas; the theorem and criterion above are the
dimension-free argument.

This closes a real structural gap: noncommon support no longer prevents a
single exactness witness from coupling the selections, extreme coupling has
linear coalition support, and `(MWP2)` exhausts every inequality obtainable
from that witness.  It does **not** prove `(H)`.  The next missing lemma is a
root-selection statement: whenever the spectral floor fails, prove that some
distinguished root has target-valid direct rows plus mixed projection, or
produce an exact branch on which every root's one-witness minimum is below
the target.

The three hostile spectral failures separate the two currencies:

| control | spectral deficit | `C_top` | `C_label` |
|---|---:|---:|---:|
| optimized label-free failure | `5/216` | `1/30` | `4/15` |
| actual-top-fixed failure | `1/24` | `0` | `5/12` |
| top-and-bottom-fixed failure | `1/42` | `0` | `11/28` |

The new effective-bipartition counterexample has no spectral deficit:
`B_*=234/391>7/12`, while `C_label=145/782`.  Both sharp seven-player
orientations have `B_*=O=7/12` and zero currencies.  Thus equality remains
concentrated in the zero-currency common-hinge geometry, while every known
spectral obstruction carries more labelled currency than its deficit.

Reproduce the exact decomposition and the nonzero threshold layers with

```bash
python3 verifiers/divergence/audit_spectral_label_currency.py \
  --output verifiers/divergence/spectral_label_currency_audit.json
```

### Facet interface

Fix the actual and spectral-minimizing top blocks and both ordered payoff
partitions.  The integers in `(LC2)` are constants, so `(LC4)` is a rational
linear inequality in the stratum levels.  Pulling it back through the
labelled generator coordinates gives exactly the target row for the
common-hinge branch-circuit theorem.  Support-minimal proofs are positive
circuits of that augmented relative configuration.  Projection to the game
cone still requires the resulting coalition coefficients to pass the
Studeny--Kratochvil indecomposable semi-balanced test; the threshold currency
does not turn a relative labelled circuit into a full-cone facet by itself.
