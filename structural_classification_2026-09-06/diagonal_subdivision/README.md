# C4 diagonal subdivision: exact transfer obstructions

The [no-go proof](DIAGONAL_SUBDIVISION_NO_GO.md) proves two restrictions on splitting the ac edge of the known triangle family with a diagonal bonus. For EVERY fixed M>0, all players have ratio at least M/[4(4+M)], uniformly in family depth. For the original source target, an explicit partial matching proves ratio at least1/12 for EVERY M>0, even if M shrinks with family depth. Thus the source target's vanishing cannot transfer through this gadget. This is not a universal1/12 theorem for C4.

The reason is explicit: the bonus produces a full-core cover with uniform floor M/4, while an optimal diagonal team's worth bounds each ideal by M+4. A separate partial matching bounds the source target's ideal by3M. For M<2, the floor cover is obtained by interpolation from the M=0 and M=2 markets. The [review disposition](REVIEW_RESPONSE.md) records the scope and checked corrections.

## Reproduction

Run `bash build.sh` with Python3.10 or later. It verifies206,090 full-team covers across q=1..4 and M=1/4,1/2,1,2,4, the diagonal matching/ideal bounds, and twenty instances of the source-target partial matching.

With z3-solver5.1.0.0, `COOPGT_PYTHON=/absolute/path/to/python bash build.sh --smt` also reproduces eight full-leximin and all-player-ideal profiles at q=1,2 and M=1/4,1/2,1,2. These are finite observations corroborating the conventional proofs. Q3_QUARTER.json retains a separate q=3 profile; its tight-dual artifact is for pattern extraction, not an inferred recurrence.

The raw-core solver is copied from the earlier exact probe, with one explicit adaptation: it accepts a separately proved grand worth rather than enumerating all perfect matchings. For this source family and every M>=0, each edge's sum of row maxima is attained by its diagonal matching. The values are2q for A,2q for B,2q+1 for C, and mM for the diagonal bonus. Therefore every four-team matching is bounded by6q+1+mM, and the full diagonal matching attains it. Summing row-price covers also proves nonempty core. This justifies the fixed-T numerical models even below the dominating-bonus threshold.

## Remaining goal

C4 remains unresolved between0 and5/44. Trees are settled at1/k, and triangle-containing allowed graphs at0. The subsequent [uniform-bound proof](../subdivision_uniform_bound/README.md) closes the remaining different-target/shrinking-bonus regime: the whole exact family has ratio at least1/676. This package retains the earlier proof and computational history. A different C4 mechanism remains necessary. No new source-priority claim, purchase or outreach is made.
