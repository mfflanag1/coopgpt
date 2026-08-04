# Canonical packet slack transfer

## Result

Let `v` be a singleton-normalized exact game, let `phi` be a core
allocation, and split the players as `N=H disjoint-union L`. Suppose a
normalized minimal balanced packet of nonempty rich traces is lifted to
proper `phi`-tight coalitions `T`, with weights `lambda_T` and poorer load
vector

```text
r_i = sum_(T containing i) lambda_T,    i in L.
```

Put

```text
b       = max_i r_i,
d_i     = b-r_i,
delta   = 1+(|L|-1)b-sum_i r_i
        = 1-b+sum_i d_i.
```

Whenever `delta>0`, the canonical completion identity is

```text
sum_T lambda_T 1_T
+ sum_i d_i 1_(H union {i})
- delta 1_H
= b 1_N.
```

Exact balancedness and tightness of the packet imply the **slack-transfer
inequality**

```text
delta s_phi(H) <= sum_i d_i s_phi(H union {i}).       (ST)
```

If `b<1` and `H` is slack, then `sum_i d_i>0` and hence

```text
max_(i:d_i>0) s_phi(H union {i}) / s_phi(H)
 >= delta/sum_i d_i
 = 1 + (1-b)/sum_i d_i
 > 1.                                                   (SA)
```

Thus every genuinely underloaded trace packet strictly transfers the failed
suffix slack to a larger proper coalition. Such a packet cannot be a
terminal obstruction.

## Two-poorer specialization

At a slack Lmin boundary with exactly two poorer players, balanced-trace
transport selects a lifted minimal packet whose poorer loads, after labeling
the losing player `a` and gaining player `b`, satisfy

```text
0 <= r_a < r_b < 1.
```

The canonical completion has only one positive spoke:

```text
sum_T lambda_T 1_T
+ (r_b-r_a) 1_(H union {a})
- (1-r_a) 1_H
= r_b 1_N.
```

Consequently

```text
s_phi(H union {a})
 >= [(1-r_a)/(r_b-r_a)] s_phi(H)
 > s_phi(H).                                          (2P)
```

The coalition receiving the amplified slack is canonical: it adjoins the
losing poorer player and omits the unique gaining poorer player.

Equivalently, the losing player's marginal contribution to the richer side
has the strict quantitative deficit

```text
v(H union {a})-v(H)
 <= phi_a - [(1-r_b)/(r_b-r_a)] s_phi(H)
 < phi_a.                                             (MD)
```

Indeed, subtracting the two slack definitions gives
`s_phi(H union {a})-s_phi(H)=phi_a-[v(H union {a})-v(H)]`.
Thus a global exact-partition failure has a local witness on one adjacent
edge of the coalition lattice.

There is also a direct transport interpretation. Exactify `H` at a core
point `z` and put `Delta=z-phi`. Transport gives

```text
Delta_a<0<Delta_b,    Delta_a+Delta_b=s_phi(H).
```

Since

```text
z(H union {a})=phi(H union {a})-Delta_b,
```

core feasibility already gives
`s_phi(H union {a})>=Delta_b>s_phi(H)`. The packet inequality sharpens this
to the factor in `(2P)`.

## Sharp examples

The inequality is attained in both known irreducible trace classes.

- In the three-column half-integral family,
  `(r_a,r_b)=(0,1/2)`, `s_phi(H)=1`, and
  `s_phi(H union {a})=2`; hence `v(H union {a})-v(H)=0`.
- In the smallest four-co-singleton family,
  `(r_a,r_b)=(0,2/3)`, `s_phi(H)=4`, and
  `s_phi(H union {a})=6`; again `v(H union {a})-v(H)=0`.

Thus the amplification factor is not a proof artifact. It is an exact
numerical invariant of both the external three-column and internal
co-singleton mechanisms.

## Significance and limit

The theorem is dimension-free and uses no enumeration. It strengthens the
single-packet reduction by attaching a monotone scalar to every underloaded
trace-coupled obstruction. No analogous strict-ascent conclusion follows
from the pure block-star identity, so the result gives a structural
separation between the two branches.

This is not yet a classification of all minimal packets. The next target is
to determine whether repeated slack transfer forces a finite forbidden
configuration, a terminal star, or a bounded-depth decomposition. Novelty
and the exact-balancedness step require hostile specialist review.
