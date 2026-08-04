# Thin four-label residual normal form

This note isolates the first label cardinality not eliminated by the
dimension-free Lehman arguments.

## Setup and parameter reduction

Assume a positive Lehman pair with `k=1` supports an underloaded two-poor
packet with `|V|=4`, and neither singleton residual band applies.  The
four-column odd-multiplier lemma gives a row with `w=1`.  Its residual is

```text
F=(r-4)(1-u).
```

The residual bands exclude `u=0,1,2`.  Therefore a survivor must have

```text
r>=6, |U|=3, |U intersect V|<=1,
```

and every `V`-simple row has `u=3`.  Conversely, on a row with `u=1`,

```text
F=(r-3)(w-1),
```

so a survivor requires `w>=2`.

## Six neutral-trace tiles

For every packet column `c` outside `U union V`, the transpose Lehman identity
gives

```text
sum_(d in col_c(A)) w_d=4,
sum_(d in col_c(A)) u_d=3.
```

The residual bands permit only the following nonzero row-load types:

```text
w=0: u=2,3
w=1: u=3
w=2: u=0,1
w=3: u=0,1,2
w=4: u=0,1,2,3.
```

Ignoring `(0,0)` rows, the complete multiset in a neutral trace is therefore
one of exactly six tiles:

```text
1. (4,3)
2. (1,3),(3,0)
3. (0,3),(4,0)
4. (0,3),(2,0),(2,0)
5. (0,2),(4,1)
6. (0,2),(2,0),(2,1).
```

This is the elementary partition of total load `(4,3)`: the `w`-parts are
`4`, `3+1`, or `2+2`; two `w=1` parts already use too much `u`-load.  If
`|U intersect V|=1`, tiles 3 and 4 are impossible because a row with `u=3`
must contain the common column and hence cannot have `w=0`.

## What remains

The thin `|V|=4` problem has been reduced from arbitrary Lehman labelings to
these local tiles, with overlap zero or one.  A complete exclusion would show
that the tiles cannot be assembled consistently across all columns and rows
of a positive Lehman pair.  The current result does not prove that global
incompatibility.  It is a structural human reduction, not finite enumeration,
and its novelty remains subject to specialist review.
