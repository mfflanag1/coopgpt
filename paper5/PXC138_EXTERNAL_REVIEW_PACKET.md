# External review packet — PXC138 diagonal-release curve

Date: 2026-08-24

Branch: `codex/pxc119-mechanism-price`

Status: internally exact-replayed; no cooperative-game specialist review.

## Claim under review

Let `D` be the feasible region of the PXC136 zero-diagonal stationary dual,
`D(q)` its objective, and

```text
d_r=x_r z_r/T^2,
Delta_r=T sum_(S contains r) lambda_rS-A_r-B_r,
E(q)=sum_r d_r [Delta_r]_+.
```

For `0<=t<=1`, replace `F_rr=0` in the stationary primal by
`0<=F_rr<=t*d_r`, and denote its bridge value by `Psi_t`.  PXC138 claims

```text
T+Psi_t = min_(q in D) {D(q)+t E(q)}.                 (PXC138a)
```

Thus `Psi_t` is a nondecreasing concave piecewise-linear function,
`Psi_0=Psi_stat`, and `Psi_1=O`.  Its right derivative is the minimum `E`
on the current minimizing dual face and

```text
O-Psi_stat = integral_0^1 Psi'_+(t) dt.              (PXC138b)
```

The sharp total-four equality control has the exact curve

```text
Psi_t=45/17+min(9t/17,1/51).                          (PXC138c)
```

Hence the right derivative at zero is `9/17`, while the total price is only
`1/51`.  This refutes, by a factor of 27, the proposed strengthening that
the minimum positive diagonal defect on the optimal zero-diagonal dual face
equals the stationary loss.  Here `B_star=c_nT`; this is not a counterexample
to a theorem assuming strict spectral failure, but it proves that strictness
would have to do genuine quantitative work.

## Proof skeleton to audit

1. A diagonal upper bound `F_rr<=t*d_r` has a nonnegative dual multiplier
   `gamma_r`.
2. The formerly absent diagonal arc constraint becomes
   `gamma_r>=Delta_r`.
3. Minimizing over `gamma_r>=0,Delta_r` gives
   `gamma_r=[Delta_r]_+`, proving PXC138a.
4. An infimum of affine functions of `t` is concave and piecewise linear.
   The smallest active slope is its right derivative.
5. At `t=1`, the PXC137 product flow is feasible and has value `O`; the
   pointwise bridge inequality supplies the reverse bound.
6. For the sharp control, exact primals at `t=0` and `t=1/27` interpolate to
   the lower affine segment.  An exact `t=0` dual with exposure `9/17`
   supplies the matching upper segment.  The pointwise `O` bound supplies
   the constant segment.

## Exact reproduction

From `coopgames/verifiers/divergence`:

```bash
python3 verify_pxc138_diagonal_release_curve.py \
  --output /tmp/pxc138.json
cmp /tmp/pxc138.json pxc138_diagonal_release_curve.json

python3 verify_pxc138_diagonal_release_curve_independent.py \
  --output /tmp/pxc138-independent.json
cmp /tmp/pxc138-independent.json \
  pxc138_diagonal_release_curve_independent.json
```

The independent script imports no project game, selector, LP, or PXC136--138
implementation.  It checks the two primal arrays against the six defining
core rows and independently checks every inequality of the supported dual.

## Prior-art status

The search was refreshed on 2026-08-24.  Parametric LP value functions,
breakpoints, and shadow-price sensitivity are standard; see Adler and
Monteiro, [*A Geometric View of Parametric Linear Programming*](https://doi.org/10.1007/BF01758841),
and Ho, [*Computing True Shadow Prices in Linear Programming*](https://doi.org/10.3233/INF-2000-11406).
The latter is particularly relevant to the warning that a dual multiplier
at a degenerate optimum need not equal a finite total price.  Searches for
`zero diagonal transportation polytope parametric diagonal capacity`,
`stationary flow diagonal release`, and combinations with leximin/leximax
and exact cooperative games found no source for this selector-specific
construction.  That negative search is not a novelty determination.

## Questions for a hostile reviewer

1. Is the sign of the new diagonal multiplier correct, and does eliminating
   it really give `+[Delta_r]_+` in a minimization dual?
2. Does the product-flow endpoint prove `Psi_1=O` without assuming either
   selector is itself a stationary bridge?
3. At a degenerate breakpoint, is the *minimum* active slope the right
   derivative and the maximum the left derivative?
4. Do the displayed sharp primals and dual prove the whole curve by convex
   interpolation, or only its two sampled values?
5. Is the factor-27 conclusion stated at the correct evidence level?
6. Is any equivalent forced-diagonal sensitivity construction already known
   in cooperative-game selection theory under different terminology?

## Remaining open theorem

Under `B_star<c_n*T`, PXC138 rewrites the hybrid target as

```text
integral_0^1 e_+(t) dt
 <= C_top+C_label-(c_n*T-B_star).
```

The left side is explicit root-labelled diagonal shadow load.  No proof yet
charges that integral to the PXC112 staged polars or the PXC114
common/reciprocal labels.  PXC138 is a reduction and route correction, not a
proof of the dimension-free hybrid-overlap inequality.
