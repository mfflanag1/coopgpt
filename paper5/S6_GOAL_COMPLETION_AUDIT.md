# Completion audit for the sharp six-player program

Date: 2026-08-10

This ledger maps every requested component of the six-player research goal to
current repository evidence.  It distinguishes mathematical proof,
independent proof-object checking, bug audits, and work that still requires
external review.

## 1. Boundary example and missing condition

**Requirement.** Formalize the two-packet obstruction, recompute its complete
staged leximin behavior, and identify the condition lost by retaining only the
two aggregate first-stage certificates.

**Status: complete.** `TWO_PACKET_EXACTIFICATION_BOUNDARY.md` gives the rational
example and the dual incidence identities.  The source and frozen JSON are

```text
coopgames/verifiers/s6/audit_two_packet_exactification.py
coopgames/verifiers/s6/two_packet_exactification_audit.json
coopgames/verifiers/s6/verify_two_packet_staged_certificates.py
```

Two independently formulated exact LP implementations agree.  The audit
records both complete two-stage Lmin/Lmax traces in both games and emits six
per-player certificates per selection per game (24 total).  A separate checker
replays every incidence and objective identity.  The abstract pair has overlap
`1/2`; singleton exactification preserves the sparse aggregate certificates
but unpins player 3 from the alleged first Lmin stratum, and the recomputed
overlap is exactly `2/3`.  The missing condition is therefore full per-player,
per-stage pinning, or an equivalent full Lmin packet.

## 2. Strengthened system and counterexample search

**Requirement.** Incorporate the missing staged information, exhaust the
relevant six-player support types, and actively search for a genuine strict
counterexample.

**Status: complete as an independent, superseded route.** The core-closure
pipeline encodes all per-player Lmin and Lmax stages and uses six
singleton-attaining witnesses.  Its audited universe contains 37,277
stratum/table configurations; hand reductions leave 3,350 support types, and
the strict census returns

```text
0 SAT / 3350 UNSAT / 0 UNKNOWN.
```

The authoritative map and explanation are

```text
coopgames/paper5/S6_GENERATOR_CENSUS_CHECKPOINT.md
coopgames/verifiers/s6/core_closure_pipeline.py
coopgames/verifiers/s6/core_generator_census.json
coopgames/verifiers/s6/merge_core_closure_census.py
```

This census was search and differential evidence, not the final proof: its raw
UNSAT verdicts were not promoted beyond their status.

## 3. Sharp upper bound

**Requirement.** Prove or refute `s(6)=2/3` without relying on archive testing
as proof.

**Status: proved by a direct table-free computer-assisted theorem.** The final
proof does not use the support census, generator normal form, first crossing,
or selection continuity.  It maps every strict counterexample into one of
fifteen exact QF_LRA relaxations indexed only by the sign counts of
`Lmin-Lmax`.  Every formula is UNSAT in Z3 and cvc5; cvc5 emits a
trust-disabled CPC proof and Ethos checks every proof as `correct`.

The human portion consists of normalization, the exhaustive sign split, three
convex-segment selection anchors, the lex-improvement criterion, and the
negative-tight-coalition blocker lemma using six singleton exactness witnesses.
The finite lemma uses 252 retained labeled directions in 64 sign-preserving
orbits.  Its source, frozen formulas, proofs, hashes, and reproduction driver
are listed in `S6_DIRECT_EXCHANGE_BOUND.md`.

This is a rigorous proof-object theorem, not an all-human structural proof.
It is stronger than the goal's finite-obstruction fallback because no support
configuration remains unresolved, but it must continue to be described as
computer-assisted.

The two coefficient-two sign cases now have a separately written
reconstruction that shares only the frozen retained direction menus as theorem
data.  It uses its own variables, lex-improvement predicates, blocker cuts,
anchor encoding, and SMT serialization.  Both base systems are SAT, both full
systems are UNSAT in Z3 and cvc5, and their new trust-disabled CPC proofs check
`correct` in Ethos.  This materially reduces correlated implementation risk;
it does not independently prove the human counterexample-to-formula map.

The 52-, 71-, and 90-direction cases have also been compressed from 213
labeled directions to 44 sign-role orbits and six coefficient archetypes up
to reversal.  This is explanatory progress, not yet a complete hand proof of
those 44 placements.

## 4. Sharpness and equality cases

**Requirement.** Supply the matching lower bound and classify equality if the
upper bound holds.

**Status: complete in proof-object form.** The hand-proved family theorem gives
the exact singleton-normalized game `G(2,3)` with ratio `2/3`; the targeted
exact regression `verify_g23_witness.py` rebuilds its lower envelope and
independently recomputes both selections.

`EQUALITY_EXCHANGE_CLASSIFICATION.md` gives a second fifteen-case table-free
theorem: up to a common player permutation, equality has exactly the starved
or positive payoff pair displayed there.  All fifteen equality formulas have
independent Z3/cvc5 verdicts and trust-disabled CPC proofs checked by Ethos.
The two pairs are independently realized and recomputed from explicit exact
games.  The older 3,348 equality exclusions are not proof dependencies.

## 5. Paper and hostile review

**Requirement.** Produce a self-contained paper section, reproducible exact
artifacts, and a hostile-review packet; do not overstate novelty.

**Status: reviewer packet complete, external review pending.** The theorem and reduction are in
`divergence.tex` and the compiled `divergence.pdf`.  The focused review packet
is `EXTERNAL_REVIEW_S6_DIRECT_BOUND.md`.  It asks reviewers to audit every
load-bearing interface, independently encode the two bound-two cases, verify
the lower witness, and separate correctness, novelty, and significance.

`S6_LITERATURE_NOVELTY_AUDIT.md` records a targeted primary-source search.
No equivalent quantitative fixed-dimensional separation theorem was found,
but this negative result is expressly not treated as proof of novelty.

No claim of external validation or field-level novelty is made.  The branch
must not be merged before that review.  A negative external verdict would
reopen the affected item in this ledger.

## Reproduction commands

Run from the repository root with the repository's Z3-enabled Python where
needed:

```bash
python3 coopgames/verifiers/s6/audit_two_packet_exactification.py \
  --output /tmp/two_packet_current.json
cmp coopgames/verifiers/s6/two_packet_exactification_audit.json \
  /tmp/two_packet_current.json
python3 coopgames/verifiers/s6/verify_two_packet_staged_certificates.py
python3 coopgames/verifiers/s6/audit_lex_improvement_predicate.py
python3 coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
python3 coopgames/verifiers/s6/verify_independent_bound_two.py
python3 coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py \
  --output /tmp/strict_exchange_large_case_templates.json
cmp coopgames/verifiers/s6/strict_exchange_large_case_templates.json \
  /tmp/strict_exchange_large_case_templates.json
python3 coopgames/verifiers/s6/reproduce_equality_exchange_classification.py
python3 coopgames/verifiers/s6/verify_g23_witness.py
```

Passing these commands verifies exact artifact regeneration and stored proof
records.  It does not replace human review of the counterexample-to-formula
mapping or establish literature novelty.
