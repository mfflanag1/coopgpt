# Complete cardinality classification of slack Lmin boundaries

## Result

Let `phi=Lmin(v)` for a singleton-normalized exact game.  At any strict
payoff boundary, let `L` be the cumulative poorer side, let `H` be the richer
suffix, and write

```text
m = |L|,  h = |H|.
```

A slack richer suffix `v(H)<phi(H)` is possible exactly when

```text
m >= 4  if h=1,
m >= 3  if h=2 or h=3,
m >= 2  if h>=4.
```

The lower bounds are the existing human consequences of balanced-trace
transport:

- `m=1` is impossible for every `h` because the required poor displacement
  cannot have both signs;
- `h=1,m<=3` is impossible by the unique-richest protector-packing theorem;
- `m=2,h<=3` is impossible by the two-poorer minimal-balanced-packet theorem.

The upper bounds are supplied by three dimension-free integral
indecomposable lower-envelope families:

- `h=1,m>=4`: the indecomposable unique-richest family;
- `m=2,h>=4`: the internal-sacrifice family, with `Lmin=Lmax`;
- `m>=3,h>=2`: the new universal three-poorer family below.

This is a classification of arbitrary strict Lmin boundaries.  The poorer
side may contain more than one payoff stratum; no two-stratum hypothesis is
used.

The `m=2` boundary has a stronger, dimension-free structural reading.  For
any richer-side size, a slack suffix above exactly two poorer players forces
the active rich-trace exact-cover polytope to be nonintegral; hence its
incidence matrix contains an odd balanced-matrix obstruction.  The `h=3`
triangle is the only small fractional packet and is eliminated by exact
singleton faces.  The `h>=4` realizing family activates every co-singleton
trace and therefore contains the symbolic odd-cycle matrix
`[[0,1,1],[1,0,1],[1,1,0]]`.  See
`paper3/INTEGRAL_TRACE_OBSTRUCTION.md`.

## Universal three-poorer family

Write the poorer side as `{p1,p2,p3} disjoint-union Q`, where `|Q|=m-3`,
and the richer suffix as `H={r1,...,rh}`.  The lower envelope of

```text
a   = 2 e_p1 + 3 e_p3 + 1_Q + 5 e_r1 + 3 1_(H\{r1,rh}),
b   = 2 e_p2 +   e_p3 + 1_Q + 4 e_r1 + 3 1_(H\{r1}),
c   = 1_Q + (3h+4) e_rh,
phi = e_p1 + e_p2 + 2 e_p3 + 1_Q + 3 1_H,
q^j = phi + e_p1 - e_j  for j in Q
```

is exact because all rows have common total `m+3h+1`.  It is
singleton-normalized because each player is zero in a displayed row.  The
load-bearing values are

```text
v(N\{j})   = m+3h                 (j in Q),
v(H+p3)    = 3h+2,
v(H+p1)    = 3h+1,
v(H)       = 3h-1.
```

At a core point giving everyone at least one, the complement faces first pin
`Q`, then `v(H+p3)` pins `p1,p2` at one.  On that face `v(H+p1)` pins `p3`
at two.  Efficiency leaves total `3h` on `H`, which is equalized at three.
Thus

```text
Lmin = (1 on p1,p2,Q; 2 on p3; 3 on H),
v(H) = 3h-1 < 3h = Lmin(H).
```

The same family also has a closed-form, distinct Lmax.  With
`epsilon=1/(h+1)`,

```text
Lmax = (2-epsilon on p1, epsilon on p2,
        3-epsilon on p3 and H, 1 on Q),
||Lmin-Lmax||_1 = 4h/(h+1).
```

The rich-plus-`p3` face forces the first Lmax ceiling `3-epsilon`; the
rich-plus-`p1` face forces the second ceiling `2-epsilon`; and the
rich-plus-`p1`-plus-`j` faces force every `j in Q` to one.  A two-row
coalition-difference argument verifies the displayed point is in the core in
every dimension.

The family is indecomposable.  If `Q` is nonempty, any fixed `j in Q` has
pair worth one with every other player, so the positive-pair graph is
connected.  If `Q` is empty, positive pair worths connect all players except
`p2`, while

```text
v({p1,p3,rh}) = 4 < 5 = v({p1,p2,p3,rh})
```

attaches `p2` to the same summand.  Thus the construction specializes at
`(m,h)=(3,2)` to a cleaner member of the same boundary type as the earlier
five-player escape, but it is not obtained by null padding or direct sums.

## Reproduction

From `coopgames/` run:

```bash
python src/verify_three_poorer_boundary_family.py \
  --max-poorer-side 6 --max-richer-suffix 6 \
  --exact-replay-through-players 6 \
  --output results/three_poorer_boundary_family.json
```

The verifier checks all symbolic identities in 20 parameter cases and uses
the generic exact staged Lmin and Lmax solvers for
`(m,h)=(3,2),(3,3),(4,2)`.  The finite grid is an audit; the manuscript proof
is dimension-free.

## Significance discipline

The complete phase diagram is a materially broader theorem than the original
four/five classification: it identifies the exact boundary-side cardinality
threshold in every dimension and explains it through three transport
mechanisms.  It is not yet safe to call it a major field breakthrough.  The
new family, the synthesis into a complete classification, and the relevant
prior-art boundary must receive hostile mathematical and literature review.
