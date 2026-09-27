# Review response and verification scope

Two new frozen Claude reviews completed. Review records preserve the exact source hashes and requests. Neither review executed tools or assessed novelty.

## All-tree proof

See review/tree/review.md. Claude re-derived the tree cut representation under arbitrary rooting, minimum closure, both reconstruction cases, the root lower bound H-(k-1)*beta, and the strict sorted-leximin contradiction including alpha=0. No correctness defect was found. Its minor observation that the lower bounds use nonnegativity of y was checked and made explicit. The standing hypotheses already require equal sectors, nonnegative matrices, positive worth and full-core ideals.

The final proof differs from the reviewed snapshot only in its status statement and explicit reminder that core points are nonnegative. The scope paragraph is updated to the new C4 finite bound; the clipping proof itself is unchanged. The later finite tests execute120 clipping constructions against raw full-team inequalities and observe57 strict improvements from nonleximin starting points. They do not replace the all-parameter proof.

## Stronger four-cycle witness

See review/cycle/review.md. Claude hand-checked the matching worth51, positive floor cover, ten dual terms and deficits, target pinning at5/4, the two disjoint teams worth3+37=40, and ideal attainment11. It found no mathematical defect and distinguished its hand arithmetic from execution.

The checker default now points to C4_INTEGER_CERTIFICATE.json, addressing the reproducibility note. The command is `python3 check_synthesis.py C4_INTEGER_CERTIFICATE.json`; build.sh invokes it explicitly. An integer-entry check and four corrupted-certificate rejections strengthen the final validation without changing the reviewed numerical witness. All-player optimizer fields remain auxiliary and are not covered by the standard-library target proof.

## Limits

These are internal model reviews. No human specialist has approved the results. Novelty is unconfirmed. Acyclic sufficiency is proved, but cyclic necessity, C4 vanishing and the complete graph classification remain open. Unknown solver results are not interpreted as impossibility results. No purchases or outreach occurred.
