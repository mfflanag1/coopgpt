# Exact CPC certificate controls

Date: 2026-08-09

This directory contains several generations of independently checked
six-player proof objects.  The older generator-normal-form and local-handover
queries do not replace the complete 3,350-configuration census by themselves.
The newer table-free `strict_exchange_*` suite is different: together with
the elementary exactness-exchange reduction documented below, its fifteen
formulas prove the global six-player upper bound.  The parallel
`equality_exchange_*` suite classifies every equality payoff pair.

| Formula | Survivor | Query | Verdict |
|---|---:|---|---|
| `failure_index0000.smt2` | 0 | strict distance `>2/3` | UNSAT |
| `equality_noncanonical_index1408.smt2` | 1408 | distance `=2/3`, payoff pair differs from the displayed canonical pair | UNSAT |
| `equality_noncanonical_index2236.smt2` | 2236 | distance `=2/3`, payoff pair differs from the displayed canonical pair | UNSAT |
| `equality_no_common_triple_index1408.smt2` | 1408 | distance `=2/3`, no Lmax-top triple tight at both selections | UNSAT |
| `equality_no_common_triple_index2236.smt2` | 2236 | distance `=2/3`, no Lmax-top triple tight at both selections | UNSAT |
| `equality_no_triple_index1408.smt2` | 1408 | distance `=2/3`, no tight triple of Lmax-top players | UNSAT |
| `equality_no_triple_index2236.smt2` | 2236 | distance `=2/3`, no tight triple of Lmax-top players | UNSAT |
| `equality_subthird_index1408.smt2` | 1408 | distance `=2/3`, Lmax over-cover dispersion `<1/3` | UNSAT |
| `equality_subthird_index2236.smt2` | 2236 | distance `=2/3`, Lmax over-cover dispersion `<1/3` | UNSAT |
| `positive_lmax_direction_index0040.smt2` | 40 | positive critical residue plus a blocker to direction `(0,0,0,-1,0,1)` | UNSAT |
| `positive_lmax_direction_index0200.smt2` | 200 | representative `N(1,1),P(-2,-2,-1),r=3` Lmax direction blocker | UNSAT |
| `positive_lmax_direction_index0504.smt2` | 504 | representative distance-sensitive `N(-1,1),P(0,0,0),r=0` Lmax direction blocker | UNSAT |
| `positive_lmax_boundary_n_l.smt2` | abstract | blocker `{n,l}` plus distance `>2/3` | UNSAT |
| `positive_lmax_boundary_n_j_k_r.smt2` | abstract | blocker `{n,j,k,r}` plus distance `>2/3` | UNSAT |
| `positive_lmax_boundary_n_j_l_r.smt2` | abstract | blocker `{n,j,l,r}` plus distance `>2/3` | UNSAT |
| `positive_lmax_boundary_n_k_l_r.smt2` | abstract | blocker `{n,k,l,r}` plus distance `>2/3` | UNSAT |
| `positive_lmax_critical_boundary.smt2` | abstract | shared 16-row critical order plus distance `>2/3` | UNSAT |
| `positive_lmin_critical_boundary_nnpppr_low.smt2` | abstract | `NNPPPR`, low common pair | UNSAT |
| `positive_lmin_critical_boundary_nnpppr_outer.smt2` | abstract | `NNPPPR`, outer common pair | UNSAT |
| `positive_lmin_critical_boundary_nnpppr_high.smt2` | abstract | `NNPPPR`, high common pair | UNSAT |
| `positive_lmin_critical_boundary_npnppr_low.smt2` | abstract | `NPNPPR`, low common pair | UNSAT |
| `positive_lmin_critical_boundary_npnppr_outer.smt2` | abstract | `NPNPPR`, outer common pair | UNSAT |
| `positive_lmin_critical_boundary_npnppr_high.smt2` | abstract | `NPNPPR`, high common pair | UNSAT |
| `positive_lmin_critical_boundary_nppnpr_outer.smt2` | abstract | `NPPNPR`, outer common pair | UNSAT |
| `positive_lmin_critical_boundary_nppnpr_high.smt2` | abstract | `NPPNPR`, high common pair | UNSAT |
| `positive_lmin_direction_pattern_*.smt2` (23 files) | abstract | complete 322-row Lmin single-direction layer mapped to 23 order-pattern lemmas | UNSAT |
| `positive_lmin_menu_pattern_*.smt2` (22 files) | abstract | complete 97-row Lmin exchange-menu layer mapped to 22 order-pattern lemmas | UNSAT |

