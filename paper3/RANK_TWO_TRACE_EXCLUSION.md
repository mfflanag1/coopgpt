# Rank-two trace exclusion at two-poorer Lmin boundaries

## Result

Let `v` be a singleton-normalized exact game, `phi=Lmin(v)`, and let a strict
payoff boundary split the players into exactly two poorer players
`L={a,b}` and a richer suffix `H`. If the boundary is slack, every
underloaded extreme packet forced by balanced-trace transport contains a
**proper** rich trace `R` satisfying

```text
3 <= |R| <= |H|-1.
```

Such an underloaded packet always exists. Consequently every slack
two-poorer boundary has `|H|>=4`, and a boundary whose proper active traces
all have size at most two is tight. The statement is dimension-free and uses
no finite enumeration.

## Why rank two is special

For a trace hypergraph containing only singleton and pair edges, consider

```text
Q(H)={beta>=0 : sum_R beta_R 1_R=1_H}.
```

Every vertex of this exact-cover polytope is half-integral. Its positive
support decomposes into:

- singleton components of weight one;
- isolated pair edges of weight one;
- vertex-disjoint odd cycles whose edges have weight one half.

This follows directly from linear independence of the positive incidence
columns. A tree component with more than one edge has a leaf whose equation
forces an adjacent positive column to zero. A component of minimum degree two
has at least as many edges as vertices, while independence allows at most as
many; hence it is a cycle. Even-cycle incidence columns are dependent, and an
odd cycle has the unique solution `beta=1/2`.

## Transport and rounding proof

Assume the suffix slack is `s>0`. Exactness supplies a core point exact on
`H`; balanced-trace transport gives poor displacements

```text
Delta_a<0<Delta_b,
Delta_a+Delta_b=s,
```

and a mixture of lifted extreme trace covers whose average load on each poor
player is below one. Fix any packet with `b`-load below one. Its minimal
balanced support cannot contain the full trace `H`: `{H}` is already a
balanced collection, so minimality would make it the entire unit-weight
packet, whose zero `b`-load violates transport. If the packet had no proper
trace of size at least three, all its traces would therefore have size at
most two. The graph decomposition above applies. An integral packet must load
the gaining player `b` at least once, so this packet is fractional.
Half-integrality and the packet transport inequality force

```text
r_b=1/2,
r_a=0.
```

Thus exactly one edge of one odd-cycle component carries `b`, and none of the
packet coalitions carries `a`.

If it is the only odd-cycle component, number it `e_0,...,e_{2k}` so that
`e_0` carries `b`. Replace its half weights by unit weights on

```text
e_0,e_2,...,e_{2k}.
```

The alternating edges cover every cycle vertex once and duplicate the common
endpoint `d=e_0 cap e_{2k}`. All other components are then integral blocks;
leaving them unchanged produces
a nonnegative combination of original `phi`-tight coalitions with incidence
load

```text
1_H + e_d + e_b.
```

Exactify singleton `d`, obtaining a core point `x` with `x_d=0`. Summing the
tight inequalities gives

```text
x(H)+x_b >= phi(H)+phi_d+phi_b.
```

Since singleton normalization gives `x_a>=0` and `phi_d>phi_a` across the
strict boundary, efficiency implies

```text
phi(N)=x(N)
      >= phi(H)+phi_d+phi_b
       > phi(H)+phi_a+phi_b
       = phi(N),
```

a contradiction.

Equivalently, the alternating edges form a safe rooted tight cover with root
`d`, multiplicity one, and poor load `e_b`. The general reason it is
impossible is the exact-face rooted-semigroup theorem in
[`ROOTED_SEMIGROUP_OBSTRUCTION.md`](ROOTED_SEMIGROUP_OBSTRUCTION.md).

Round the distinguished cycle containing the unique `b`-edge and leave every
other component at its original exact-cover weights. This includes weight
`1/2` on any other odd-cycle component. The resulting tight-coalition
combination has

```text
rich load = 1_H + e_d,
poor load = e_b.
```

The exact-face overload budget accepts nonnegative real weights, so it gives
`phi_d<=phi_a`, contradicting the strict boundary. This remains valid with
multiple odd-cycle components precisely because they need not be rounded.
What fails in that case is only the stronger interpretation as an integer
semigroup fibre: the untouched cycles still have half weights. Thus every
underloaded packet must contain the claimed proper rank-three-or-higher
trace.

## Significance

The earlier odd-cycle theorem says that a slack two-poorer boundary must make
the active trace matrix non-balanced. The present theorem is stronger in a
different direction: no graph-like underloaded packet is realizable. The
proof uses a real tight-cover overload, not necessarily an integer rooted
fibre.

This explains the sharp family structurally. A failure requires a proper
rank-three trace, so four is the first possible rich-side size. At four rich
players the active co-singletons are proper triples; the smallest realizable
obstruction is not the bare triangle on three vertices but a triangle
submatrix whose columns can use an additional rich player. The remaining
research target is
to characterize which rank-three and higher hypergraph obstructions admit
exact-face realizations.

Correctness and novelty have not yet received external specialist review.
