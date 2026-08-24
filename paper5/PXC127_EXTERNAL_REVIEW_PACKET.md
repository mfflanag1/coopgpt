# Hostile external review packet — PXC127 square falsifier and row-cut price

Review the PXC127 block in `paper5/divergence.tex` and the two exact verifier
pairs listed below.  Do not treat verifier output as a proof of the symbolic
cut inequality.

## Claims to audit

1. The total-25 lower envelope defined by
   `rh>=12`, `rhj>=69/5`, `rhak>=89/5`, `rhbk>=23`, and
   `rhajk>=99/5` is exact and singleton-normalized.
2. Its selectors are
   `x=(32/5,32/5,1,51/10,1,51/10)` and
   `z=(6,6,1/5,26/5,9/5,29/5)`.
3. `{rhj,rhbk}` is the unique complete proper-row Lmin certificate; the full
   proper z-tight menu is `{rh,rhj,rhk,rhbk,rhajk}`; and `{rh}` is the only
   extreme normalized positive-top cover.
4. The corresponding lift keeps Lmin but changes Lmax to
   `(6,6,1/5,11/2,9/5,11/2)`.
5. Every eligible PXC126 Boolean square has an empty cell, so the square price
   is zero while `D_H=2/3`; this refutes only the square-extraction conjecture,
   not hybrid overlap.
6. For an arbitrary row cut, the maximum-weight bipartite matching with edge
   weight `max((a_i-b_j)_+,(a_j-b_i)_+)` is always at most `O-B_H`.
   Opposite-rank matching is the fixed-orientation specialization.
7. For `C=rhbk`, that price is exactly
   `(51/10-1)+(51/10-9/5)=37/5=O-B_H>D_H`.

## Proof points requiring independent attention

- Check the hand Lmin and Lmax stage arguments, including uniqueness at every
  tied stage.
- Solve the normalized cover equations directly rather than trusting the
  enumerator.
- Check that all four certificate/blocker incidence tables really have an
  empty cell.
- Audit the layer-count proof of the cut bound.  In particular, confirm that
  every active rectangle uses distinct high-high and low-low endpoints, even
  when different matched edges use opposite orientations.
- Decide whether this cut construction is known under a standard name in
  rearrangement, bipartite matching, Lorenz-order, or cooperative-game
  exactness literature.  No novelty is claimed before that check.
- Hostilely test the open pure-cut implication.  A counterexample needs
  `max_C P_cut(C)<D_H`; an empty Boolean square is no longer sufficient.

## Reproduction

From the repository root:

```bash
/Users/maxf/miniforge3/bin/python3 \
  verifiers/divergence/verify_pxc127_common_row_cut_falsifier.py \
  --output /tmp/pxc127-primary.json
cmp verifiers/divergence/pxc127_common_row_cut_falsifier.json \
  /tmp/pxc127-primary.json

/Users/maxf/miniforge3/bin/python3 \
  verifiers/divergence/verify_pxc127_common_row_cut_falsifier_independent.py \
  --output /tmp/pxc127-independent.json
cmp verifiers/divergence/pxc127_common_row_cut_falsifier_independent.json \
  /tmp/pxc127-independent.json
```

The independent script uses a separate exact Fraction active-set selector and
Gaussian cover implementation.  It imports no project selector, cover,
PXC108, PXC126, PXC127, or primary-verifier implementation.

## Scope

PXC127 is a rigorous correction and structural advance: it kills the square
conjecture and proves a stronger dimension-free allocation subpacking.  It
does not prove the universal common branch, the reciprocal branch, or the
global hybrid-overlap inequality.
