# Hostile external review packet — PXC143 n=7 overlap counterexample

Review target: PXC143 in `paper5/divergence.tex` on branch
`codex/pxc119-mechanism-price`.

## Claimed result

An explicit seven-player exact singleton-normalized game of total `119376`
has

```text
Lmin=(8507,24825,41719,17026,8555,8519,10225)
Lmax=(36,132,25137,25137,25125,25113,18696)
```

and therefore distance `99492 > 5T/6 = 99480`, equivalently overlap
`69630 < 7T/12 = 69636`. The game is the lower envelope of nine displayed
nonnegative efficient allocations. The separately proved six-player theorem
is used only for the dimension-minimality conclusion.

## Files

- `paper5/divergence.tex` — PXC143a--d and the sparse hand proof.
- `verifiers/divergence/verify_pxc143_n7_hybrid_overlap_counterexample.py`
- `verifiers/divergence/pxc143_n7_hybrid_overlap_counterexample.json`
- `verifiers/divergence/verify_pxc143_n7_hybrid_overlap_counterexample_independent.py`
- `verifiers/divergence/pxc143_n7_hybrid_overlap_counterexample_independent.json`
- `paper5/PROTECTED_RESULTS_LEDGER.md`
- `paper5/MECHANISM_PRICE_PROGRAM.md`

## Reproduction

```bash
python3 verifiers/divergence/verify_pxc143_n7_hybrid_overlap_counterexample.py \
  --output /tmp/pxc143.json
cmp verifiers/divergence/pxc143_n7_hybrid_overlap_counterexample.json \
  /tmp/pxc143.json
python3 verifiers/divergence/verify_pxc143_n7_hybrid_overlap_counterexample_independent.py \
  --output /tmp/pxc143-independent.json
cmp verifiers/divergence/pxc143_n7_hybrid_overlap_counterexample_independent.json \
  /tmp/pxc143-independent.json
```

## Hostile questions

1. Independently verify that the lower-envelope construction is an exact
   singleton-normalized game, rather than accepting either JSON artifact.
2. Check every coalition summation in the hand Lmin/Lmax proof and confirm
   that it certifies the full staged lexicographic selectors, including the
   tied first Lmax block.
3. Recompute the distance/overlap conversion and confirm that the target at
   seven players is `c_7=7/12`.
4. Audit whether Theorem `s6` has exactly the domain needed for the statement
   that seven is minimal inside the corrected `n>=6` conjecture.
5. Assess whether this construction, or an equivalent selector-separation
   counterexample, is already known. Correctness, significance, and novelty
   must be reported separately.
6. Do not infer the sharp value of `s(7)`: PXC143 supplies only the strict
   lower bound `s(7)>=8291/9948`.

No external specialist has reviewed PXC143 yet. The two verifier
formulations reduce implementation correlation but are not substitutes for
the requested mathematical and prior-art review.
