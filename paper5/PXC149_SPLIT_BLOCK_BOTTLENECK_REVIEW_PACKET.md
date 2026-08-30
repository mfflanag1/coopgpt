# Hostile review packet — PXC149 split-block bottleneck

Review the version pinned by the commit accompanying this packet.  Do not
treat verifier output as proof and do not infer novelty from the PXC label.

## Claims to audit

1. Let `U,A,B` be symmetric blocks of sizes `m,u,v`, with `u,v>=2`, and
   let the singleton-normalized Lmin candidate have role values
   `(1,X_b,X_c,1,1,1,1)`.  If

   ```text
   R3=bcdAB, R4=cdg, R7=cABg,
   F^A_i=b a_i B, F^B_j=b A b_j
   ```

   are tight, exactness supplies separate `b=0` and `c=0` core witnesses
   and forces

   ```text
   X_b <= m(uv-1)/((u-1)(v-1)),
   X_c <= 2m + m(uv-1)/((u-1)(v-1)).
   ```

   This statement is independent of the number of lower-envelope
   generators.  It is not an upper bound for arbitrary exact games.

2. For `k>=2`, `m>=k`, the displayed three-generator family `J_{m,k}` is
   exact and singleton-normalized, with the manuscript's closed Lmin and
   Lmax formulas.  Its first Lmax ceiling is certified by the four-orbit
   dual supported on `cdg`, `Ubd`, every `cd(A\i)`, and every `cd(B\j)`.

3. The exact overlap ratio is

   ```text
   2(3km-k-m+1)/(2k^2+5km-m-2),
   ```

   tending to `6a/(5a+2)<6/5` when `m/k->a`.  The `k=1` boundary is defined
   separately as PXC146's `H_m`; no continuity or common rational formula
   at that boundary is claimed.

## Load-bearing proof checks

- Verify that block averaging preserves each designated zero witness.
- Recompute the two multipliers
  `u(v-1)/(uv-1)` and `v(u-1)/(uv-1)` and check every coefficient in the
  `X_b` bound.
- Check that the `X_c` proof uses the independent `c=0` witness and does not
  silently reuse the `b=0` witness.
- Check every generator total and every asserted tight-row value.
- Check that `m>=k` is sufficient and necessary for the stated `C_0`
  non-undercutting comparison; the `m=k-1` control should fail by one.
- Independently sum the minimax-dual incidence loads and objective.
- Check that equality in that dual really pins `c,d,g,A,B`, after which the
  cross-block rows and efficiency uniquely determine `b,U`.
- Check all positivity, ordering, denominator, and empty-block edge cases.
- Decide whether the theorem's stated scope accidentally includes
  nonsymmetric games, nonzero singleton values, or row menus not covered by
  the proof.

## Reproduction

From the repository root:

```bash
python3 coopgames/verifiers/divergence/verify_pxc149_split_block_bottleneck.py \
  --output /tmp/pxc149-primary.json
cmp coopgames/verifiers/divergence/pxc149_split_block_bottleneck.json \
  /tmp/pxc149-primary.json

python3 coopgames/verifiers/divergence/verify_pxc149_split_block_bottleneck_independent.py \
  --output /tmp/pxc149-independent.json
cmp coopgames/verifiers/divergence/pxc149_split_block_bottleneck_independent.json \
  /tmp/pxc149-independent.json
```

The second implementation directly generates block-count coalition orbits
and runs fresh Z3 QF_LRA selector stages.  It imports neither the project
selector nor the primary verifier.  Its finite cases calibrate the human
all-parameter theorem; they do not prove its quantifiers.

## Prior-art questions

- Is the use of separate exactness witnesses to bound two rich coordinates
  a known lemma in exact-game, large-core, Lorenz-core, or min-balanced
  systems literature?
- Is the weighted two-row elimination simply a standard balanced-collection
  argument under an established name?
- Does the three-generator family `J_{m,k}` or its minimax dual coincide
  with a known exact-game construction after relabeling or normalization?
- Is the conclusion best presented as a new structural no-go, a routine
  corollary of known exact-cone duality, or only an internal construction
  diagnostic?
- Is a pair-indexed menu `b a_i b_j` genuinely the smallest remaining
  symmetric escape, or is a simpler row operation omitted?

## Required verdict

Report critical, major, minor, and presentational findings.  Give separate
verdicts for PXC149b (universal bottleneck), PXC149c--e (sharp family and
selectors), the `k=1` calibration, and the claimed next live cell.  Separate
correctness, significance, and novelty.  Until that review is complete,
PXC149 is an internally verified candidate theorem, not a field-level
breakthrough.
