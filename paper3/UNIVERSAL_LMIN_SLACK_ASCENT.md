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
trace-coupled obstruction branches, and is an instance of a theorem for
arbitrary compact convex efficient allocation sets.  It uses no strict-cover
duality, enumeration, or classification of minimal balanced collections.

## Cover-free displacement proof

Exactify `H` at a core point `z`, write `Delta=z-phi`, and put
`s=s_phi(H)>0`. Then

```text
Delta(H)=-s,       Delta(L)=s.
```

If every poorer displacement were nonnegative, at least one would be
positive.  Along a sufficiently short segment from `phi` toward `z`, the
strict poorer/richer payoff gap is preserved, every poorer coordinate weakly
increases, and one strictly increases.  The increasingly sorted payoff vector
would lexicographically improve, contradicting `phi=Lmin(v)`.  Hence some
`Delta_i<0`. Core feasibility on `H union {i}` gives

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

This is the exact-game specialization of
`paper3/LEXIMIN_FACE_ASCENT_GEOMETRY.md`.  For a compact convex efficient set
`K`, define

```text
sigma_phi(A)=phi(A)-min_(x in K)x(A).
```

The same segment proof shows that every slack richer face ascends.  Exactness
identifies `sigma_phi` with ordinary game slack.

The entire interval above `H` has the exact formula

```text
max_(H subseteq C subseteq N) s_phi(C)
 = max_(z in Core(v)) sum_(i in L)(z_i-phi_i)_+.
```

Thus the terminal slack is the maximum one-sided total variation of the
poorer-side core projection.  Its maximizing coalitions are precisely the
sign cells that include the poorer coordinates decreased by a maximizing
core point and exclude those increased by it, with zero coordinates optional.
When the suffix is slack, this variation is strictly larger than
`s_phi(H)`, which is the maximum aggregate displacement of the poorer block.
A maximizing exactifier may be chosen at a core vertex.

## Quantitative canonical completion

A strict Lmin cover is needed only for a sharper quantitative statement. Put

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
