# External review packet — PXC139 strict-spectral single-dual no-go

Date: 2026-08-24

Branch: `codex/pxc119-mechanism-price`

Status: internally exact-replayed; no cooperative-game specialist review.

## Claim

Let `v` be the lower envelope of the nonnegative total-eight polytope with

```text
0123>=4, 0234>=6, 1234>=6,
025>=2, 125>=2, 245>=2, 01345>=8.
```

PXC139 claims that this is an exact singleton-normalized game with

```text
x=Lmin=(1,1,0,5/2,5/2,1),
z=Lmax=(2,2,0,2,2,0),
B_star=5 < 16/3=c_6*T,
O=6,
Psi_stat=191/34 > 16/3.
```

Thus the main hybrid inequality and the spectral--stationary disjunction
both hold.  However, if `E(q)` is the PXC138 product-weighted positive
diagonal exposure, then

```text
min {E(q): q is an optimal zero-diagonal stationary dual}
  =54/17 > 2/3=O-c_6*T.
```

This falsifies the proposed intermediate theorem

```text
B_star<c_n*T
 => some optimal zero-diagonal dual has E(q)<=O-c_n*T.
```

It does not falsify the main overlap inequality.

## Conventional proof map

1. The defining polytope has exactly four vertices:

   ```text
   (0,0,0,4,2,2), (0,0,0,6,0,2),
   (2,2,0,0,4,0), (2,2,0,2,2,0).
   ```

   Its lower envelope is therefore exact, and the vertices supply a zero
   witness for every coordinate.
2. `01345>=8` fixes player 2 to zero.  Complements of `0234>=6` and
   `1234>=6` bound the first nonfixed Lmin floor by one and pin players
   0,1,5 at equality; efficiency then equalizes players 3,4 at `5/2`.
3. `0234>=6` contains only three nonfixed coordinates, forcing the ceiling
   to at least two.  At ceiling two, it and `1234>=6` pin `z` uniquely.
4. The tight row `134>=6`, scaled by `1/3`, has zero hinge surplus.  The
   sharpened four-top anchor requires selected `x`-mass at least six.
   Clipping at `M=2` loses at most one, and `{2,3,4,5}` attains five, proving
   `B_star=5`; the actual top assignment has value six.
5. Matched exact stationary primal and dual certificates prove
   `Psi_0=191/34`.
6. The displayed optimal dual has exposure `54/17`.  A released primal at
   `t=1/20` attains
   `491/85=191/34+(1/20)(54/17)`.  PXC138a then forces every optimal
   zero-diagonal dual to have exposure at least `54/17`.

## Reproduction

```bash
python3 verifiers/divergence/verify_pxc139_strict_spectral_single_dual_no_go.py \
  --output /tmp/pxc139.json
cmp /tmp/pxc139.json \
  verifiers/divergence/pxc139_strict_spectral_single_dual_no_go.json

python3 \
  verifiers/divergence/verify_pxc139_strict_spectral_single_dual_no_go_independent.py \
  --output /tmp/pxc139-independent.json
cmp /tmp/pxc139-independent.json \
  verifiers/divergence/pxc139_strict_spectral_single_dual_no_go_independent.json
```

The independent audit imports no project game, selector, LP, spectral, or
stationary implementation.  It enumerates the core vertices with standalone
Fraction Gaussian elimination, reconstructs all 64 coalition values, checks
the human selector and spectral arguments, and replays every primal/dual
inequality.

## Hostile questions

1. Does the lower-envelope construction prove that the displayed seven-row
   polytope is exactly the core, rather than merely a subset of it?
2. Do the Lmin and Lmax arguments cover every lexicographic stage, including
   the fixed zero player?
3. Is the support-26 top certificate normalized correctly when one actual
   top player has coefficient zero?
4. Does the four-top enumeration really implement the sharpened spectral
   anchor, including the two zero lower-spectrum entries?
5. Does the `t=1/20` primal plus PXC138a prove minimal exposure over the
   entire optimal dual face, not just for the displayed dual?
6. Is any conclusion accidentally promoted from “the pointwise route is
   false” to “the main hybrid inequality is false”?

## Significance and prior art

This is a route-closing counterexample, not a new cooperative-game solution
concept.  PXC138's parametric sensitivity ingredients are standard; see
Adler--Monteiro (1992), https://doi.org/10.1007/BF01758841, and Ho (2000),
https://doi.org/10.3233/INF-2000-11406.  A 2026-08-24 search found no
selector-specific use of this exact lower-envelope witness, but no novelty
claim should be made without specialist review.  Its value is to prove that
the global campaign must control the integrated diagonal-release curve (or
an equivalent global quantity), not merely select a favorable dual at
`t=0`.
