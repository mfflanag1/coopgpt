# Response to the hostile review of the rich-block family

## Review scope and verdict

The review examined commit `f0bc63c` and returned the mathematical verdict
`verified`: it independently reconstructed the lower-envelope games,
recomputed exactness, Lmin, and Lmax, and confirmed every closed formula.
Its requested changes concern significance framing and verifier coverage, not
a defect in the theorem.

## Changes made

1. The paper now leads with the strong axis: at `h=1`, the indecomposable
   four-generator family has normalized distance
   `(m-3)/(m-1) -> 1`.
2. A human proof of indecomposability was added.  Positive pair worths connect
   the first five poorer/rich players; explicit coalition interactions attach
   each later poorer player.  The endpoint cases `m=4,5,6` are handled
   separately.
3. Null-player padding and the direct sum of five-player copies are stated
   explicitly as trivial competitors.  Dimensional existence and a large tied
   rich block are no longer presented as the principal contribution.
4. The fixed-`h` qualifier is explicit:
   the normalized gap tends to `2/(h+1)` as `m -> infinity`; no uniform
   positive-gap claim is made as `h -> infinity`.
5. `src/verify_rich_block_family.py` now invokes the generic exact staged
   Lmax implementation, as well as staged Lmin, for every case up to a
   caller-selected player bound.  The artifact reports the exact replay count.
6. The `m=4` implementation now omits the formal zero
   `h(m-4)e_5` assignment instead of temporarily indexing a rich player.

## Remaining qualification

The review found no replication theorem subsuming the construction, but that
literature search was not definitive.  The novelty question is therefore
narrowed to whether an indecomposable exact-game family with growing
normalized Lmin--Lmax separation is known.  The manuscript does not claim
that the tied-rich-block axis alone is novel or superior to direct sums.
