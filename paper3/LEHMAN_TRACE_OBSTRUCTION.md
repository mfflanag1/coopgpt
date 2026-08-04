# Positive-Lehman trace obstruction

## Classical matrix identity

A positive Lehman pair consists of square zero--one matrices `A,B` with

```text
A B^T = J + k I,       k>=1.
```

The matrices are regular: write `r` for the row and column sum of `A` and
`s` for that of `B`.  Lehman's theorem makes this identity central to the
cores of nondegenerate minimally nonideal matrices.  None of that classical
structure is claimed as new here.

In the exact-game application, rows of `A` are rich players and columns are
the supported tight-coalition traces.  Every row of `B`, used as a zero--one
selector of those columns, has rich incidence

```text
1_H + k e_d.
```

It is exactly the rooted rounding sought by the exact-face theorem.

## Two-label density theorem

Suppose the packet weights every column of `A` by `1/r`.  Let `U` be the
columns whose lifted coalitions contain the losing poor player and `V` those
containing the gaining poor player.  Transport implies

```text
0 <= |U| < |V| < r.
```

For a column set `Z`, define

```text
Pi_B(Z) = sum_d binom(|row_d(B) intersect Z|,2).
```

The packet is impossible if

```text
s|V| - 2 Pi_B(V) > Pi_B(U).                          (LH-D)
```

Indeed, let `n_1` be the number of dual rows meeting `V` exactly once.
Column regularity and `t<=2 binom(t,2)` for `t>=2` give

```text
n_1 >= s|V| - 2 Pi_B(V).
```

If every such row met `U` at least twice, each would contribute at least one
to `Pi_B(U)`, contradicting (LH-D).  Therefore some dual row meets `V`
once and `U` at most once.  Its Lehman identity is a safe rooted cover, which
exactness forbids.

If any two columns of `B` occur together in at most one row, then
`Pi_B(Z)<=binom(|Z|,2)`, so the simpler sufficient condition is

```text
|V|(s-|V|+1) > binom(|U|,2).                         (LH-L)
```

The density condition is automatic for `|V|<=2`.  With one gaining column
there are no losing columns. With two gaining columns there is at most one
losing column, while nonsingularity makes the two dual columns distinct and
their codegree at most `s-1`.

The natural stronger conjecture is that every positive Lehman pair has the
two-label property without a density hypothesis: whenever
`|U|<|V|<r`, some dual row meets `V` once and `U` at most once. This has been
checked only on small classical examples and is not used as a theorem.

## Canonical internal face without the density hypothesis

There is an unconditional substitute for a single safe row. Put
`T=s|V|`. The Lehman diagonal gives `k+1<=s`, so `T<n` because `|V|<r` and
`rs=n+k`. Take every dual row meeting `V` and add arbitrary zero-`V` rows
until there are exactly `T` rows; call their index set `D`. Averaging these
rows gives

```text
rich load = 1_H + (k/T) 1_D,
gaining-poor load = 1,
losing-poor load = u(D)/T < 1.
```

The exact-face overload budget therefore forces

```text
k [phi(D)-v(D)] <= [T-u(D)] phi_a,                  (LH-F)
```

where `a` is the losing poor player. Thus every positive Lehman packet,
including any packet outside the density theorem, canonically exposes a
proper internal rich face with a quantitative slack budget. This is the
candidate recursive invariant for lifting minimally-nonideal contractions.

## Structural significance

This theorem places the earlier arguments in a standard combinatorial
framework:

- an odd trace cycle is the `r=2` thin-Lehman case, and its dual row is the
  alternating rounding;
- a projective plane is a self-dual, column-linear positive Lehman matrix,
  and (LH-L) recovers its coarse simple-point density bound;
- the sharp co-singleton support `J-I` instead satisfies the opposite-sign
  identity `(J-I)I=J-I`, so it is not eliminated by the positive theorem.

This is a genuine structural distinction, not a classification yet.  Two
steps remain before one can claim a dimension-free characterization:

1. reduce an arbitrary nonintegral active exact-cover packet to a Lehman core
   while preserving the two poor labels through deletions and contractions;
2. settle the two-label selection problem when (LH-D) fails.

The classical source is Cornuéjols, Guenin, and Tunçel, *Lehman matrices*,
Journal of Combinatorial Theory B 99 (2009), 531--556,
<https://doi.org/10.1016/j.jctb.2008.06.009>.  The exact-game bridge and the
two-label density argument require specialist novelty review.
