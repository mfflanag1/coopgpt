# Hostile external review — six-player equality exchange classification

Review the repository branch and commit supplied with this packet.  The target
is the new table-free computer-assisted claim in
`paper5/EQUALITY_EXCHANGE_CLASSIFICATION.md`:

> For every singleton-normalized exact game on six players, if
> `||Lmin-Lmax||_1=2/3`, then the payoff pair is, up to permutation, exactly
> the displayed starved or positive pair.

Take an adversarial stance.  The author does **not** claim a hand proof,
external validation, novelty, or a field-level breakthrough.  The older
3,348-row equality census is no longer intended as a proof dependency; check
whether the new reduction really justifies removing it.

## Read first

```text
coopgames/paper5/EQUALITY_EXCHANGE_CLASSIFICATION.md
coopgames/verifiers/s6/audit_equality_universal_exchange_relaxation.py
coopgames/verifiers/s6/minimize_equality_exchange_directions.py
coopgames/verifiers/s6/equality_exchange_direction_cores.json
coopgames/verifiers/s6/export_equality_exchange_classification_smt.py
coopgames/verifiers/s6/verify_equality_exchange_classification_certificates.py
coopgames/verifiers/s6/reproduce_equality_exchange_classification.py
coopgames/verifiers/s6/certificates/equality_exchange_*.{smt2,cpc,json}
```

For context on how this changes the larger proof program, then read:

```text
coopgames/paper5/S6_EQUALITY_CLASSIFICATION.md
coopgames/paper5/STARVED_EXACTNESS_EXCHANGE_HANDOVER.md
coopgames/paper5/FIXED_N_UPPER_BOUND_PROGRAM.md
```

## Priority audit questions

1. **Selection anchors.** Independently prove or refute all three claims:
   Lmax has at least two top players; some Lmax-top player has
   `Lmin_i>=Lmax_i`; and some Lmin-bottom player has
   `Lmax_i<=Lmin_i`.  Check the short convex-segment arguments, including
   tied strata and singleton normalization.
2. **Exactness blocker lemma.** For an efficiency-preserving direction which
   satisfies the encoded sufficient lex-improvement predicate, verify that
   selection optimality forces a negative tight coalition, and that exactness
   converts it into the displayed inequalities against the opposite selection
   and all six singleton-zero witnesses.  Check inequality directions and all
   quantifiers.
3. **Lex predicates.** Hostilely test `lex_improves` for both Lmin and Lmax,
   especially ties, zero coefficients, coefficient two, and directions which
   affect several strata.  Only sufficiency is claimed; find any false
   positive.
4. **Sign split.** Verify that the fifteen `(p,m,e)` cases are exhaustive up
   to a common player permutation, and that
   `||x-z||_1=2 sum_{i in P}(x_i-z_i)` is encoded correctly.
5. **Canonical alternatives.** Check every coordinate and multiplicity in
   `canonical_equality_formula`, including which players can be rich after the
   sign-preserving relabeling.  Confirm that the `p3_n3_t0` and `p4_n2_t0`
   formulas prove rigidity rather than accidentally excluding the canonical
   profile itself.
6. **Formula minimization.** Check that the last `2*direction_count`
   assertions extracted by `minimize_equality_exchange_directions.py` are
   exactly the min/max directional implications, that each retained menu is
   rebuilt without assumption literals, and that the exporter reconstructs
   exactly that formula.  Treat UNSAT cores only as navigation aids.
7. **Independent proof objects.** Run
   `reproduce_equality_exchange_classification.py`; inspect strict SMT-LIB
   parsing, Z3/cvc5 agreement, cvc5's `--no-proof-allow-trust`, forbidden
   marker scan, CPC signatures, Ethos result, and formula/proof hashes.  Report
   any sense in which the CPC checks are not independent of the Python model.
8. **Theorem boundary.** Decide whether these ingredients prove the stated
   equality classification for arbitrary exact games, or only a relaxation,
   normal form, or finite sample.  Identify every implicit assumption.
9. **Larger-program consequence.** Check the narrower claim that this removes
   the 3,348 equality-type exclusions as a dependency.  Separately assess
   whether the first-crossing and contiguous-refinement bridge is sufficient
   to combine this theorem with the two local handover results; do not credit
   the global `s(6)=2/3` theorem unless you have audited that bridge.

## Negative control

`audit_equality_unlabeled_exchange_theorem.py` attempted a single unlabeled
formula and returned `unknown` on both branches at a 300-second timeout per
branch.  No theorem claim rests on this.  Confirm that the documentation does
not treat timeout, UNSAT-core membership, or cross-solver agreement alone as
proof evidence.

## Deliverable

Return separate verdicts—`verified`, `verified with qualifications`, or `not
verified`—for:

1. the three selection anchors;
2. the exactness blocker lemma;
3. the Lmin/Lmax lex-improvement predicates;
4. the fifteen-case and canonical-profile encoding;
5. the minimized-formula reconstruction;
6. the CPC/Ethos proof controls;
7. the equality-classification theorem as stated;
8. removal of the 3,348-row census dependency; and
9. the claimed remaining first-crossing gap.

Classify each issue as fatal, repairable, or expository.  Cite exact file and
line numbers.  If you find a countermodel, give exact rational coordinates
and identify whether it violates an intended theorem premise or exposes a
missing one.  End with a calibrated assessment of mathematical significance,
explicitly separating (a) the equality theorem, (b) the still-unreviewed
six-player upper-bound route, and (c) any novelty judgment.
