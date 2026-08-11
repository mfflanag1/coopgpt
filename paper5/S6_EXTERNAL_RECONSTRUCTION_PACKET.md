# Independent reconstruction packet for the six-player theorem

Date: 2026-08-10

Review branch `codex/fixed-n-handover-facets` at commit `02524cc` or later.
The target theorem is the sharp singleton-normalized exact-game bound

```text
||Lmin(v)-Lmax(v)||_1 <= 2/3 v(N)    for n=6.
```

This packet is deliberately shorter than `EXTERNAL_REVIEW_S6_DIRECT_BOUND.md`.
It identifies the remaining logical gates after exactification and orbit-level
compression.  A solver rerun is not a substitute for any gate below.  The
work has not received the requested external specialist validation, and the
literature search does not establish novelty.

## Gate 1: reconstruct the counterexample-to-relaxation implication

Read first:

```text
coopgames/paper5/S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md
coopgames/paper5/S6_INTERFACE_REVIEW_WORKSHEET.md
coopgames/verifiers/s6/strict_exchange_formula_interface.json
coopgames/verifiers/s6/strict_exchange_semantic_interface.json
coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py
coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py
```

Independently prove or refute each arrow:

```text
exact game
 -> normalized nonnegative core allocations x,z and singleton witnesses q^i
 -> one of the fifteen canonical sign cases
 -> the three selection anchors
 -> every retained direction is genuinely sorted-lex improving when active
 -> optimality supplies a negative tight blocker
 -> the blocker supplies every retained opposite/witness comparison
 -> one complete frozen implication row.
```

Pay particular attention to tied payoff strata, zero coordinates, the common
short-step choice across all nontight coalitions, and the orientation switch
between Lmin and Lmax.  Then manually trace at least one complete implication
in each coefficient-two sign case `(2,3,1)` and `(3,3,0)` from its human
direction through every negative cut and all seven blocker comparisons.

Section 3 now uses `min(1,Delta)` for all three core-segment anchors.  Section
6 uses the single radius `(E1)`, the minimum of `1`, `Delta`, and every
nontight-coalition slack ratio.  Verify positivity and the resulting
sorted-vector comparison; do not accept the phrase “sufficiently small” as a
separate premise.  Record verdicts H1--H14 and F1--F9 directly in the
worksheet.

Section 7 then writes one full coefficient-two implication in each difficult
case without SMT syntax: `p2_n3_t1:a72` has 24 explicitly parametrized
negative cuts, while `p3_n3_t0:a74` has 26.  Check both activation
equivalences, the cut counts, and all seven comparison sources against the
formula-interface JSON before sampling any additional rows.

Required reviewer output: a table with one row per assertion family, marked
`proved`, `false`, or `not checked`, with a citation to the precise source
line or a counterexample.  Passing JSON audits prove transcription and local
equivalence only; they do not prove the mathematical arrows.

## Gate 2: independently reconstruct the two coefficient-two cases

The existing second formulation is here:

```text
coopgames/verifiers/s6/independent_bound_two_reconstruction.py
coopgames/verifiers/s6/verify_independent_bound_two.py
coopgames/verifiers/s6/independent_bound_two/audit.json
coopgames/verifiers/s6/independent_bound_two/p2_n3_t1.{smt2,cpc,json}
coopgames/verifiers/s6/independent_bound_two/p3_n3_t0.{smt2,cpc,json}
```

It shares only the frozen retained menus with the production proof and imports
none of the production encoder, lex predicate, blocker builder, direction
generator, minimizer, or serializer.  It records:

```text
(2,3,1): 14 retained directions, base SAT, full formula UNSAT;
(3,3,0): 71 retained directions, base SAT, full formula UNSAT.
```

A third formulation is now frozen here:

```text
coopgames/paper5/S6_THIRD_BOUND_TWO_RECONSTRUCTION.md
coopgames/verifiers/s6/third_bound_two_direct_smt.py
coopgames/verifiers/s6/verify_third_bound_two.py
coopgames/verifiers/s6/third_bound_two/audit.json
coopgames/verifiers/s6/third_bound_two/verification.json
coopgames/verifiers/s6/third_bound_two/p2_n3_t1.smt2
coopgames/verifiers/s6/third_bound_two/p3_n3_t0.smt2
```

Its generator imports only the standard library, constructs no Z3 AST, uses
strict positive/negative-support separation instead of pivot activation,
enumerates coalitions by cardinality combinations, and serializes SMT-LIB
directly.  It reconstructs all 1,726 cuts and 12,082 comparisons.  The
verifier checks 458 assertion equivalences against both previous encodings;
both bases are SAT and both full formulas are UNSAT.  Non-strict activation
and cut-omission mutations are detected on all 85 direction rows.

For external validation, inspect or rewrite this third formulation without
assuming its verdict.  The minimal specification remains:

1. declare `x,z,q^0,...,q^5` directly;
2. encode the sign case, efficiency, nonnegativity, strict distance and three
   anchors from the mathematical statement;
