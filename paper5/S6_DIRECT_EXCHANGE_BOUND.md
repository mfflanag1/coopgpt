# Direct exactness-exchange proof that `s(6)=2/3`

Date: 2026-08-09

## Theorem and status

For every singleton-normalized exact game `v` on six players with
`T=v(N)>0`,

```text
||Lmin(v)-Lmax(v)||_1 / T <= 2/3.
```

The explicit exact game `G(2,3)` attains `2/3`.  Consequently

```text
s(6)=2/3.
```

The upper bound is a **direct table-free computer-assisted theorem**.  It
does not use the generator normal form, support/table census, equality
classification, a path or continuity theorem, first crossing, or either
local equality-profile handover.  Its only game-theoretic inputs are
singleton exactness and the defining lexicographic optimality of Lmin and
Lmax.  Its finite component is an exact QF_LRA split into the fifteen possible
sign counts of `Lmin_i-Lmax_i`.

All fifteen minimized formulas are UNSAT in Z3 and cvc5.  cvc5 emits CPC with
`--proof-pedantic=1` and `--no-proof-allow-trust`; no forbidden proof marker is
present; Ethos checks all fifteen proofs as `correct`.  The aggregate CPC size
is 52,856,780 bytes.  This result has not yet received external specialist
review, so it should not yet be presented as externally validated or as a
field-level breakthrough.

## 1. Normalize and split by comparison signs

Scale to `T=1` and write

```text
x=Lmin(v),       z=Lmax(v).
```

Both points are nonnegative and sum to one.  Put

```text
P={i:x_i>z_i},   M={i:z_i>x_i},   E={i:x_i=z_i}.
```

If the two selections differ, then `p=|P|` and `m=|M|` are positive and
`p+m+e=6`.  Up to a common relabeling of players there are exactly fifteen
such triples.  In each one,

```text
||x-z||_1 = 2 sum_{i in P}(x_i-z_i).                    (1)
```

The contradiction formulas assert that the right side of (1) is strictly
greater than `2/3`.

## 2. Exactness witnesses and automatic anchors

For every player `i`, exactness at `{i}` supplies a core allocation `q^i`
with `q^i_i=v({i})=0`.  The proof uses only nonnegativity, efficiency, and
this zero coordinate from each witness.

Three anchors follow directly from convexity of the core:

1. **Lmax has no singleton top stratum.**  If `z_i` were the unique maximum,
   then `z_i>0`; a short move from `z` toward `q^i` would lower the unique old
   maximum before any lower coordinate could cross it, improving the
   decreasing lexicographic vector.
2. **Lmax-top cross anchor.**  Some top player of `z` has `x_i>=z_i`.
   Otherwise a short move from `z` toward `x` would lower every old top
   coordinate.
3. **Lmin-bottom cross anchor.**  Some bottom player of `x` has `z_i<=x_i`.
   Otherwise a short move from `x` toward `z` would raise every old bottom
   coordinate.

These arguments use only line segments between core points and the positive
gap from the relevant extreme stratum to the next stratum.

## 3. Universal exactness blocker lemma

Let `h(N)=0`.  The finite formulas use the following sufficient improvement
tests.

- At `x`, `h` improves Lmin if the lowest payoff level touched by `h` has at
  least one positive coefficient and no negative coefficient.
- At `z`, `h` improves Lmax if the highest payoff level touched by `h` has at
  least one negative coefficient and no positive coefficient.

The predicates in `lex_improves` express exactly these sufficient conditions;
they do not claim to recognize every improving direction.

As a differential control, `audit_lex_improvement_predicate.py` compares the
pivot formulation with a separately written first-affected-stratum criterion
on all 4,683 labeled weak orders, all 1,610 bound-two directions, and both
sides: 15,079,260 Boolean comparisons with zero mismatches.

If such an `h` improves a selection `y`, optimality implies that some proper
coalition `S` tight at `y` has `h(S)<0`.  Otherwise every tight inequality has
nonnegative derivative, every nontight inequality has positive slack, and a
sufficiently short step `y+epsilon h` remains in the core while improving the
selection.

Core membership of the opposite selection and all six exactness witnesses
then gives the necessary blocker conditions

```text
y=x:  z(S)>=x(S) and q^i(S)>=x(S) for all i;             (2)
y=z:  x(S)>=z(S) and q^i(S)>=z(S) for all i.             (3)
```

