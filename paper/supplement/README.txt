Online Resource 1
=================

Article:  Coalitional monotonicity and the core: minimal impossibility, an
          exact-games escape, and the boundary of surplus-distributor
          solutions
Journal:  International Journal of Game Theory (submitted)
Author:   Maxwell Flanagan
Contact:  maxwell.flanagan@gmail.com

Caption:  Machine-readable exact-rational certificates for all computational
          theorems of the article (game tables, per-coalition exactness
          witnesses, satisfaction/excess tables, balancing weights for every
          cumulative level set, Farkas multipliers, the disjoint n=5 circuit
          frontier and its neutralization duals, the glued n=6
          forbidden-ratio circuit, the exhaustive fixed-{5} glued audit,
          the Peleg coefficient-ceiling counterexample and its lifted
          eight-player gluing audit, the complete six-player Peleg census,
          the ratio-five seven-player gluing frontier, and the first-leaf-
          uniform unit root-absorption theorem,
          and segment samples),
          together with a self-contained verifier and an environment
          manifest.

Contents:
  certificates.json   Core theorem certificate data (exact rationals as
                      strings); the Type-I exactness dual is encoded
                      explicitly in verify_paper.py.
  circuit_frontier.json
                      Complete exact data for the (3,2,0) disjoint shape:
                      420 circuit orbits and their rational neutralization
                      certificates through maximum support thirteen.
  circuit_frontier_221.json
                      Complete exact data for the (2,2,1) disjoint shape:
                      189 circuit orbits and their rational neutralization
                      certificates through maximum support thirteen.
  forbidden_ratio_glued_circuit_n6.json
                      Exact local-block gluing, global nullity-one circuit,
                      forbidden arm ratios, and non-scalar capacity-one
                      primal--dual certificate.
  glued_local_circuit_hunt_n6_321.json
                      Factorized local-circuit enumeration, 5,035 exact
                      capacity screens, 21 deficient nonexclusive
                      circuits, and canonical fixed-witness certificates.
  glued_product_forbidden_fixed16_audit_n6_321.json
                      Exact fixed-{5} audit of all 59,304 product-forbidden
                      gluings: minimum capacity 9/8, complete capacity and
                      dual-template histograms, and sharp certificates.
  glued_fixed16_dual_arrangement_n6_321.json
                      Exact enumeration of all 87 feasible dual-arrangement
                      rays and all 5,159,448 ray--circuit evaluations. The
                      arrangement minimum reproduces the LP histogram.
  glued_fixed16_local_factorization_n6_321.json
                      Exact root--leaf factorization of all 87 ray
                      inequalities. It uses 59,595 local comparisons and
                      covers all 105,168 raw local gluing triples; embedded
                      local circuits permit dependency-free rechecking.
  glued_fixed16_analytic_compression_n6_321.json
                      Degree-only compression to 12 root mass types. It
                      proves 86 rays directly and records the three exact
                      root-incidence checks for the exceptional ray, for
                      1,047 comparisons in total.
  peleg_coefficient_ceiling_escape_n7.json
                      Exact Peleg case-2 disproof of the proposed
                      q_A <= |A|m_A leaf bound: 186 seven-player violations,
                      including ratio four on a two-player arm, plus the
                      rank-certified three-player lift.
  lifted_bad_leaf_gluing_n8.json
                      All 168 exact nullity-one gluings of the ratio-four
                      eight-player leaf with the lifted 56 roots and three
                      second leaves. The minimum fixed-{5} capacity is 9/8.
  peleg_descendant_arm_ratio_n8.json
                      Exact one-generation closure of the seven-player
                      violations (17,921 descendants) and 377,154 targeted
                      next-generation tests; no three-player ratio exceeds
                      four in this finite search.
  full_n5_peleg_escape_n7.json
                      Complete four-case Peleg generation: 1,292 five-player
                      sources reproduce all 200,214 six-player minimal
                      balanced collections and yield 1,320 ratio-five
                      three-arm leaves on seven players.
  ratio5_leaf_orbits_n7.json
                      Exact classification of those 1,320 leaves into four
                      distinguished-arm symmetry orbits.
  ratio5_bad_leaf_gluing_n7.json
                      All 168 exact gluings of one ratio-five leaf with the
                      lifted roots and second leaves. Twenty-one capacities
                      are below 9/8; the exact minimum is 13/12.
  ratio5_leaf_orbit_gluings_n7.json
                      Canonical audit of all four leaf orbits, covering 672
                      global circuits. Every orbit breaks 9/8; none breaks 1.
  unit_root_absorption_n7.json
                      Exact absorbers and matching primal--dual remainder
                      certificates for all 168 root--second-leaf pairs. The
                      normalized reserve is at least 1/3 and the result is
                      uniform over every compatible first leaf.
  root_absorption_descendants_n7.json
                      All-four-case Peleg lift of the certified roots: 604
                      distinct seven-player roots, 1,812 root--second pairs,
                      zero absorber failures, and unchanged minimum reserve
                      1/3.
  peleg_case1_absorption_closure.json
                      Exact interpolation-potential certificates proving
                      Peleg case-1 closure: 93 direct root-only lifts and 66
                      adversarial markings in five nonnegative types.
  peleg_case23_absorption_closure.json
                      Exact corrected-potential sign audit proving all 113
                      case-2 emissions preserve absorption, and structural
                      classification of the 104 case-3 splits.
  peleg_case3_split_transport.json
                      Exact closure certificate for all 104 case-3
                      emissions: role-specific split potentials, 21 sharp
                      B-loss dual certificates, 50 root-only b-split
                      absorbers, and 36 split-aware residual lifts.
  peleg_case4_split_aware_closure.json
                      Exact closure certificate for all 228 two-parent
                      case-4 emissions and all 684 root--second pairings,
                      using source-side split-aware absorbers.
  hunt_glued_local_circuits.py and dependencies
                      Reproducible exhaustive generator for the preceding
                      audit. Run:
                        python hunt_glued_local_circuits.py \
                          --audit-witness 16 --output rerun.json
                      The run takes about five minutes in the recorded
                      environment and uses SciPy, SymPy, and NumPy.
  audit_glued_fixed16_arrangement.py
                      Exact arrangement generator and all-ray evaluator. Run:
                        python audit_glued_fixed16_arrangement.py \
                          glued_product_forbidden_fixed16_audit_n6_321.json \
                          --evaluate --output rerun-arrangement.json
  audit_glued_fixed16_local_factorization.py
                      Exact local-factorization generator. Run:
                        python audit_glued_fixed16_local_factorization.py \
                          --output rerun-local-factorization.json
  audit_glued_fixed16_analytic_compression.py
                      Standard-library analytic compression audit. Run:
                        python audit_glued_fixed16_analytic_compression.py \
                          --input glued_fixed16_local_factorization_n6_321.json \
                          --output rerun-analytic-compression.json
  hunt_peleg_coefficient_ceiling_escape.py
                      Reproduces the seven-player coefficient-ceiling
                      counterexamples and the rank-certified lift. Run:
                        python hunt_peleg_coefficient_ceiling_escape.py \
                          --output rerun-peleg.json
  audit_lifted_bad_leaf_gluing_n8.py
                      Reproduces the 168 lifted global circuits and their
                      exact fixed-witness capacities. Run:
                        python audit_lifted_bad_leaf_gluing_n8.py \
                          --output rerun-lifted.json
  hunt_peleg_descendant_arm_ratio.py
                      Runs the two-generation targeted Peleg frontier. Run:
                        python hunt_peleg_descendant_arm_ratio.py \
                          peleg_coefficient_ceiling_escape_n7.json \
                          --output rerun-descendants.json
  hunt_full_n5_peleg_escape.py and classify_ratio5_leaf_orbits.py
                      Reproduce the complete six-player census, ratio-five
                      leaves, and their four symmetry orbits.
  audit_ratio5_bad_leaf_gluing_n7.py and
  audit_ratio5_leaf_orbit_gluings_n7.py
                      Reproduce the 168-circuit representative audit and the
                      672-circuit four-orbit audit.
  audit_unit_root_absorption_n7.py
                      Reproduces the exact first-leaf-uniform absorber audit.
                      Run:
                        python audit_unit_root_absorption_n7.py \
                          --output rerun-unit-absorption.json
  hunt_root_absorption_descendants_n7.py
                      Reproduces the all-four-case root-descendant screen.
                      Run:
                        python hunt_root_absorption_descendants_n7.py \
                          --output rerun-root-descendants.json
  audit_peleg_case1_absorption_closure.py
                      Reproduces the exact case-1 closure certificates. Run:
                        python audit_peleg_case1_absorption_closure.py \
                          --output rerun-case1-closure.json
  audit_peleg_case23_absorption_closure.py
                      Reproduces the case-2 proof audit and case-3
                      classification. Run:
                        python audit_peleg_case23_absorption_closure.py \
                          --output rerun-case23-closure.json
  audit_peleg_case3_split_transport.py
                      Reproduces the complete case-3 closure audit. Run:
                        python audit_peleg_case3_split_transport.py \
                          --output rerun-case3-closure.json
  audit_peleg_case4_split_aware_closure.py
                      Reproduces the complete case-4 closure audit. Run:
                        python audit_peleg_case4_split_aware_closure.py \
                          --output rerun-case4-closure.json
  verify_paper.py     Standalone verifier; requires only Python >= 3.8
                      standard library. Run:  python3 verify_paper.py
  environment.txt     Environment used for the original computations.