Indices 1408 and 2236 are the two equality-feasible stratum/table
configurations left by the complete staged census:

```text
index 1408: Lmin (4,2), Lmax (2,4), table ((2,2),(0,2));
index 2236: Lmin (5,1), Lmax (2,4), table ((2,3),(0,1)).
```

The separate reconstruction audit supplies and independently recomputes a
realizable equality game in each configuration.  Thus all eight equality
queries are nonvacuous: each base equality query is SAT; every equality payoff
pair in the type is the displayed canonical pair; a common tight top triple is
forced; and both asserted negations of the observed anchor geometry are UNSAT
in each surviving type.

## What is checked

`export_core_closure_smt.py` rebuilds each formula from `triage32.json`.  Its
small serializer emits the QF_LRA/Boolean AST without Z3-specific unary sums
or local `let` aliases and names every premise.  The frozen formula is then:

1. decided independently by Z3 5.0.0 and cvc5 1.3.3;
2. proved UNSAT by cvc5 with `--proof-pedantic=1` and
   `--no-proof-allow-trust`; and
3. checked as an exact CPC proof by Ethos, which returns `correct`.

The `.cpc` files contain the path-independent proof bodies.  The JSON files
bind each formula and proof body to SHA-256 hashes and record both solver
verdicts and the Ethos result.  CPC arithmetic is exact rational arithmetic.
This is stronger evidence than an unsat core: no unsat core is treated as a
proof, and the proof checker validates the complete proof body against the
official CPC signatures.

The paragraph below concerns the older generator-normal-form lanes only.  In
that subsystem, equality rigidity covers both solver-surviving types while
the archived strict-bound controls are representative rather than exhaustive.
The later table-free exchange suites supply the now-complete proof-object
theorems without relying on those support/configuration exclusions.

The three representative positive-handover controls represent the three role-normalized Lmax
direction templates.  Each base critical-triple system is SAT.  The added formula says
that at least one coalition blocks the displayed lexicographically improving
Lmax direction, with the blocker required to be eligible at `z` for `x` and
for all six singleton-exactness witnesses.  Its UNSAT proof therefore checks
one genuinely nonvacuous direction argument per template.  They do **not**
certify the other 106 single-direction Lmax rows or the 230 Lmax rows killed by
critical algebra.  They also do not certify any Lmin direction-menu row.

The four abstract boundary controls no longer encode a contingency table.
They assume only the shared weak orders of the eight distance-sensitive rows,
the two common-triple equalities, six simplex witnesses satisfying all three
critical-triple inequalities, one displayed blocker, and distance `>2/3`.
Their checked UNSAT proofs show that each blocker shape forces distance at
most `2/3`.  A separate finite audit is still needed to map the eight refined
support types to exactly these four shapes.

The abstract critical-boundary control similarly removes all contingency
tables.  It assumes the shared weak order of the sixteen critical rows that
survive every single premise ablation, their forced common pair, all six
critical witnesses, and distance `>2/3`.  Its checked UNSAT proof covers the
abstract implication; the finite dependency audit separately verifies that
the sixteen rows have the required order and common pair.

The eight abstract Lmin critical-boundary controls use the **global** weak
Lmin order, recorded as an `N/P/R` role word.  This distinction matters: a P
player can lie between the two poor players.  Each formula retains only that
role word, one common excluded-player pair, one Lmax relation, the critical
witness system, and distance `>2/3`.  The separate map covers 342 rows and 470
feasible-pair instances; it must be audited together with these proof objects.

