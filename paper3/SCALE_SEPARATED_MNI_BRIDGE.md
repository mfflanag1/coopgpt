# Scale-separated MNI bridge

At an underloaded two-poorer packet, let `q` be the number of active lifted
columns and choose an integer `Lambda>q`. Assign the integral cost

```text
c_T = Lambda |T intersect H| + 1_{b in T}.
```

The fractional exact-cover packet costs

```text
Lambda |H| + r_b < Lambda |H| + 1.
```

Every integral cover costs at least `Lambda|H|+1`. An overlapping cover has
at least `|H|+1` units of rich incidence. An exact partition has to use the
gaining player `b`, by the tight-coalition displacement contradiction.

Now take a positive Lehman core whose uniform weight `1/r` is feasible for
every row of its set-cover minor, lift it with unit-weight contracted columns
to a cover of the original rich rows, and evaluate it with the original
costs. Any positive rich-row excess is a sum of integer contracted
incidences and multiples of `1/r`, so it is at least `1/r`. Because
`r<=q<Lambda`, this single excess contributes

```text
Lambda/r > 1
```

above the rich-incidence baseline. Therefore any lifted minor point that
still costs less than `Lambda|H|+1` is automatically exact on every rich
row. Exactness itself forces the unit-weight contracted traces to be
pairwise disjoint and every surviving column to avoid them. The remaining
cost above the baseline is precisely the gaining-player load, which is below
one; its contracted part is integral and hence zero. The transport inequality
then removes the losing-player label from every contracted column as well.

This collapses the two apparent lifting invariants into one:

> preserve the strict scale-separated objective gap.

No separate assumptions about exact noncore rows, disjoint contractions,
survivor avoidance, or either contracted poor label are needed.

It does not prove that ordinary minimally-nonideal reduction preserves that
objective. Establishing a cost-aware or minor-compatible reduction with this
property is the remaining theorem-level bottleneck. The manuscript statement
is Corollary `cor:lx-scale-separated-exactness` in
`paper3/sections_leximin.tex`.
