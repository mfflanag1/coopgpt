# Hostile external review packet — PXC129 carrier-to-cover price dichotomy

Date: 2026-08-24

## Claim to review

PXC129 does **not** prove the dimension-free hybrid-overlap inequality.  It
proves a local bridge for every positive canonical carrier
`i -> j` satisfying

```text
min(x_i,z_i) > max(x_j,z_j).
```

If no coalition tight at both selectors separates `i,j`, then for every
normalized `z`-tight top cover exactly one of the following happens:

1. the cover contains both orientations of the `i,j` cut and pays a strictly
   positive part of its explicit top-selection slack; or
2. every positive cover row gives `i,j` identical incidence, so `e_j-e_i`
   is a staged Lmax descent of the lift and full-game optimality forces an
   omitted `z`-tight outside blocker containing `i` and omitting `j`.

The theorem also records the exact cover identity

```text
sum_R lambda_S [x(S)-z(S)]
  = sum_{u in Top(z)} alpha_u (x_u-z_u).
```

## Load-bearing questions

1. Does the staged tangent argument really force an oriented `x`-tight row
   and an oriented `z`-tight row for every strictly concordant carrier?
2. Is the active-nonnegativity boundary handled correctly when `z_j=0`?
3. Does equal outsider load force the two oriented cover weights to agree,
   including the `eta=0` pair-cover boundary?
4. Does absence of a common separator make every separated `z`-tight cover
   row strictly slack at `x`, rather than merely weakly slack?
5. In the zero-cut case, are all `C_x` rows active at `z` necessarily common,
   and is the forced blocker genuinely outside `C_x union R`?
6. Does any sentence accidentally claim that the local positive charge
   aggregates to the full deficit `D_H`?  It does not yet do so.
7. PXC104/PXC118 have zero positive canonical carrier length.  Is their use
   clearly labelled as an incidence-boundary calibration rather than evidence
   for the positive-carrier premise?

## Exact artifacts

```bash
python3 verifiers/divergence/verify_pxc129_carrier_cover_price_dichotomy.py \
  --output /tmp/pxc129.json
cmp /tmp/pxc129.json \
  verifiers/divergence/pxc129_carrier_cover_price_dichotomy.json

python3 \
  verifiers/divergence/verify_pxc129_carrier_cover_price_dichotomy_independent.py \
  --output /tmp/pxc129-independent.json
cmp /tmp/pxc129-independent.json \
  verifiers/divergence/pxc129_carrier_cover_price_dichotomy_independent.json
```

The primary audit checks PXC101/PXC116, PXC104/PXC118, PXC127, and PXC90.
The standalone audit uses no project selector or cover implementation.

## Current significance

PXC129 is a conventional dimension-free structural lemma.  It converts the
unseparated-carrier residue of PXC128 into the two permitted sources of
currency: actual cover-selection slack or a forced outside blocker.  Its
remaining quantitative obligation is substantial: couple the PXC128 dual
carrier measure to those coverwise charges without double counting and prove
that top plus blocker currency reaches the full spectral deficit.

## Prior-art caution

The tangent-cone alternative, balanced-load identity, LP duality, and
Pigou--Dalton transfer language are standard ingredients.  No novelty claim
is made for those ingredients.  The potentially new object is their specific
coupling for Lmin/Lmax core selectors of exact games.  No cooperative-game
specialist has yet certified that this selector-specific formulation is new.
