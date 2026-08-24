# External review packet — PXC140 slope–saturation price factorization

Date: 2026-08-24

Branch: `codex/pxc119-mechanism-price`

Status: internally exact-replayed; no cooperative-game specialist review.

## Claim

For the PXC138 diagonal-release bridge, let

```text
tau_* = min {t in [0,1]: Psi_t=O},
e_0   = Psi'_+(0).
```

PXC140 proves, in every dimension,

```text
O-Psi_0 <= tau_* e_0.
```

Consequently `tau_*e_0<=O-c_nT` is sufficient for the hybrid-overlap
target.  Equivalently, under strict spectral failure it is enough to prove

```text
tau_*e_0 <= C_top+C_label-(c_nT-B_*).
```

This last mechanism estimate remains open.  PXC140 does not prove the main
hybrid-overlap conjecture.

## Conventional proof

PXC138 gives a nondecreasing concave piecewise-linear function `Psi_t` with
`Psi_0=Psi`, `Psi_1=O`, and right derivative `e_+(t)`.  Once the curve first
reaches its global upper bound `O`, it remains constant.  Hence

```text
O-Psi = integral_0^tau_* e_+(t) dt.
```

The right derivative of a concave function is nonincreasing, so
`e_+(t)<=e_+(0)=e_0` and the claimed product bound follows.  The threshold
`tau_*` is also the optimum of the primal LP minimizing the common normalized
diagonal cap subject to attaining bridge value `O`.

## Exact controls

The sharp total-four equality game has

```text
tau_*=1/27, e_0=9/17,
O-Psi=tau_*e_0=1/51.
```

For the strict-spectral PXC139 game,

```text
tau_*=14/81, e_0=54/17,
O-Psi=13/34 < tau_*e_0=28/51 < 2/3=O-c_6T.
```

The upper bound on `tau_*` is an exact box-saturating primal.  The matching
lower bound is certified by a feasible left supporting dual with

```text
D_left=469/34, E_left=81/68,
D_left+(14/81)E_left=T+O=14.
```

Because `E_left>0`, the same dual bounds `Psi_t` strictly below `O` for
every `t<14/81`.

## Reproduction

```bash
python3 verifiers/divergence/verify_pxc140_slope_saturation_price.py \
  --output /tmp/pxc140.json
cmp /tmp/pxc140.json \
  verifiers/divergence/pxc140_slope_saturation_price.json

python3 \
  verifiers/divergence/verify_pxc140_slope_saturation_price_independent.py \
  --output /tmp/pxc140-independent.json
cmp /tmp/pxc140-independent.json \
  verifiers/divergence/pxc140_slope_saturation_price_independent.json
```

The independent script imports no project Python module.  It reconstructs
the PXC139 lower envelope from its four vertices and checks all new primal,
core-row, cap, and dual inequalities with exact rational arithmetic.  It
uses the separately standalone PXC138/PXC139 artifacts only for their
already independently pinned initial-slope values.

## Hostile questions

1. Does PXC138 really make `Psi_t` concave rather than convex, including at
   degenerate dual faces?
2. Is `e_+(0)` the minimum exposure on the full optimal dual face, with the
   correct one-sided derivative convention?
3. Does equality `Psi_tau=O` plus monotonicity prove constancy after `tau`,
   or is an upper bound being used implicitly?
4. Does the displayed PXC139 left dual remain feasible for every `t`, so
   that it genuinely excludes all smaller saturation times?
5. Are coordinates with `x_rz_r=0` handled correctly by the primal
   definition of `tau_*`?
6. Is the product theorem ever described as necessary?  It is only a
   sufficient bound and may strictly overestimate the integrated price.
7. Does any proposed proof of the open product estimate smuggle overlap
   itself into `C_top` or `C_label` without a tight-row, witness, cover, or
   staged-polar identity?

## Significance and prior art

This is a useful reduction, not a resolution of the cooperative-game
conjecture.  Parametric LP value functions, shadow prices, and breakpoints
are classical; see Adler–Monteiro (1992),
https://doi.org/10.1007/BF01758841, and Ho (2000),
https://doi.org/10.3233/INF-2000-11406.  No novelty is claimed for the
concavity argument.  The selector-specific interpretation of the two
factors and any future PXC112/PXC114 product estimate require specialist
prior-art review before a novelty claim.