3. implement lex activation directly, preferably by the `(Tmin)/(Tmax)`
   support-separation lemma rather than either pivot code;
4. enumerate nonempty proper coalitions and retain exactly those with
   negative direction sum;
5. generate opposite plus six singleton-witness comparisons directly; and
6. check base SAT, full UNSAT, and logical equivalence of every complete
   implication row against the frozen SMT-LIB.

Do not count a byte comparison, a shared helper, or a second solver on the
same formula as independent reconstruction.  The CPC/Ethos records establish
UNSAT of the stored formulas after the human-to-formula map is accepted.

Reproduction command:

```bash
python3 coopgames/verifiers/s6/verify_independent_bound_two.py
python3 coopgames/verifiers/s6/verify_third_bound_two.py \
  --output /tmp/third_bound_two_verification.json
cmp /tmp/third_bound_two_verification.json \
  coopgames/verifiers/s6/third_bound_two/verification.json
```

The verifier permits the recorded local Z3 version to differ as provenance,
but requires every substantive audit field and both generated SMT-LIB files
to reproduce exactly; it separately checks the frozen formula and CPC hashes.
The third verifier byte-regenerates its direct-text formulas and compares each
assertion semantically with both earlier formulations.  Neither internal
reconstruction supplies the external verdict required by Gate 1.

## Gate 3: reconstruct the 52/71/90 orbit quotient

Read:

```text
coopgames/paper5/S6_EXCHANGE_ORBIT_LEMMAS.md
coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py
coopgames/verifiers/s6/audit_strict_exchange_large_case_orbit_cores.py
coopgames/verifiers/s6/audit_strict_exchange_large_case_activation_atlas.py
coopgames/verifiers/s6/strict_exchange_large_case_orbit_cores.json
coopgames/verifiers/s6/strict_exchange_large_case_activation_atlas.json
```

Independently verify that relabelling within `P`, `M`, and `E` sends the 213
labelled rows of the `52+71+90` cases to 44 sign-role orbits, and that the
reduced proof retains 19 complete orbits containing 136 rows.  For the
three cases, derive the A1--A8, B1--B5, and C1--C6 activation atlases
directly.  Their `29+39+68=136` retained rows must reduce to the 19 displayed
min/max order-statistic tests with the stated multiplicities.  In B4/B5,
confirm explicitly that swapping coefficient magnitudes leaves activation
unchanged but changes the negative-cut family.  This settles the activation
vocabulary, not the coexistence of the resulting blockers.

Then derive the three negative-cut templates without enumeration: 16 cuts
for one-for-one, 20 for two-for-two, and 24 for either asymmetric
coefficient-two orientation.  Confirm the aggregate
`64*16+60*20+12*24=2512` and the seven comparison sources on every cut.  The
frozen atlas audit checks the expansion and counts; the reviewer must still
assess the mathematical derivation and the blocker coexistence proof.

Finally verify the blocker-coexistence projection lemma in
`S6_EXCHANGE_ORBIT_LEMMAS.md`.  After fixing one blocker cut per active
direction, (W1)--(W2) must eliminate each witness simplex exactly, while
(W3) retains the opposite-selection comparison.  Check the five-column
incidence-hull formulation for all six zero anchors, its exact reduction to
the second-largest incidence load, the pairwise intersection corollary, and the pointwise
five-requirement Helly bound.  State explicitly whether this reduces the
remaining proof to a finite transversal/facet problem or whether any coupling
between witnesses was lost.

Then independently check the constructive refinement in
`S6_ZERO_ANCHOR_FACET_RAYS.md`: partition the weight orthant into the
anchor/maximizer cones `K(i,k)`, prove that their extreme rays give an exact
finite inequality system, and verify the support bound `n-1` and its
five-coalition sharp example.  Distinguish this standard polyhedral reduction
from the still-open global blocker-transversal argument.

Confirm separately that `(3,3,0)` needs the H4/H5 asymmetric
coefficient-two pair in addition to H7/H8, while `(3,2,1)` and `(4,2,0)` use
only one-for-one and two-for-two exchanges.  Treat orbit-level UNSAT and SAT
ablations as finite-proof and irredundancy evidence, not as a human derivation
of the blocker layer.

## Gate 4: reconstruct the class-5 large map

Read:

```text
coopgames/paper5/S6_P4_CLASS5_PACKET_SKELETON.md
coopgames/verifiers/s6/verify_strict_exchange_p4_class5_cut_census.py
coopgames/verifiers/s6/strict_exchange_p4_class5_cut_census_audit.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class5_allocation_identities.py
coopgames/verifiers/s6/verify_strict_exchange_p4_class5_activation_identities.py
```

The arithmetic status is complete conditional on the map:

```text
1736 = 1464 pure exclusions + 34 context + 150 target + 88 branches;
285 activation failures = 195 direct contradictions + 90 witness covers.
```

The map is now compressed.  Reconstruct, without reading the relay JSON while
deriving it:

- the fifteen rich-player-parametric menu templates and their 24 labelled
  expansions;
