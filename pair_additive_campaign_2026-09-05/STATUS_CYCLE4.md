# Current pair-additive research frontier

Updated September 5, 2026 after the fourth bounded cycle. The new result **disproves one-sixth protection**, including at a positive first leximin level. Conventional proofs and independent exact checks are available; priority and genuine external specialist review remain pending.

## Established bounds

For complete equal-sector strict-triple markets with nonnegative pair matrices, triple values `w_ijk=A_ij+B_ik+C_jk`, positive integral matching worth T, and nonempty full core:

    0 <= c_pair <= 1/9,
    4/3 <= d_pair <= 2.

Here c_pair is the best universal fraction of each player's positive maximum core payoff guaranteed by full ascending leximin; d_pair is the supremum of normalized L1 distance between the opposing full sorted selectors. No positive universal lower bound is proved. The value 1/9 is not claimed sharp. The distance frontier is unchanged.

The sharp strict-chain constants remain c_chain=1/3 and d_chain=4/3. Their partial-slack method is classical; application-specific priority remains unresolved.

## Main result: a 21-player one-ninth example

The [fourth cycle](cycle4/README.md) constructs a market with seven players per sector, 16 nonzero pair entries in {1,2,3}, and total worth 15. A target player a_3 satisfies

    first global floor = 1/3,
    full leximin payoff x_(a_3) = 1/3,
    maximum whole-core payoff H_(a_3) = 3,
    x_(a_3)/H_(a_3) = 1/9.

The [short proof](cycle4/root/ONE_NINTH_COUNTEREXAMPLE.md) subtracts six triple inequalities from seven matching equalities, with multiplicity three on one matching team. It yields

    a_3 + a_4 + a_6 + 3 b_0 + c_0 + c_1 + c_6 <= 3.

The coefficient mass is 9. An explicit whole-core floor witness attains 1/3, so every coordinate in this budget is pinned at 1/3 throughout the entire first optimal face. The target's matched-team equality caps its ideal at 3, attained by a second whole-core witness. This identifies the target under full leximin without claiming that the entire floor witness is the final selector.

The canonical construction passes 686 rational triple-cover checks, an independent explicit coefficient reconstruction, and three independent raw-core UNSAT exclusions. The original 63-player discovery and its separate exact audits are preserved. There is no assertion that deletion preserves the original whole core, all ideals, or all selector coordinates.

## Why this cycle progressed

The two fixed-weight 63-player compositions from cycle3 remain correctly certified at minimum ratio 2/9. This cycle instead freed their 65 positive pair positions while retaining a known first-floor budget, matching structure, and complete triple constraints on two payoff witnesses. The first of six planned inverse LPs attained the budget's ideal ceiling 9 at floor 1; the other five were not run. A deterministic seven-team restriction and rescaling gave the 21-player example.

The [inverse formulation](cycle4/root/INVERSE_CERTIFICATE_DESIGN.md) uses classical linear programming. It explores a continuous weight cone that the previous fixed-input no-go did not exclude. Its exact witnesses, not floating optimization status, establish the counterexample.

## Structural lemmas and preserved no-go ledger

- The [residual partial-matching dual](cycle4/theory/RESIDUAL_PARTIAL_MATCHING.md) is valid: an optimal dual with positive target deficit d_i gives `H_i <= tau sum(d)/d_i`. The proposed universal six-deficit certificate is false. The new example has an explicit ratio-nine certificate, and its attained ideal forces every such target certificate to have ratio at least nine.
- The [zero-face projection](cycle4/zero_face/ZERO_FACE_REDUCTION.md) is exact only after retaining induced productive singleton and pair constraints. A 12-player pair-additive example rules out a universal replacement by a strict three-player market with the same surviving core, ideals, and selectors.
- The earlier finite 27-player one-sixth example and the all-q family with ratios `1/6+1/(2q)` remain valid. They are superseded as class-wide upper bounds, not retracted as constructions.
- The proposed within-sector bridge `R_i<=3x_i` remains false. The sector-minimum identities are valid. The sharp 3/2 cover-splitting factor need not preserve efficiency or leximin, and its proposed fairness transfer remains false.
- The faithful completion obstruction for the old unrestricted recurrence retains its explicit old-point and clause-preservation hypotheses. Arbitrary new replacement gadgets remain outside that no-go.
- The small-team delta modification, specific ring closure, and matched-team cloning results retain their prior scopes. Do not extrapolate them to every change of weights, endpoint, ring, or composition.

The [cycle3 status](STATUS_CYCLE3.md) preserves the previous frontier and its hypotheses; the older cycle1 and cycle2 status files are also retained.

## Next decision

This bounded goal is resolved by disproof. The useful next target is to determine whether the exact nine-unit mechanism admits an iterable construction with ratios tending to zero, or whether a structural theorem forces a size-independent positive lower bound. A parameterized construction must control every induced mixed triple, integral matching worth, a positive first-floor face, and true ideal attainment. Larger certificate coefficients alone are not a construction.

Do not replace the disproved one-sixth conjecture with an unsupported one-ninth conjecture. Further work should deliver a reusable recurrence, a substantive structural lemma, or an exact scoped obstruction. The opposing-selector distance problem stays secondary.

## Sources and app state

The [fourth-cycle primary-source check](cycle4/theory/SOURCE_CHECK.md) distinguishes bipartite sorted selectors, generalized cycle-free composition, and strict cyclic triples. The bounded search found no directly matching result, but original-source gaps remain. This is an internally verified counterexample to this campaign's conjecture, not a claim to have settled a previously published open problem. Global novelty and field-level significance are unestablished.

The app still holds the older blocked external-review goal. The user's explicit request authorized this research, and its [contract](cycle4/CAMPAIGN.md) is recorded in the workspace. The tracker was not switched, the old review was not marked complete, and no outreach was sent.
