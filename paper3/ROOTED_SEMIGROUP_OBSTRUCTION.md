# Exact-face rooted-semigroup obstruction

## The dimension-free theorem

Let `v` be singleton-normalized and exact, let `phi` be a core allocation,
and let a strict payoff boundary split the players into two poorer players
`L={a,b}` and a richer side `H`.

Take any finite family of proper `phi`-tight coalitions. A nonnegative
integer multiplicity vector on these coalitions is a **safe rooted tight
cover** if, for some rich player `d` and integer `k>=1`, its incidence loads
are

```text
rich load = 1_H + k e_d,
poor load in {0,1}^{a,b} setminus {(0,0)}.
```

No such cover exists.

This statement is independent of the number of rich players, the ranks or
sizes of the tight traces, and the particular fractional exact-cover vertex
from which the coalitions were obtained.

It is the discrete singleton specialization of the stronger real-valued
[`EXACT_FACE_OVERLOAD_BUDGET.md`](EXACT_FACE_OVERLOAD_BUDGET.md): with root
`D={d}`, that inequality says

```text
k phi_d <= payoff of the omitted poor players.
```

The strict two-poorer boundary makes this impossible whenever the zero--one
poor load is nonzero.

## Proof

Exactify singleton `d`: exactness gives a core point `x` with `x_d=0`.
Summing the selected tight-coalition inequalities with their integer
multiplicities gives

```text
x(H) + sum_i p_i x_i
  >= phi(H) + k phi_d + sum_i p_i phi_i.
```

Add `x_i>=0` for an omitted poor player. If both poor players are loaded,
efficiency says

```text
phi(N)=x(N) >= phi(N)+k phi_d > phi(N).
```

If exactly one is loaded and `j` is omitted, efficiency says

```text
phi(N)=x(N) >= phi(N)+k phi_d-phi_j > phi(N),
```

because the boundary is strict, so `phi_d>phi_j>=0`. Both cases are
impossible.

## Why this is a general mechanism

Write `M` for the rich trace-incidence matrix of a lifted tight packet and
`U` for its two poor-incidence rows. The integer columns generate an affine
semigroup. A slack two-poorer boundary can use an underloading fractional
exact cover only if its supported semigroup avoids every fibre

```text
M y = 1_H + k e_d,
U y in {0,1}^2 setminus {0},
y integer and nonnegative.
```

Thus the obstruction is not merely that the trace exact-cover polytope is
fractional. Its supported integer semigroup must avoid a specific family of
**rooted fibres**. We do not call these fibres semigroup holes: that term
usually carries the additional requirement that the point lie in the
group/cone saturation of the semigroup, which is not asserted here. This
separates three layers:

1. balanced-trace transport forces a fractional underloading packet;
2. combinatorial rounding tries to enter a rooted integer fibre;
3. exact singleton faces prohibit every safe rooted fibre.

The existing human theorems are now instances of this one mechanism:

- rank-two traces: alternating an odd cycle produces `1_H+e_d+e_b`;
- the four-rich classification: four of the five fractional vertex types
  have a multiplicity-one rooted cover;
- projective-plane packets: a pencil through a safe point produces
  `1_H+q e_d` with safe poor loads.

## Research consequence

The next general target is an affine-semigroup theorem: characterize the
zero--one trace matrices and poor labelings whose underloading exact-cover
vertices avoid all safe rooted fibres. A normality or Hilbert-basis result
forcing a safe rooted fibre would rule out an entire hypergraph class at once
and could yield a dimension-free converse. Such a result would require a
separate saturation argument; the theorem above does not itself establish
normality, nonnormality, or the existence of a semigroup hole.

This formulation does not claim that normality theory, affine semigroups, or
Hilbert bases are new. The candidate contribution is the exact-game bridge:
rooted integer fibres of tight trace packets are forbidden by exact singleton
faces. Correctness, terminology, and novelty still require specialist
review.
