# Three-column separation in positive Lehman pairs

## The structural lemma

Let `A,B` be square zero-one matrices satisfying

```text
A B^T = J + k I,
```

where `k>=1`, `A` is `r`-regular, `B` is `s`-regular, and `r>=4`.
Every three columns `V` of `B` have a row meeting `V` exactly once.

This is a dimension-free incidence statement; it does not use a catalogue or
classification of Lehman matrices.

## Proof

Assume no row meets `V` once and put `y=B 1_V`.  Then every entry of `y` is
`0`, `2`, or `3`.  Let `x` count the rows where `y=3`.  The classical
transpose identity `A^T B=J+kI` for Lehman pairs gives

```text
A^T y = (J+kI)1_V = 3 1 + k 1_V.
```

Every column of `A` outside `V` therefore has scalar product three with `y`.
Because the only positive values of `y` are two and three, such a column meets
exactly one `y=3` row and no `y=2` row.  Hence

```text
n-3 <= r x.
```

Regularity gives `n=rs-k`, while the diagonal Lehman intersection gives
`k+1<=r`.  Therefore

```text
x >= s-(k+3)/r >= s-3/2,
```

and integrality gives `x>=s-1`.

The three columns have total incidence `3s`.  Their common `x` rows contribute
`3x`; every other nonzero row contributes two.  Thus `3(s-x)` is even.  Since
`x<=s` and `x>=s-1`, parity forces `x=s`.  The three columns are then supported
on precisely the same `s` rows and are identical, contradicting nonsingularity
of `B`.  The required row exists.

## Exact-game consequence

In an underloaded two-poor positive-Lehman packet, write `U,V` for the losing
and gaining label columns and `p=|U|<ell=|V|<r`.  The cases `ell<=2` were
already excluded by the pair count.  If `ell=3`, the lemma gives a dual row
with `w=1`.  Since `p<=2`, its losing load `u` is `0`, `1`, or `2`, and the
label residual is

```text
F=(r-3)(1-u).
```

- `u=0`: `0<F=r-3<=k(r-3)`, so the positive residual band applies.
- `u=1`: `F=0`, so the positive residual band applies at its endpoint.
- `u=2`: necessarily `p=2`, and
  `-k(r-2)<=-(r-3)=F<0`, so the negative residual band applies.

Thus every positive-Lehman packet with `|V|<=3` is impossible.  Any surviving
positive-Lehman obstruction must satisfy

```text
|V|>=4 and r>=5.
```

The result does not classify positive Lehman matrices and does not yet exclude
the `|V|>=4` residual-polarized regime.  Novelty relative to the Lehman-matrix
literature requires specialist review.
