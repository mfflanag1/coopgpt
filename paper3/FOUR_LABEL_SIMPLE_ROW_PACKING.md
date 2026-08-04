# Four-label simple-row packing

This note strengthens the thin four-label residual normal form by using the
classical triple-intersection property of a Lehman pair.

## Packing lemma

Continue with `k=1`, `|V|=4`, `|U|=3`, `|U intersect V|<=1`, and assume both
singleton residual bands fail.  Write

```text
Q={d: u_d=3}.
```

The `A`-row supports indexed by `Q` are pairwise disjoint.  Indeed, fix two
columns `a,b` of `U`.  The column version of the Lehman triple-intersection
property, applied after swapping the pair `(A,B)`, gives

```text
|col_a(B) intersect col_b(B) intersect col_c(A)| <= 1
```

for every `A`-column `c`.  Two rows of `Q` lie in both `B`-columns `a,b`, so
they cannot occur together in any `col_c(A)`.  Since every `A`-row has size
`r` and `n=rs-1`,

```text
|Q| r <= n = rs-1,
```

and hence `|Q|<=s-1`.  Four-column separation supplies at least one row with
`w=1`, and every such row has `u=3`, so

```text
1 <= #{d:w_d=1} <= |Q| <= s-1.
```

## Forced neutral star

Let `d` have `(w_d,u_d)=(1,3)`.  Its `B`-row contains all three `U` labels.
If the label sets are disjoint it contains one further `V` label; if their
overlap is one, that common label is its unique `V` label.  In either case
exactly three labels in `U union V` lie outside `row_d(B)`.

The diagonal identity gives

```text
|row_d(A) intersect row_d(B)|=2.
```

Thus `row_d(A)` contains at most five label columns and at least `r-5`
neutral columns.  On any such neutral column, row `d` already supplies load
`(1,3)` out of the required total `(4,3)`.  Every other nonzero row must have
`u=0` and the remaining `w`-load is three.  The residual bands allow only one
completion:

```text
(1,3),(3,0).
```

Therefore every simple row anchors at least `r-5` type-2 neutral traces, each
with a unique `(3,0)` companion.

## Significance and remaining step

The negative-extreme rows are not merely rare load patterns: they form a
packing of disjoint primal supports, and each carries a forced star of
opposite-sign companions.  A global exclusion would follow from showing that
the required `(3,0)` companion stars cannot be accommodated by the remaining
Lehman intersections.  That final congestion bound is not proved here.
