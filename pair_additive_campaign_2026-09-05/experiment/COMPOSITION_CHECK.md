# Block-diagonal composition check — 2026-09-05

This is a theory-only check for two identical copies of the reduced nine-player gadget. No search was run and no frozen pilot artifact was changed.

**Result:** block-diagonal pair matrices do not give the full product core. They give a proper intersection of the product core with mixed-triple inequalities. Nevertheless the full leximin and descending-lexicographic-minimum selectors are precisely two repeated copies of the old selectors, and every coordinate ideal is unchanged. Thus this composition preserves the fraction5/18 and the distance11/24; it does not amplify either phenomenon.

## The mixed triples

Let `K` denote the original gadget's core, with total8, and put two copies of each sector into block-diagonal matrices

```
A' = diag(A,A), B' = diag(B,B), C' = diag(C,C).
```

A triple entirely within one block has its original weight. Every mixed triple has exactly two members from one block and its third member from the other. Its only possibly nonzero contribution is the pair entry of the two members within the same block. Therefore, writing block allocations as `p,q`, its constraint is one of

```
p_Ai + p_Bj + q_Ck >= A_ij,
p_Ai + q_Bj + p_Ck >= B_ik,
q_Ai + p_Bj + p_Ck >= C_jk,
```

or the same inequalities with `p,q` interchanged. No mixed triple can receive two positive pair contributions under block-diagonal matrices.

For any original core point `p`, the repeated allocation `(p,p)` satisfies all mixed constraints. For example

```
p_Ai+p_Bj+p_Ck >= A_ij+B_ik+C_jk >= A_ij,
```

using the original triple constraint and nonnegative pair entries. The other two cases are identical.

## Exact grand worth and core description

The union of the two original optimal matchings has weight16. Repeating any original core point supplies a feasible covering allocation of total16 for every enlarged triple. Summing its inequalities over any disjoint matching bounds that matching's weight by16. Hence the enlarged integral optimum is exactly16.

For any enlarged core point, summing the three original matching inequalities within either block gives a block total at least8. Efficiency at16 forces each block total to equal8. Its restriction to each block therefore belongs to `K`. Consequently the entire enlarged core is exactly

```
K' = (K × K) intersect {all the mixed-triple inequalities above}.
```

There is no hidden assumption of compatible bilateral optima or of fractional matching integrality in this argument: the weight16 integral matching and weight16 covering allocation prove the optimum directly.

## Explicit failure of product-core inclusion

Use the independently certified old core points

```
x=(1/3,4/3,5/6 ; 5/6,5/6,1/3 ; 7/3,5/6,1/3),
z=(0,3/2,1     ; 1,3/2,1     ; 3/2,1/2,0).
```

The product point `(z,x)` is in `K×K`. Take `A_1,C_3` from the first block and `B_3` from the second. Its triple weight is the within-block entry `B_13=1`; the two cross-block pair entries vanish. Its payoff at `(z,x)` is

```
z_A1 + x_B3 + z_C3 = 0+1/3+0 = 1/3 < 1.
```

Thus `(z,x)` is excluded from `K'`. The product claim fails by an exact gap2/3.

More generally, for two potentially different core polytopes `K_1,K_2`, product-core inclusion under this construction is equivalent to every mixed-triple minimum being sufficient. For each within-block pair `(u,v)` of block `r`, each opposite-block player `w` in the missing sector, and its nonnegative pair weight `P_uv`, the condition is

```
min_{p in K_r}(p_u+p_v) + min_{q in K_s} q_w >= P_uv,  s != r.
```

The minima split because the two block choices are independent in the product. Checking all three pair types and both block orientations is necessary and sufficient for satisfying every mixed inequality. One should establish the enlarged total separately when the blocks differ; the identical-block cover argument above handles the present construction.

## Why the selectors and ideals still repeat

The full leximin optimum on `K×K` is `(x,x)`, and the full descending lexicographic minimum is `(z,z)`. This follows directly from the complete progressive-face procedure: both independent copies have the same first optimum level and the same forced coordinates, so the stage system is the product of two identical faces; induction repeats every subsequent level and pinned coordinate. Both repeated points are feasible in `K'` by the mixed-constraint argument.

Since `K'` is a subset of `K×K` containing both respective unique product optima, neither selector changes under the additional mixed inequalities:

```
Lmin(K')=(x,x), Lmax(K')=(z,z).
```

For a player in either block, its ideal in `K'` is at most its old ideal `H_i`, because restriction lies in `K`. If `p` is an original ideal-attaining point for player `i`, then `(p,p)` lies in `K'` and attains `H_i` in either copy. Thus every ideal remains exactly `H_i`.

The new normalized selector distance is

```
(2 ||x-z||_1)/(2 T) = 11/24,
```

and the minimum coordinate ratio remains5/18. Adding identical diagonal blocks does not create a declining sequence of ratios.

## What amplification would require

The diagonal construction has an exact diagonal embedding `p -> (p,p)` which preserves the old ideals and includes both product-optimal selectors. Any proposed amplification must break this argument: merely adding independent copies, zeros or identical pair blocks cannot work.

A successful coupled construction would need new interface inequalities that change the lexicographic optimum in a quantifiable way while retaining a strictly positive, controlled coordinate ideal. In particular, it would need a proved cross-block recurrence or other nontrivial growth relation; a repeated5/18 witness supplies neither. All new mixed triples, the enlarged integral matching value, full core admission, later lexicographic stages and ideal attainment would have to be proved again. This check supplies no candidate scalable coupling and no infinite-family theorem.
