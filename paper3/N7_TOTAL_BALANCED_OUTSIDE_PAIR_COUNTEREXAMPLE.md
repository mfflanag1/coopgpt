# Seven-player totally balanced outside-pair counterexample

Let `N={1,...,7}`, `S={1,...,5}`, and `P={6,7}`.  There is an integer
totally balanced game `v`, with reference core point zero, for which

\[
\gamma_S(0)=1,\qquad \eta_S(0)=0.
\]

Thus total balancedness does **not** suffice for the quantitative carrier
bound in dimension seven, even when `|P|=2`.  Combined with the complete
six-player audit, this makes the six-player totally balanced outside-pair
theorem dimension-sharp.  The example is not exact, so it neither contradicts
the exact seven-player outside-pair theorem nor settles the exact `|P|=2`
question in higher dimensions.

## Exact construction

Write `v(A)=-s(A)` and encode a coalition by its seven-bit mask.  In mask
order `0,...,127`, the integer slack vector is

```text
0,2,2,1,2,1,0,0,2,1,0,0,1,1,0,0,
2,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,
3,3,3,3,4,3,3,2,3,3,3,2,3,3,0,1,
3,0,2,1,3,2,2,0,3,0,2,0,3,0,1,0,
1,1,1,1,2,0,1,0,2,0,1,0,2,0,1,0,
2,1,0,0,0,0,0,0,2,1,0,0,0,0,0,0,
3,3,3,3,3,2,3,2,3,2,3,2,3,2,1,1,
3,1,2,1,2,1,2,1,3,1,2,1,2,1,1,0.
```

The following seven zero-slack coalitions, with the displayed positive
weights, form a balanced collection of common degree 12:

```text
12345:1, 2346:7, 156:5, 137:2, 147:4, 257:4, 357:2.
```

Their incidence vectors have rank seven.  Hence every point in the full core
is tight on all seven coalitions and must be zero.  This proves that the full
core is the singleton `{0}`, so `eta_S(0)=0`.  It also proves nonexactness:
for example, `v({1})=-2`, while the unique core allocation pays player 1 zero.

For every nonempty proper `C` contained in `S`, direct integer evaluation gives

\[
s(P\cup C)-s(C)\geq1,
\]

with equality attained, proving `gamma_S(0)=1`.  Deleting `S` from the
balanced collection gives a zero-cost eta dual with `rho=11`.

## Solver-free verification

Run from `coopgames/`:

```sh
python src/verify_n7_total_balanced_outside_pair_counterexample.py
```

The verifier uses integer/rational arithmetic and no optimizer.  It checks a
saved core allocation for each of all 127 nonempty subgames, every subgame
coalition inequality, the carrier differences, the degree-12 balanced
identity, exact incidence rank, zero eta-dual cost, singleton full core, and
nonexactness.
