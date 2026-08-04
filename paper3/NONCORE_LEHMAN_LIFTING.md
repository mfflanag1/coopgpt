# Noncore-aware Lehman lifting

A classical minimally-nonideal matrix can have rows outside its square
Lehman core. Its uniform fractional vertex may cover those rows more than
once, so an exact-game lift cannot simply ignore them.

There is nevertheless a direct selector criterion. Let `A,B` be a positive
Lehman pair and let `E` be the additional row supports. Every blocker-core
row is a transversal of every row of the MNI clutter, so

```text
|row_d(B) intersect W| >= 1       for every d and W in E.
```

As before, at least

```text
s|V| - 2 Pi_B(V)
```

dual rows meet the gaining-label set `V` exactly once. At most `Pi_B(U)` of
them meet the losing-label set `U` twice. For each noncore support `W`, none
meets it zero times, and the number meeting it at least twice is at most its
total excess incidence

```text
sum_d (|row_d(B) intersect W|-1)
  = s|W|-n
  = s(|W|-r)+k.
```

Therefore

```text
s|V| - 2 Pi_B(V) > Pi_B(U) + sum_(W in E) [s|W|-n]
```

guarantees a single dual row that

- meets `V` once;
- meets `U` at most once; and
- meets every noncore row exactly once.

Its lifted coalitions have Lehman rooted load on the core, unit load on all
noncore rich rows, and safe nonzero poor load. Adding any neutral contracted
partition columns, whose rich rows the surviving columns avoid, completes the
forbidden rooted cover of the original rich suffix.

This theorem does not show that the displayed density condition is automatic.
It does remove the hidden assumption that noncore rows can be discarded and
gives a precise additional term for each such row. The manuscript proof is
Corollary `cor:lx-noncore-lehman-rounding` in
`paper3/sections_leximin.tex`.
