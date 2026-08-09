# Sparse Lmax over-covers and the hybrid-overlap bridge

Date: 2026-08-09

This note constructs the missing sparse Lmax certificate, couples it to Lmin,
and derives a spectral lower bound for the cross-selection overlap.  The bound
closes every archived six-player pair after the null-player reduction, and is
sharp on all archived equality cases.  This is not yet an exhaustive proof of
`s(6)=2/3`: the remaining task is to prove that the spectral/certificate
conditions cover every exact six-player game, not merely the archived bank.

Throughout, let

```text
x = Lmin(v),       z = Lmax(v),       T = v(N) > 0,
O(x,z) = sum_i min(x_i,z_i),
mu = min_i x_i,   M = max_i z_i,
H = {i:z_i=M}.
```

The interesting case has `H` proper.  If `z` is uniform, then the uniform
point lies in the core and simultaneously maximizes the minimum, so `x=z` and
there is no divergence.

## 1. The first-stage Lmax over-cover

### Theorem (sparse top over-cover)

If `H` is proper, there are nonnegative weights `lambda_A`, a scalar
`eta>=0`, and a probability vector `alpha` supported on `H` such that

```text
sum_A lambda_A 1_A = eta 1_N + alpha,                 (OC)
sum_{i in H} alpha_i = 1,
```

where every `A` is a proper `z`-tight coalition.  The certificate can be
chosen with at most `n` positive coalitions.

### Proof

The first Lmax stage is

```text
minimize t
subject to w in Core(v),
           w_i <= t       for every i.
```

Give `v(A)-w(A)<=0` multiplier `lambda_A>=0`, `w_i-t<=0`
multiplier `alpha_i>=0`, and efficiency a free multiplier `eta`.  Stationarity
in `t` gives `sum_i alpha_i=1`, and stationarity in `w_i` gives `(OC)`.
Complementary slackness restricts `alpha` to the top stratum and `lambda` to
proper `z`-tight coalitions.  For a player outside the proper set `H`, `(OC)`
reads `sum_{A contains i}lambda_A=eta`, hence `eta>=0`.

The feasible certificate polyhedron is pointed.  It has `n+1` equality rows:
the `n` incidence equations and the probability normalization.  At a basic
solution at most `n+1` variables are positive; at least one is an `alpha`
variable, so at most `n` positive variables are coalition weights.  QED.

The dual objective identity is

```text
M = sum_A lambda_A v(A) - eta T.                       (1)
```

Thus this is a genuine over-cover: after normalization by `eta>0`, every
player has baseline load one and the top stratum receives extra load.  When
`eta=0`, the certificate is a balanced anchor supported entirely inside `H`.

## 2. Direct coupling to Lmin

Evaluate `(OC)` at any core point `w`.  Since every supported coalition is
tight at `z` and feasible at `w`,

```text
eta T + alpha.w
  = sum_A lambda_A w(A)
 >= sum_A lambda_A v(A)
  = eta T + M.
```

Therefore

```text
alpha.w >= M                                             (2)
```

for every core point `w`; in particular `alpha.x>=M`.  This recovers the
top-stratum cross anchor `max_{i in H}x_i>=M`, but the probability vector
contains more quantitative information than that scalar statement.

Define the **dispersion parameter**

```text
theta(v) = min max_{i in H} alpha_i,                     (3)
```

where the minimum ranges over all certificates `(OC)`.  It is computed by
one rational LP: add `alpha_i<=theta` and minimize `theta`.  Once an optimal
`(eta,alpha)` is fixed, conic Caratheodory reduction in `R^n` again represents
its incidence load using at most `n` tight coalitions.  Thus optimizing
dispersion does not destroy the linear support bound.

Since `x_i>=mu`, (2) and `alpha_i<=theta` imply

```text
M-mu
 <= sum_{i in H} alpha_i(x_i-mu)
 <= theta sum_{i in H}(x_i-mu).                          (4)
```

Equation (4) is the promised bridge: it converts an Lmax normal certificate
into a restriction on which part of the Lmin spectrum can occupy the Lmax top
block.

## 3. The spectral-anchor overlap theorem

Let `x_1,...,x_n` denote the Lmin spectrum with labels forgotten, and let
`z^-` be the multiset of Lmax coordinates strictly below `M`.  For every
`h=|H|` element subset `J` of the Lmin coordinates satisfying

```text
sum_{j in J}(x_j-mu) >= (M-mu)/theta,                    (5)
```

put

```text
B(J) = sum_{j in J} min(x_j,M)
     + sum_r min(a_r,b_r),                               (6)
```

