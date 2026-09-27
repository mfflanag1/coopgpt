# Current pair-additive research frontier

Updated September 6, 2026 after the fifth bounded cycle and manuscript consolidation. The mathematical vanishing-family target is proved: **there is no positive uniform leximin protection constant**, even with bounded nonnegative integer pair data and a positive first global floor. Novelty and external specialist review remain unresolved.

## Established bounds

For complete equal-sector strict-triple markets with `w_ijk=A_ij+B_ik+C_jk`, nonnegative pair matrices, positive integral matching worth, and nonempty full core:

    c_pair = 0,
    4/3 <= d_pair <= 2.

Here c_pair is the infimum, over admissible games and players with positive whole-core ideal H_i, of their full ascending-leximin fraction x_i/H_i. The opposing full-selector distance d_pair remains unresolved. Strict-chain constants remain c_chain=1/3 and d_chain=4/3; their methods are classical and application-specific priority is unconfirmed.

## Main result: a linear-size vanishing family

The [fifth-cycle theorem](cycle5/root/VANISHING_FAMILY.md) constructs, for every integer q>=1:

    9q+3 labeled players, equally split across three sectors;
    8q+1 nonzero pair entries, each1 or2;
    every full triple available, with value at most5;
    true integral matching worth T=6q+1;
    a whole-core floor witness positive in all coordinates;
    target full-leximin payoff x=1/[3(q+1)];
    target whole-core ideal H=1.

Thus x/H tends to zero. This proves the all-size protection conclusion, not an optimal finite-size ratio or a minimum player count.

The proof has a simple certificate. A diagonal perfect matching is worth 6q+1. An explicit disjoint partial matching is worth 6q and leaves 3q+3 players. Its core inequality caps their total payoff at one. A complete cover equalizes all of them at 1/[3(q+1)], fixing the target on the entire first optimal face. Another complete cover attains its matching-team ideal bound of one. Four pair-pattern cases establish every mixed-triple inequality for all q.

The [independent proof](cycle5/independent/INDEPENDENT_FAMILY_PROOF.md) checks all-parameter positivity, cover completeness, integral worth, partial-matching disjointness, first-face pinning, and ideal attainment. Two independent constructions also pass all 7,208 rational triple checks at q=1,2,3,4, and three raw-core SMT exclusions at q=4 pass. The universal result rests on the symbolic proof, not extrapolation. The saved floor witness is not asserted to be the entire final selector.

## Priority disposition

The [September 6 priority follow-up](priority_confirmation_2026-09-06/REVIEW.md) adds 33 focused queries, new primary reads, and checks for deductive anticipation. No earlier establishment of the exact theorem was identified. The family is excluded from every three-sector strict-chain ordering even with signed values truncated at zero; the inspected general representation theorems do not preserve the necessary full payoff core and selector. The strongest supported status remains a credible specific novelty candidate, with priority unconfirmed. The meaningful boundedness strengthening is the fixed integer pair alphabet {0,1,2}, since ordinary real-valued bounds can be obtained by ratio-preserving scaling. Lucas pagination is now confirmed as 55–65 by the primary publisher record; its full text remains unread.

The [new claim ledger](cycle5/NOVELTY_LEDGER.md) classifies the result as a **surviving constrained-realization candidate; novelty unconfirmed**. The protection criterion has explicit earlier assignment-bargaining precedent, and an earlier flow-path example already gives vanishing protection in a broader game class. Sorted selectors and LP/matching certificates are established tools.

The historical audit obtained the 2020 assortative author texts and the modern followup inspected the distinct 2026 supermodular/local-monotonicity extrema paper. A zero-row/disjoint-support obstruction excludes this family's actual tensor from their supermodular hypotheses under any within-sector relabeling for q>=3. That is not a universal exclusion of other constructions or labeled-core representations.

The [current original-source comparison](../paper5/chain_cycle_separation/sources/ORIGINAL_COMPARISONS.md) closes the distinct 2023 SSRN4369524 gap after reading the full original. Its general Theorem 2 can redescribe an assignment core; it does not state the present vanishing family or payoff-to-ideal separation. No universal exclusion of strip-prone representations is claimed. Quint, Lucas and Stuart retain full-original gaps. The user declined purchases and requested skipping paid access. The two extreme-core titles are separated correctly, and Lucas’s volume/issue is confirmed as 81(1). Broader claims of a newly discovered fairness metric, a first vanishing example in all combinatorial games, a new LP method, or a confirmed field-level breakthrough are unsupported.

## Preserved results and failed routes

The earlier finite examples at5/18,1/6,1/9 and the older all-q family approaching1/6 remain valid. They are superseded as the main class-wide protection frontier. The new q=2 family member and the earlier21-player witness are distinct inputs. The old fixed-weight63-player composition results at2/9 remain correct; they did not exclude reweighting or this serial construction.

The residual partial-matching dual remains valid, while the proposed universal six-deficit bound was false. The [fixed-size bound](cycle5/root/FIXED_SIZE_CERTIFICATE_BOUND.md), derived from classical LP duality and determinant bounds, confirms that positive-first-face vanishing must use unbounded player counts. Its proof is independently audited; it is a supporting observation rather than methodological novelty.

All earlier no-go statements retain their original scopes: the specific delta modification and ring closure, fraction-preserving cloning, the failed sector-spread bridge, non-transfer of the3/2 cover split to fairness, the faithful-completion obstruction, and the strict-class obstruction to zero-ideal deletion. They must not be generalized beyond their recorded hypotheses. The [cycle4 status](STATUS_CYCLE4.md) and older status files preserve the progression.

## Manuscript and verification release

The [chain–cycle separation package](../paper5/chain_cycle_separation/README.md) contains an eight-page manuscript with complete proofs and a two-page specialist review brief. A frozen Claude review found no mathematical error; its three precision comments were addressed. This is model review, not external specialist approval. The full build passes, including 7,208 exact triple-cover checks in each of two routes, three raw-core exclusions, three selected chain markets and 21 explicit per-player cycle certificates. Three corrupted input checks fail as intended. The portable ZIP passes clean-extraction hash checks and standard and solver replay. Both PDFs were visually inspected. The technical package is complete for specialist review; novelty remains qualified and author/journal metadata remain to be supplied for submission. No outreach or submission was sent.

## Current decision and app state

The mathematical branch has reached its target and this bounded cycle is complete. The remaining publication decision depends on priority and specialist review of the exact theorem and unresolved original sources. The opposing-selector distance problem is separate and unchanged; no new distance claim was pursued here.

The user explicitly asked to set the new goal. The app's create-goal call rejected replacement because the older external-review goal is unfinished. The authorized [working goal](cycle5/CAMPAIGN.md), proof, audit, and replay materials are saved in the repository. The app tracker was not changed, the old review was not marked complete, and no outreach was sent.
