# Projective-plane trace exclusion and density barrier

## Result

Let `v` be a singleton-normalized exact game, let `phi=Lmin(v)`, and consider
a slack strict boundary with two poorer players `a,b`.  Suppose an
underloading extreme trace packet is the line-versus-point incidence system
of a finite projective plane of order `q`, with weight `1/(q+1)` on every
line.  Let

```text
A = lines whose lifted tight coalition contains a,
B = lines whose lifted tight coalition contains b.
```

Put `C=A intersect B` and `D=A setminus B`.

Balanced-trace transport gives

```text
1 <= |B| <= q,                 |A| < |B|.
```

Such a packet is impossible whenever either

```text
|B|(q+2-|B|) > |C||D| + binom(|D|,2),              (PP)
```

or

```text
|D| < 2(q+2-|B|).                                  (PP-L)
```

Consequently:

- all projective-plane packets of orders at most `6` are impossible;
- more generally, every packet with `|B|<=6` is impossible, in every order;
- at order `7`, the only pattern not excluded by this theorem is the extremal
  count `(|A|,|B|)=(6,7)`; a separate arc argument below eliminates this
  final pattern in the Desarguesian plane `PG(2,7)`.

The extremal pattern remains open here only for arbitrary non-Desarguesian
incidence systems. The theorem is a human counting argument, not a
finite-search claim.

## Simple-point count

Write `a0=|A|` and `b0=|B|`.  A point is `B`-simple if it lies on exactly one
line of `B`.  If `n_k` is the number of points lying on exactly `k` lines of
`B`, then

```text
sum k n_k = b0(q+1),       sum binom(k,2)n_k = binom(b0,2).
```

Since `k <= 2 binom(k,2)` for `k>=2`, the number `n_1` of `B`-simple points
satisfies

```text
n_1 >= b0(q+1)-2 binom(b0,2) = b0(q+2-b0).
```

Suppose every `B`-simple point lay on at least two lines of `A`. At most one
of those lines belongs to `C`, since each `C`-line is also a `B`-line. If the
unique incident `B`-line is in `C`, map the point to one incident pair in
`C x D`; otherwise map it to a pair of incident `D`-lines. Distinct points
give distinct line pairs, so

```text
n_1 <= |C||D| + binom(|D|,2),
```

contradicting `(PP)`.

For the local bound, choose `ell in B setminus A`, which exists because
`|A|<|B|`. At least `q+2-|B|` points of `ell` are `B`-simple. Avoiding a safe
star at each requires at least two `D`-lines, and one `D`-line cannot meet
`ell` at two points. Hence `|D|>=2(q+2-|B|)`, contradicting `(PP-L)`.

Under either condition some point `d` therefore lies on exactly one `B`-line
and at most one `A`-line.

## Safe star rounding

Select the `q+1` supported lifted tight coalitions whose trace lines pass
through `d`.  Their rich-side incidence load is

```text
1_H + q e_d,
```

because every other point lies on one line through `d`, while `d` lies on
all `q+1`.  The selected coalitions load `b` exactly once and `a` at most
once.  Thus this is a safe star rounding, allowing a duplicated rich
singleton with arbitrary multiplicity `q`, not merely multiplicity one.

It is therefore a safe rooted tight cover in the sense of
[`ROOTED_SEMIGROUP_OBSTRUCTION.md`](ROOTED_SEMIGROUP_OBSTRUCTION.md), which
supplies the general exact-face contradiction.

Exactify singleton `d`, so a core point `x` has `x_d=0`, and sum the selected
tight-coalition inequalities.  Add singleton inequalities for an omitted
poor player.  If both poor players are present, the right side exceeds
efficiency by `q phi_d`; if one is omitted, it exceeds efficiency by
`q phi_d-phi_i>0`.  Both are impossible because `d` is strictly richer than
either poor player.

## Cardinality corollaries

Because

```text
|C||D|+binom(|D|,2) <= binom(a0,2)
```

and `a0<b0`, condition `(PP)` follows from

```text
b0(q+2-b0) > binom(b0-1,2).
```

For `b0<=6` and `q>=b0`, the left side is at least `2b0`, which is strictly
larger than `binom(b0-1,2)`.  This proves the dimension-free `|B|<=6`
exclusion.  If `q<=6`, transport already gives `b0<=q<=6`, so every packet
is excluded.  For `q=7`, only `b0=7,a0=6` escapes the same count.

## Closing the extremal case in `PG(2,7)`

Assume `a0=6,b0=7` and no safe star exists. The exact simple-point identity
is

```text
n_1 = 14 + sum_(k>=3) k(k-2)n_k.
```

Every simple point lies on at least two `A`-lines and therefore injects into
one of the 15 pairs of `A`-lines. Hence `n_1<=15`, so no three `B`-lines are
concurrent and `n_1=14`. Those 14 simple points already consume 14 distinct
pairs of `A`-lines. Three concurrent `A`-lines would consume three pairs at
one point and leave too few pairs for the remaining simple points. Thus the
six `A`-lines are also in general position.

Dualize. The `B`-lines become a seven-arc `B*`, the `A`-lines become a
six-arc `A*`, and the 14 simple points become all 14 tangents of `B*`. Every
one of those tangents is a secant of `A*`. Segre's `q`-arc theorem extends
`B*` to an eight-point oval, hence a conic in odd Desarguesian order; Thas
(1987) gives a short proof. If `R` is the missing conic point, the seven
lines `RP`, `P in B*`, are concurrent tangents of the seven-arc. They would
therefore be seven concurrent secants of the six-arc `A*`.

That is impossible. Through a point of `A*` there are only five secants;
through a point outside `A*`, distinct secants use disjoint pairs of its six
points, so there are at most three. This contradiction eliminates the final
pattern in `PG(2,7)`.

In particular, the Fano plane (`q=2`) cannot be the required underloading
witness, even though its seven-line incidence vertex is fractional,
nonsingular, and contains no four-co-singleton incidence submatrix. Exact
singleton faces eliminate it by star rounding.

## Significance and limit

This extends the structural progression beyond graph traces and the
four-rich classification:

```text
integral traces are impossible;
rank-two fractional traces are impossible;
the first four-rich obstruction is uniquely co-singleton;
projective-plane incidence packets are impossible below a sharp density gate.
```

It does **not** prove that every higher-dimensional failure contains a
four-co-singleton minor. The simple counting theorem does not settle the
extremal pattern for arbitrary non-Desarguesian incidence systems; the arc
argument closes it specifically in `PG(2,7)`. Correctness and novelty still
require hostile specialist review.