The 23 abstract Lmin single-direction controls contain no contingency tables.
The separate mapping audit globally Lmin-sorts every row, permutes its role
word and direction, checks every feasible common excluded-player pair, and
maps all 494 pair instances from all 322 rows to a minimized abstract case.
Each formula contains normalization, the global weak Lmin chain, strict role
signs, one common pair, the critical comparisons and six singleton witnesses,
distance `>2/3`, the exact blocker disjunction for its direction, and between
one and four additional stratum-order relations.  The mapping audit is finite
classification evidence; the 23 CPC files independently check the abstract
implications.  Neither component alone certifies the complete layer.

The 22 abstract Lmin exchange-menu controls apply the same separation to the
remaining 97 rows.  For the 95 ordinary rows the formulas use every
lexicographically eligible member of the canonical fourteen-direction subset
exchange family; the two exceptional tables use their stored two- and
four-direction menus.  Global normalization gives 161 feasible-pair instances
and 21 role/menu/pair patterns.  Twenty close with their shared weak orders;
one eight-instance pattern splits into two one-relation cases.  After premise
minimization, four formulas need no additional stratum relation, sixteen need
one, one needs two, and one needs three.  The mapping and proof objects must
again be audited as separate dependencies.

The two `starved_universal_exchange_{min,max}` controls replace the complete
504-row starved-only refinement census by one table-free formula per handover
branch.  They retain coarse `N/P/R` signs and gaps, the tied rich Lmin pair,
standard top/bottom selection anchors, six singleton-zero witnesses,
opposite-side swap blockers, and selected-side blockers from 240 labeled
permutations of three exchange shapes.  The separate structural map verifies
that starved-only is exactly the tied-rich branch within the 1,352 starved
survivor refinements and differentially checks the symbolic lex predicate.
The shape ablation shows that swaps plus two-for-two exchanges close Lmax,
while Lmin genuinely needs the coefficient-two shape; the observed
three-for-three shape is redundant.  Both table-free formulas have trust-free
CPC proofs checked `correct` by Ethos.  These objects are conditional on their
displayed selection-anchor and first-crossing premises; they do not certify
the equality classification.

The fifteen `equality_exchange_p*_n*_t*` controls certify the equality
classification without support tables or staged-generator variables.  After
relabeling players by the sign of `Lmin_i-Lmax_i`, each formula contains the
simplex and exact-distance equations, the three standard selection anchors,
six singleton-zero witnesses, and a minimized labeled menu of exactness
blocker implications.  Thirteen formulas exclude their sign regime outright;
the `p3_n3_t0` and `p4_n2_t0` formulas instead exclude the positive and
starved canonical payoff profiles.  Their conjunction therefore leaves
exactly those two profiles at distance `2/3`.  UNSAT cores were used only to
choose smaller menus; every frozen formula is rebuilt without assumption
literals.  Z3 and cvc5 return UNSAT, and all fifteen trust-disabled CPC proofs
check `correct` in Ethos.  The prose reduction from exact-game selection
optimality to the displayed blocker formulas remains a human-review boundary;
see `paper5/EQUALITY_EXCHANGE_CLASSIFICATION.md`.

The fifteen `strict_exchange_p*_n*_t*` controls strengthen the same reduction
from equality to the strict upper bound.  They replace the distance equation
by `||Lmin-Lmax||_1>2/3`, use no canonical-profile exclusion, and close all
fifteen sign-count regimes directly.  Thirteen cases need only coefficient-one
efficiency-preserving directions; `p2_n3_t1` and `p3_n3_t0` use coefficients
in `[-2,2]`.  The frozen unguarded formulas retain 252 labeled directions in
total.  Z3 and cvc5 return UNSAT and every trust-disabled CPC proof checks
`correct` in Ethos.  Together with the exact `G(2,3)` witness these controls
prove `s(6)=2/3`, subject to hostile review of the short human reduction in
`paper5/S6_DIRECT_EXCHANGE_BOUND.md`.  The separate lex-predicate audit checks
all 4,683 weak orders against all 1,610 bound-two directions on both sides
(15,079,260 comparisons, zero mismatches); it is a combinatorial differential
control rather than part of the CPC proof objects.