where `(a_r)` is the increasing ordering of the coordinates outside `J` and
`(b_r)` is the decreasing ordering of `z^-`.  Define

```text
B_theta(x,z) = min_J B(J),                               (7)
```

with the minimum over the subsets satisfying (5).

### Theorem (spectral anchor)

Every singleton-normalized exact game with nonuniform Lmax satisfies

```text
O(Lmin,Lmax) >= B_theta(Lmin,Lmax).                       (SA)
```

### Proof

The actual Lmax top block, viewed as a subset of the Lmin coordinates,
satisfies (5) by (4).  Its contribution to overlap is the first term of (6).
After deleting that block, the remaining Lmin and Lmax coordinates have fixed
multisets but unknown matching.  The elementary swap inequality

```text
min(a,c)+min(b,d) >= min(a,d)+min(b,c)
                    for a<=b and c<=d
```

shows that opposite sorting minimizes their overlap.  Hence the actual
remaining overlap is at least the second term of (6).  Finally minimize over
all subsets allowed by the certificate.  QED.

This theorem is dimension-free.  For fixed `n`, evaluating (7) requires at
most `binomial(n,h)` subsets plus a sort for each, after the certificate LP.

## 4. The first-stage Lmin companion

The floor problem has the exact mirror form.  If
`P={i:x_i=mu}` is a proper bottom stratum, LP duality gives nonnegative
`gamma_A`, a scalar `xi`, and a probability `beta` on `P` with

```text
sum_A gamma_A 1_A = xi 1_N - beta,                       (UC)
```

supported on proper `x`-tight coalitions.  Nonnegativity of the incidence
loads forces `xi>=max beta_i>0`.  A basic certificate uses at most `n-1`
coalitions.  Evaluating it at `z` gives

```text
beta.z <= mu.                                            (8)
```

This is the first-stage shadow of the full Lmin one-packet theorem.  The next
proof attempt should retain the individual supported inequalities on both
sides:

```text
x(A) >= z(A)   for Lmax-certificate coalitions A,
z(B) >= x(B)   for Lmin-certificate coalitions B.         (9)
```

The spectral theorem uses only their weighted aggregate.  Keeping the two
sparse set systems in (9) is the natural route to a complete fixed-`n` proof.

## 5. Exact six-player audit

The verifier

```text
verifiers/divergence/audit_lmax_overcover.py
```

reconstructed the dispersion-optimal certificate in exact rational arithmetic
for 374 archived six-player games.  Its reproducible output is

```text
verifiers/divergence/lmax_overcover_audit.json
```

Results:

```text
positive Lmin floor:                     249
zero Lmin floor:                         125
positive-floor failures of (SA)>=2T/3:    0
```

Every zero-floor case deletes a null player and is therefore bounded by the
proved `s(5)=1/2`.  Thus the new argument certifies all 374 archived games,
without using their actual Lmin/Lmax player matching.  This remains an archive
audit, not exhaustive proof evidence.

All five archived equality records have the rigid certificate data

```text
theta = 1/3,       eta = 0,
one positive tight coalition of size 3, with weight 1/3,
B_theta/T = O/T = 2/3.
```

This common certificate geometry occurs for both the `3|3` and `4|2`
comparison-cut equality games.  The sign cut is therefore not the invariant;
the invariant visible at equality is a dispersed three-player Lmax anchor.

## 6. What remains before `s(6)=2/3` is a theorem

The certificate and spectral theorem alone do not make a purely numerical
statement about arbitrary equal-sum spectra.  For example, the abstract data

```text
x = (7,17,18,30,14,5)/91,
z = (20,3,30,30,30,30)/143,
theta = 1/2
```

satisfy the elementary sum, order and dispersed-anchor conditions but give
`B_theta=657/1001<2/3`.  No claim is made that these spectra come from an exact
game or from a realizable pair of certificates.  They show why a proof must
retain exact-game structure rather than optimize (7) over arbitrary vectors.

There are now two sharply defined completion routes:

1. **Two-packet theorem.**  Prove directly from the two sparse tight set
   systems in (9) that `B>=2T/3` when `n=6` and `mu>0`.
2. **Finite incidence theorem.**  Enumerate the linearly independent supports
   of the two certificates up to permutation, then solve the remaining
   payoff inequalities symbolically.  Each side has at most six coalitions;
   this is far smaller than enumerating exact games or all staged strata.

The first route would be a human structural proof.  The second could give a
computer-assisted fixed-six-player theorem with short rational certificates,
and may reveal the missing human inequality.
