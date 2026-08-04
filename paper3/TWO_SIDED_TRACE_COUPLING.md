# Two-sided trace-coupling normal form

Fix a nontrivial split `N=H dot-union L`.  A rooted obstruction identity has
exceptional coalition `H`, positive rooted spokes `H union {i}`, and other
positive coalitions `T`:

```text
sum_T lambda_T 1_T + sum_i u_i 1_(H union {i}) - gamma 1_H
    = beta 1_N.                                      (RC)
```

All coefficients are nonnegative except the displayed root coefficient,
which has `gamma>0`.  Put

```text
R_T = T intersect H,       Q_T = T intersect L,
tau = sum_i u_i.
```

## Normal-form theorem

Identity (RC) holds if and only if there is a scalar `alpha` such that

```text
sum_T lambda_T 1_(R_T) = alpha 1_H,                 (H-cover)
sum_T lambda_T 1_(Q_T) + sum_i u_i e_i = beta 1_L, (L-cover)
gamma = alpha - beta + tau.                         (coupling)
```

The proof is coordinatewise.  Restrict (RC) first to `L`, obtaining the
`L`-cover.  Restriction to `H` gives

```text
sum_T lambda_T 1_(R_T) + (tau-gamma)1_H = beta 1_H,
```

which is the `H`-cover with `alpha=beta+gamma-tau`.  The converse follows by
adding the two block equations.

Thus every rooted Lmin atom is a coupling of two exact-cover hypergraphs:

- the non-spoke rich traces form a uniform cover of `H` whenever
  `alpha>0`;
- their poor traces, completed by singleton spokes, form a uniform cover of
  `L`;
- the exceptional coefficient is exactly the difference of the two cover
  loads plus the total completion mass.

This is a complete dimension-free incidence normal form.  As a linear
isomorphism of the corresponding nonnegative relation and coupling cones, it
preserves extreme rays.  In particular, a rooted circuit, which is
support-minimal in its fixed sign cone, becomes an extreme coupling ray.  The
normal form does not depend on the number of players, payoff strata, or
enumeration of games.

## Star and trace-cycle alternatives

If there are no non-spoke coalitions, the `L`-cover forces `u_i=beta` for
every poorer player.  Consequently

```text
gamma = (|L|-1) beta,
```

and (RC) is exactly the block-star facet.  If non-spoke coalitions occur and
`alpha>0`, their normalized rich traces form a balanced packet on `H`.
If `alpha=0`, every positive-weight non-spoke coalition is disjoint from `H`,
so the residual geometry is entirely on the poorer side.  Hence a genuinely non-star rooted
atom cannot be structureless: it contains either a balanced rich-trace packet
or a poorer-side incidence circuit.

The three-trace obstruction illustrates the rich-active case.  Its three
non-spoke rich traces form the internal triangle cover of `H`, while the poor
trace of the third coalition couples that packet to the two poorer players.
The five-player broken diamond and the universal one-/three-poorer escape
identities have no non-spoke terms after rooting and are pure block stars.

## Lmin single-packet star-or-trace reduction

The poorer-side residual case can be removed for Lmin-selected atoms.  Start
with the strict tight cover supplied at a slack richer suffix and delete every
positive-weight tight coalition disjoint from `H`.  The load on `H` is
unchanged and all poorer loads only decrease, so the cover remains strict.
Apply rooted completion and conformal circuit reduction to this pruned cover.
Every surviving non-spoke coalition then has a nonempty rich trace.

Normalize the pruned cover's rich load to one and decompose it into extreme
points of its bounded exact-cover polytope.  These are lifted minimal balanced
packets.  If `r` is a packet's poorer load vector and `m=|L|`, define

```text
delta(r) = 1 + (m-1) max_i r_i - sum_i r_i.
```

The function `delta` is convex.  The average poorer load `c` is strictly
below one coordinatewise, so, with `beta=max_i c_i`,

```text
delta(c) >= 1-beta > 0.
```

Jensen's inequality forces `delta(r)>0` for at least one minimal packet.
Completing that packet by rooted spokes of weights
`max_j r_j-r_i` gives a rooted relation with exceptional coefficient exactly
`delta(r)`.  A conformal circuit containing the root either uses no
non-spoke term, or its rich traces are a balanced subcollection of the
minimal packet and hence the whole packet.

Consequently every slack Lmin boundary selects a rooted circuit with at most
`|N|` coalitions of exactly one of the following two types:

1. **star type:** there are no non-spoke coalitions, and the circuit is the
   pure block star on all poorer singleton blocks;
2. **trace-coupled type:** `alpha>0`, and the normalized non-spoke rich traces
   are exactly one minimal balanced collection on `H`.

Thus every failure is forced into an exterior-sacrifice star or an internal
minimal balanced-transport mechanism.  Mixtures are unnecessary.  This
dichotomy is dimension-free and applies before any classification by player
count.

## Canonical slack transfer

The canonical completion also supplies a scalar invariant. For a selected
packet with poorer loads `r`, put `b=max_i r_i`, `d_i=b-r_i`, and
`delta=1-b+sum_i d_i`. Exact balancedness applied to the completed packet
gives

```text
delta s_phi(H) <= sum_i d_i s_phi(H union {i}).
```

If `b<1`, some completion coalition has strictly greater slack than `H`.
With exactly two poorer players, transport labels their packet loads as
`r_a<r_b<1`, so only the losing-player completion remains and

```text
s_phi(H union {a})
  >= (1-r_a)/(r_b-r_a) s_phi(H)
  > s_phi(H).
```

Equivalently,

```text
v(H union {a})-v(H)
  <= phi_a-(1-r_b)/(r_b-r_a) s_phi(H)
  < phi_a.
```

Hence the global suffix failure has a local marginal-deficit witness on one
adjacent edge of the coalition lattice.

The trace-coupled branch therefore has forced strict slack ascent; no
analogous conclusion follows from the pure block-star identity. The full statement and sharp examples are in
`paper3/CANONICAL_PACKET_SLACK_TRANSFER.md`.

## Consequence for the breakthrough program

The earlier conjecture that every rooted atom should be assembled only from
block stars and internal facets is too syntactic.  The invariant object is
the cone of **couplings** between a balanced rich-trace packet and a
singleton-completed poor-trace packet.  Its extreme rays are the correct
candidate obstruction types.  A general classification or forbidden-minor
theorem for these coupling rays would be a dimension-free theory rather than
a list of small games.

The exact verifier `src/verify_two_sided_trace_coupling.py` checks both
directions of the identities and the claimed parameters for the sharp
five-player atom, the universal block stars, and the three-trace atom.  Those
checks are bug detectors; the theorem is the coordinatewise argument above.
