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

The 52-, 71-, and 90-direction cases were first compressed from 213 labeled
directions to 44 sign-role orbits.  A later unguarded minimization closes them
with 136 directions in an irredundant 8/5/6 split, only 19 sign-role schemas
total and three coefficient archetypes up to reversal.  Z3/cvc5 and checked
CPC proofs certify all three smaller formulas; all 19 single-orbit ablations
are SAT.  These large-case cores need only the two cross-selection anchors,
not the no-unique-Lmax-top anchor.  In `(4,2,0)`, blocker alternatives need
only the opposite-selection comparison and the four `P`-indexed
singleton-witness comparisons; the two `M`-indexed blocker-comparison
families are dispensable, while deleting any of the five retained source
families makes the relaxation SAT.  The base constraints for all six witnesses
remain.  This is substantial explanatory progress, not yet a complete hand
proof of those 19 schemas.

The separately proof-checked anchor-localized `(4,2,0)` alternative goes
further.  A one-line order chain closes the coincident bottom/top-anchor
branch.  In the distinct branch, sign-preserving relabeling leaves an 18-real
formula with one singleton exactness witness, nineteen labelled directions,
and ten residual role orbits.  Z3/cvc5 and a trust-disabled CPC proof checked
by Ethos certify it; every single direction, residual orbit, and either of its
two blocker-comparison sources is irredundant by SAT ablation.  The remaining
ten-orbit incompatibility is still machine-resolved.  A further
forced-blocker decomposition now replaces the two sixteen-way C1 blocker
disjunctions by eleven exact packet classes: 32 of 64 labelled blocker pairs
are base-infeasible, and the 32 feasible pairs form eleven residual-symmetry
orbits.  Each row closes using a subset-minimal menu of at most seven
remaining directions.  This materially improves readability but does not yet
replace every residual blocker alternative by hand inequalities.
Nine packet classes now have exact hand-checkable proof objects.  Class 8, covering two labelled
pairs, uses a single two-for-two direction.  Its activation
and all twenty blocker exclusions use only the opposite-selection comparison;
the audit verifies the reduced inequalities independently of `q^1`.  Class 3
(four labelled pairs) is also closed by hand using a two-exchange blocker
relay.  Its exact two-candidate blocker lists and four terminal contradictions
are independently restated and checked.  Class 4, covering four labelled
pairs, is a three-leaf star: its root classification and child activations are
structural, and twenty exact nonnegative weighted identities close all
terminal cuts.  The certificate checker uses pure rational coefficient
arithmetic, no solver call, and no production encoder.  Class 11, covering
four labelled pairs, is a unique three-exchange chain.  A structural cut split
plus 37 source-specific exact identities proves its two unique blockers and
empty terminal blocker list.  Class 7, covering four labelled pairs, now has
an exact eight-stage difference-cone census plus 25 rational identities.
Class 9, covering four labelled pairs, closes after `x_3<=x_4` versus
`x_3>x_4`; its ten exact cut censuses and 52 distinct identities are checked
at all 71 stage uses by a solver-free rational verifier.  Class 10, covering
two labelled pairs, adds eighteen exact cut censuses and 108 identities
checked at all 122 uses.  Class 1, covering one labelled pair, adds twenty-one
exact censuses and 109 identities checked at all 160 uses.  A minimum-level
lemma reduces its complete activation audit to 75 cases.  Class 2, covering two labelled
pairs, adds 21 exact censuses and 108 identities at 132 uses.  Its shared
minimum/maximum-level lemma reduces activation to 72 cases.  Of the last two
packet classes covering five labelled pairs, class 6 now has complete exact
arithmetic conditional on frozen integration maps, while class 5 remains
machine-resolved.  A
separate forced-exchange audit sharpens that boundary: classes
`1,2,3,4,7,8,9,10,11` now have complete exact relay certificates and together
cover twenty-seven labelled packets.  All nine now have independently
specified hand-checkable proof objects; class 6 has a complete conditional
arithmetic certificate and class 5 remains machine-resolved at the
hand-certificate layer.
A universal order audit eliminates their open leaves: `x_3<=x_4` versus
`x_3>x_4` closes every one of the eleven packet classes, with class 10 the
unique row requiring a nested `x_1`/`x_2` split.  The remaining gap is
completion of class 5, conceptual compression and independent map validation
for class 6, not unknown finite anatomy.
There is now a first solver-free class-5 compression: the symmetric packet
sandwich and cross-anchor chain replace all ten `h15` activation checks by one
lemma and reduce each of its sixteen-cut blocker censuses to the same ten
packet-level candidates.  This is a verified partial skeleton, not a tenth
complete hand-checkable packet row.  Three exact crossing identities also
exclude seven of the thirty formal `h10`/`h15` blocker pairs in only three
orbits.  The weak and strict roots also have complete hand classifications:
twenty cuts reduce respectively to three and four blockers, using only one
seven-term witness identity beyond the packet/sign arguments.  The 51 relay
leaves remain to be compressed.
Class 6 now has complete solver-free arithmetic conditional on its frozen
relay/use maps.  Its stronger sandwich reduces both twenty-cut roots to two
blockers apiece without a witness identity.  Across 49 nodes, exact
Fourier--Motzkin elimination partitions 924 eligible cut uses into 711 pure
difference exclusions and 213 candidates.  Eleven candidates are excluded by
the existing packet/ancestor witness context, 155 by the target `q^1`
witness, and 47 are exactly the relay branches.  The eleven context exclusions
have nine exact rational identities.  The 155 target-witness rejections have
incidence over-covers of support
at most five; 150 use unit coefficients and five use a coefficient two.  The
incidence bounds are human consequences of the general theorem, but their
allocation-side strict lower bounds are now 53 deduplicated exact rational
identities checked solver-free at all 155 uses.  The digest-protected use map
still comes from the shared localized relay, but a separate exact census
checks that the 11, 155, and 47 uses exhaust all 213 candidates and hence every
terminal closure.  No cut arithmetic remains machine-only.
The same incidence theorem now compresses activation: of 124 elementary
failure cases, 84 are structural, four are allocation-infeasible, and the
other 36 have over-covers of support at most four.  Their allocation-side
strict reductions are now 26 solver-free rational identities, while the four
direct cases share one more identity.  No activation arithmetic remains
machine-only.  Coverage remains relay-derived, so independent validation of
the map is still required before calling this an externally reviewed hand
certificate.
The single-witness component now has a general exact-cone theorem rather than
case-specific Farkas sums.  For any blocker menu, its coalition-sum image is
the convex hull of the non-anchor incidence columns; feasibility of lower
requirements is characterized by all nonnegative support inequalities.  The
result supplies a sparse LP/facet algorithm and explains the class-5 crossing
identities as incidence over-covers.  It is elementary convex duality, not a
novelty claim or a completion of the remaining opposite-comparison work.

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