The coefficient-two cases have an additional, independently formulated lane
under `../independent_bound_two/`.  Its reconstruction script imports none of
the production encoder, lex predicate, blocker builder, direction pool,
minimizer, or serializer; only the frozen retained direction menus are shared
as theorem data.  It rewrites the first-affected-stratum test and every
negative coalition cut, uses a logically dual encoding of the no-unique-top
anchor, and byte-regenerates both SMT formulas.  Removing the exchange
implications leaves each base system SAT.  The full `(2,3,1)` and `(3,3,0)`
systems are UNSAT in both solvers and have separate trust-disabled CPC proofs
checked `correct` by Ethos.  Run:

```text
python3 coopgames/verifiers/s6/verify_independent_bound_two.py
```

The three largest menus are additionally summarized by the non-proof audit
`../strict_exchange_large_case_templates.json`: 213 labeled rows quotient to
44 sign-role orbits and eight oriented coefficient templates (six modulo sign
reversal).  See `paper5/S6_EXCHANGE_ORBIT_LEMMAS.md`.  This quotient is an
explanatory map, not an independent certificate of the formulas.

The follow-up orbit-core suite under `../orbit_core_certificates/` is a genuine
proof reduction for those three cases.  It retains every labeled implication
in each selected sign-role orbit and reduces 44 orbits/213 directions to an
irredundant 19 orbits/136 directions.  The split is 8, 5, and 6 orbits for
`p3_n2_t1`, `p3_n3_t0`, and `p4_n2_t0`.  Every single-orbit deletion is SAT;
every complete reduced formula is UNSAT in Z3 and cvc5 and has a separate
trust-disabled CPC proof checked `correct` by Ethos.  Run

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py
```

Unlike the uniform fifteen-case suite, these three reduced formulas omit the
no-unique-Lmax-top anchor.  They retain only the Lmax-top and Lmin-bottom cross
anchors; both are irredundant in each reduced relaxation.

The `p4_n2_t0` formula additionally deletes the blocker comparisons from the
two singleton witnesses indexed by `M`.  Its alternatives retain the opposite
selection and `q0` through `q3`, indexed by `P`; all six base witness blocks
remain.  Each of those five retained comparison-source families is separately
irredundant by a SAT ablation.  The audit records the exact source list and
ablations in `../strict_exchange_large_case_orbit_cores.json`.

The stronger anchor-localized alternative for `p4_n2_t0` is under
`../p4_anchor_core_certificates/`.  It closes the coincident `x`-bottom/
`z`-top anchor branch by the four-inequality chain
`x_m>=x_a>z_a>=z_m>x_m`.  In the distinct branch it fixes `a=0,b=1`, keeps
only `x,z` and the top anchor's exactness witness `q1`, and retains nineteen
directions in ten residual `S2 x S2` orbits.  The formula has 18 declared
reals and 58 assertions.  Z3 and cvc5 return UNSAT, and a trust-disabled CPC
proof checks `correct` in Ethos.  Reproduce the audit and verify the frozen
objects with

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_anchor_core.py \
  --output /tmp/strict_exchange_p4_anchor_core.json \
  --formula /tmp/strict_exchange_p4_anchor_core.smt2
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_anchor_core_certificate.py
```

The explanatory forced-blocker audit then conditions the two automatic C1
directions on their concrete blockers.  It exhausts 64 labelled blocker
pairs, finds 32 base-feasible pairs in eleven residual-symmetry classes, and
closes every class with a subset-minimal menu of at most seven remaining
directions.  Regenerate its frozen table with

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py \
  --output /tmp/strict_exchange_p4_packet_classes.json
