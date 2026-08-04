# Convex Lehman-row exclusion

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

## The new row band

The packet is impossible if some row with `w_d>=1` satisfies

```text
r w_d - ell - k(r-ell)
    <= p(w_d-1) + u_d(r-ell)
    <= r w_d - ell.                                 (LH-C)
```

The previous integer safe-row test is the special case `w_d=1,u_d<=1`.
The new band can also accept rows meeting the gaining labels more than once.

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

The upper side of `(LH-C)` says `a_d<=1`. The lower side says
`t k>=1-a_d`. The real exact-face overload budget therefore gives

```text
t k phi_d <= (1-a_d) phi_a.
```

This contradicts `phi_d>phi_a`: if `a_d<1`, the left coefficient is at least
the right coefficient; if `a_d=1`, the right side is zero.

## Significance and limit

The result replaces a discrete row-selection requirement with a continuous
interpolation test and uses the original rich-player row as the overload
root. It is unconditional for any row satisfying the band, but it does not
prove that every positive Lehman pair has such a row. Determining whether the
band is universal, or deriving a global counting condition that forces it,
is the next concrete combinatorial question.
