# Hostile external review — direct six-player exactness-exchange bound

Review the repository branch and commit supplied with this packet.  The target
claim is:

```text
s(6)=2/3
```

for singleton-normalized exact TU games, proved by a direct table-free
exactness-exchange argument.  Take an adversarial stance.  This result has not
been externally validated, and no claim of field-level novelty should be
accepted without an independent literature search.

## Read first

```text
coopgames/paper5/S6_DIRECT_EXCHANGE_BOUND.md
coopgames/verifiers/s6/audit_equality_universal_exchange_relaxation.py
coopgames/verifiers/s6/minimize_equality_exchange_directions.py
coopgames/verifiers/s6/strict_exchange_direction_cores.json
coopgames/verifiers/s6/strict_exchange_sign_orbits.json
coopgames/verifiers/s6/export_strict_exchange_bound_smt.py
coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
coopgames/verifiers/s6/verify_strict_exchange_bound_certificates.py
coopgames/verifiers/s6/certificates/strict_exchange_*.{smt2,cpc,json}
```

The equality theorem is a useful differential check but is not a dependency:

```text
coopgames/paper5/EQUALITY_EXCHANGE_CLASSIFICATION.md
coopgames/verifiers/s6/certificates/equality_exchange_*.{smt2,cpc,json}
```

## Load-bearing mathematical questions

1. **Normalization and signs.** Check scaling to `v(N)=1`, nonnegativity of
   core allocations after singleton normalization, the fifteen exhaustive
   triples `(p,m,e)`, and
   `||x-z||_1=2 sum_{x_i>z_i}(x_i-z_i)`.
2. **Three anchors.** Independently prove or refute: Lmax cannot have a unique
   top player; some Lmax-top player has `Lmin_i>=Lmax_i`; some Lmin-bottom
   player has `Lmax_i<=Lmin_i`.  Audit the short convex-segment proofs at tied
   strata and boundary coordinates.
3. **Lex-improvement predicates.** For both sides, prove that every direction
   accepted by `lex_improves` genuinely improves the sorted lexicographic
   objective for a sufficiently short positive step.  Test ties, zeros,
   multiple affected strata, and coefficients `-2` or `2`.  A single false
   positive is fatal.  Audit, but do not merely trust, the 15,079,260-case
   differential truth table in `lex_improvement_predicate_audit.json`.
4. **Negative-tight-blocker lemma.** Prove that if an efficiency-preserving
   improving direction has no negative tight proper coalition, a short step
   remains in the core.  Include singleton nonnegativity constraints and the
   grand-coalition equality.
5. **Use of exactness.** Verify that singleton exactness supplies six core
   points `q^i` with `q^i_i=0`, and that a coalition tight at one selection
   satisfies the encoded comparisons against the opposite selection and all
   witnesses.  Check every inequality direction.
6. **Relaxation logic.** Confirm that the SMT formulas need not encode a
   common game or actual tightness: every real counterexample maps into the
   relaxation, so UNSAT is sound.  Look specifically for any omitted premise
   needed by that map.
7. **Direction pools.** Verify that `direction_pool(1)` and
   `direction_pool(2)` contain exactly the asserted efficiency-preserving
   integer directions, that only the two named cases use bound two, and that
   no sign case is silently skipped.
8. **Minimization and export.** Check assertion ordering, the extraction of
   the last `2*direction_count` blocker implications, assumption-literal core
   handling, unguarded rebuild, JSON menu serialization, and exact SMT-LIB
   regeneration.  UNSAT cores are navigation aids only.
9. **Independent proofs.** Run `reproduce_strict_exchange_bound.py` and audit
   Z3/cvc5 agreement, strict parsing, proof pedantry, trust disabling,
   forbidden-marker scan, CPC signatures, Ethos output, and hashes.  State
   precisely what the proof objects do and do not independently certify.
10. **Lower bound.** Independently recheck exactness and the displayed Lmin,
    Lmax, and ratio of `G(2,3)`; do not infer `s(6)=2/3` from the upper suite
    alone.
    `coopgames/verifiers/s6/verify_g23_witness.py` is a targeted repository
    regression; treat it as an audit aid and independently inspect the family
    proof in the manuscript.

## Independence and scope checks

The direct theorem claims not to depend on any of the following:

```text
generator normal form
37,277 support/table universe
3,348 equality exclusions
selection continuity or first crossing
positive/starved local refinement handovers
```

Check that none is imported implicitly through a helper function, artifact,
or premise.  Conversely, report if the direct proof only applies to a
restricted subclass of exact games.

## Deliverable

Return `verified`, `verified with qualifications`, or `not verified` for:

1. normalization/sign split;
2. selection anchors;
3. both lex predicates;
4. negative-tight-blocker lemma;
5. exactness-witness reduction;
6. complete counterexample-to-SMT mapping;
7. minimized formula reconstruction;
8. CPC/Ethos proof controls;
9. the upper bound `s(6)<=2/3`;
10. the lower bound and equality `s(6)=2/3`;
11. claimed independence from the older programs; and
12. novelty and mathematical significance.

Classify every issue as fatal, repairable, or expository and cite exact file
and line numbers.  If possible, independently encode at least the two bound-two
cases rather than reusing the Python formulas.  End with a calibrated answer
to three separate questions: is the theorem correct, is it new, and how large
a contribution is it if both answers are yes?