cmp /tmp/strict_exchange_p4_packet_classes.json \
  coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
```

This table strengthens selected disjuncts of the proof-checked parent formula;
it is a readability decomposition, not an additional proof object.
Packet class 8 is independent of the residual disjunction and closes by hand
with `-e1-e3+e4+e5`.  The same audit checks the reduced negated
activation formula and all twenty eligible opposite-blocker comparisons,
without a `q1` premise.
Packet class 3 also closes by hand as a two-exchange relay.  The audit rebuilds
its premises separately, verifies two possible blockers for each exchange,
checks both relay activations, and closes all four terminal blocker pairs.

The follow-up relay-tree audit applies that pattern to every packet core.
Classes `3,4,7,8,11`, covering eighteen labelled packets, close without an
order split.  The frozen JSON records every surviving coalition and every
open or closed leaf:

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py \
  --output /tmp/strict_exchange_p4_relay_trees.json
cmp /tmp/strict_exchange_p4_relay_trees.json \
  coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
```

Classes 3, 4, 7, 8, 9, 10, and 11 now have complete separate hand-checkable
proofs.  For
class 4 the packet audit checks the five-candidate opposite classification,
the exact three root blockers, all three child activations, and the
source-localized terminal closures.  A separate certificate table replaces
those terminal enumerations by sixteen `q1`-complement identities and four
opposite-base-cut identities:

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class4_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class4_hand_certificates.json
cmp /tmp/strict_exchange_p4_class4_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class4_hand_certificates.json
```

The checker uses only sparse affine forms with exact `Fraction` coefficients,
requires nonnegative multipliers on every inequality, and checks each weighted
sum equals its recorded positive integer multiple of `D-1/3`.  It imports no
production encoder, makes no solver call, and rejects a one-coefficient
mutation control.  For class 11, the packet audit checks all three activation
negations and recovers its unique two-blocker chain.  The human proof first
reduces twenty first-stage cuts to seven by sign membership, then uses 37
source-specific identities to leave the unique first and second blockers and
exclude every terminal cut:

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class11_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class11_hand_certificates.json
cmp /tmp/strict_exchange_p4_class11_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class11_hand_certificates.json
```

This checker also uses only exact `Fraction` arithmetic, imports no production
encoder, makes no solver call, verifies cut-family exhaustiveness, and rejects
a coefficient mutation.

Class 9 closes its five-leaf order-split relay through ten exact
difference-cone censuses and a deduplicated proof object.  The source table has
43 blocker, seven activation, and two terminal-anchor identities, with an
explicit map to all 71 required uses:

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class9_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class9_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class9_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_audit.json
```

The checker reconstructs every premise at every use site with exact
`Fraction` arithmetic, imports no solver or production encoder, and rejects
coefficient, use-site, candidate-set, use-map, and strict-target mutations.

Class 10 closes its nine-leaf nested order tree through eighteen exact
difference-cone censuses.  Its proof object has 95 blocker and thirteen
activation identities mapped to 122 uses:

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class10_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class10_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class10_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_audit.json
```

The checker localizes 103 blocker exclusions to `q1` alone and two to the
opposite selection alone.  It uses exact `Fraction` arithmetic, imports no
solver or production encoder, and rejects the same five mutation classes.

