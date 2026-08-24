# Hostile external review packet — PXC121–PXC123

Status: candidate results, internally and independently replayed; no claim of
novelty before cooperative-game specialist review.

## Requested review

Please independently audit the conventional proofs, not merely the JSON
outputs. Check exactness, singleton normalization, every selector stage,
proper tight-row menus, complete-`Cx` quantifiers, normalized extreme-cover
exhaustions, spectral formulas, parameter chambers, and the all-`n`
extensions. Check especially that every displayed price comes from explicit
rows, witnesses, or payoff-stratum rectangles rather than renaming overlap.

Separately search the cooperative-game and polyhedral literature for a result
equivalent to the forced-zero cover-blocker mechanism or its two-rung
rank-paired price. Distinguish correctness, significance, and novelty.

Review the checkpoint head on branch `codex/pxc119-mechanism-price`; the
handoff message should pin the immutable commit SHA.

## Authoritative paths

Theorems and conventional proofs:

- `paper5/divergence.tex`, displays PXC121a–PXC123e
- `paper5/MECHANISM_PRICE_PROGRAM.md`
- `paper5/PROTECTED_RESULTS_LEDGER.md`

Primary and independent audits:

- `verifiers/divergence/verify_pxc121_obstruction_spectral_closure.py`
- `verifiers/divergence/verify_pxc121_obstruction_spectral_closure_independent.py`
- `verifiers/divergence/verify_pxc122_positive_common_price.py`
- `verifiers/divergence/verify_pxc122_positive_common_price_independent.py`
- `verifiers/divergence/verify_pxc123_dimension_free_common_price.py`
- `verifiers/divergence/verify_pxc123_dimension_free_common_price_independent.py`
- matching JSON files beside each verifier

Scoped negative result:

- `verifiers/divergence/verify_pxc124a_reciprocal_affine_no_go.py`
- `verifiers/divergence/pxc124a_reciprocal_affine_no_go.json`

## Theorem-by-theorem questions

### PXC121: zero-demand parametric closures

1. Does the PXC101 elimination cover its entire stated chamber for every
   `k>=2`, including the split at `k=5/6`?
2. Is the bound for the PXC106 reciprocal family valid for all admissible
   `m,A`, rather than only sampled parameter points?
3. Are these correctly described as spectral closures, without promoting
   them to the full PXC114 common or reciprocal branches?

### PXC122: positive-demand falsifier of PXC120

1. Do the chamber inequalities imply `2A<B`, `B-A<C<K0<M`, while leaving
   the relative order of `B` and `C` genuinely free?
2. Is the lower-envelope game exact and singleton-normalized for all rational
   points in the chamber?
3. Is `Cx={rhj,rhbK}` uniquely complete for every `t`, not just at the
   audited values?
4. Does the typed normal-cone argument exclude every additional tight
   coalition using a proper nonempty subset of the symmetric `K` block?
5. Are the five displayed supports all normalized extreme top covers, and is
   `rhaK` forced to coefficient zero throughout the full cover polytope?
6. Does every cover lift have the claimed reduced upper selector, making the
   common descent and universal cover failure genuine?

### PXC123: dimension-free common price

1. Are the piecewise formulas for `B_H`, overlap, and `P_C` the true
   opposite-order spectral expressions in both `C<B` and `C>B` chambers?
2. Are the rectangles `B-A` and `B-2A` (or `min(B,C)-2A` at `t=1`)
   genuinely supported by the stated certificate/blocker/stratum data?
3. Is the split `t=1`, `t=2`, `t>=3` exhaustive, and do the displayed strict
   inequalities establish `P_C>=D_H` throughout the full chamber?
4. Does the result prove one open family in every dimension without implying
   a universal common-branch theorem?

### PXC124a: reciprocal affine no-go

1. Do the three cases for the repeated Lmin level exhaust the stated
   asymmetric PXC104 selector profile?
2. Do the chamber inequalities make each symbolic value
   `2T/3-B_H` strictly negative?
3. Is the result correctly scoped as a selector-profile no-go, not a theorem
   about every reciprocal incidence pattern?

## Reproduction

From the repository root, run:

```sh
bash paper5/verify_release.sh /Users/maxf/miniforge3/bin/python3
```

The release gate regenerates and byte-compares every cited artifact, checks
TeX safety, and performs two byte-identical PDF/arXiv builds.

## Present significance claim

PXC121–PXC123 do not prove the global hybrid-overlap conjecture. They provide
two whole parametric zero-demand closures, a counterexample to the
positive-demand-implies-fidelity shortcut, and a conventional
all-dimensional quantitative theorem on one open common-obstruction family.
The universal common-price theorem, a positive-demand reciprocal theorem,
and the global inequality remain open.
