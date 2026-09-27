# Cycle3: finite attainment of one-sixth

The authorized [one-sixth investigation](CAMPAIGN.md) has produced an exact27-player pair-additive market with a full leximin coordinate1/3 and true core ideal2. It attains the ratio1/6 at finite size; the previous path family only approached that value. The universal one-sixth lower bound remains unresolved.

## Accepted main result

Read the short [conventional proof](root/FINITE_ATTAINMENT.md). A matching of value24 and two independently constructed whole-core vectors certify nonemptiness and the ideal. A six-coordinate budget fixes the target in the FIRST optimal leximin face, so the full selector is addressed even without computing its later stages.

- [Root exact verifier](root/verify_finite_attainment.py): independent construction,1,458 raw rational triple checks, ideal row identity.
- [Independent full-selector audit](independent/FINITE_ATTAINMENT_AUDIT.md):2,187 raw rational triple covers, all stages of both saved selectors, and target-ideal bound through19 exact exclusion checks. Other listed ideals are not part of that independent audit.
- [Discovery data](experiment/finite_attainment_exact.json): matrices, matching, complete selectors, target ideal witness and solver-computed ideals. The separately audited normalized selector distance is5/9; it does not improve the known class-wide distance frontier.

## Proof routes and obstructions

The [certificate report](theory/CERTIFICATE_GATE.md) states exact LP duals and proves a sharp3/2 factorization of feasible triple covers into signed bilateral cover components after increasing total payoff. It does not preserve efficiency or leximin and yields no fairness bound by itself.

The elementary [sector-shift reduction](root/SECTOR_SPREAD.md) is valid, but its proposed stronger within-sector bound R_i<=3x_i is FALSE. The finite example has R_i=2 and x_i=1/3. Its first142 clean archived numerical diagnostics therefore supplied no universal evidence.

The [six-player cube obstruction](independent/EMBEDDING_NO_GO.md) blocks faithful completion of the old unrestricted recurrence while preserving two old core points and two productive clauses. It covers auxiliary extensions only under those explicit hypotheses; it does not exclude arbitrary replacement gadgets or all pair-additive amplifiers.

The root's [audit](root/AUDIT.md) distinguishes accepted claims and remaining obligations. The [source check](SOURCE_CHECK.md) preserves classical-method attribution and unresolved priority gaps. No result has external specialist endorsement or a global novelty certificate.

Two specified63-player compositions were checked exactly: both have minimum ratio2/9, so this direct nesting does not amplify the finite1/6 loss. Each has complete leximin and all63 ideals certified by127 rational dual identities and592,704 raw triple checks. The intended central target has ratio4/9. See [experiment report](experiment/EXPERIMENT.md) and [certificate verifier](experiment/verify_composition.py); this conclusion is restricted to those two inputs.

## Reproduce

The main target proof, signed factorization controls, and both complete composition certificates use only the standard library:

```sh
bash build.sh
```

For the additional independent raw solver checks, use Python with z3-solver5.1.0.0:

```sh
COOPGT_PYTHON=/path/to/python bash build.sh --full
```

The discovery scripts additionally use NumPy2.5.2 and SciPy1.18.1, as recorded in provenance. The401-cell initial search is a bounded numerical discovery screen, not an exhaustive theorem about all weights or market sizes. Its manifest and complete records are retained. The new finite mechanism justified one additional two-orientation composition test; see the experiment report for its exact evidence tier and outcome.

## Status

The bounded pilot produced a verified construction and explicit failed-proof mechanisms. The original all-class goal is still open. Continue only for a new structural mechanism, proof lemma or exact violation below1/6; do not repeat the rejected spread bridge or infer fairness from the3/2 cover split.

The app tracker rejected replacement of the earlier unfinished external-review goal. This campaign was authorized and executed in the workspace; that previous goal has not been falsely marked complete.
