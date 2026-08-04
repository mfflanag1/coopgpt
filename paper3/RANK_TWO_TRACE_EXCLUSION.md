# Rank-two trace exclusion at two-poorer Lmin boundaries

## Result

Let `v` be a singleton-normalized exact game, `phi=Lmin(v)`, and let a strict
payoff boundary split the players into exactly two poorer players
`L={a,b}` and a richer suffix `H`. If the boundary is slack, every
underloaded extreme packet forced by balanced-trace transport satisfies one
of two alternatives:

```text
(i)  it contains a proper trace R with 3 <= |R| <= |H|-1; or
(ii) its rank-one/two support contains at least two disjoint odd cycles.
```

In alternative (ii), transport forces `r_b=1/2`, `r_a=0`, and exactly one
edge to carry `b`. Alternating every cycle, with the labeled edge selected,
duplicates one vertex from each component. For every resulting transversal
`D` of cycle vertices,

```text
s_phi(D) <= phi_a.
```

Such an underloaded packet always exists. Consequently every slack
two-poorer boundary has `|H|>=4`; a failure using only rank-one and rank-two
traces needs at least six rich players. The statement is dimension-free and
uses no finite enumeration.

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

If there is only one odd-cycle component, this is the forbidden safe rooted
cover above. With several odd cycles, however, all of them must be rounded:
leaving any at half weight would not give an integer cover. Choose an
alternating near-perfect cover on every cycle. On the distinguished cycle,
choose the orientation containing the unique `b`-edge. If `D` contains the
one duplicated vertex from each cycle, the selected tight coalitions have

```text
rich load = 1_H + 1_D,
poor load = e_b.
```

The exact-face overload budget therefore gives `s_phi(D)<=phi_a`. If there
were only one cycle, `D={d}` and singleton normalization would give
`s_phi(D)=phi_d>phi_a`, a contradiction. Hence a rank-two underloaded packet
must have at least two odd-cycle components, using at least six rich players.

This corrects an earlier draft shortcut that rounded the labeled cycle while
silently leaving other odd cycles at half weight. The singleton-root
conclusion is valid only in the one-cycle case.

## Significance

The earlier odd-cycle theorem says that a slack two-poorer boundary must make
the active trace matrix non-balanced. The present theorem is stronger in a
different direction: a graph-like obstruction cannot consist of one odd
cycle. It needs at least two disjoint odd cycles, and every simultaneous
alternating rounding must land on a low-slack transversal face.

This explains the sharp family structurally. Below four rich players neither
a proper rank-three trace nor two disjoint odd cycles can exist. At four rich
players the active co-singletons are proper triples; the smallest realizable
obstruction is not the bare triangle on three vertices but a triangle
submatrix whose columns can use an additional rich player. The remaining
research target is
to characterize which rank-three and higher hypergraph obstructions admit
exact-face realizations.

Correctness and novelty have not yet received external specialist review.
