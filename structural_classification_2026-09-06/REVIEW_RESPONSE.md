# Review disposition

Two separate frozen Claude consultations were completed. Neither executed code, accessed sources, or assessed novelty. Their mathematical findings were checked against the derivation and exact replay before edits.

## Tree representation and path theorem

See review/path/review.md and its request.json for the precise reviewed source hash. Claude verified diagonal matching composition, both directions of the cut representation, cut signs, invertibility, the potential-network encoding, the exact k-payoff-arc count, and the sharp simplex example. No correctness defect was found.

Applied clarity corrections: explicitly require k>=2, m>=1, equal sector sizes and T>0; define c(G) using positive ideals; keep zero-ideal coordinates in the full selector; explain equivalence of team covers and the integral coalition core; omit structural self-loops; include compactness/uniqueness and simple-cycle extraction; expand the lexicographic perturbation argument. No theorem statement was strengthened beyond the reviewed claim. The original integral convention remains fixed; an incidental review suggestion about fractional games was not adopted as a new claim.

## Four-cycle certificate

See review/cycle/review.md and request.json. Claude hand-checked the matching team values 7,6,5; the six rational dual weights and their loads; the deficit identity with sum d=2 and target deficit 1/4; the target pinning; and ideal bound/attainment at5. It also reported checking both full-team covers by hand. Separately, our standard-library checker executes all162 cover checks exactly.

Applied robustness corrections: reject a missing edge matrix, require the exact C4 graph and {0,1,2} matrix alphabet, validate matrix shapes and positive dual terms, and clarify that matching perfectness does not require dual teams to be disjoint. Explicitly label auxiliary all-player H and level fields as optimizer results not certified by the standard-library target checker. Four deliberately corrupted certificates are rejected. These changes do not change the numerical witness or proof.

## Remaining limits

There is no external specialist endorsement. A source audit is incomplete, with three original texts skipped at the user's request. The general acyclicity question, the star constant, and four-cycle vanishing remain unresolved. Model review of the completed claims does not certify those open extensions.
