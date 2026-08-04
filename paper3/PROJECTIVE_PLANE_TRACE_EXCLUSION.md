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

Balanced-trace transport gives

```text
1 <= |B| <= q,                 |A| < |B|.
```

Such a packet is impossible whenever

```text
|B|(q+2-|B|) > binom(|A|,2).                       (PP)
```

Consequently:

- all projective-plane packets of orders at most `6` are impossible;
- more generally, every packet with `|B|<=6` is impossible, in every order;
- at order `7`, the only pattern not excluded by this theorem is the extremal
  count `(|A|,|B|)=(6,7)`.

The last pattern is explicitly left open here.  The theorem is a human
counting argument, not a finite-search claim.

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

If every `B`-simple point lay on at least two lines of `A`, each such point
would consume a distinct pair of `A`-lines: two projective-plane lines meet
at only one point.  Hence `n_1 <= binom(a0,2)`, contradicting `(PP)`.
Therefore some point `d` lies on exactly one `B`-line and at most one
`A`-line.

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

Exactify singleton `d`, so a core point `x` has `x_d=0`, and sum the selected
tight-coalition inequalities.  Add singleton inequalities for an omitted
poor player.  If both poor players are present, the right side exceeds
efficiency by `q phi_d`; if one is omitted, it exceeds efficiency by
`q phi_d-phi_i>0`.  Both are impossible because `d` is strictly richer than
either poor player.

## Cardinality corollaries

Because `a0<b0`, condition `(PP)` follows from

```text
b0(q+2-b0) > binom(b0-1,2).
```

For `b0<=6` and `q>=b0`, the left side is at least `2b0`, which is strictly
larger than `binom(b0-1,2)`.  This proves the dimension-free `|B|<=6`
exclusion.  If `q<=6`, transport already gives `b0<=q<=6`, so every packet
is excluded.  For `q=7`, only `b0=7,a0=6` escapes the same count.

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
four-co-singleton minor, and it does not settle the extremal order-seven
incidence pattern.  Correctness and novelty still require hostile specialist
review.
