# Local transport of the Lehman label residual

## Identity

Let `A,B` be a positive Lehman pair

```text
A B^T = J+kI,
```

with `A` `r`-regular.  Let `U,V` be label sets of sizes `p,ell`, define

```text
u=B 1_U,
w=B 1_V,
F=(r-p)w+(p-ell)1-(r-ell)u.
```

Then the full residual vector satisfies

```text
A^T F = k[(r-p)1_V-(r-ell)1_U].                    (LH-T)
```

This is stronger than the scalar conservation law.  In particular, every
column `c` carrying neither label has exact local balance

```text
sum_(d in col_c(A)) F_d = 0.                        (LH-T0)
```

If both singleton exclusion bands fail everywhere, no residual is zero: a
zero on a gaining-bearing row is in the positive band, while a row carrying
no gaining label has strictly negative residual.  Therefore every neutral
trace column meets at least one positive-residual row and at least one
negative-residual row.

## Proof

The classical transpose identity for a Lehman pair is
`A^T B=J+kI`.  Therefore

```text
A^T u = p 1+k1_U,
A^T w = ell 1+k1_V,
A^T 1 = r 1.
```

Substitution gives

```text
A^T F
 = (r-p)(ell 1+k1_V)
   +(p-ell)r1
   -(r-ell)(p1+k1_U).
```

The coefficient of `1` is

```text
(r-p)ell+(p-ell)r-(r-ell)p=0,
```

leaving `(LH-T)`.

Left multiplication by `1^T` recovers

```text
r sum_d F_d
 = k[(r-p)ell-(r-ell)p]
 = kr(ell-p),
```

and hence `sum_d F_d=k(ell-p)`.

## Structural use

If both singleton residual bands fail, every positive residual overshoots
`k(r-ell)` and every negative residual on a losing-labeled row overshoots
`k(r-p)` in absolute value.  Formula `(LH-T0)` says these extremes must cancel
exactly inside every unlabeled trace column of `A`.  Thus residual
polarization is not merely a global distribution with a small positive sum;
it is a signed local-balance system on the original rich trace hypergraph.
The positive and negative residual rows are both transversals of the
label-free trace subfamily.

For the first open case `ell=4`, this identity is the intended replacement
for finite label enumeration.  In the thin case, the residual bands and local
loads reduce every neutral trace to one of the six tiles in
`FOUR_COLUMN_RESIDUAL_NORMAL_FORM.md`.  This does not yet prove that the tiles
cannot be assembled globally.  The remaining task is to combine `(LH-T0)`
with three-column separation, the subset face budget, or a Lehman minor
reduction.  Novelty of this label-residual formulation remains subject to
specialist review; the underlying transpose Lehman identity is classical.
