# External review packet — PXC141 literal-target counterexample

Date: 2026-08-24

## Claim to review

The literal statement `O(Lmin,Lmax) >= [n/floor(n^2/4)] T` for every exact
singleton-normalized game is false, first at `n=5`.  The counterexample is
not newly discovered: it is exactly the manuscript's existing five-player
extremal game (Theorem `n=5`), now recognized as a domain obstruction to the
later mechanism-price program.

Its generators are `(1,0,0,1,2)` and `(0,1,3,0,0)`, its total is `T=4`, and

`Lmin=(1/2,1/2,5/4,1/2,5/4)`,
`Lmax=(1,0,1,1,1)`.

Thus `O=3`, whereas `c_5 T=(5/6)4=10/3`.  The failure margin is `-1/3`.
The existing n<=4 coincidence theorem proves that five is the smallest
dimension.

## What was independently checked

- all 32 lower-envelope game values and singleton normalization;
- exact staged recomputation of both selectors;
- all 16 subfamilies of the proper x-tight pool `{3,10,21,28}` and every
  complete Lmin certificate among them;
- a standalone symbolic proof from the complementary tight partitions;
- the exhaustive spectral-top decomposition;
- the domain boundary: `Top(Lmax)={0,2,3,4}`, so the two-top hypotheses of
  PXC112/PXC114 do not apply.

## Reproduction

```bash
python3 verifiers/divergence/verify_pxc141_n5_dimension_free_counterexample.py \
  --output /tmp/pxc141.json
cmp verifiers/divergence/pxc141_n5_dimension_free_counterexample.json \
  /tmp/pxc141.json
python3 verifiers/divergence/verify_pxc141_n5_dimension_free_counterexample_independent.py \
  --output /tmp/pxc141-independent.json
cmp verifiers/divergence/pxc141_n5_dimension_free_counterexample_independent.json \
  /tmp/pxc141-independent.json
```

## Questions for hostile review

1. Do the lower-envelope construction and complementary-partition argument
   conventionally prove exactness and both selectors?
2. Is `O=T-||x-z||_1/2` applied correctly?
3. Does the n<=4 coincidence theorem suffice for dimension minimality?
4. Is the distinction between falsifying the all-n statement and leaving
   the corrected n>=6 statement open completely explicit?
5. Is any claim accidentally presented as novel, given that the game and
   `s(5)=1/2` already occur earlier in the manuscript?

## Significance and prior-art posture

This decisively falsifies the newly posed literal target, but is not a new
cooperative-game counterexample.  Its mathematical content was already
proved earlier in this manuscript as the five-player anomaly.  The new point
is scope: the coefficient `n/floor(n^2/4)` is incompatible with that theorem
at `n=5`.  PXC140 remains a valid optimization reduction for the corrected
n>=6 campaign.
