# Review response

Claude checked both full-team cover cases, the cover/matching equality for integral worth, the full-leximin floor implication, diagonal-team ideal bounds and the specialization1/12. No correctness defect was found. The model review was by hand and did not execute tests or certify novelty; see review/general/review.md and its request.json.

Verified corrections:
- Define strict coalitional worth explicitly as integral matching of full teams. The review's shorthand that all non-full coalitions have zero worth is not literally adopted: a larger coalition can contain full teams and have positive worth.
- Clarify that T is worth computed using integral matchings, not an assumption that its numerical value is an integer. Existence of an optimal perfect matching follows directly from nonnegative values and equal sizes.
- The precise uniformity condition is an upper bound on D/M. The review suggested bounding both D and M, but no upper bound on M is necessary; with D=4 and every M>=2 the1/12 bound holds. This follows directly from M/[4(D+M)].
- All ideals in the constructed market are positive, since every player receives at least M/4 at the displayed core point.

The final proof has only these scope/clarity edits beyond the reviewed algebra. The exact profile computations were performed separately. The small-bonus profiles are not claimed to have an all-q theorem. The large-bonus no-go lemma is an internal route-elimination result, not a new broad contribution or a solution of C4.

## Subsequent substantive extensions

A separate review in review/fixed_bonus checked the all-fixed-bonus interpolation argument and the diagonal row-maximum proof. No defect was found. The final text distinguishes endpoint cover interpolation from affine efficiency. At M=0 the appropriate boundary theorem is the path c-b-a-d guarantee, not the zero-sector transfer, because d still interacts with a.

A further review in review/source_target checked the explicit3q-team partial matching for q=1 and arbitraryq, its exact unmatched set, total T-3M, and the resulting source-target ratio bound1/12 even for a shrinking positive bonus. No defect was found. The twenty finite partial-matching cases and exact raw-core profiles were checked separately by execution. Neither extension was assumed covered by the original review; each received a new frozen consultation.
