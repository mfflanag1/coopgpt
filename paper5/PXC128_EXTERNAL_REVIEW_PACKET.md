# Hostile external review packet — PXC128 fractional common-cut cover

Review PXC128 in `paper5/divergence.tex` independently of the verifier output.
The theorem is an allocation-level carrier-separation reduction; it is not a
claim that the hybrid-overlap inequality or the common PXC114 branch is
finished.

## Claims to audit

1. The positive rank-paired rectangles in `(CS)` form a matching `E` with
   lengths `ell_e>0` summing to `O-B_H`.  In particular, audit the short
   contradiction excluding one player from being a low endpoint at one rank
   and a high endpoint at another.
2. For a retained common row `C`, the canonical edges crossing its cut form a
   feasible submatching, hence their total length `K_C` is at most
   `P_cut(C)`.
3. If `chi` is the fractional set-cover number of these carriers by the
   predeclared common-row cuts, multiplying the cover constraints by
   `ell_e` proves
   `max_C P_cut(C) >= (O-B_H)/chi`.
4. If `chi` is infinite, some positive canonical carrier is unseparated by
   every common row.  If it is finite, rational LP duality gives the carrier
   measure in `(PXC128c)` whenever every cut price is below `D_H`.
5. PXC122 and PXC127 have `chi=1`; the three-edge triangle control has
   `chi=3/2`, so the formulation is genuinely fractional.

## Hostile questions

- Check the strict inequality and reciprocal in the deduction
  `max P_cut<D_H => chi>(O-B_H)/D_H`.
- Check that zero-length rank pairs are harmlessly deleted and that a
  positive rank pair cannot reuse one player as both endpoints.
- Check that mixed orientations in `P_cut` can only strengthen the canonical
  crossing submatching used in the proof.
- Decide whether this reduction is merely the standard fractional set-cover
  theorem in new notation.  The paper should claim no novelty for set-cover
  duality itself; any potential novelty lies in coupling its dual carrier
  measure to exact-game singleton witnesses and staged selector certificates.
- Try to extend the dual carrier measure together with the actual
  outside-union blocker to an `(MCP)--(MWP)` packet.  A failure should be
  supplied as an exact singleton-normalized game, not an allocation-only
  incidence table.

## Reproduction

```bash
/Users/maxf/miniforge3/bin/python3 \
  verifiers/divergence/verify_pxc128_fractional_common_cut_cover.py \
  --output /tmp/pxc128-primary.json
cmp verifiers/divergence/pxc128_fractional_common_cut_cover.json \
  /tmp/pxc128-primary.json

/Users/maxf/miniforge3/bin/python3 \
  verifiers/divergence/verify_pxc128_fractional_common_cut_cover_independent.py \
  --output /tmp/pxc128-independent.json
cmp verifiers/divergence/pxc128_fractional_common_cut_cover_independent.json \
  /tmp/pxc128-independent.json
```

The standalone verifier imports neither the project LP solver nor the primary
PXC128 implementation.  It independently rebuilds the rank carriers and
solves both LPs by exact rational Gaussian vertex enumeration.

## Current frontier

PXC128 proves the exact cut-or-dual-witness reduction.  The load-bearing open
step is game-theoretic: use the outside-union blocker, its basic staged Lmax
Farkas support, and singleton-attainment allocations to convert the dual
carrier measure into a target-reaching mixed tagged packet.  The reciprocal
PXC114 branch and final global synthesis remain open.

## Dated prior-art screen (2026-08-24)

- Fractional set-cover LP duality is standard; PXC128 does **not** claim it as
  new.  See Chvátal, “A Greedy Heuristic for the Set-Covering Problem” (1979),
  DOI `10.1287/moor.4.3.233`, for the classical set-cover LP setting.
- Opposite-order assignment and sorted matching belong to the Monge and
  rearrangement literature; see Burkard, Klinz, and Rudolf, “Perspectives of
  Monge properties in optimization” (1996), DOI
  `10.1016/0166-218X(95)00103-X`.  PXC128 claims no novelty for that ingredient.
- The cooperative-game background was screened against Schmeidler, “Cores of
  exact games, I” (1972), DOI `10.1016/0022-247X(72)90045-5`, and Studený and
  Kratochvíl, “Facets of the cone of exact games” (2022), DOI
  `10.1007/s00186-022-00770-4`.

This screen did not locate a result coupling a fixed complete Lmin
certificate, the Lmin/Lmax canonical carrier matching, fractional separation
by common tight rows, and an outside-union staged-Lmax blocker.  That negative
search is not a novelty determination.  A cooperative-game specialist must
still review the selector-specific coupling before any novelty claim.
