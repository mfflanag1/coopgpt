# Leximin face ascent and positive variation

## Convex-geometric setup

Let `K` be a nonempty compact convex subset of the efficient hyperplane

```text
x(N)=c.
```

Let `phi` be the leximin point of `K`.  For every coalition `A subseteq N`,
define its face deficit at `phi` by

```text
sigma_phi(A) = phi(A)-min_(x in K)x(A).
```

At a strict payoff boundary, write `N=H dot-union L`, with every coordinate
of `phi_H` strictly larger than every coordinate of `phi_L`.

## Theorem 1: cover-free face ascent

If `sigma_phi(H)>0`, then some `i in L` satisfies

```text
sigma_phi(H union {i}) > sigma_phi(H),
```

and `H union {i}` is proper.

Equivalently, the best one-sided poorer-coordinate variation strictly
exceeds the best aggregate poorer-side gain:

```text
max_(z in K) sum_(i in L)(z_i-phi_i)_+
 > sigma_phi(H)
 = max_(z in K) sum_(i in L)(z_i-phi_i) > 0.        (VG)
```

### Proof

Choose `z in K` minimizing `z(H)`, put `Delta=z-phi`, and write
`s=sigma_phi(H)>0`.  Efficiency gives

```text
Delta(H)=-s,       Delta(L)=s.
```

If every `Delta_i` on `L` were nonnegative, at least one would be positive.
For sufficiently small `t>0`, the segment
`phi+t Delta` remains in `K` and preserves the strict gap between `L` and
`H`.  Every poorer coordinate weakly increases and one strictly increases,
so the increasingly sorted payoff vector lexicographically improves.  This
contradicts leximin optimality of `phi`.

Hence `Delta_i<0` for some `i in L`.  Since `z` is feasible,

```text
sigma_phi(H union {i})
 >= phi(H union {i})-z(H union {i})
 = s-Delta_i
 > s.
```

Because `Delta(L)=s>0`, a distinct poorer coordinate is positive; hence the
extension is proper.

This proof uses no tight-cover duality, balanced collection, enumeration, or
game-specific inequality.

## Theorem 2: positive-variation duality

For any `phi in K` and any split `N=H dot-union L` (leximin optimality is not
needed),

```text
max_(H subseteq C subseteq N) sigma_phi(C)
 = max_(z in K) sum_(i in L) (z_i-phi_i)_+.          (PV)
```

Thus maximum slack above `H` is exactly the largest one-sided total
variation of the poorer-side projection of `K` away from `phi`.

### Proof

Write `C=H union D`, `D subseteq L`, and `a=phi-z`.  Efficiency gives
`a(N)=0`.  Compactness and finiteness allow the two maxima to be exchanged:

```text
max_D sigma_phi(H union D)
 = max_z max_D a(H union D)
 = max_z max_D [-a(L)+a(D)]
 = max_z sum_(i in L)(-a_i)_+
 = max_z sum_(i in L)(z_i-phi_i)_+.
```

## Exact terminal sign-cell correspondence

Let `M` denote the common value in `(PV)`.  For `z in K`, put

```text
D_-(z) = {i in L : z_i<phi_i},
Z(z)   = {i in L : z_i=phi_i}.
```

Then `z` maximizes the right side of `(PV)` if and only if every coalition

```text
C=H union D,       D_-(z) subseteq D subseteq D_-(z) union Z(z),
```

is an interval slack maximizer exactified by `z`.  Conversely, if `C=H union
D` maximizes interval slack and `z` minimizes `z(C)`, then

```text
z_d<=phi_d  (d in D),       z_e>=phi_e  (e in L\D),
```

`z` maximizes positive variation, and the same containment relation holds.

For the converse signs, use the two neighboring interval coalitions.  For
example,

```text
sigma_phi(C union {e}) >= phi(C union {e})-z(C union {e})
                       = sigma_phi(C)+phi_e-z_e.
```

Interval maximality forces `z_e>=phi_e`; deletion gives the other sign.
The forward direction follows because the chosen sign set attains the inner
maximum in the proof of `(PV)`.

Because the positive-variation objective is convex and piecewise linear, its
maximum over a polytope is attained at a vertex.  In particular, when `K` is
a cooperative-game core, at least one terminal coalition is exactified by a
core vertex.

## Exact-game corollary

If `v` is exact, then for every core allocation `phi`,

```text
v(A)=min_(x in Core(v))x(A),
```

so `sigma_phi(A)` is exactly the ordinary coalition slack
`s_phi(A)=phi(A)-v(A)`.  The universal Lmin slack-ascent theorem and the
terminal punctured-suffix theorem are therefore direct instances of the
convex-geometric results above.

The strict-cover completion remains useful only for its quantitative
cover-dependent amplification and sacrifice budget.  It is not needed for
existence of the ascent edge, opposing poorer-side signs, or the terminal
sign-cell classification.

## Scope and significance

The theorem applies to arbitrary compact convex efficient allocation sets,
not only cooperative-game cores.  The positive-variation identity is an
elementary support-function calculation; it should not be claimed as a new
convex-analysis identity without specialist review.  The candidate
contribution is its use to turn exact-game Lmin partition failures into a
cover-free face-ascent and terminal sign-cell theory.

The exact audit in `src/verify_leximin_face_ascent_geometry.py` checks two
unrelated rational line-segment allocation sets and the three defining
exact-game mechanisms.  For each segment it also gives a symbolic leximin
certificate: every nontrivial point lowers a coordinate that is globally
minimal at `phi`.  It is still a bug-detecting audit, not proof evidence.
