# Deficit-preserving Lehman-minor lifting

This note isolates the exact obstruction in lifting a minimally-nonideal
minor back to a two-poorer Lmin boundary. The classical minor reduction may
fix some trace columns at one. Their rich traces are disjoint and partition
the rows removed by contraction. At first sight, their two poor-player
labels appear to be uncontrolled.

They are in fact controlled by one scalar condition.

Let `a` lose and `b` gain at a core point exact on a slack richer suffix `H`:

```text
Delta_a < 0 < Delta_b,
Delta_a + Delta_b = sigma = phi(H)-v(H) > 0.
```

Suppose contracted tight coalitions have unit weights and counts `t_a,t_b`,
while a surviving positive Lehman core has uniform weight `1/r` and label
sets `U,V`. The lifted exact-cover packet obeys

```text
-sigma + (t_a+|U|/r) Delta_a
       + (t_b+|V|/r) Delta_b >= 0.                 (LM)
```

If its gaining load is below one,

```text
t_b+|V|/r < 1,
```

then `t_b=0` and `|V|<r`. Substituting
`Delta_b=sigma-Delta_a` into (LM) shows

```text
r t_a + |U| < |V|.
```

Hence

```text
t_a=t_b=0,              0 <= |U| < |V| < r.
```

Thus no contracted column carries either poor player. Poor-label
preservation need not be imposed separately: it follows from preservation of
the gaining-player deficit.

This observation lifts both structural consequences of a positive Lehman
core to the original rich suffix:

1. any dual row meeting `V` once and `U` at most once, together with the
   contracted columns, is a forbidden safe rooted tight cover of all `H`;
2. even if no such row is found, averaging `s|V|` suitable dual rows and
   adjoining the contracted columns gives a proper internal face `D` with

```text
phi(H)-v(H) < phi(D)-v(D) <= [s|V|-u(D)] phi_a/k.
```

The second statement remains strict because the uncontracted rows outside
`D` gain strictly, while the contracted tight coalitions are poor-label-free
and have nonnegative displacement.

The remaining reduction problem is therefore narrower and precise: prove
that an underloaded extreme packet admits a positive Lehman minor whose
**lifted fractional core still has gaining-player load below one**. No
separate two-label invariant is needed once this scalar deficit survives.

The manuscript statement and full proof are Corollary
`cor:lx-deficit-preserving-lehman-minor` in
`paper3/sections_leximin.tex`.