Class 1 closes its fifteen-leaf universal-order tree through twenty-one exact
difference-cone censuses.  A minimum-level lemma compresses each two-donor
activation to four failure conjunctions.  Its proof object has 65 blocker and
44 activation identities mapped to 160 uses and audits all 75 activation cases:

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class1_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class1_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_audit.json
```

The checker uses exact `Fraction` arithmetic, imports no solver or production
encoder, and rejects coefficient, use-site, candidate-set, use-map,
activation-atom, and strict-target mutations.  The length of this proof object
is still a conceptual-compression target.

Class 2 closes an eleven-leaf universal-order relay through 21 exact cut
censuses.  The minimum-level lemma and its maximum-level dual reduce activation
to 72 cases.  Its proof object has 52 blocker and 56 activation identities
mapped to 132 uses:

```text
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class2_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class2_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class2_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_audit.json
```

The solver-free checker independently encodes the asymmetric packet sandwich,
all mixed min/max branch orientations, both extremal-level activation forms,
and the same six mutation classes.

Class 5 now has a complete solver-free arithmetic partition conditional on
its 90-node frozen relay/use maps.  Exact elimination gives
`1736 = 1464 + 34 + 150 + 88`; 107 rational identities certify the 184
context/target exclusions, and 72 rational identities certify all 285
activation failures:

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class5_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class5_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_allocation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class5_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class5_allocation_identity_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_cut_census.py \
  --output /tmp/strict_exchange_p4_class5_cut_census_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class5_activation_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class5_activation_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_activation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class5_activation_details.json \
  --output /tmp/strict_exchange_p4_class5_activation_identity_audit.json
```

The identity verifiers import no solver or production encoder, reconstruct
every named affine premise over the rationals, check path availability, and
exercise mutation controls.  The 34/150/88 cut map and 195/90 activation map
remain encoding-shared integration records requiring external review.
The cut verifier additionally checks a fifteen-template menu atlas and the
complete path-local 88-edge grammar.  The activation verifier separates 253
path-free uses from a 32-use ancestor-dependent residual and canonicalizes the
72 identities to 47 affine motifs under the rich-player swap.

Class 6 has a complete solver-free cut partition conditional on the frozen
relay/use maps.  Exact Fourier--Motzkin elimination gives
`924 = 711 + 213`; the 213 candidates split disjointly as 11 pre-target
allocation-context exclusions, 155 target-witness exclusions, and 47 relay
branches.  Nine exact rational identities certify the 11 new exclusions:

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_context_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_context_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_context_identities.py \
  --context-details /tmp/strict_exchange_p4_class6_context_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_context_identity_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_cut_census.py \
  --output /tmp/strict_exchange_p4_class6_cut_census_audit.json
```

The two verifiers import no solver or production encoder.  The context use map
is regenerated by an encoding-shared audit; it remains an external-review
boundary rather than independent evidence for the game-to-formula implication.

The general witness-side projection is checked independently by

```text
python3 coopgames/verifiers/s6/verify_zero_anchor_overcover_duality.py \
  --output /tmp/zero_anchor_overcover_duality_audit.json
cmp /tmp/zero_anchor_overcover_duality_audit.json \
  coopgames/verifiers/s6/zero_anchor_overcover_duality_audit.json
```

For one zero anchor, the support value is the maximum non-anchor incidence
load.  With a witness at every anchor, the conjunction is exactly the
second-largest player load.  The audit checks this identity on 160 weighted
small menus, exhausts all 1,953 unordered pairs of nonempty proper
coalitions, replays the class-5 applications, and rejects replacing the
second-largest load by the largest.  This is standard convex duality and
eliminates witness coordinates only after blocker cuts have been chosen.

The all-class relay audit imposes `x3<=x4` versus `x3>x4` at every packet root.
All eleven classes then close, with class 10 alone requiring its nested
`x1<=x2` versus `x1>x2` split:

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py \
  --output /tmp/strict_exchange_p4_universal_order_relays.json
cmp /tmp/strict_exchange_p4_universal_order_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json
```

This audit shares the parent encoder.  It is a structural decomposition, not
an independent certificate or an all-human proof of the four remaining rows.

The reduced `52+71+90` large-case cores also have a solver-free activation
atlas audit:

