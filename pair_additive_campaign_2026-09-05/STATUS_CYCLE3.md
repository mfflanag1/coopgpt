# Current pair-additive research frontier

Updated September5,2026 after the third bounded cycle. The user authorized the one-sixth investigation. Conventional proofs and independent exact checks are available; external specialist review and priority remain pending.

## Established bounds

For complete equal-sector strict-triple markets w_ijk=A_ij+B_ik+C_jk with nonnegative pair matrices, positive integral matching value T, and nonempty full core:

    0 <= c_pair <=1/6,
    4/3 <= d_pair <=2.

Here c_pair is the best universal fraction of each player's maximum core payoff guaranteed by full leximin; d_pair is the supremum of normalized L1 distance between the two opposing full sorted selectors. The universal lower bound c_pair>=1/6 is NOT established.

The sharp strict-chain constants remain c_chain=1/3 and d_chain=4/3. Their method applies classical partial slack balancing; application-specific priority is unresolved.

## Main new result: finite one-sixth attainment

The [third cycle](cycle3/README.md) constructs a27-player nonnegative pair-additive market with T=24 and a designated player b_1 satisfying

    x_(b_1)=1/3, H_(b_1)=2, x_(b_1)/H_(b_1)=1/6.

The [short proof](cycle3/root/FINITE_ATTAINMENT.md) uses a six-coordinate budget and a first-optimal-face argument. An independent standard-library verifier regenerates the pair matrices and checks1,458 rational triple covers plus the ideal certificate. A separate raw audit verifies all stages of both saved selectors and the designated ideal using19 exact exclusion checks. The full-selector distance of this example is5/9; it improves no class-wide distance bound. No claim of minimum market size is made.

The cycle2 all-q family remains valid:9q players, T=8q, designated ratio1/6+1/(2q). Finite attainment sharpens the type of upper-bound witness without proving the conjectured matching lower bound.

## Third-cycle proof state

| Route | Verified outcome and scope |
|---|---|
|401 structured three-block cells|Completed numerical discovery screen; none observed below1/6. The nominated finite example was subsequently certified exactly. No exhaustive class-wide theorem follows.|
|Two explicit seven-block nested compositions|Both63-player markets have exact minimum ratio2/9, first floor2/9, and central-target ratio4/9. Each complete leximin/all-ideal computation has127 rational dual certificates and592,704 raw triple checks. This particular nesting does not amplify1/6.|
|Within-sector spread R_i|Elementary identities H_i=max_P[p_i-min_sector p+sum_sector minima] and H_i<=R_i+3tau are valid. The proposed R_i<=3x_i bridge is FALSE: the finite example has R=2,x=1/3.|
|Approximate bilateral factorization|Every feasible nonnegative triple cover p can be split after scaling by3/2 into signed bilateral cover components; the factor is sharp. It need not preserve efficiency, nonnegative components, or leximin. The tempting2/9 fairness inference is false.|
|Faithful completion of the old unrestricted recurrence|A six-player pair-additive cube identity blocks preservation of two old core points and two specified positive clauses for every depth>=2. Auxiliary extensions are excluded only under those preservation hypotheses. General replacement gadgets remain outside the no-go.|
|Ideal/floor LP certificates|Exact duals retained, including signed frozen-coordinate multipliers. Short ideal certificates can need triples slack at x; rescaling a long-path floor dual can lose size independence.|

## Preserved earlier no-go ledger

The analyzed small-team delta modification cannot lower internal designated fractions below1/6; at delta0 those ideals are zero. Closing the specific cycle2 path into a ring restores its designated1/3 ratio. Matched-team cloning preserves individual fractions and gives the separate local-team reduction for distance. Exact bilateral factorization can fail through negative cycles. The [preserved cycle2 status](STATUS_CYCLE2.md) and [cycle2 proof package](cycle2/README.md) retain their exact hypotheses; do not extrapolate these obstructions to every endpoint, ring, or alternative coupling.

## Next decision

The original all-class question remains live: establish a size-independent positive ideal bound, ideally1/6, or construct an exact below1/6 mechanism. The finite extremizer now supplies a small concrete test for any proposed lemma. A valid proof must allow non-tight ideal inequalities and survive both its six-coordinate budget and the old long-path examples.

The third pilot is complete. Continue only for a new structural lemma, exact counterexample or substantive reduction. Do not revive R_i<=3x_i, infer fairness from the3/2 cover split, repeat the two certified nested inputs, or treat clean numerical cells as a universal bound. The selector-distance problem remains secondary and unresolved.

## Sources and app state

The [cycle3 source check](cycle3/SOURCE_CHECK.md) distinguishes fixed-player-order lexicographic procedures from full sorted leximin and retains the strict/generalized core-composition boundary. Original-source gaps and the specialist priority review remain open; no global novelty or field-level breakthrough claim follows.

The app still holds the earlier blocked external-review goal and rejected a new goal because that one is unfinished. The user's explicit instruction authorized the research documented here; the old review was not marked complete. The [new contract](cycle3/CAMPAIGN.md) records the one-sixth objective in the workspace. Earlier status documents are preserved as STATUS_CYCLE1.md and STATUS_CYCLE2.md.