`S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md` now proves the human-to-machine map
assertion by assertion.  The accompanying literal audit verifies that every
frozen formula has exactly 48 declared reals, 72 documented base assertions,
and only the recorded exchange implications afterward.  This makes the
remaining external task sharply falsifiable, but it is not a substitute for
an independent human verdict.  A second, separately formulated semantic audit
now reconstructs every assertion without importing the production encoder,
lex predicate, blocker, direction generator, minimizer, exporter, or
serializer.  It proves local logical equivalence for all 1,080 base assertions
and 252 direction implications, rebuilding 4,722 negative-cut alternatives
and 33,054 blocker comparisons.  This closes the literal transcription gap;
it still does not independently prove the human anchor, lex-improvement, or
tight-blocker lemmas.

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
python3 coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py \
  --output /tmp/strict_exchange_formula_interface.json
cmp coopgames/verifiers/s6/strict_exchange_formula_interface.json \
  /tmp/strict_exchange_formula_interface.json
python3 coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py \
  --output /tmp/strict_exchange_semantic_interface.json
cmp coopgames/verifiers/s6/strict_exchange_semantic_interface.json \
  /tmp/strict_exchange_semantic_interface.json
python3 coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_anchor_core_certificate.py
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py \
  --output /tmp/strict_exchange_p4_packet_classes.json
cmp coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json \
  /tmp/strict_exchange_p4_packet_classes.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py \
  --output /tmp/strict_exchange_p4_relay_trees.json
cmp coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json \
  /tmp/strict_exchange_p4_relay_trees.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class4_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class4_hand_certificates.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class4_hand_certificates.json \
  /tmp/strict_exchange_p4_class4_hand_certificates.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class11_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class11_hand_certificates.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class11_hand_certificates.json \
  /tmp/strict_exchange_p4_class11_hand_certificates.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class7_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class7_hand_certificates.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class7_hand_certificates.json \
  /tmp/strict_exchange_p4_class7_hand_certificates.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_order_split_relays.py \
  --output /tmp/strict_exchange_p4_order_split_relays.json
cmp coopgames/verifiers/s6/strict_exchange_p4_order_split_relays.json \
  /tmp/strict_exchange_p4_order_split_relays.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class9_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class9_hand_certificate_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_audit.json \
  /tmp/strict_exchange_p4_class9_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class10_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class10_hand_certificate_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_audit.json \
  /tmp/strict_exchange_p4_class10_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class1_hand_certificate_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_audit.json \
  /tmp/strict_exchange_p4_class1_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class2_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class2_hand_certificate_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_audit.json \
  /tmp/strict_exchange_p4_class2_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class5_packet_skeleton_audit.json \
  /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class6_packet_skeleton_audit.json \
  /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json
python3 coopgames/verifiers/s6/verify_zero_anchor_overcover_duality.py \
  --output /tmp/zero_anchor_overcover_duality_audit.json
cmp coopgames/verifiers/s6/zero_anchor_overcover_duality_audit.json \
  /tmp/zero_anchor_overcover_duality_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --output /tmp/strict_exchange_p4_class6_overcovers.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class6_overcovers.json \
  /tmp/strict_exchange_p4_class6_overcovers.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_allocation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_allocation_identity_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class6_allocation_identity_audit.json \
  /tmp/strict_exchange_p4_class6_allocation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_activation_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_activation_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_activation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_activation_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_activation_identity_audit.json
cmp coopgames/verifiers/s6/strict_exchange_p4_class6_activation_identity_audit.json \
  /tmp/strict_exchange_p4_class6_activation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py \
  --output /tmp/strict_exchange_p4_universal_order_relays.json
cmp coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json \
  /tmp/strict_exchange_p4_universal_order_relays.json
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