```text
python3 coopgames/verifiers/s6/audit_strict_exchange_large_case_activation_atlas.py \
  --output /tmp/strict_exchange_large_case_activation_atlas.json
cmp /tmp/strict_exchange_large_case_activation_atlas.json \
  coopgames/verifiers/s6/strict_exchange_large_case_activation_atlas.json
```

It expands all 19 selected role schemas to 136 labelled directions and checks
their min/max order-statistic activation formulas on all 4,683 labelled weak
orders, for 636,888 comparisons.  It also checks the three-template census of
2,512 eligible negative cuts and 17,584 comparison occurrences.  It
deliberately excludes feasibility of the blocker consequents; its result
humanizes activation and cut shape without proving the finite coexistence
contradiction.

Finally, `../strict_exchange_formula_interface.json` is the literal
human-to-machine manifest.  It parses all frozen strict formulas and verifies
that each declares only the 48 expected selection/witness reals, has the same
72 documented base assertions, and contains only the recorded direction
implications afterward.  It maps every implication to its named assertion and
negative-cut count.  This audit excludes hidden machine premises; the human
soundness proof remains `paper5/S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md`.

`../strict_exchange_semantic_interface.json` is the independent semantic
differential.  Its generator imports none of the production formula machinery,
rebuilds the anchors, first-affected-level predicates, and every negative cut,
then checks each of the 1,332 frozen assertions for local logical equivalence.
It reconstructs 4,722 cut alternatives and 33,054 individual comparisons.  It
checks the transcription from the documented mathematics into SMT, not the
human proof that those documented premises are necessary.

The sharp lower-bound witness also has a targeted exact end-to-end regression:

```bash
python3 coopgames/verifiers/s6/verify_g23_witness.py
```

It reconstructs the lower envelope, checks a generator attains every
coalition value (hence exactness), recomputes both selections using the
repository's exact-rational staged LP implementation, and verifies
`distance = 4`, `T = 6`, and `rho = 2/3`. It is a bug audit; the family
theorem in the manuscript supplies the human proof of the lower bound.

## Pinned checker sources

- cvc5 tag `cvc5-1.3.3`, commit
  `8ff882e3e42f046867d2ac2e33e92b3d026144ae`, including
  `proofs/eo/cpc/`;
- Ethos commit `59e9ea6a077e1fd73dfc3107966b9f5603896c86`.

Both are official cvc5 repositories.  Build Ethos from that commit with

```text
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

## Reproduction template

Run from the repository root, replacing the three tool paths:

```text
PYTHON=.../python3
Z3=.../z3
CVC5=.../cvc5
ETHOS=.../ethos
CPC_SIGNATURES=.../cvc5/proofs/eo/cpc

$PYTHON coopgames/verifiers/s6/export_core_closure_smt.py \
  --index 1408 --mode equality-no-triple \
  --output /tmp/equality_no_triple_index1408.smt2

$PYTHON coopgames/verifiers/s6/replay_core_closure_smt.py \
  --formula /tmp/equality_no_triple_index1408.smt2 \
  --z3 $Z3 --cvc5 $CVC5 --ethos $ETHOS \
  --cpc-signatures $CPC_SIGNATURES --timeout-seconds 120 \
  --cpc-proof /tmp/equality_no_triple_index1408.cpc \
  --output /tmp/equality_no_triple_index1408.json
```

The analogous modes are `failure` at index 0, and all four equality modes
(`equality-noncanonical`, `equality-no-common-triple`, `equality-no-triple`,
`equality-subthird`) at indices 1408 and 2236.  Compare the regenerated
formula/proof hashes and the final `PASS`/`correct` fields with the committed
JSON records.

An offline integrity check regenerates every formula from the current exporter
and `triage32.json`, checks byte identity, and then verifies all committed
formula/proof hashes and recorded Ethos verdicts:

```text
python3 coopgames/verifiers/s6/verify_frozen_certificates.py
python3 coopgames/verifiers/s6/verify_positive_handover_certificates.py
python3 coopgames/verifiers/s6/reproduce_starved_universal_exchange.py
```