- the weak/strict path grammar generating all 88 edges and 51 leaves; and
- the activation split into 253 path-free uses and a 32-use ancestor-dependent
  residual.

The 32 residual uses have only three families: eight terminal `h11/h12`,
thirteen exceptional `h16`, and eleven terminal `h17/h18` cases.  Exact affine
canonicalization reduces all 72 activation identities to 47 motifs, including
20 for this residual.  Forgetting source-depth aliases does not prove that a
motif is available at a given path; verify every residual placement.

## Gate 5: reconstruct the class-6 large map

Read:

```text
coopgames/paper5/S6_P4_CLASS6_PACKET_SKELETON.md
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_cut_census.py
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_context_identities.py
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_allocation_identities.py
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_activation_identities.py
```

Reconstruct the seven direction menus plus the weak `h11:C124` refinement and
the seven-rule transition grammar.  Confirm

```text
924 = 711 pure exclusions + 11 context + 155 target + 47 branches
```

and all 29 terminal leaves.  Then reconstruct the `124=84+4+36` activation
partition and the placement of the 36 witness plus four direct identities.
The 40 uses compress into 19 path-free cases and a 21-use residual with three
families: nine weak-terminal `h17`, eight strict-chain endpoint, and four
direct weak-`h7` cases.  Forgetting source-depth aliases reduces the 27
identities to 25 affine motifs.  Verify the residual placements rather than
inferring availability from motif equality.
The rational identities remove solver dependence from arithmetic; they do not
derive their relay/use sites.

## Gate 6: novelty is a separate review

Start with:

```text
coopgames/paper5/S6_LITERATURE_NOVELTY_AUDIT.md
coopgames/paper5/S6_SPECIALIST_NOVELTY_SIGNOFF.md
```

Search beyond its terminology in exact-partition games, antiduality,
large-core games, exact-cone facets and indecomposable semi-balanced systems,
base-polyhedron decreasing/increasing minimizers, polymatroid exchange, and
coherent lower probabilities.  Specifically ask whether any known theorem
implies the sharp fixed-six inequality or an equivalent exchange principle.

The closest checked adjacent results do three different jobs: Frank--Murota
develop decreasing minimization and canonical partitions for
base-polyhedra/M-convex sets, while Studený--Kratochvíl and
Kroupa--Studený classify facets of the exact and totally balanced game cones.
Gong--Dietzenbacher--Peters give a clipped-level formula on the special class
of box--hyperplane (two-bound) cores, and Gong--Dietzenbacher extend exact-
core-bound reductions to all balanced games using coordinate-bound values
that can fall outside the core already with three players.  Do not infer the
present theorem from any of these vocabularies without supplying the
missing translation.  The reviewer should answer these concrete questions:

1. Can every exact-game core needed here be represented as a
   base-polyhedron in a way that sends `Lmin` and `Lmax` to a known opposing
   pair of lexicographic selectors?
2. If yes, does an existing exchange/proximity theorem imply the `2/3`
   distance bound and its equality cases?
3. Can the six-player exact cores be reduced to two-bound cores, or does some
   known exact-core-bound consistency theorem preserve both Lorenz selectors?
   If so, identify the theorem and verify core membership of the transported
   values; the general clipped coordinate values do not have it.
4. If no, do indecomposable semi-balanced facet inequalities nevertheless
   imply the singleton-exactness blocker used by this proof?
5. Is there an equivalent selector-distance statement in coherent-lower-
   probability terminology?

The current defensible statement is only: a targeted primary-source search
did not locate an equivalent theorem.  Report correctness and novelty as two
separate conclusions.

The sign-off packet defines collision criteria and requires the reviewer to
record identity, expertise, databases, search scope, the inspected commit,
and either an explicit prior-theorem translation or a scoped negative-search
opinion.  An unsigned repository copy is not external validation.

For the base-polyhedron question, audit the elementary transfer obstruction
recorded in `S6_LITERATURE_NOVELTY_AUDIT.md`: exactness plus a direct
`C(v)=B(f)` representation forces
`v(S)=f(N)-f(N\S)` and hence convexity.  A claimed transfer for nonconvex exact
games must therefore provide a genuinely different affine/extended
representation and prove that it preserves both selectors and the metric.

## Requested final review format

Classify every issue as `fatal`, `repairable`, or `expository`, with exact
file and line references.  End with separate answers:

1. Does every genuine counterexample map into a frozen relaxation?
2. Are the two coefficient-two cases independently reconstructed?
3. Is the 52/71/90 orbit quotient, including the A/B/C activation atlases,
   independently derivable from role relabelling and order statistics?
4. Are the class-5 and class-6 maps independently derivable from the stated
   orbit grammars?
5. Is the theorem already known under another formulation?
6. If correct and new, is this a finite computational theorem, a substantial
   structural theorem, or a major field-level result?

Until Gates 1--6 receive specialist answers, describe the result as a strong
computer-assisted six-player theorem candidate with extensive solver-free
arithmetic and structural compression, not as externally validated or a
major field breakthrough.