The SMT formulas disjoin (2) or (3) over all proper coalitions with `h(S)<0`.
They do not encode a game or require the eligible coalition to be genuinely
tight.  They are therefore relaxations of the exact-game problem.  UNSAT of
the relaxation is sufficient for the theorem.

## 4. Complete strict-distance classification

All efficiency-preserving integer directions with coefficients in `[-1,1]`
already eliminate thirteen sign-count cases.  Only `(p,m,e)=(2,3,1)` and
`(3,3,0)` require the pool with coefficients in `[-2,2]`.  No canonical
payoff profile and no equality-specific premise is used.

UNSAT cores were used only to find smaller direction menus.  Every retained
menu was rebuilt without assumption literals and checked again.  The frozen
suite contains 252 labeled directions in total, occupying 64 sign-preserving
orbit signatures.

| sign counts `(p,m,e)` | direction bound | retained directions | sign orbits |
|---|---:|---:|---:|
| `(1,1,4)` | 1 | 1 | 1 |
| `(1,2,3)` | 1 | 1 | 1 |
| `(1,3,2)` | 1 | 1 | 1 |
| `(1,4,1)` | 1 | 1 | 1 |
| `(1,5,0)` | 1 | 0 | 0 |
| `(2,1,3)` | 1 | 2 | 2 |
| `(2,2,2)` | 1 | 5 | 2 |
| `(2,3,1)` | 2 | 14 | 5 |
| `(2,4,0)` | 1 | 8 | 1 |
| `(3,1,2)` | 1 | 2 | 2 |
| `(3,2,1)` | 1 | 52 | 17 |
| `(3,3,0)` | 2 | 71 | 18 |
| `(4,1,1)` | 1 | 2 | 2 |
| `(4,2,0)` | 1 | 90 | 9 |
| `(5,1,0)` | 1 | 2 | 2 |

Every row asserts the common simplex, signs, strict distance, three anchors,
six singleton witnesses, and only its retained blocker implications.  Every
row is UNSAT.  Since the sign split is exhaustive, a strict counterexample
cannot exist.

## 5. Lower bound and equality information

The family theorem for `G(p,k)` gives

```text
rho(G(p,k)) = 2(p(k-1)-1)/(k(p+1)).
```

At `(p,k)=(2,3)` this is `2/3`, and the family membership proof establishes
that the game is exact and singleton-normalized.  This supplies the matching
lower bound.

The separate proof-object family in `EQUALITY_EXCHANGE_CLASSIFICATION.md`
shows more: every exact six-player game attaining `2/3` has, up to player
permutation, one of the two canonical starved or positive payoff pairs.  That
rigidity theorem is not needed for the upper bound.

## 6. Proof-object boundary and review standard

The checked implication is

```text
strict exact-game counterexample
  => one of 15 sign labels + anchors + singleton witnesses + blockers
  => one of 15 frozen QF_LRA formulas
  => contradiction.
```

The CPC objects independently prove the last implication for the exact
formulas.  Human review must still verify the first implication: normalization,
sign relabeling, the three anchors, both lex-improvement predicates, and the
exactness blocker lemma.  None is a large theorem, but each is load-bearing.

The highest-risk implementation overlap has a second lane.  The two cases
that require coefficient-two directions, `(2,3,1)` and `(3,3,0)`, are rebuilt
by an independently formulated encoder.  It shares only the frozen retained
menus as theorem data and imports no production encoder, lex predicate,
blocker, direction pool, minimizer, or serializer.  Both base systems with the
exchange implications removed are SAT; both full systems are UNSAT in Z3 and
cvc5; fresh trust-disabled CPC proofs check `correct` in Ethos.

The three largest menus have also been quotiented under relabelings internal
to `P`, `M`, and `E`: 213 labeled directions become 44 sign-role orbits and
eight oriented coefficient templates, or six up to sign reversal.  The
one-for-one and two-for-two templates cover 179 of the 213 rows.  This is a
readability reduction, not an all-human replacement for the finite proof.

