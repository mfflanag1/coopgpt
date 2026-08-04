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
phi(H)-v(H) < phi(D)-v(D) <= [T-u(D)] phi_a/k.      (LH-F)
```

For the strict inequality, evaluate each dual row outside `D` at the core
point exact on `H`. Such a row carries no gaining-poor label, so its rooted
tight-coalition sum forces the corresponding rich displacement to be
positive. Every rich player outside `D` therefore gains, while `H` loses its
total suffix slack. The displacement of `D` is consequently more negative
than that total slack, and core feasibility converts this into the strict
lower bound above.

Thus every positive Lehman packet, including any packet outside the density
theorem, canonically amplifies the suffix slack onto a proper internal rich
face. This is the candidate recursive invariant for lifting
minimally-nonideal contractions.

## Contractions need only preserve one scalar deficit

Suppose a classical minor lift adjoins unit-weight contracted columns whose
disjoint traces partition the rich rows outside a positive Lehman core. Let
`t_a,t_b` count their losing- and gaining-poor labels. The combined tight
packet satisfies

```text
-sigma + (t_a+|U|/r) Delta_a
       + (t_b+|V|/r) Delta_b >= 0.
```

If its total gaining load is below one, then `t_b=0`, `|V|<r`, and substitution
of `Delta_b=sigma-Delta_a` forces

```text
r t_a + |U| < |V|.
```

Hence `t_a=t_b=0` and `|U|<|V|<r`: every contracted column is automatically
poor-label-free. Adding those neutral columns to a safe Lehman dual row gives
the same rooted cover of the original suffix, and adding them to the averaged
dual rows preserves the strict internal-face amplification. The unresolved
minor step is therefore only preservation of the scalar gaining-player load
below one, not separate preservation of two label sets. See
`LEHMAN_MINOR_LIFTING.md` for the standalone statement and
Corollary `cor:lx-deficit-preserving-lehman-minor` for the proof.

## Structural significance

This theorem places the earlier arguments in a standard combinatorial
framework:

- an odd trace cycle is the `r=2` thin-Lehman case, and its dual row is the
  alternating rounding;
- a projective plane is a self-dual, column-linear positive Lehman matrix,
  and (LH-L) recovers its coarse simple-point density bound;
- the sharp co-singleton support `J-I` instead satisfies the opposite-sign
  identity `(J-I)I=J-I`, so it is not eliminated by the positive theorem.

The other classical branch of the minimally-nonideal theorem, a degenerate
projective plane, is eliminated directly by
`DEGENERATE_MNI_TRACE_EXCLUSION.md`. Its unique nonuniform fractional cover
always yields a safe two-column rooted rounding under the required poor-load
ordering. The explicit objective in `UNIT_GAP_MNI_BRIDGE.md` proves that an
underloaded active trace matrix is nonideal and identifies the scalar
underload with a strict unit set-cover gap.

This is a genuine structural distinction, not a classification yet.  Two
steps remain before one can claim a dimension-free characterization:

1. reduce an arbitrary underloaded active exact-cover packet to a positive
   Lehman core while preserving its scalar gaining-player deficit below one;
2. settle the two-label selection problem when (LH-D) fails.

The classical source is Cornuéjols, Guenin, and Tunçel, *Lehman matrices*,
Journal of Combinatorial Theory B 99 (2009), 531--556,
<https://doi.org/10.1016/j.jctb.2008.06.009>.  The exact-game bridge and the
two-label density argument require specialist novelty review.
