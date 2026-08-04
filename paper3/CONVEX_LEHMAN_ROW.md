# Two-sided convex Lehman-row exclusion

## Setup

Let `A,B` be a positive Lehman pair

```text
A B^T = J + k I,
```

with `A` `r`-regular. An underloaded lifted packet assigns weight `1/r` to
every column. Let `U,V` be the columns carrying respectively the losing and
gaining poor players, and write

```text
p = |U| < ell = |V| < r.
```

For a row `d` of `B`, let

```text
u_d = |row_d(B) intersect U|,
w_d = |row_d(B) intersect V|.
```

Define the label residual

```text
F_d = (r-p)w_d + p-ell - (r-ell)u_d.                (LH-R)
```

## The two row bands

The packet is impossible if some row satisfies either

```text
w_d>=1 and 0 <= F_d <= k(r-ell),                    (LH-C+)
```

or

```text
u_d>=1 and -k(r-p) <= F_d <= 0.                     (LH-C-)
```

The positive band is the earlier criterion written more transparently.  The
negative band is its missing counterpart: it interpolates until the losing,
rather than gaining, load reaches one.  The previous integer safe-row test is
the special case `w_d=1,u_d<=1` of the positive band.

## Proof

The uniform packet has poor loads

```text
alpha = p/r < beta = ell/r < 1.
```

For a row with `w_d>=1`, set

```text
t = (1-beta)/(w_d-beta),
```

so `0<t<=1`. Convexly combine weight `1-t` on the uniform packet with weight
`t` on the zero-one selector given by row `d`. The Lehman identity gives

```text
rich load    = 1_H + t k e_d,
gaining load = (1-t) beta + t w_d = 1,
losing load  = a_d = (1-t) alpha + t u_d.
```

In integers,

```text
a_d = [p(w_d-1)+u_d(r-ell)]/[r w_d-ell].
```

The positive residual band says `a_d<=1` and
`t k>=1-a_d`. The real exact-face overload budget therefore gives

```text
t k phi_d <= (1-a_d) phi_a.
```

This contradicts `phi_d>phi_a`: if `a_d<1`, the left coefficient is at least
the right coefficient; if `a_d=1`, the right side is zero.

For the negative band, instead set

```text
t_hat = (1-alpha)/(u_d-alpha) = (r-p)/(r u_d-p).
```

The losing load is exactly one, while the gaining load is

```text
b_d = [ell(u_d-1)+w_d(r-p)]/(r u_d-p).
```

Now `F_d<=0` is exactly `b_d<=1`, and
`F_d>=-k(r-p)` is exactly `t_hat k>=1-b_d`.  The overload budget gives

```text
t_hat k phi_d <= (1-b_d) phi_b,
```

contradicting `phi_d>phi_b`.

## Residual conservation

Regularity gives a dimension-free conservation identity:

```text
sum_d F_d
 = (r-p)s ell + n(p-ell) - (r-ell)s p
 = (rs-n)(ell-p)
 = k(ell-p) > 0.                                    (LH-S)
```

Every row with `w_d=0` has
`F_d=p-ell-(r-ell)u_d<0`.  Therefore some gaining-bearing row has positive
residual.  Any packet surviving the two-sided theorem must exhibit a genuine
positive overshoot `F_d>k(r-ell)`; the remaining obstruction is no longer an
unnamed failure to find a safe row.

## All projective planes are excluded

For a projective plane of order `q`, the self-dual Lehman parameters are
`r=q+1,k=q`.  Among any `ell<=q` gaining lines, a point lies on exactly one.
At that point `w=1`, and if `u` losing lines pass through it, then

```text
F=(r-ell)(1-u).
```

If `u<=1`, this lies in the positive band.  If `u>=2`, then

```text
-F=(r-ell)(u-1)
   <=(r-ell)(p-1)
   <=q(r-p)=k(r-p),
```

so it lies in the negative band.  Hence no projective-plane packet of any
finite order can realize the underloading boundary.

## Significance and limit

The result replaces a discrete row-selection requirement with two continuous
interpolation tests and uses the original rich-player row as the overload
root.  It eliminates the entire projective-plane branch in all orders, but it
does not prove that every positive Lehman pair has a row in one of the bands.
The conservation law shows precisely what a survivor must do: positive
residuals must jump over the interval `[0,k(r-ell)]`, with compensating large
negative residuals.  Ruling out that polarization for general positive
Lehman matrices is the next concrete combinatorial question.

The multi-row extension in
[`SUBSET_LEHMAN_FACE_BUDGET.md`](SUBSET_LEHMAN_FACE_BUDGET.md) turns the same
residual into a quantitative bound on any uniformly overloaded rich face. It
contains both singleton bands and the canonical internal-face certificate as
special cases and is the current route toward a recursive classification.
