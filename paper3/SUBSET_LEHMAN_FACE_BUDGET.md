# Subset Lehman residual face budget

## Statement

Let `A,B` be a positive Lehman pair

```text
A B^T = J + k I,
```

with `A` `r`-regular.  A supported packet uses every column of `A` with
weight `1/r`.  Let `U,V` be the columns carrying the losing and gaining poor
players, with

```text
p=|U| < ell=|V| < r.
```

For a dual row `j`, put

```text
u_j=|row_j(B) intersect U|,
w_j=|row_j(B) intersect V|,
F_j=(r-p)w_j+p-ell-(r-ell)u_j.
```

For any nonempty row set `D`, identify the row indices with their
corresponding rich players and write

```text
d=|D|,
U_D=sum_(j in D) u_j,
W_D=sum_(j in D) w_j,
F(D)=sum_(j in D) F_j.
```

Then:

```text
W_D>=d and F(D)>=0
    => k(r-ell) [phi(D)-v(D)] <= F(D) phi_a,         (LH-B+)

U_D>=d and F(D)<=0
    => k(r-p) [phi(D)-v(D)] <= -F(D) phi_b.         (LH-B-)
```

In particular, under either average-load hypothesis, `F(D)=0` forces `D`
to be tight at `phi`.

## Positive-residual proof

Average the selectors supplied by the dual rows in `D`.  The Lehman identity
gives rich load

```text
1_H + (k/d) 1_D,
```

and poor loads `U_D/d,W_D/d`.  If `W_D>=d`, interpolate this average with the
uniform packet using

```text
t=d(r-ell)/(r W_D-d ell),       0<t<=1.
```

The gaining load becomes one.  The rich overload on `D` and losing deficit
are respectively

```text
q = k(r-ell)/(r W_D-d ell),
1-a_D = F(D)/(r W_D-d ell).
```

Thus `F(D)>=0` makes both poor loads at most one.  The real exact-face
overload budget gives

```text
q [phi(D)-v(D)] <= (1-a_D) phi_a.
```

Clearing the positive denominator proves `(LH-B+)`.

## Negative-residual proof

If `U_D>=d`, use instead

```text
t_hat=d(r-p)/(r U_D-d p),       0<t_hat<=1.
```

The losing load becomes one.  The rich overload and gaining deficit are

```text
q_hat = k(r-p)/(r U_D-d p),
1-b_D = -F(D)/(r U_D-d p).
```

When `F(D)<=0`, the overload budget gives `(LH-B-)` after clearing the
denominator.

## What it unifies

- For `D={j}`, `(LH-B+)` and `(LH-B-)` are the two convex Lehman row bands.
  Singleton normalization changes their face bounds into contradictions at a
  strict poor/rich payoff boundary.
- Take every dual row meeting `V` and pad to `d=s ell` rows.  Then `W_D=d`
  and

  ```text
  F(D)=(r-ell)(d-U_D).
  ```

  Formula `(LH-B+)` becomes exactly the canonical Lehman internal-face bound

  ```text
  phi(D)-v(D) <= (d-U_D) phi_a/k.
  ```

- A zero-residual row set with average poor loads at least one forces a proper
  tight rich face.  This is the prospective recursive move for a polarized
  positive Lehman obstruction that avoids every singleton band.

The theorem does not yet prove that every polarized positive Lehman matrix
contains such a zero-residual row set, nor that a forced tight face inherits a
smaller positive Lehman packet.  Those are the two remaining steps needed for
a complete recursive classification.
