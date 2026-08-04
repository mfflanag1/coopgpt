# Rank-two trace exclusion at two-poorer Lmin boundaries

## Result

Let `v` be a singleton-normalized exact game, `phi=Lmin(v)`, and let a strict
payoff boundary split the players into exactly two poorer players
`L={a,b}` and a richer suffix `H`. If every nonempty `H`-trace of a proper
`phi`-tight coalition has size at most two, then

```text
phi(H)=v(H).
```

Equivalently, every slack two-poorer boundary is **genuinely hypergraphic**:
some proper coalition tight at `phi` intersects `H` in at least three players.
The statement is dimension-free and uses no finite enumeration.

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
player is below one. Every integral cover packet must load the gaining player
`b` at least once. Therefore some fractional packet has `b`-load below one.
Half-integrality and the packet transport inequality force

```text
r_b=1/2,
r_a=0.
```

Thus exactly one edge of one odd-cycle component carries `b`, and none of the
packet coalitions carries `a`.

Number that odd cycle `e_0,...,e_{2k}` so that `e_0` carries `b`. Replace its
half weights by unit weights on

```text
e_0,e_2,...,e_{2k}.
```

The alternating edges cover every cycle vertex once and duplicate the common
endpoint `d=e_0 cap e_{2k}`. Leaving all other components unchanged produces
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

## Significance

The earlier odd-cycle theorem says that a slack two-poorer boundary must make
the active trace matrix non-balanced. The present theorem is stronger in a
different direction: **no graph-like odd-cycle obstruction is realizable at
all**. A realizable failure needs a trace of rank at least three.

This explains the sharp family structurally. At four rich players its active
co-singleton traces have size three; the smallest realizable obstruction is
not the bare triangle on three vertices but a triangle submatrix whose three
columns all use an additional rich player. The remaining research target is
to characterize which rank-three and higher hypergraph obstructions admit
exact-face realizations.

Correctness and novelty have not yet received external specialist review.