The verifier recomputes every satisfaction and excess table from scratch,
checks stored level sets against recomputed ones, validates all balancing
weights and Farkas multipliers by pure rational arithmetic, and confirms
the witness comparisons stated in the article. It also reconstructs the
disjoint n=5 unit circuit, verifies a balanced negative-right-hand-side
family, and checks coefficientwise the exact rational dual proving that this
six-support circuit orbit is nonnegative on exact endpoints. It also verifies
the eight original follow-on symmetry types (96 transported supports),
including exact rank/nullity-one checks for the original nine prototypes, and
then verifies both complete bundled frontiers, the glued six-player
forbidden-ratio circuit, the sharp deficient nonexclusive circuit, every
stored 9/8 fixed-witness frontier certificate, and the complete 87-ray
arrangement summary. It independently reconstructs every stored local
circuit and all 59,595 root--leaf comparisons in the stronger
local-factorization certificate, then rechecks the 1,047-comparison
degree-only analytic compression and its exceptional three-root correction.
It additionally verifies all 186 Peleg violations, the rank-seven
three-player lift, and all 168 lifted eight-player global circuits and their
fixed-witness certificates. It also checks all 168 explicit unit absorbers
and their exact dual reserve certificates. The earlier frontier component checks 611 exact
circuit records (5,670 transported five-player supports plus the two glued
supports). For the
(3,2,0) shape, 411
orbits (4,812 supports) are neutralized by balancedness, eight (96 supports)
by balancedness plus bump nonnegativity, and the remaining six-support Type-I
orbit by endpoint exactness. For the (2,2,1) shape, 117 orbits (468 supports)
are neutralized by balancedness and the remaining 72 (288 supports) by
balancedness plus bump nonnegativity. The exact terminal UNSAT enumerations
are rerun by the development script
src/enumerate_disjoint_circuits_exact.py, which requires Z3; this packaged
standard-library verifier independently checks every emitted circuit, orbit,
balanced collection, bump multiplier, and coefficient identity.
Expected output ends with
"ALL CHECKS PASSED".
