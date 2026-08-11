# Hybrid overlap and rooted-facet program

Date: 2026-08-11

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

The conclusion is that the correct missing object is a **fully labelled
fractional coupling with a distinguished singleton root**.  The one-witness
reduction in Section 8 turns it into a rooted two-tangent budget and gives a
linear-support certificate if the correct root can be selected.  The newest
premise ablation narrows the Lmax contribution further: only tight coalitions
shared by a sparse ceiling over-cover and the complete Lmin packet need be
retained in every tested branch.  This common-hinge reduction is proved as a
sufficient implication and has a sharp exact negative control when all such
hinges are deleted, but its dimension-free target bound remains conjectural.
A literal partition of the players is already false at six players, while
treating the Lmin packet itself as one exact-cone facet is also false in
general.

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
equality, and the sharp overlap.  It uses the proved selection formulas;
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
staged subpacket having the protector/deficit form assumed by `(RMC)`, its
`w^r`-slacks are the corresponding coordinates of `a` or `b`.  The two
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
active indecomposable factors of the Lmin packet with sufficient rooted
multiplicity.  The exact negative control above shows that a theorem using
the Lmin packet alone would be too strong.

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
root: combine `(RC)` with the rooted marginal-completion coefficient of the
active indecomposable Lmin factors, and prove that the common hinges selected
by the sparse ceiling over-cover transmit enough exceptional-root
multiplicity to pay the deficit in `(RTB)`.

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

### Theorem (carrier intervals are label-currency rectangles)

Put `d=x-z`.  Let `i` gain (`d_i<0`) and `j` lose (`d_j>0`).

1. If `x_j<=x_i`, then throughout the interval

   ```text
   I^x_(i,j)=(x_j,x_i]
   ```

   player `i` is high in both selections and player `j` is low in both.

2. If `z_j>=z_i`, the same is true with the roles reversed throughout

   ```text
   I^z_(i,j)=(z_i,z_j].
   ```

Consequently, when both endpoints lie in the residual set `R`, each interval
is a unit rectangle under the capacity integrand `(LC5)`.  The two carrier
packets supplied by the sign-coherent staged theorem consist entirely of
intervals of these two respective forms.

#### Proof

In the first case the payoff chain is

```text
z_j<x_j<=x_i<z_i.
```

For `t in (x_j,x_i]`, player `i` lies in both upper sets while player `j`
lies in neither.  In the second case,

```text
x_i<z_i<=z_j<x_j,
```

so on `(z_i,z_j]` player `j` lies in both upper sets and player `i` in
neither.  The carrier-order assertions are exactly `(AT-min)` and `(AT-max)`.
QED.

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
4. If interval supplies `0<=rho_e<=b_e` inherited from a chosen staged packet
   are included, the augmented constraint matrix remains totally unimodular.
   Integral `b,c` still give integral vertices; arbitrary rational supplies
   still give an exact polynomial-time primal--dual certificate.

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

For fixed payoff strata and fixed staged carrier supports, `(IPD)` is an
exact algorithm, not an existence slogan:

1. construct the merged threshold layers and their integer capacities;
2. obtain carrier intervals and any supplies from the exact staged incidence
   rays;
3. solve the rational packing and cover pair and retain both checkable
   certificates;
4. if the optimum pays the residual target, combine the packing with the
   rooted staged identities and the sparse over-cover;
5. lift the resulting incidence inequality and apply the published
   indecomposable semi-balanced-system test before calling it a facet of the
   exact-game cone.

The interval matrix proves integrality and sparsity only for the relative
threshold-packing problem.  Its threshold rows are not coalition-incidence
rows, and a support-minimal interval cover need not lift to an indecomposable
semi-balanced system.  Thus this is a fixed-stratum algorithmic theorem and a
facet-generation interface, not yet a facet characterization of the full
exact-game cone.  Enumerating all projected staged circuits and all basic
packings is finite and exact but can be exponential; no polynomial full
facet-enumeration claim is made.

### Theorem (cellwise pullback and an exact fixed-`n` decision algorithm)

Fix `n` and refine the singleton-normalized exact-game cone into rational
polyhedral cells on which all of the following data are fixed:

- active staged bases and tight-coalition hypergraphs for Lmin and Lmax;
- payoff orders and equality strata;
- the actual Lmax ceiling block and the minimizing spectral branch;
- the signs of `x_i-z_i` and the strict carrier endpoints.

On each such cell, `x`, `z`, every threshold endpoint `beta_l`, `B_H`, and
`delta` are rational linear functions of the game coordinates, while the
capacity vector, interval incidence matrix, and staged incidence cones are
constant.  For every rooted spanning tree in the threshold-potential graph,
solving its tight equalities makes `p` a rational linear function of those
coordinates.  The conditions that this tree solution is cover-feasible and
that

