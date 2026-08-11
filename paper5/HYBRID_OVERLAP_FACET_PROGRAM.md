# Hybrid overlap and rooted-facet program

Date: 2026-08-10

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

The conclusion is that the correct missing object is a **fractional coupling
of rooted Lmin circuits with an Lmax over-cover**.  A literal partition of
the players is already false at six players, while treating the Lmin packet
itself as one exact-cone facet is also false in general.

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

For a fixed Lmax over-cover `(lambda,eta,alpha)`, let
`B(lambda,alpha)` denote the sharpened spectral bound `(SR)`--`(SA)`, using
its actual `theta=max alpha_i` and hinge surplus `epsilon_+`.  Define

```text
B_spec(v)=sup B(lambda,alpha)
```

over all normalized Lmax top over-covers.  Every term in the supremum is a
proved lower bound for the true overlap.  The sharp family has
`B_spec=O=nT/floor(n^2/4)`.  The new coefficient-two and coefficient-seven
obstructions have, respectively,

```text
B_spec>=11>7,               B_spec>=139/13>8.
```

This isolates a cleaner surviving statement.

> **Spectral-residual exclusion (SRE).**  For every singleton-normalized
> exact game,
>
> ```text
> B_spec(v)>=nT/floor(n^2/4).                           (SRE)
> ```
>
> Equivalently, if a proposed pair of spectra makes every sparse Lmax
> spectral certificate fall below the sharp constant, then the complete
> staged Lmin rooted-circuit system and exactness witnesses are infeasible.

`(SRE)` is stronger than `(H)` but is not a statement about arbitrary equal-
sum spectra: the abstract counterexample in `LMAX_OVERCOVER_COUPLING.md`
shows that exact-game and staged-selection structure is indispensable.  It
also survives every known local-congestion counterexample because those
examples are discharged before their large primitive coefficients need to be
bounded.

The minimal live target is therefore:

> **Compatible fractional-hinge and acyclic-congestion lemma.**  From a
> sparse Lmax top over-cover and the sign-coherent Lmin packets in Section 6,
> prove `(SRE)` directly, or first discharge every spectrum for which the
> sharpened spectral anchor already proves `(H)` and show that the residual
> spectra contradict an exact rooted Lmin circuit.  Equivalently, construct
> nonnegative price-weighted coupling weights whose normalized loads pack as
> in `(FSP)`; charge every large primitive coefficient against spectral-anchor
> slack or hinge surplus, and control cross-stage source reuse so that the
> resulting carrier inequality implies
> `sum_i min(x_i,z_i)>=nT/floor(n^2/4)`.

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
   spectral bound is `139/13>8`.

The program has advanced beyond a bare outcome D: the common-hinge theorem,
hinge-surplus spectral refinement, surplus dispersion budget, first-floor
transport theorem, projected staged-circuit classification, and sign-coherent
nested-incidence theorem are proved dimension-free.  The exact audit has now
disproved both `(UB)` and `(TC)`, then proved that even a support-minimal
eight-player circuit can force coefficient seven while the opposite spectral
certificate closes the target.  The final all-`n` inequality remains open:
the new residual price-weighted coupling lemma is not yet proved.  This is
meaningful structural progress and a decisive pruning of the proof tree, but
not yet the requested central breakthrough.
