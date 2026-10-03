**Provisional verdict: findings.** The LP formulation and the counterexample/upper-certificate logic hold on the supplied text, but the registry exclusion rule would let already-examined supports count as new, and two gates are too loose.

## Findings

**1. Medium — GOAL.md:33, registry exclusion.**
- Evidence: only isomorphs of "all-coefficient-certified supports and proven safe classes" are excluded. The 34 CYCLIC_FRONTIER records and the IDEAL_DIFFERENCE example are labelled provenance but never excluded, and no equivalence relation is defined.
- Correction: exclude isomorphs of every previously examined support. Define isomorphism on the sector-coloured label/P-team incidence multigraph, under simultaneous label relabelling and sector permutation, keeping repeated incidences (REDUCTIONS.md:52).
- Verification: canonical-form the 34 records and confirm each is rejected by the registry filter.

**2. Medium — GOAL.md:43, hour-20 gate.**
- Evidence: "at least one explicit new constraint/certificate" is met by any fixed-support LP dual, which Phase 2 produces automatically.
- Correction: require a dual stated parametrically, with hypotheses, that is valid on at least one held-out support or separates a named relaxation point.

**3. Medium — GOAL.md:29–35 and 39, feasibility.**
- Evidence: Phase 2 worst case is 12 supports × 2 attempts × 60 minutes = 24 hours against a 12-hour phase, before the paired relaxation solves. Phase 1 packs five reproductions, an LP, an independent checker, controls and a canonicalised registry into 8 hours.
- Correction: fix a priority order and a total compute cap, or cut the registry to about 6. State whether solver wall-clock counts as active hours.

**4. Low–Medium — GOAL.md:25, counterexample acceptance.**
- The logic is sound: h_i ≤ H_i and weak duality give s ≥ J(M,P) > T/3.
- Correction: separate the two tiers. The lower-bound claim needs only nonnegative weights, a matching P, total-one covers and a value-one diagonal; exact ideals and the subsidy dual are needed only for exact s.
- Add a tripwire: any J > 39999/100000 contradicts the stated bound and must be treated as a bug until resolved.

**5. Low — GOAL.md:47, 51, 55, upper-certificate wording.**
- Evidence: line 55 says "reconstruct any … new upper bound from raw pair matrices"; a universal bound cannot be reconstructed from matrices.
- Correction: phrase any "bounded support theorem" as a bound on J(M,P) for that labelled (m,P), not on s or S3. A support-class lemma does not change 39999/100000.

**6. Low — GOAL.md:31, negative controls.** Add corruptions of a witness total, a P player-disjointness violation, an off-support nonzero weight and a wrong unmatched set.

**7. Medium — REVIEW_GUIDE.md:11, statement.**
- Evidence: the results are asserted as fact; q and "worst-market constants" (c(G), R(G)) are undefined; the allocation set behind rho is unspecified.
- Correction: write "the manuscript claims", define the terms, and flag that K=2 is the known bilateral half-optimal result.

**8. Low — REVIEW_GUIDE.md:7, 37.** Line 7 mixes sender instructions into a reviewer-facing document. "September 27 and migration replays passed" is unexplained and cannot be checked by the reader. Novelty is otherwise properly hedged (lines 22, 35).

## Checked, no finding

- Full-witness formulation is a single joint LP in weights and witnesses; it is bounded, and independent witnesses give the true ideals (consistent with REDUCTIONS §3–4).
- "All-size suffices, a census does not" is correct.
- 29/82 arithmetic and its diagnostic-only status match AFFINE_REFINEMENT.md.
- No retired route is reused.
- No execution or guaranteed breakthrough is claimed.

## Scope limitations

Nothing was run. STATUS.json, CORE_COMPATIBILITY_UPPER.md, IDEAL_DIFFERENCE_LIMITS.md, the CYCLIC_FRONTIER records and the manuscript were not supplied. The 39999/100000 bound, the 76/303 and 3/8 examples, the forest-support counterexample and the "ideal-difference relaxation" definition are therefore unverified.
