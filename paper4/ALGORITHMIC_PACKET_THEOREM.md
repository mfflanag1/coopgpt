# Constructive one-packet extraction and the facet boundary

Date: 2026-08-09

This note answers two questions left by the one-packet theorem.

1. The packet can be extracted directly by linear programming; no vertex
   enumeration, minimal-balanced catalogue, or explicit convex decomposition
   is needed.
2. The packet always gives a valid exact-cone inequality, but it does **not**
   always give a facet.  Full-trace packets give star facets; split packets
   require a separate indecomposability test and can be decomposable.

## 1. Direct extraction LP

Fix a slack strict boundary `N=L dot-union H` of `phi=Lmin(v)`.  Let

```text
T_H={T: T is proper, phi-tight, and T intersects H}.
```

For `lambda>=0` on `T_H`, write

```text
r_i(lambda)=sum_{T contains i} lambda_T,       i in L.
```

Consider the rich exact-cover polytope

```text
C_H={lambda>=0:
     sum_T lambda_T 1_(T intersect H)=1_H}.                  (C)
```

The strict-cover lemma says that `(C)` contains a point `lambda^0` with
`r_i(lambda^0)<1` for every `i in L`.  It can be obtained from the margin LP

```text
maximize epsilon
subject to lambda in C_H,
           r_i(lambda) <= 1-epsilon    for every i in L.     (M)
```

The optimum is positive.  Both `(C)` and `(M)` are bounded: summing the rich
cover equations gives
`sum_T lambda_T |T intersect H|=|H|`, and every listed coalition meets `H`.

For each `j in L`, define the linear functional

```text
G_j(lambda)=1+(|L|-1)r_j(lambda)-sum_{i in L}r_i(lambda).    (G)
```

For every poor-load vector `r`,

```text
max_j G_j = 1+(|L|-1)max_i r_i-sum_i r_i = F(r).
```

At the strict cover,

```text
F(r(lambda^0)) >= 1-max_i r_i(lambda^0) > 0.
```

Therefore some `j` has `G_j(lambda^0)>0`.  Maximize that `G_j` over `(C)`
and choose an optimal basic feasible solution `lambda*`.  Its value remains
positive.

### Theorem (LP packet extraction, conditional on the Lmin boundary)

Once `phi=Lmin(v)` and its proper tight coalitions are known, an Lmin
one-packet obstruction can be found by:

1. the margin LP `(M)`, producing a strict cover and an index `j` with
   `G_j>0`;
2. one linear program maximizing `G_j` over `(C)`;
3. choosing an optimal basic solution.

The basic solution has at most `|H|` positive coalitions.  No two positive
coalitions have the same trace on `H`, their positive trace columns are
linearly independent, and the traces form one minimal balanced collection.
Completing its poorer loads produces the rooted identity `(P)` with at most
`|N|-1` positive coalitions.

### Proof

The positivity argument is above.  Polytope `(C)` has `|H|` equality rows, so
a basic solution has at most `|H|` positive variables.  Two coalitions with
the same trace have identical columns in `(C)` and therefore cannot both be
basic.  The remaining positive trace columns are linearly independent.  They
carry a positive exact cover of `H`; if a proper subcollection also carried
one, subtracting the two cover equations would give a nonzero dependence.
Thus they form a minimal balanced collection and the solution is a pure
lifted packet.

Put

```text
b=max_i r_i(lambda*),
u_i=b-r_i(lambda*),
delta=1+sum_i u_i-b=F(r(lambda*))>0.
```

The incidence calculation from the one-packet theorem gives

```text
sum_T lambda*_T 1_T
 + sum_i u_i 1_(H union {i})
 - delta 1_H
 = b 1_N.
```

At least one poor player attains `b`, so at most `|L|-1` spokes have positive
weight.  The total positive support is at most
`|H|+|L|-1=|N|-1`.  QED.

For an explicitly listed characteristic function, computing `phi`, its tight
coalitions, and these LPs is polynomial in the explicit input length and
rational bit size (using the standard sequence of LPs for leximin).  The two
LPs above are the additional packet-extraction cost after the boundary is
known.  The exponential dependence on the number of players is already
present in the `2^n`-entry characteristic-function input.

## 2. Certificate verification

The output is independently checkable from rational data:

1. every packet coalition is proper and `phi`-tight;
2. its traces cover each player of `H` with load one;
3. the displayed incidence identity holds coordinatewise;
4. `delta>0` and the number of positive coalitions is at most `|N|-1`;
5. exactifying `H` gives
   `delta s_phi(H) <= sum_i u_i s_phi(H union {i})`.

Thus the general theorem is constructive and supplies a short obstruction
certificate.  The earlier convex-decomposition proof remains conceptually
useful, but is not an algorithmic dependency.

## 3. What this does and does not imply about facets

The rooted system is semi-balanced with exceptional coalition `H`, so its
inequality is valid for the cone of exact games.  By the established facet
theory, it defines a facet exactly when the associated minimal semi-balanced
system is indecomposable.

The one-packet theorem alone cannot guarantee this:

- every full-trace packet is the star `St(H,Q)` and is indecomposable, hence a
  facet;
- the five-player split example in `paper4/threshold.tex` is a one-packet
  obstruction but is decomposable by `E={d}`;
- split facets do occur in larger dimensions.

So the correct general conclusion is a **facet-or-decomposition boundary**,
not a universal facet theorem.

There is nevertheless a catalogue-free exact decision procedure.  Let
`S` be the positive coalitions in the rooted system together with `H`, and let
`A` be their player--coalition incidence matrix.  A coalition `E` decomposes
the system exactly when

```text
A sigma - 1_E = rho 1_N,       sigma>=0                    (D)
```

is feasible after scaling the negative coefficient to `-1`, with `E` a
nonempty proper coalition outside `S`.  Hence indecomposability can be decided
by a finite family of rational LPs, one for each such `E`, or by a single
mixed-integer feasibility problem with the entries of `1_E` binary.

The LP support has at most `|N|` sets, so this test concerns a small incidence
system even when the original tight family is large.  Players with identical
incidence signatures across `S` must have the same membership in any
decomposing `E`; therefore it is enough to enumerate unions of signature
classes rather than all coalitions.

This is algorithmically useful but not claimed as a new facet
characterization: the equivalence between indecomposable minimal
semi-balanced systems and exact-cone facets is prior art.  The new consequence
is that every Lmin failure supplies, by two LPs, one linear-size candidate to
which that established criterion can be applied.

## 4. Focused prior-art check

Studeny--Kratochvil already provide the exact-cone facet equivalence and discuss
generation of min-semi-balanced systems from minimal balanced systems
([*Facets of the cone of exact games*, MMOR 95 (2022), 35--80](https://doi.org/10.1007/s00186-022-00770-4)).
Recent algorithmic work gives strongly polynomial leximin/leximax algorithms
for assignment games
([Vazirani, arXiv:2402.11437](https://arxiv.org/abs/2402.11437)) and polynomial
algorithms on the Owen sets of max-flow, MST and b-matching games
([Gangam--Garg--Shahkar--Vazirani, arXiv:2403.06037](https://arxiv.org/abs/2403.06037)).
In the sources inspected, neither line states the Lmin-boundary LP `(M)`--`(G)`,
the positive-defect packet extraction, or its `|N|-1` rooted certificate.  This
is only a focused search; specialist review is still required before making a
novelty claim.
