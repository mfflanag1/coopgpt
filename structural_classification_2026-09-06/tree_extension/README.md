# All-tree protection and a stronger four-cycle certificate

This is the second research checkpoint within the active structural-classification goal. It completes the acyclic sufficient direction, including branching stars, but does not settle cyclic necessity or the full four-sector milestone.

- [All-tree theorem](ALL_TREES.md): for every fixed tree G with k>=2 sectors, c(G)=1/k. An explicit minimum-and-subtree-shift construction supplies the full-core leximin improvement argument. This includes all stages and zero-ideal coordinates.
- [Stronger C4 example](C4_INTEGER.md): twelve players, integer pair entries0..25, integral worth51, target leximin payoff5/4 and ideal11, hence ratio5/44. The earlier9/40 example remains valid but is superseded as an upper bound. No claim c(C4)=0.
- [Source scope](SOURCE_STATUS.md) and [review response](REVIEW_RESPONSE.md): novelty remains unconfirmed; model reviews do not replace external specialist review.

## Replay

Run `bash build.sh` with Python3.10 or later for exact rational certificate checks and four corrupted-certificate rejections. This requires no solver. The main witness is [C4_INTEGER_CERTIFICATE.json](C4_INTEGER_CERTIFICATE.json); the original rational synthesis witness is also replayed. All-player optimizer fields are auxiliary; the standard-library proof certifies the target only.

With z3-solver5.1.0.0 available, run `COOPGT_PYTHON=/absolute/path/to/python bash build.sh --smt`. It performs120 exact clipping checks across15 path, star and binary-tree markets with k=2..6, using raw full-team constraints, and confirms57 strict sorted-leximin improvements from deliberately nonleximin starting allocations. These finite checks corroborate the all-tree conventional proof; they are not extrapolated into it.

The optional synthesis script uses disjunctive linear complementarity constraints to seek first-face certificates. A star m=3 query reportedUNSAT, consistent with the newly proved theorem. A C4 m=3 query returned a rational witness; one attempt hit an export bug afterSAT, now corrected and recorded in FAILED_EXPORT.json. A ratio-below1/16 query timed out and is recorded asunknown. Neither unknown nor failed export is a negative mathematical result.

## What remains

Determine whether C4 has a positive uniform constant or admits an all-size vanishing family. The stronger finite witness is a starting point for a structural amplification argument, not a reason to keep searching only for smaller constants. If C4 is resolved, finish the four-sector graphs and prove any transfer lemmas needed for general cyclic G. Do not assume adding sectors, deleting edges or contracting an edge preserves full leximin and whole-core ideals. The general classification goal remains active.
