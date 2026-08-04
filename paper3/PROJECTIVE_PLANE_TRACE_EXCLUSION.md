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
  count `(|A|,|B|)=(6,7)`; a separate convex-row argument below eliminates
  this final pattern in every finite projective plane of order seven.

The order-seven closure is incidence-theoretic: it does not assume
Desarguesian coordinates or use finite enumeration. The theorem is a human
counting argument.

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

## Closing the extremal order-seven case

Assume `q=7`, `a0=6`, and `b0=7`.  View the line-incidence matrix as the
self-dual positive Lehman pair with `r=8` and `k=7`.  At a point `P`, let
`u(P)` and `w(P)` count the incident `A`- and `B`-lines.  The convex
Lehman-row band becomes

```text
2w(P)-8 <= u(P) <= 2w(P)-1.                         (PG7-C)
```

If some point satisfies this band, interpolate the uniform line packet with
the pencil through that point.  The gaining-poor load becomes exactly one,
the losing-poor load is at most one, and the rich overload is large enough
for the real exact-face overload budget to contradict the strict payoff
boundary.  See [`CONVEX_LEHMAN_ROW.md`](CONVEX_LEHMAN_ROW.md).

Suppose no point satisfies the band.  Every point on exactly one `B`-line
then lies on at least two `A`-lines and injects into one of the fifteen pairs
of `A`-lines, so `n_1<=15`.  The exact identity for seven `B`-lines is

```text
n_1 = 14 + sum_(k>=3) k(k-2)n_k.
```

Every positive summand is at least three, so `n_1<=15` forces `n_k=0` for
all `k>=3`.  The 21 pairs of `B`-lines therefore meet at 21 distinct points
with `w(P)=2`.  At each such point, failure of `(PG7-C)` forces `u(P)>=4`.
But the six `A`-lines have only fifteen pairs in total:

```text
sum_P binom(u(P),2) = binom(6,2) = 15,
```

whereas those 21 points alone contribute at least `21 binom(4,2)>15`.
This contradiction closes the extremal pattern in every finite projective
plane of order seven.

In particular, the Fano plane (`q=2`) cannot be the required underloading
witness, even though its seven-line incidence vertex is fractional,
nonsingular, and contains no four-co-singleton incidence submatrix. Exact
singleton faces eliminate it by star rounding.

## Significance and limit

This extends the structural progression beyond graph traces and the
four-rich classification:

```text
integral traces are impossible;
rank-two fractional packets are impossible by a real-valued overload budget;
the first four-rich obstruction is uniquely co-singleton;
projective-plane incidence packets are impossible through order seven.
```

It does **not** prove that every higher-dimensional failure contains a
four-co-singleton minor.  Orders eight and above retain poor-label patterns
not settled by the present density estimates or convex row band. Correctness
and novelty still require hostile specialist review.
