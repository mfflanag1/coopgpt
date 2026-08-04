# Universal Lmin slack ascent

## Main theorem

Let `v` be an exact game and let `phi=Lmin(v)`. At a strict payoff boundary
write `L` for the cumulative poorer side and `H=N\L` for the richer suffix.
If `H` is slack, then some poorer player `i` satisfies

```text
s_phi(H union {i}) > s_phi(H),
v(H union {i})-v(H) < phi_i.                         (UA)
```

Thus every failure of exact partition at Lmin has a strict local witness on
one adjacent edge of the coalition lattice. Equivalently, no slack Lmin
suffix is an upper local maximum of the core-slack function.

The theorem is dimension-free, applies to both the pure-star and
trace-coupled obstruction branches, and uses no enumeration or classification
of minimal balanced collections.

## Two-line displacement proof

The strict richer-side cover lemma supplies nonnegative weights on proper
`phi`-tight coalitions whose common load on `H` is positive and whose load on
every player of `L` is strictly smaller. Normalize the rich load to one and
write the poor loads as `c_i<1`.

Exactify `H` at a core point `z`, write `Delta=z-phi`, and put
`s=s_phi(H)>0`. Then

```text
Delta(H)=-s,       Delta(L)=s,
0 <= sum_T lambda_T Delta(T) = -s+sum_i c_i Delta_i.
```

If every poorer displacement were nonnegative, `c_i<1` and
`sum_i Delta_i=s>0` would give `sum_i c_i Delta_i<s`, contradicting the last
inequality. Hence some `Delta_i<0`. Core feasibility on `H union {i}` gives

```text
s_phi(H union {i}) >= s-Delta_i > s.
```

Because `Delta(L)=s>0`, a distinct poorer player gains, so the amplified
coalition is proper. Finally,

```text
s_phi(H union {i})-s_phi(H)
 = phi_i-[v(H union {i})-v(H)],
```

which proves the marginal statement.

## Quantitative canonical completion

The same strict cover gives more than existence. Put

```text
b       = max_i c_i,
d_i     = b-c_i,
delta   = 1-b+sum_i d_i.
```

The cover has the canonical completion

```text
sum_T lambda_T 1_T
+ sum_i d_i 1_(H union {i})
- delta 1_H
= b 1_N.                                             (CC)
```

Indeed, a rich player receives load
`1+sum_i d_i-delta=b`, while poorer player `i` receives
`c_i+d_i=b`.

Apply exact balancedness to `(CC)`; if `b=0`, first add any positive common
grand-coalition coefficient and rescale, which changes no slack. All original cover coalitions are tight
at `phi`, so subtracting the worth inequality from the incidence equality at
`phi` gives

```text
delta s_phi(H) <= sum_i d_i s_phi(H union {i}).       (ST)
```

If `H` is slack, `sum_i d_i` cannot vanish: otherwise the right side is zero
while `delta=1-b>0`. Therefore

```text
max_(i:d_i>0) s_phi(H union {i})/s_phi(H)
 >= delta/sum_i d_i
 = 1+(1-b)/sum_i d_i
 > 1.                                                 (SA)
```

Moreover, `d_i>0` leaves a distinct maximally loaded poorer player outside
`H union {i}`, so the amplified coalition is proper.

## Two-poorer sharp factor

When `L={a,b}`, balanced-trace transport selects a lifted minimal packet
whose poor loads, after labeling the losing and gaining players, satisfy

```text
0 <= r_a < r_b < 1.
```

Its canonical completion has only the losing-player spoke, so

```text
s_phi(H union {a})
 >= [(1-r_a)/(r_b-r_a)] s_phi(H)
 > s_phi(H),

v(H union {a})-v(H)
 <= phi_a-[(1-r_b)/(r_b-r_a)] s_phi(H)
 < phi_a.                                             (2P)
```

This packet-dependent factor sharpens the universal strict inequality.

## Three saturated mechanisms

The verifier recomputes all coalition values from the defining exact games.

- In the five-player pure-star example, the normalized protector cover has
  poor loads `(1/2,0,1/2)`. The richer suffix has slack one and adjoining the
  uniquely least-loaded poor player gives slack two.
- In the three-column half-integral family,
  `(r_a,r_b)=(0,1/2)`, `s_phi(H)=1`, and
  `s_phi(H union {a})=2`; hence `v(H union {a})-v(H)=0`.
- In the smallest four-co-singleton family,
  `(r_a,r_b)=(0,2/3)`, `s_phi(H)=4`, and
  `s_phi(H union {a})=6`; again `v(H union {a})-v(H)=0`.

All three attain equality in `(ST)`. The ascent is therefore not a proof
artifact and is not confined to one obstruction branch.

## Significance and limits

The exact-balanced inequality associated with `(CC)` belongs to classical
semi-balanced-system theory. The candidate new contribution is that
lexicographic Lmin optimality supplies the simultaneous strict cover, whose
canonical completion forces universal slack ascent and a local marginal
witness for every exact-partition failure.

This is a conceptual, dimension-free theorem rather than a finite
classification. It still requires hostile correctness and novelty review.
It does not by itself classify the possible ascent targets or prove that the
unrestricted exact-partition conjecture holds. The next target is to combine
the ascent edge with exact-face structure to classify terminal slack maxima
and recover the pure-star/trace packet from that terminal geometry.
