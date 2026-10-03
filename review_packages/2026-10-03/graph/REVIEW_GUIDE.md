# Graph paper: request for specialist assessment

Prepared 3 October 2026. Author: Maxwell Flanagan. Manuscript version: 20 September 2026, 10 pages; unchanged mathematical source/PDF. No message has been sent by this task and no specialist has agreed to review it.

## Read first

Please read manuscript.pdf. The source and exact checks are in verification_and_source.zip; they are optional for the initial assessment.

## Exact statement and qualifications

Fix a connected simple allowed graph G with K>=2 sectors, equal finite sector sizes, nonnegative pair values (zeros allowed), productive full K-teams only, integral coalition matching worth, positive grand worth, and nonempty entire original core. Let H_i be player i's maximum over that core, x its full nominal leximin allocation, and rho=max_{p in C} min_{i:H_i>0} p_i/H_i, where C is the entire original core. Define c(G) as the infimum, over admissible markets on G, of the minimum positive-ideal ratio for x; define R(G) as the infimum of rho over those markets. The manuscript claims c(G)=R(G)=1/K on trees and zero on cyclic allowed graphs. For its explicit triangle family indexed by integer q>=1, it claims rho=1/(2q+3). The K=2 half-optimal guarantee is an established bilateral result.

Zero is an infimum over growing finite markets, not an assertion that a finite market has rho=0. On cyclic graphs the poorly protected player can vary with the allocation. On trees the positive guarantee concerns the leximin allocation and optimal simultaneous protection, not every core point. Zero matrices on allowed chords are permitted. Productive partial-sector coalitions, unequal sector sizes, and strictly positive matrices throughout are outside the theorem.

## Requested assessment

1. Priority: Is the exact strict-full-team protection classification already stated or implied in the multisided/half-optimal-core literature? A specific theorem or counterexample to the novelty claim would be especially helpful.
2. Model: Does our separation from productive partial-sector coalition models correctly account for Atay-Nunez and older Quint/Lucas/Stuart models?
3. Correctness: Is there a gap in the whole-core tree representation/clipping, triangular simplex, or cyclic transfer?
4. Significance: Does the optimal-allocation impossibility add enough beyond known fairness failures for a standalone paper? What narrower presentation would be appropriate otherwise?

An initial pointer or objection is useful; a full report is not expected without agreement. We are not asking for an endorsement or a guarantee of novelty.

## Proof map

- Section 2, pp. 2-3: frozen model, c(G), rho, R(G), and Theorem 2.1.
- Section 3, pp. 3-4: Lemma 3.1 entire-core cut representation; Lemma 3.2 clipping; same fixed leximin allocation protects every target.
- Section 4, pp. 4-6: original triangle family, complete cover checks and unit unmatched-player budget.
- Section 5, pp. 6-7: entire-core simplex, separate attainment of all ideals, exact best fraction.
- Section 6, pp. 8-9: selective subdivision, ideal-witness lift and zero-edge embedding into arbitrary cyclic allowed graphs.
- Section 7, p. 9: evidence, model and contribution boundaries.

## Attribution and evidence

Bilateral half-optimal cores, tree/cycle structure in other multisided models, leximin, LP duality, matching tightness and difference constraints are established ingredients. The proposed contribution is the precise protection theorem in the frozen model, not those tools. SOURCE_BOUNDARIES.md and ORIGINAL_COMPARISONS.md record the comparisons and the remaining original-source gaps for Quint, Lucas and Stuart. No global priority clearance is asserted.

The manuscript was developed with AI assistance. Scoped model reviews and exact finite checks are documented; they are not independent human review or proof-assistant certification. The October 3 full build and all three finite verification stages passed, including the optional SMT checks; VALIDATION.json records the scope and file hashes. The universal claims rely on the written conventional proofs.