A second, proof-checked orbit reduction is stronger.  It retains complete
orbits but shrinks the three cases to 19 selected sign-role schemas and 136
labeled implications.  The `(3,2,1)` and `(4,2,0)` cases use only one-for-one
and two-for-two exchanges.  The balanced `(3,3,0)` case additionally uses one
asymmetric coefficient-two shape and its reversal.  Each of the three reduced
unguarded formulas is UNSAT in Z3 and cvc5 and has a fresh trust-disabled CPC
proof checked by Ethos; deleting any one selected orbit makes that reduced
relaxation SAT.  The SAT ablations establish irredundancy only inside the
relaxation and are not games or independent proof evidence.
All three reduced formulas omit the no-unique-Lmax-top anchor: only the two
cross-selection anchors remain, and each is necessary within the reduced
relaxation.

The `(4,2,0)` reduced formula admits one more weakening.  Its blocker
alternatives use the opposite-selection comparison and only the four
singleton-witness comparisons indexed by `P`; the two `M`-indexed witness
comparisons are omitted, although all six base witness blocks remain.  The
weakened formula is proof-checked UNSAT, while deleting any one of the five
retained comparison-source families makes the relaxation SAT.  These are
internal irredundancy controls, not realizing games.

An anchor-localized alternative makes the structure sharper.  Let `a in P`
be an Lmin-bottom anchor and `b in P` an Lmax-top anchor.  The case `a=b` is
impossible by `x_m>=x_a>z_a>=z_m>x_m` for `m in M`.  With distinct anchors
relabelled as `a=0,b=1`, a separately certified formula uses only `x,z`, the
single exactness witness `q^b`, and nineteen directions in ten residual
orbits.  It declares 18 reals and has a fresh trust-disabled CPC proof checked
by Ethos.  See `S6_P4_ANCHOR_LOCALIZATION.md`.

The two automatically active C1 directions in that localized formula admit
an exact packet split.  Their blockers are `{1,4} union A` and `{1,5} union
B`, with `A,B` subsets of the three remaining `P` players.  The 64 labelled
pairs contain 32 base-infeasible pairs; the 32 feasible pairs quotient to
eleven residual-symmetry classes, each closed by a subset-minimal menu of at
most seven other directions.  The aggregate packet inequalities are derived
by hand in `S6_P4_PACKET_CLASSIFICATION.md`.  This makes the remaining finite
anatomy smaller and more explicit, but does not turn it into an all-human
proof.  Seven of the eleven rows now close completely by hand.  In class 8 the
packet forces `-e_1-e_3+e_4+e_5` to improve Lmin, and elementary `d=x-z`
inequalities exclude all twenty of its eligible blockers without using the
`q^1` comparison.  Class 3 also closes by hand through a two-exchange relay:
the first blocker has two possible forms, either activates the second
exchange, and the four final blocker pairs all force the distance back to at
most `1/3`.  Class 4 is a depth-one three-leaf star: the root classification
and child activations are structural, while sixteen `q^1`-complement identities
and four opposite-base-cut identities close every terminal cut.  A pure
rational-coefficient checker verifies each nonnegative weighted sum without a
solver or production-encoder import.  Class 11 is a unique three-exchange
chain.  Its twenty first-stage cuts reduce structurally to seven candidates;
six exact identities leave the unique first blocker, fifteen `q^1` identities
leave the unique second blocker, and sixteen more exclude every terminal cut.
Class 7 reduces its depth-three relay to eight exact difference-cone cut
censuses, sixteen blocker filters, and nine activation identities.  Class 9
closes after the exhaustive split `x_3<=x_4` versus `x_3>x_4`: ten exact
difference-cone censuses and a 71-use map reduce to 43 blocker, seven
activation, and two terminal-anchor identities.  Its terminal leaves share
the threshold contradiction `x_1>1/3` versus `x_1<=1/3`.  Class 10 closes its
nine-leaf two-order tree through eighteen exact difference-cone censuses and
108 identities checked at 122 uses.  Its terminal leaves force `D<=1/3`
directly; 103 of 105 blocker exclusions use only the `q^1` comparison.
Class 1 adds a fifteen-leaf universal-order relay: twenty-one exact cut censuses,
85 blocker exclusions, and a minimum-level lemma compressing activation to 75
failure cases.  Its 109 deduplicated identities are checked at 160 uses.
Class 2 adds an eleven-leaf extremal-level relay with 21 cut censuses and 108
identities at 132 uses.  Together the nine hand lemmas remove twenty-seven
labelled packets from the
finite residue.

