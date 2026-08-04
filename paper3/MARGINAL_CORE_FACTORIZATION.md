# Exact faces as marginal-core compatibility

## Factorization theorem

Let `v` be exact, `phi` a core allocation, and split
`N=H disjoint-union L`, with both parts nonempty.  Define the game on the
complement `L` by

```text
w_H(Q)=v(H union Q)-v(H),       Q subseteq L.
```

Then:

1. `w_H` is balanced.
2. `phi(Q)-w_H(Q)=s_phi(H union Q)-s_phi(H)` for every `Q subseteq L`.
3. `phi(L)=w_H(L)-s_phi(H)`.
4. `H` is tight at `phi` if and only if `phi_L` belongs to `Core(w_H)`.

## Proof

Exactness supplies `z in Core(v)` with `z(H)=v(H)`.  Its restriction to `L`
has total

```text
z(L)=v(N)-v(H)=w_H(L),
```

and for every `Q subseteq L`,

```text
z(Q)=z(H union Q)-z(H) >= v(H union Q)-v(H)=w_H(Q).
```

Thus `z_L in Core(w_H)`, proving balancedness.  The slack and total identities
follow by direct expansion.  If `H` is tight, restricting the core
inequalities of `phi` gives every inequality of `Core(w_H)`, including
efficiency.  Conversely, marginal-core efficiency together with the total
identity forces `s_phi(H)=0`.

## Consequence for exact partition

A core point witnesses exact partition precisely when, at every cumulative
payoff suffix `H`, its complementary restriction is a core allocation of the
canonical balanced marginal game `w_H`.

At a failed Lmin boundary, `phi_L` is not merely outside an arbitrary core.
It lies exactly `s_phi(H)` below the efficiency hyperplane of a balanced game:

```text
w_H(L)-phi(L)=s_phi(H).
```

The rooted completion functional is the weighted fractional-cover deficit of
this under-efficient allocation:

```text
kappa^H_phi,L(d)=d dot phi_L
  - max sum_Q nu_Q w_H(Q)
    subject to sum_Q nu_Q 1_Q=d, nu_Q>=0.
```

This factorization converts the exact-partition problem from a statement
about all faces of the original exact game into a compatibility problem
between one selected allocation and a canonical family of balanced games on
smaller player sets.

Marginal games, balancedness, exactness, and core restriction arguments are
classical objects.  The candidate contribution is the exact-face equivalence,
its use at Lmin payoff boundaries, and the identification of rooted
completion cost as the marginal game's weighted fractional-cover gap.
Focused searches did not locate this combined statement; specialist review
is still required before any novelty claim.
