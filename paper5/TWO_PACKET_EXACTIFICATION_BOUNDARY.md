# Two-packet exactification boundary at six players

Date: 2026-08-09

This note records a sharp obstruction to the proposed first-stage two-packet
proof of `s(6)=2/3`.  The obstruction is useful because singleton exactification
does not turn it into a counterexample: instead it changes a later Lmin stratum
and lands exactly on overlap `2/3`.

The conclusion is deliberately limited.  Sparse first-stage Lmax and Lmin
incidence supports, even with their individual cross-selection inequalities,
do **not** imply the six-player bound.  A valid finite-incidence proof must also
encode which players are individually pinned at every lexicographic stage (or
an equivalent full one-packet condition).

All player indices below are zero-based and all totals are one.

## 1. An abstract paired-support obstruction

Put

```text
x = (1,1,1,1,7,1)/12,
z = (0,1,0,1,1,1)/4.
```

Let `A={3,4,5}` (mask 56) and `B={1,3,4}` (mask 26).  The top
over-cover data are

```text
lambda_A = 1/3,       eta = 0,
alpha = (0,0,0,1,1,1)/3,
```

and the bottom under-cover data are

```text
gamma_B = 1/3,        xi = 1/3,
beta = (1,0,1,0,0,1)/3.
```

Their incidence identities hold coordinatewise:

```text
(1/3) 1_A = eta 1_N + alpha,
(1/3) 1_B = xi 1_N - beta.
```

Both retained cross-selection inequalities are tight:

```text
x(A) = z(A) = 3/4,
z(B) = x(B) = 3/4.
```

The aggregate anchors are also tight:

```text
alpha.x = max_i z_i = 1/4,
beta.z  = min_i x_i = 1/12.
```

Thus these data satisfy exactly the proposed paired first-stage support system.
Nevertheless

```text
O(x,z) = sum_i min(x_i,z_i) = 1/2.
```

This is not merely a free-vector solution.  If `v_0` is the lower envelope of
the two common-total allocations `x,z`, exact staged rational LP gives

```text
Lmin(v_0) = x,       Lmax(v_0) = z.
```

But `v_0` is outside the theorem domain: its singleton values are

```text
(0, 1/12, 0, 1/12, 1/4, 1/12).
```

## 2. Singleton exactification

Adjoin the following three common-total allocations:

```text
w^0 = (0,   0, 1/4, 3/4, 0,   0),
w^1 = (1/4, 0, 0,   3/4, 0,   0),
w^2 = (1/4, 0, 0,   0,   3/4, 0).
```

Let `v` be the lower envelope of `x,z,w^0,w^1,w^2`.  Every coordinate
vanishes in at least one generator, so `v({i})=0` for all players.  Every
coalition value is attained by a displayed common-total core allocation.
Consequently `v` is singleton-normalized and exact directly from its defining
lower-envelope representation.

Every new row has value at least `3/4` on both `A` and `B`.  Hence the two
tight support coalitions, both incidence identities, and both individual
cross-selection equalities from Section 1 survive unchanged.  Exactification
therefore does not repair the deficient first-stage abstraction by invalidating
its displayed certificates.

## 3. The later Lmin stage is the missing information

Two independently formulated exact rational simplex encodings recompute

```text
Lmax(v) = (0,1/4,0,1/4,1/4,1/4),
Lmin(v) = (1/12,1/12,1/12,1/3,1/3,1/12).
```

The full stage traces are

```text
Lmax:  level 1/4 pins {1,3,4,5}; level 0 pins {0,2}.
Lmin:  level 1/12 pins {0,1,2,5}; level 1/3 pins {3,4}.
```

By contrast, in the unnormalized two-generator game the first Lmin level
`1/12` pins `{0,1,2,3,5}` and the second pins player 4 at `7/12`.
The proposed trial vector `x` therefore ceases to be Lmin after exactification
because player 3 is no longer forced at the floor.  The actual Lmin point is an
explicit core witness that holds the floor fixed while raising player 3:

```text
(1,1,1,4,4,1)/12.
```

The recomputed overlap is exactly

```text
O(Lmin(v),Lmax(v)) = 2/3.
```

This example also clarifies what the bottom aggregate certificate does and
does not say.  Its `beta` is supported only on `{0,2,5}`.  It proves the scalar
floor optimum and the aggregate cross anchor, but it does not by itself prove
that every coordinate displayed at the trial floor is individually forced
there.  Other tight coalitions may pin additional players (player 1 here), so
the support of `beta` is not itself a complete pinning classification either.

## 4. Consequence for the fixed-six proof program

The earlier proposed finite incidence theorem—classify only one sparse
first-stage support on each side and solve the retained cross inequalities—is
false as a sufficient reduction.  The example above is a realizable exact
lower-envelope game before normalization and continues to satisfy all those
linear conditions after normalization, while its trial pair violates `2/3`.

A strengthened support type must contain, at minimum:

1. the first-stage Lmax over-cover and its tight coalitions;
2. the first-stage Lmin under-cover and its tight coalitions;
3. for every alleged member of a pinned stratum, a certificate that its
   opposite extremum equals the current stage level; and
4. the recursively restricted core face on which the next stage is solved.

Equivalently, one may encode the full Lmin one-packet boundary rather than a
single aggregate under-cover.  The next computational test should enumerate
the small paired first-stage supports only as an outer loop, then reject each
candidate payoff pattern unless exact per-player pinning certificates exist.

The boundary behavior suggests—but does not prove—a possible repair lemma:
singleton exactification of a paired-support violation may create a feasible
same-floor Lmin improvement whose overlap reaches `2/3`.  Proving such a lemma,
or finding a support type for which the repair remains below `2/3`, is now the
highest-value structural target.

## 5. Reproduction

Run from `coopgames/`:

```text
python3 verifiers/s6/audit_two_packet_exactification.py \
  --output verifiers/s6/two_packet_exactification_audit.json
```

The verifier checks exactness and normalization from the generators, both
incidence identities, both cross equalities, the two aggregate anchors, both
stage traces, and both overlap values.  It compares the pre-existing
nonnegative-variable simplex with a separate staged encoding using
`src/exactlp.py`.  The JSON output is a reproducible audit artifact, not an
exhaustive proof or evidence of novelty.