Class 5 now has a verified hand skeleton and complete exact arithmetic
conditional on its frozen relay/use maps.  Its symmetric packet gives
`d0+d1<=delta4,delta5<=d2+d3`; two cross-anchor chains make `h10` and `h15`
automatic, and one exact cut argument reduces all ten `h15` nodes from sixteen
eligible cuts to the same ten opposite-comparison candidates.  Three crossing
identities exclude seven of the thirty formal `h10`-predecessor/`h15`-blocker
pairs.  The root split itself is structural: its two twenty-cut censuses
reduce to exact three- and four-blocker lists, with only one seven-term witness
identity beyond signs.  Across the full 90-node tree, 1,736 eligible cuts
split exactly into 1,464 pure difference-cone exclusions, 34 context
exclusions, 150 target-witness exclusions, and 88 relay branches.  The 184
witness exclusions reduce to 107 exact rational identities.  The 285
activation-failure cases split into 195 exact allocation contradictions and
90 unit-weight witness over-covers, all covered by 72 exact rational
identities.  Solver-free checkers verify every arithmetic identity and the
exhaustive partitions.  This is not yet a tenth independently derived hand
lemma.  The 24 labelled cut menus now collapse to fifteen rich-player
templates, and a path-local grammar generates all 88 edges and 51 leaves.
On activation, 41 path-free identities cover 253 of 285 uses; the 32
path-dependent uses lie in three endpoint/exceptional families.  Rich-player
canonicalization reduces all 72 identities to 47 affine motifs, only 20 of
them path-dependent.  Independent derivation of the grammar and the 32-use
residual from the relay semantics remains the external-review boundary.
The other remaining row, class 6, has an asymmetric sandwich
`d0+d1<=delta4<=d3` and `d0+d1+d2<=delta5<=d2+d3`.  It reduces both
twenty-cut roots to two blockers using signs alone.  Its 29 non-root leaves
now have complete solver-free arithmetic conditional on the frozen relay/use
maps.  Across 49 nodes, 924 eligible cuts split into 711 pure difference-cone
exclusions, 11 packet/ancestor-witness context exclusions, 155 target-witness
exclusions, and 47 relay branches.  The 11 context exclusions have nine exact
rational identities.  All 155 target-witness cuts have incidence over-covers of
support at most five.  Of these, 150 use only unit coefficients and five use a
coefficient two.  The incidence bound is a human theorem.  The allocation-side
strict inequalities deduplicate to 53 exact rational identities checked
solver-free at all 155 uses; 118 uses need no path comparison, 33 use ancestors
only, and four also use the target comparison.  Exact arithmetic verifies that
the three surviving layers exhaust all 213 candidates, including every
terminal no-blocker closure.  Activation is
now governed by the same geometry: 84 of 124 elementary failure cases collapse
by anchor/order chains, four are allocation-infeasible, and all remaining 36
have packet/ancestor over-covers of support at most four.  Their incidence
bounds are human.  The 36 lower bounds reduce to 26 solver-free rational
identities, and the four direct cases share one further identity.  No
arithmetic leaf remains machine-only; the relay-derived cut and activation use
maps remain the hand-proof and external-review boundary.

The single-witness filters admit a general exact projection theorem.  For a
fixed blocker menu, `q^b` maps the zero-anchor simplex onto the convex hull of
the non-anchor incidence columns.  Therefore every nonnegative weighted sum
of witness comparisons is bounded exactly by its maximum non-anchor incidence
load, and every such support bound is attained at a unit vector.  This
zero-anchor over-cover duality explains the sparse crossing identities and
turns discovery of the remaining witness filters into a small LP/facet
problem.  It is standard convex duality, not an additional novelty claim.

The corresponding forced-exchange audit closes nine packet classes
`1,2,3,4,7,8,9,10,11` as exact relay certificates, covering twenty-seven of the
32 feasible labelled packets.  All nine now have hand-checkable proof objects;
the other two packet classes, covering five labelled packets, now both have
complete exact arithmetic conditional on their frozen maps.  They are no
longer structurally or arithmetically open: the single universal split
`x_3<=x_4` versus `x_3>x_4` closes all eleven packet classes as relay trees,
with only class 10 requiring the nested `x_1`/`x_2` split.  Thus the remaining
gap is orbit-level compression of classes 5 and 6 and external validation of
their maps, not an unexplained SAT leaf.  See
`S6_P4_UNIVERSAL_ORDER_RELAY.md`.