```text
sum_l c_l p_l>=delta
```

are therefore finitely many rational linear inequalities on the cell.
Enumerating the rooted trees and checking these inequalities by exact LP
decides the unsupplied interval-packing statement on that cell.  If staged
coefficient supplies `(SS1)` are retained, enumerate bases of the combined
staged-incidence/interval LP instead; the same parametric-LP argument gives a
finite exact decision procedure.

Consequently, for every fixed `n`, universal validity of `(SSP)` is decidable
by a finite rational polyhedral computation, and every cellwise obstruction
has an exact rooted-tree/basis certificate.  This is not advertised as an
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
each resulting implication on the cell.  The supplied version is the same
standard parametric-basis argument applied to the combined linear system.
QED.

This theorem answers the algorithmic half of the one-packet question: the
theory gives an exact fixed-`n` decision and certificate-enumeration method.
It does **not** yet answer the facet half with a one-to-one correspondence.
The missing mathematical content is precisely the gluing and
indecomposability theorem for the rooted threshold-tree lifts.

For a desired residual amount `delta`, the exact remaining condition is now
equivalent to either side of

```text
nu(E,c)>=delta

<=> every fractional threshold cover p has sum_l c_l p_l>=delta.  (IPC)
```

This is the sharp Hall-type gate for a specified carrier family.  A cover
with smaller cost is a checkable obstruction to that packet family, even
when the main overlap inequality itself remains true.

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

The minimal live lemma is now an **interval-packing lemma**: after crediting
the sharpened spectral floor and `C_top`, select fractional intervals from
the two sign-coherent staged carrier packets with total length at least the
remaining target deficit and satisfying the threshold capacities `(LC6)`.
Carrier intervals touching the removed ceiling block must instead be charged
to `C_top` or to the explicit top contribution.  Large primitive staged
coefficients are permitted; what must be controlled is their simultaneous
threshold occupancy.  The previous coefficient-congestion counterexamples
do not refute this formulation because `(LC6)` measures geometric occupancy,
not the raw sum of circuit multipliers.

### Precise staged-supply conjecture

The word "from" in that lemma can be made exact.  Normalize each selected
sign-coherent staged relation by giving its forced player column coefficient
one, as in `(SP)`.  If the auxiliary coefficient on a losing carrier `j` is
`a_(i,j)`, permit the corresponding strict residual carrier interval to have
supply

```text
0<=rho_(i,j)<=a_(i,j).                                (SS1)
```

Choose the Lmin and Lmax relations, their auxiliary coefficients, and the
interval weights simultaneously.  All incidence identities, sign
restrictions, `(SS1)`, and the layer capacities `(LC6)` are linear rational
constraints.  Put

```text
delta=max(0, nT/floor(n^2/4)-B_H),
```

where `B_H=B_*+C_top` uses the actual Lmax ceiling block.  The exact remaining
packet statement is

```text
there are normalized staged relations and rho satisfying
sum_e rho_e |I_e|>=delta.                              (SSP)
```

`(SSP)` implies the hybrid-overlap target immediately by `(LC7)`.  It is
strictly stronger than the target and is not yet proved.  Its value is that
it is no longer ambiguous about carrier availability, normalization, or
coefficient supply.  Projecting the joint rational feasibility system onto
the payoff-stratum coordinates gives the proposed exact-cone interface; a
Farkas obstruction combines a rooted staged-incidence functional with a
threshold-cover potential.  Showing that no such obstruction exists (or
classifying its support-minimal forms as indecomposable semi-balanced lifts)
is now the structural task.

The two hostile controls for which `delta>0` have exceptionally small exact
witnesses.  In the actual-top-fixed control, the Lmin relation

```text
1_{0,2,4}+1_{0,1,2,3,6}+1_{4,6}+2e_5+e_1+e_3=2 1_N
```

pins gainer `3` and supplies the interval `(x_5,x_3]=(1/2,8]`.  Giving it
weight `1/5` packs `(15/2)(1/5)=3/2`, exactly the deficit.  In the
top-and-bottom-fixed control,

```text
1_{1,3,4,5,6}+e_2+e_0=1_N
```

supplies `(x_2,x_0]=(1/2,19/2]`; weight `1/9` packs `1`, again exactly the
deficit.  Every coalition displayed is tight at the relevant Lmin point and
the layer capacities are checked exactly.  The full simultaneous certificate
replay is

```bash
python3 verifiers/divergence/verify_staged_interval_deficit_controls.py \
  --output verifiers/divergence/staged_interval_deficit_controls.json
```

This proves only that the sharpened formulation survives the named hostile
controls.  It is not finite evidence for universal `(SSP)`.

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
