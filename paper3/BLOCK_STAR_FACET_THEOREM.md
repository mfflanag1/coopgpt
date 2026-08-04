# The block-star exact-cone facet

Let

```text
N = H dot-union P_1 dot-union ... dot-union P_k,
```

where every block is nonempty and `k >= 2`, and put `S_j = H union P_j`.
Then

```text
sum_j 1_{S_j} - (k-1) 1_H = 1_N.                 (BS)
```

The system with positive coalitions `S_1,...,S_k` and exceptional coalition
`H` is a pure minimal semi-balanced system.  More strongly, it is
indecomposable in the sense of Studeny and Kratochvil, and therefore defines
a facet of the cone of exact games.

## Proof

The incidence rows are constant on every displayed block.  The row of
`P_j` occurs only in `S_j`, so any relation modulo `1_N` forces all spoke
coefficients to be equal.  The `H` row then forces the coefficient of `H`.
Thus (BS) is the unique relation up to scale and loses dependence when any
supported coalition is deleted.  The system is pure and minimal.

For indecomposability, suppose a proper coalition `E` outside the displayed
support could be a new exceptional set.  Normalize its coefficient to
`-1`; let `a_j >= 0` be the coefficients on `S_j`, `b >= 0` the coefficient
on `H`, and `r` the common load.  Equal supported incidence rows force `E`
to be a union of entire blocks.  Write `e_H,e_j` for the indicators that
`E` contains `H,P_j`, and put `q=sum_j e_j`.  The peripheral and root rows
give

```text
a_j = r + e_j,
(k-1)r + q + b - e_H = 0.                         (D)
```

If `e_H=0` and some peripheral block is excluded, then `r>=0`; (D) forces
`r=q=b=0`, hence `E` is empty.  If all peripheral blocks are included, then
`r>=-1`, while the left side of (D) is at least one.

If `e_H=1` and some peripheral block is excluded, then `r>=0`.  If `q=0`,
the exceptional set is `E=H` (the coefficients need not be unique); if
`q=1`, equation (D) forces `b=r=0` and gives `E=S_j`; and `q>=2` is
impossible.  The first two sets are already supported.  If every
peripheral block is included, then `E=N`.  Thus there is no new proper
exceptional set, proving indecomposability.

## Lmin applications

This one facet has three previously separate appearances.

1. In every two-column broken diamond, rooting the exterior block gives
   peripheral blocks `X,Y,R` and spokes `H union X`, `H union Y`, and
   `H union R`.  The full rooted obstruction is one `k=3` block-star facet.
2. In the universal three-poorer family, take the poorer players as singleton
   peripheral blocks.  The spoke slacks, ordered as
   `p_1,p_2,p_3,Q`, are `0,2,0,1,...,1`, while `s(H)=1`.  Hence
   `sum_j s(H union {p_j})=(m-1)s(H)`: the block-star facet is saturated for
   every `m>=3,h>=2`.
3. The complementary-diamond factor of the three-trace obstruction is the
   `k=2` block star after taking `D` as root and partitioning its complement
   into `{a} union C` and `{b}`.

Consequently these three previously separate exterior mechanisms use the
same dimension-free facet.  The three-trace family additionally needs one
internal balanced-triangle facet.  This does **not** prove that every rooted
Lmin atom has such a factorization; that is the next structural conjecture.

The facet criterion is prior art.  The candidate new contribution is the
Lmin-specific identification, saturation, and unification above.  The exact
finite audit in `src/verify_block_star_facet.py` is a bug detector, not proof
evidence independent of the displayed argument.