`S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md` supplies the assertion-by-assertion
human soundness proof.  Its literal audit confirms that every original frozen
formula declares exactly 48 reals and consists of exactly 72 documented base
assertions followed only by its recorded direction implications.  This is the
review boundary that matters: a reviewer should prove or refute that every
genuine counterexample satisfies those assertions, not merely rerun UNSAT.
A separate semantic audit now reconstructs all 1,332 frozen assertions without
the production encoder or predicates and proves each locally equivalent to its
independent statement.  It rebuilds 4,722 negative-cut alternatives and 33,054
blocker comparisons.  This closes the transcription question while leaving
the human necessity of the anchors, lex test, and blocker lemma open to review.

The direct proof makes the older first-crossing, equality-neighborhood, and
support-table programs logically unnecessary for `s(6)=2/3`.  They remain
valuable differential checks and structural information about the equality
boundary.  The old concern that leximin continuity may require a delicate
lexicographic theorem is now irrelevant to the upper bound.

## 7. Reproduction

Run from the repository root:

```text
python3 coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
python3 coopgames/verifiers/s6/verify_independent_bound_two.py
python3 coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py \
  --output /tmp/strict_exchange_formula_interface.json
cmp /tmp/strict_exchange_formula_interface.json \
  coopgames/verifiers/s6/strict_exchange_formula_interface.json
python3 coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py \
  --output /tmp/strict_exchange_semantic_interface.json
cmp /tmp/strict_exchange_semantic_interface.json \
  coopgames/verifiers/s6/strict_exchange_semantic_interface.json
python3 coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_anchor_core_certificate.py
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py \
  --output /tmp/strict_exchange_p4_packet_classes.json
cmp /tmp/strict_exchange_p4_packet_classes.json \
  coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py \
  --output /tmp/strict_exchange_p4_relay_trees.json
cmp /tmp/strict_exchange_p4_relay_trees.json \
  coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class4_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class4_hand_certificates.json
cmp /tmp/strict_exchange_p4_class4_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class4_hand_certificates.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class11_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class11_hand_certificates.json
cmp /tmp/strict_exchange_p4_class11_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class11_hand_certificates.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class7_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class7_hand_certificates.json
cmp /tmp/strict_exchange_p4_class7_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class7_hand_certificates.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_order_split_relays.py \
  --output /tmp/strict_exchange_p4_order_split_relays.json
cmp /tmp/strict_exchange_p4_order_split_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_order_split_relays.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class9_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class9_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class9_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class10_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class10_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class10_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class1_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class1_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class2_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class2_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class2_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_packet_skeleton_audit.json
python3 coopgames/verifiers/s6/verify_zero_anchor_overcover_duality.py \
  --output /tmp/zero_anchor_overcover_duality_audit.json
cmp /tmp/zero_anchor_overcover_duality_audit.json \
  coopgames/verifiers/s6/zero_anchor_overcover_duality_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --output /tmp/strict_exchange_p4_class6_overcovers.json
cmp /tmp/strict_exchange_p4_class6_overcovers.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_overcovers.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_allocation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_allocation_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_allocation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_allocation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_activation_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_activation_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_activation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_activation_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_activation_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_activation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_activation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py \
  --output /tmp/strict_exchange_p4_universal_order_relays.json
cmp /tmp/strict_exchange_p4_universal_order_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json
python3 coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py \
  --output /tmp/strict_exchange_large_case_templates.json
cmp /tmp/strict_exchange_large_case_templates.json \
  coopgames/verifiers/s6/strict_exchange_large_case_templates.json
```

This byte-regenerates all fifteen strict SMT-LIB formulas from the minimized
menu audit, compares them with the frozen files, and verifies every stored
formula hash, proof hash, Z3/cvc5 verdict, forbidden-marker field, and Ethos
status.

The relevant paths are:

