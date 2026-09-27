# Current pair-additive research frontier

Updated September 5, 2026 after the second bounded cycle. The user authorized continuation. The original all-size cyclic question remains unresolved; the campaign has produced conventional proofs with independent internal checks, not external review or a field-level breakthrough verdict.

## Established current bounds

For complete equal-sector strict triple markets w_ijk=A_ij+B_ik+C_jk with nonnegative pair matrices, positive integral matching value T, and nonempty full core:

    0 <= c_pair <= 1/6,
    4/3 <= d_pair <= 2.

Here c_pair is the best possible uniform full-leximin fraction of a player's maximum core payoff; d_pair is the supremum of normalized L1 distance between the two opposing full lexicographic selectors. A bound c_pair<=1/6 does not guarantee that any game protects its players at one-sixth.

For the strict chain subclass w=P_ij+Q_jk, the first cycle proved the sharp c_chain=1/3 and d_chain=4/3. The method is a chain-game application of classical partial slack balancing; application-specific priority is not certified.

## Main new result

The [coupled family](cycle2/theory/AMPLIFICATION_FAMILY.md) exists for every q>=3. It has9q players, T=8q, pair weights in{0,1,2,3}, and induced triple weights at most4. For every designated e_s with an incoming link,

    x_e=1/3+1/q,  H_e=2,
    x_e/H_e=1/6+1/(2q) -> 1/6.

The proof covers all local, mixed, and coupling triples. The first two optimal leximin faces force the designated coordinates; it does not claim that the displayed feasible cover is the entire final leximin vector. Corrected ideal witnesses cover the whole game. [Independent audit](cycle2/audit/AUDIT.md) found no gap.

Evidence includes exact raw checks through216 players, independent raw checks with a separate generator,20 exact solver exclusion checks, and finite affine-type certificates covering the all-size payoff witnesses. The conventional proof establishes the theorem; finite samples alone do not establish an infinite family. The new result improves the original nine-player5/18 counterexample and the intermediate11/45 coupled example without claiming either finite example was minimal.

## Completed reductions and blocked routes

| Route | Outcome |
|---|---|
| Strict chain interactions | Sharp1/3 protection and4/3 distance proof; keep as a completed control. |
| One cross-block pair increase | Produced exact11/45 loss and the transfer inequality that led to the new family. |
| Matched-team cloning | Full core, both selectors and all ideal fractions are preserved; distance can be concentrated on one optimal matched team. Thus d_pair equals the supremum of those local team ratios. Classical equal-treatment precedent is credited. |
| Search existing records for local distance>4/3 | No certified witness found; bounded non-finding only. |
| Shrink the small matched-team surplus delta | For internal e coordinates, H_e<=2delta while x_e>=delta/3 for0<delta<=3, giving ratio>=1/6. At delta0 the ideal is zero. This route cannot establish vanishing protection. |
| Close the transfer path into a ring | Designated e ideals fall to1 and leximin payoffs are1/3. This specific closure restores their ratio1/3. |
| Direct bilateral factorization | A precise negative-cycle obstruction explains why it can fail. Incompatibility alone does not prove unfairness. |

The small-team obstruction concerns only internal e coordinates and the specified parameter range; endpoint and other-coordinate conclusions must not be inferred. See the [cycle2 report](cycle2/README.md), [delta audit](cycle2/audit/DELTA_REFINEMENT_AUDIT.md), and [ring argument](cycle2/RING_NO_GO.md).

## Next research decision

A universal1/6 lower bound is now a concrete conjecture to challenge, not an assumed answer. The next bounded cycle should pursue either:

1. A whole-class payoff certificate proving a positive uniform bound, ideally1/6, using the pair-additive structure and accounting for cycles; or
2. A genuinely different coupling that beats1/6 while retaining a full ideal witness and an iterable all-triple proof.

Continue only for a new structural lemma, a reusable verified construction mechanism, or a substantive reduction. Repeating this path, scaling its already analyzed small-team parameter for the same internal coordinates, closing it into the analyzed ring, or collecting more isolated constant improvements does not answer the original question. The separate distance target can use the local-team reduction; no new distance bound was proved this cycle.

## Source, review and app state

The [first source gate](literature/SOURCE_GATE.md), [chain-method comparison](literature/NOVELTY_CHAIN.md), and [new bounded follow-up](cycle2/SOURCE_CHECK.md) distinguish classical ingredients from candidate consequences. Original Quint/Stuart/Lucas and newer extreme-core coverage remains incomplete. No theorem here receives a global priority certificate.

External specialist review of the three earlier papers remains pending. The app tracker still holds that earlier blocked goal because it rejected replacement with an unfinished goal. The user's explicit instruction authorizes the research recorded here; the old review has not been marked complete. The first-cycle status is preserved in STATUS_CYCLE1.md.
