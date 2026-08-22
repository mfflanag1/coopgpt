# Hostile external review — PXC101 forced-zero-blocker family

Checkpoint date: 2026-08-22. Review `PXC101--PXC103` in
`paper5/divergence.tex`. The claimed result is a conventional parametric
theorem with exact computational replays, not a complete classification of
all six-player failures.

## Claimed theorem

For every `n>=6` there is a positive-dimensional rational family of exact
singleton-normalized games with exactly two Lmax-top players such that:

1. the proper x-tight pool is exactly `{rha,rhb}` and this is the unique
   complete Lmin certificate;
2. the proper z-tight pool is exactly `{rh,rha,rhb,rj,rhO}`;
3. the normalized extreme top covers are exactly `{rh}` and
   `{rha,rhb,rhO}`;
4. `rj` has coefficient zero in every cover;
5. both sparse lifts preserve Lmin but change Lmax by equalizing the entire
   outsider block;
6. therefore both the fixed-Cx and existential-Cx versions fail for every
   `n>=6`.

The integer member has `k=n-4`, total `k+15`, rows

```text
rha>=11, rhb>=11, rj>=6, rhO>=k+9,
```

and selectors

```text
x=((10k+7)/(2(k+1)))^2, ((k+4)/(k+1))^(k+2)
z=(4,4,3,3,2,1^(k-1)).
```

## Dependency map

```text
four-row compact lower envelope
  -> exactness + explicit singleton witnesses
  -> hand Lmin/Lmax staged inequalities
  -> generic active-normal classification
  -> five-row z-tight menu
  -> one-dimensional normalized-cover polytope
  -> forced coefficient zero on rj
  -> common later-stage descent in both sparse lifts
  -> failure of both Cx quantifiers for every n>=6.
```

`PXC103` separately proves an iff statement only for the
**common-direction** mechanism. It does not claim that all universal-cover
failures possess a common direction.

## Exact reproduction

From the repository's `coopgames/` directory:

```bash
python3 verifiers/divergence/verify_pxc101_forced_zero_family.py \
  --output /tmp/pxc101-primary.json
cmp verifiers/divergence/pxc101_forced_zero_family.json \
  /tmp/pxc101-primary.json

python3 verifiers/divergence/verify_pxc101_forced_zero_family_independent.py \
  --output /tmp/pxc101-independent.json
cmp verifiers/divergence/pxc101_forced_zero_family_independent.json \
  /tmp/pxc101-independent.json
```

The primary implementation uses the project rational simplex and replays
`n=6,7,8`. The independent implementation contains its own rational
active-set LP and imports no project LP, selector, game, cover, or family code.

## Hostile questions

1. Do the two parameter inequalities really imply every strictness used in
   the Lmin proof, especially `p>u`, `p+u>B`, and slackness of `rhO` at x?
2. Does equality in the floor bound genuinely pin all `k+2` lower players,
   rather than only their sum?
3. Is `{rha,rhb}` the full proper x-tight menu by the normal-cone argument,
   and do the one-row retained polytopes prove both rows indispensable?
4. Does the Lmax argument establish every later stratum, not merely the top
   ceiling and the total outsider sum?
5. Is the six-coordinate-type normal calculation valid for arbitrary `k`,
   including coalitions containing only some symmetric bottom outsiders?
6. Does the normalized cover census include all extreme supports allowed by
   PXC97b, including eta zero?
7. Does positive support plus the cover identity justify the iff in PXC103,
   with common Cx and active nonnegativity treated correctly?
8. Are the singleton witnesses valid throughout the weak boundary
   `q+(k-1)K=M`?
9. Is the construction genuinely distinct from null-player padding and from
   known exact-partition/large-core examples?
10. Are any novelty claims stronger than the dated literature search permits?

## Known limitations

- This is not an exhaustive classification of six-player obstruction types.
- The generic all-dimension proof is conventional algebra; finite exact LP
  replays are calibrations, not the logical basis of the all-n quantifier.
- The independent checker changes the LP implementation but shares the
  theorem's explicit formulas.
- Literature novelty remains subject to a human cooperative-game specialist.