```text
coopgames/verifiers/s6/audit_equality_universal_exchange_relaxation.py
coopgames/verifiers/s6/minimize_equality_exchange_directions.py
coopgames/verifiers/s6/strict_exchange_direction_cores.json
coopgames/verifiers/s6/strict_exchange_sign_orbits.json
coopgames/verifiers/s6/audit_lex_improvement_predicate.py
coopgames/verifiers/s6/lex_improvement_predicate_audit.json
coopgames/verifiers/s6/export_strict_exchange_bound_smt.py
coopgames/verifiers/s6/generate_equality_exchange_certificates.py
coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
coopgames/verifiers/s6/verify_strict_exchange_bound_certificates.py
coopgames/verifiers/s6/certificates/strict_exchange_*.{smt2,cpc,json}
coopgames/verifiers/s6/independent_bound_two_reconstruction.py
coopgames/verifiers/s6/verify_independent_bound_two.py
coopgames/verifiers/s6/independent_bound_two/*.{smt2,cpc,json}
coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py
coopgames/verifiers/s6/strict_exchange_large_case_templates.json
coopgames/verifiers/s6/audit_strict_exchange_large_case_orbit_cores.py
coopgames/verifiers/s6/strict_exchange_large_case_orbit_cores.json
coopgames/verifiers/s6/orbit_core_certificates/*.{smt2,cpc,json}
coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py
coopgames/verifiers/s6/audit_strict_exchange_p4_anchor_core.py
coopgames/verifiers/s6/strict_exchange_p4_anchor_core.json
coopgames/verifiers/s6/p4_anchor_core_certificates/*.{smt2,cpc,json}
coopgames/verifiers/s6/verify_strict_exchange_p4_anchor_core_certificate.py
coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py
coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py
coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class4_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class4_hand_certificates.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class11_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class11_hand_certificates.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class7_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class7_hand_certificates.json
coopgames/verifiers/s6/audit_strict_exchange_p4_order_split_relays.py
coopgames/verifiers/s6/strict_exchange_p4_order_split_relays.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class9_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_rows.json
coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_audit.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class10_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_rows.json
coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_audit.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_rows.json
coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_audit.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class2_hand_certificates.py
coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_rows.json
coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_audit.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_packet_skeleton.py
coopgames/verifiers/s6/strict_exchange_p4_class6_packet_skeleton_audit.json
coopgames/verifiers/s6/verify_zero_anchor_overcover_duality.py
coopgames/verifiers/s6/zero_anchor_overcover_duality_audit.json
coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py
coopgames/verifiers/s6/strict_exchange_p4_class6_overcovers.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_allocation_identities.py
coopgames/verifiers/s6/strict_exchange_p4_class6_allocation_identity_rows.json
coopgames/verifiers/s6/strict_exchange_p4_class6_allocation_identity_audit.json
coopgames/verifiers/s6/audit_strict_exchange_p4_class6_activation_overcovers.py
coopgames/verifiers/s6/strict_exchange_p4_class6_activation_overcovers.json
coopgames/verifiers/s6/verify_strict_exchange_p4_class6_activation_identities.py
coopgames/verifiers/s6/strict_exchange_p4_class6_activation_identity_rows.json
coopgames/verifiers/s6/strict_exchange_p4_class6_activation_identity_audit.json
coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py
coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json
coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py
coopgames/verifiers/s6/strict_exchange_formula_interface.json
coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py
coopgames/verifiers/s6/strict_exchange_semantic_interface.json
coopgames/paper5/S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md
coopgames/paper5/S6_EXCHANGE_ORBIT_LEMMAS.md
coopgames/paper5/S6_P4_ANCHOR_LOCALIZATION.md
coopgames/paper5/S6_P4_PACKET_CLASSIFICATION.md
coopgames/paper5/S6_P4_RELAY_TREES.md
coopgames/paper5/S6_P4_UNIVERSAL_ORDER_RELAY.md
coopgames/paper5/S6_LITERATURE_NOVELTY_AUDIT.md
```

The correct significance statement before external review is: a direct,
independently proof-checked fixed-dimension theorem resolving the six-player
case.  It is a major breakthrough for this project.  Whether it is novel and
important enough to be a field-level breakthrough depends on hostile review,
literature comparison, and conversion of at least the larger sign cases into
readable exchange arguments.

For a targeted exact regression of the sharp endpoint, run
`python3 coopgames/verifiers/s6/verify_g23_witness.py`. It rebuilds `G(2,3)`,
checks the generator exactifiers, recomputes both selections by exact staged
LP, and verifies `rho=2/3`. This is a bug audit; the family theorem remains
the proof of attainment.
