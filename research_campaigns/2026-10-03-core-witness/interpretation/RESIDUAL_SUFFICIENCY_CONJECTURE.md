# Bounded hypothesis: residual-propagation sufficiency

Frozen before either reserved support is optimized. This is a CONJECTURE about an upper relaxation, not a theorem, actual-market construction, or novelty claim. Its possible failure does not refute the sharp one-third conjecture.

For every m>=1 and player-disjoint partial matching P, normalize nonnegative pair weights on diagonal/P support to diagonal totalT=1. Require an actual original core vector x>=0 of total1, covering every full triple. Let h be a vector satisfying exactly the necessary conditions in src/relaxation.py: nonnegativity and diagonal caps; h>=x; unmatched residual caps; all repeated-label completion differences; same-sector incident-diagonal range bounds; six whole-P-team-induced differences per P-team. Add for every unmatched player i the residual propagation inequality

    k h_i <= 1-w(P)+(k-1)u_i,   k=m-|P|.

For k>=1 these constraints are satisfied by the true original-core ideals, by the conventional proof in RESIDUAL_PROPAGATION.md. For k=0 no unmatched objective remains.

**Candidate implication:** every such vector satisfies

    w(P)+sum_(i unmatched) h_i/3-1 <= 1/3.

If proved for all sizes this would imply the sharp original bound through the existing reductions. It is stronger than the actual-market target, since h need not be attainable. The new scientific obligation is this all-size implication; neither the old RP inequality by itself nor below-threshold finite numerical results establish it.

## Frozen next test and stopping conditions

Use CW-05 and CW-06 from the already-hashed six-support registry, in that order. On each, run one initial full-witness solve and one initial old-relaxation solve, as prescribed by the campaign, plus one initial RP-enriched diagnostic solve. No support edits, new random patterns, or extra weight assumptions. Max30minutes per solve; recovery30minutes; total existing phase cap8hours and at most2retries continue to apply. Run sequentially.

- An exactly checked RP-feasible vector above1/3 refutes this relaxation-sufficiency conjecture. Stop expanding this relaxation; identify the missing actual-witness relation. It is not an actual subsidy counterexample.
- An actual full-witness point above1/3 stops exploratory branching for independent disproof verification.
- Otherwise record bounded evidence only; at most one bounded analytic aggregation attempt may follow before the hour20 continuation gate. It must produce a real all-parameter implication or an exact obstruction. More supports are not authorized.

CW01/CW04 enriched searches returned feasible211/714 and5167/19782. Their numerical optima were below1/3, but no exact dual for the enriched relaxation was produced; they are discovery motivation only. Classical residual/deletion bounds and graph/path tools are established ingredients.
