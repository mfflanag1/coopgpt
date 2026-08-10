# External review request: fixed-n overlap and constructive packet extraction

Please audit the research checkpoint on branch
`codex/fixed-n-handover-facets`.  Treat every novelty statement as provisional.
The two principal notes are:

```text
paper5/FIXED_N_UPPER_BOUND_PROGRAM.md
paper4/ALGORITHMIC_PACKET_THEOREM.md
```

The computational bug audit is:

```text
verifiers/divergence/audit_overlap_bound.py
verifiers/divergence/overlap_audit.json
```

## Questions requiring hostile review

1. Verify the identities
   `||Lmin-Lmax||_1=2(T-sum_i min(Lmin_i,Lmax_i))` and the equivalence of
   the proposed sharp fixed-`n` bound with the hybrid-cut inequality `(H_n)`.
2. Audit the null-player reduction carefully: does a coordinate that vanishes
   throughout the core of an exact game really imply
   `v(S)=v(S\{i})` for every coalition, with both Lmin and Lmax preserved on
   deletion?
3. Recheck the closed-form crossover proof for the starved family `C_n` and
   balanced `G(p,k)`: starved wins at five, the families tie at six, and `G`
   wins from seven onward.  Assess whether the claimed structural explanation
   is genuinely informative or merely a restatement of the formulas.
4. Try to refute the surviving hybrid-overlap conjecture.  In particular, do
   not assume the comparison cut is balanced: the archived exact six-player
   equality examples explicitly disprove that stronger route.
5. Audit the direct packet-extraction argument.  Check boundedness of `C_H`,
   positivity of some `G_j`, passage to an optimal basic feasible solution,
   the inference from independent positive trace columns to a minimal balanced
   collection, and the `|N|-1` support count.
6. Check that feasibility system `(D)` is exactly the established
   decomposability notion for minimal semi-balanced systems, including the
   scaling of the negative coefficient and the exclusions on `E`.
7. Search specifically for prior work containing an equivalent
   Lmin-boundary two-LP extraction or linear-size rooted obstruction.  The
   exact-cone facet equivalence itself is explicitly treated as prior art.

## Reproduction

Run from `coopgames/..` (the repository root):

```bash
python3 -m py_compile coopgames/verifiers/divergence/audit_overlap_bound.py
python3 coopgames/verifiers/divergence/audit_overlap_bound.py \
  --output /tmp/overlap-audit-current.json \
  coopgames/verifiers/divergence \
  coopgames/verifiers/s6 \
  coopgames/results/n5_exact_lmin_lmax_large_core.json \
  coopgames/results/n5_unique_richest_boundary.json \
  coopgames/results/n6_two_poorer_suffix_counterexample.json
cmp coopgames/verifiers/divergence/overlap_audit.json \
  /tmp/overlap-audit-current.json
```

Expected audit totals are 701 parsed pairs, 375 at `n=6`, no violation of the
global candidate among archived `n>=6` pairs, three failures of the stronger
cut-size claim, and five exact `n=6` equality records.  These counts are only
reproducibility and bug-finding evidence; they are not a proof of `(H_6)`.

Please separate your verdict into: proved as written; repairable gap; false;
novelty unclear; and prior art.  The most important outcome is whether the
packet LP theorem is correct and whether the hybrid-overlap reduction exposes
a plausible route to a genuine fixed-dimension theorem.

## Addendum: sparse Lmax over-cover checkpoint

Also audit the subsequent files:

```text
paper5/LMAX_OVERCOVER_COUPLING.md
verifiers/divergence/audit_lmax_overcover.py
verifiers/divergence/lmax_overcover_audit.json
```

In particular, check:

1. every sign in the first-stage Lmax dual and the objective identity
   `M=sum lambda_A v(A)-eta T`;
2. the `n`-coalition support bound and its preservation when dispersion
   `theta=min max alpha_i` is optimized;
3. the deduction `alpha.Lmin>=M` and the spectral excess condition (4);
4. the direction of the rearrangement inequality used in `(SA)`;
5. the first-stage Lmin under-cover companion `(UC)`, including its signs and
   `n-1` support count;
6. whether the five equality certificates really justify describing the
   three-player dispersed anchor as a common equality geometry;
7. the precise remaining gap: the archive audit is not an exhaustive
   six-player theorem, and the abstract spectra in §6 rule out silently
   replacing exact-game realizability by arbitrary equal-sum vectors.

Reproduce the new artifact with:

```bash
python3 coopgames/verifiers/divergence/audit_lmax_overcover.py \
  --output /tmp/lmax-overcover-current.json \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  coopgames/verifiers/divergence/summary2.json
cmp coopgames/verifiers/divergence/lmax_overcover_audit.json \
  /tmp/lmax-overcover-current.json
```

## Addendum: exactification boundary and generator normal form

The next checkpoint materially changes the completion route.  Audit these
files before accepting any computer-assisted six-player claim:

```text
paper5/TWO_PACKET_EXACTIFICATION_BOUNDARY.md
paper5/CORE_CLOSURE_REDUCTION.md
verifiers/s6/audit_two_packet_exactification.py
verifiers/s6/two_packet_exactification_audit.json
verifiers/s6/verify_two_packet_staged_certificates.py
verifiers/s6/core_closure_pipeline.py
verifiers/s6/coverage32.py
verifiers/s6/coverage32.json
verifiers/s6/audit_core_closure_reconstruction.py
verifiers/s6/core_closure_reconstruction_audit.json
verifiers/s6/run_core_closure_census.py
verifiers/s6/rerun_core_closure_unknowns.py
verifiers/s6/merge_core_closure_census.py
paper5/S6_GENERATOR_CENSUS_CHECKPOINT.md
paper5/S6_EQUALITY_CLASSIFICATION.md
verifiers/s6/core_generator_census.json
verifiers/s6/equality_triple_census.json
verifiers/s6/equality_no_triple_census.json
verifiers/s6/verify_equality_checkpoint.py
verifiers/s6/audit_starved_4_2_barrier.py
verifiers/s6/audit_equality_refinement_neighborhood.py
verifiers/s6/equality_refinement_neighborhood_audit.json
verifiers/s6/certificates/README.md
verifiers/s6/export_core_closure_smt.py
verifiers/s6/replay_core_closure_smt.py
verifiers/s6/verify_frozen_certificates.py
verifiers/s6/export_positive_handover_smt.py
verifiers/s6/export_positive_lmax_boundary_smt.py
verifiers/s6/export_positive_lmax_critical_boundary_smt.py
verifiers/s6/verify_positive_handover_certificates.py
verifiers/s6/audit_positive_lmax_direction_layers.py
verifiers/s6/positive_lmax_direction_layers_audit.json
verifiers/s6/audit_positive_lmin_handover_layers.py
verifiers/s6/merge_positive_lmin_handover_layers.py
verifiers/s6/reproduce_positive_lmin_handover_layers.py
verifiers/s6/positive_lmin_handover_layers_audit.json
verifiers/s6/audit_positive_common_gap_pairs.py
verifiers/s6/positive_common_gap_pair_audit.json
verifiers/s6/export_positive_lmin_critical_boundary_smt.py
verifiers/s6/audit_positive_lmin_critical_boundary.py
verifiers/s6/positive_lmin_critical_boundary_map.json
verifiers/s6/certificates/positive_lmin_critical_boundary_*.smt2
verifiers/s6/certificates/positive_lmin_critical_boundary_*.cpc
verifiers/s6/certificates/positive_lmin_critical_boundary_*.json
verifiers/s6/certificates/positive_lmax_direction_index0040.smt2
verifiers/s6/certificates/positive_lmax_direction_index0040.cpc
verifiers/s6/certificates/positive_lmax_direction_index0040.json
verifiers/s6/certificates/positive_lmax_direction_index0200.smt2
verifiers/s6/certificates/positive_lmax_direction_index0200.cpc
verifiers/s6/certificates/positive_lmax_direction_index0200.json
verifiers/s6/certificates/positive_lmax_direction_index0504.smt2
verifiers/s6/certificates/positive_lmax_direction_index0504.cpc
verifiers/s6/certificates/positive_lmax_direction_index0504.json
verifiers/s6/certificates/positive_lmax_boundary_n_l.smt2
verifiers/s6/certificates/positive_lmax_boundary_n_l.cpc
verifiers/s6/certificates/positive_lmax_boundary_n_l.json
verifiers/s6/certificates/positive_lmax_boundary_n_j_k_r.smt2
verifiers/s6/certificates/positive_lmax_boundary_n_j_k_r.cpc
verifiers/s6/certificates/positive_lmax_boundary_n_j_k_r.json
verifiers/s6/certificates/positive_lmax_boundary_n_j_l_r.smt2
verifiers/s6/certificates/positive_lmax_boundary_n_j_l_r.cpc
verifiers/s6/certificates/positive_lmax_boundary_n_j_l_r.json
verifiers/s6/certificates/positive_lmax_boundary_n_k_l_r.smt2
verifiers/s6/certificates/positive_lmax_boundary_n_k_l_r.cpc
verifiers/s6/certificates/positive_lmax_boundary_n_k_l_r.json
verifiers/s6/certificates/positive_lmax_critical_boundary.smt2
verifiers/s6/certificates/positive_lmax_critical_boundary.cpc
verifiers/s6/certificates/positive_lmax_critical_boundary.json
```

Hostile questions:

1. Confirm that the two first-stage incidence supports and both individual
   cross inequalities really permit the displayed unnormalized overlap `1/2`.
   Confirm independently that adjoining the three singleton witnesses preserves
   those supports but changes the first Lmin pinned set and restores overlap
   exactly to `2/3`.
2. Check the individual floor-pinning dual `(IP1)--(IP2)` in both directions,
   including every sign and the complementary-slackness restriction to
   trial-tight coalitions.  Then check the recursive `(SP-min)--(SO-min)` and
   `(SP-max)--(SO-max)` identities, especially the signs on the current-block,
   distinguished-player, old-pin, and efficiency terms.  The frozen boundary
   audit now contains 24 exact staged certificates; independently replay them
   with `verify_two_packet_staged_certificates.py`.
3. Audit the core-closure lemma: for
   `cl_C(S)=min_{y in C}y(S)`, is `Core(cl_C)=C`, is compactness justified,
   and do six zero-coordinate core witnesses suffice for singleton
   normalization?
4. Audit the stronger certificate-preserving finite exactification theorem.
   Given Lmin `x`, Lmax `z`, and one singleton witness per player, does their
   lower envelope always preserve every coalition used by the staged Farkas
   certificates and therefore preserve every lexicographic stage?  Try to find
   a counterexample to the claimed `n+2`-generator normal form.
5. Compare `pipeline2_core_closure` with
   `pipeline2_generator_normal_form`.  The latter removes `v(S)` entirely and
   marks a coalition support-eligible at `x` only when all other displayed
   generators have at least the `x` coalition sum (and mirrors this at `z`).
   Verify that this is existence-equivalent, not a strengthening.
6. Hostilely recheck the full staged Farkas signs inherited from `nsix.py`, the
   order of the Lmax blocks, the strict stratum inequalities, the contingency
   table convention, and the equivalence between L1 distance `>2/3` and overlap
   `<2/3` at total one.
7. Treat every current SMT count as solver evidence only.  A completed census
   still needs exact coverage reconciliation, isolated reruns of every timeout,
   independent proof evidence or rational infeasibility certificates, equality
   classification, and specialist review.
8. Audit the completed accepted-output merge: it reports all 3,350 survivors
   `UNSAT`, with no `SAT` or `UNKNOWN`.  Verify that every survivor index is
   present, each stored configuration equals `triage32.json`, all overlapping
   decisive rows agree, and all 17 earlier timeouts have decisive isolated
   generator-normal-form reruns.  Do not treat the merged JSON as an
   independently replayable infeasibility certificate.
9. Audit the representative CPC proof-object lane separately from the census.
   Confirm that the SMT exporter preserves the Z3 AST, that Z3 and cvc5 decide
   the identical frozen bytes, and that Ethos checks the CPC bodies against the
   pinned cvc5 1.3.3 signatures.  The strict-failure object remains
   representative only.  The eight equality objects cover rigidity,
   common-triple, no-triple, and sub-third negations in both solver-surviving
   equality types, but do not
   prove the 3,348 other types infeasible.
10. Audit the equality split as a genuine partition: equality with at least one
    tight Lmax-top triple versus equality with none.  Reconcile `2/3348/0` and
    `0/3350/0`, verify the two exact reconstructions, and check that the
    noncanonical CPC formulas really force the complete payoff pair rather
    than only one chosen level.  Separately check the no-common-triple formulas
    and the short algebra in `S6_EQUALITY_CLASSIFICATION.md` deriving both
    canonical payoff pairs from a common tight top triple.
11. Audit the first-crossing reduction in `S6_EQUALITY_CLASSIFICATION.md`.
    In particular, check convexity of the exact-game cone, exactness and
    singleton normalization along the unanimity path, continuity of both lex
    selections under the stated Slater condition, and the inference that a
    nearby table is a contiguous refinement.  Confirm that the complete
    positive handover covers all 1,659 positive refinements directly, not by
    extrapolating from the 22 one-split cases.  Reproduce the four bounded
    shards and merged `starved_packet_handover_audit.json`: exactly 504
    starved-only refinements, Lmin-only SAT 58, Lmax-only SAT 236, intersection
    zero, and both UNSAT 210.  Hostilely test the separator choosing Lmax iff
    a coarse-rich player lies strictly below both coarse-P players in refined
    Lmax; reconcile the `128/376` selected-packet split and verify the selected
    packet is UNSAT in every row.  Treat this starved handover as solver census
    evidence until it receives the same abstract proof-object compression as
    the positive side.  Separately reproduce
    `starved_refinement_direction_audit.json`: six Lmin and two Lmax payoff
    direction templates must close 222 rows by direct blocker checks, leaving
    282 staged-information rows.
12. Audit the human index-1408 barrier separately from the census.  Check the
    gap coordinates `u,v,w`, the identity `1=6c+8v-4w`, the inference
    `v>1/6 => 2w>v`, and the coalition count argument proving
    `h=(0,0,1,1,-1,-1)` is feasible at every Lmin-tight coalition.  Confirm
    that a small positive perturbation improves the sorted Lmin vector and
    that the equality case forces the canonical starved payoff pair.
13. Audit the human index-2236 barrier separately.  Check the eight exchange
    directions, the complete blocker classification when `w<2v`, and each of
    the zero/one/two/three-atom budget cases.  In particular verify every use
    of `c+5d>1`, `c+6d>1`, and `3c+9d>2`.  Then check the Lmin argument forcing
    `w=2v`, the three common tight triples, and the deduction
    `2q(P)>=9d => d<=2/9 => v<=1/9`.  Decide whether the small QF_LRA audit
    really matches the written exchange lemma.  Do not infer from these two
    coarse-profile barriers that arbitrary simultaneous stratum refinements
    have already been controlled.  Also check the equality corollary that the
    singleton-rich witness is uniquely `(0,0,1/3,1/3,1/3,0)` and that the
    exact local blocker residue consists only of the three common triples.
    Hostilely check the compactness and strict-margin steps in the resulting
    positive critical-residue theorem, especially the claimed uniform
    neighborhood and the two-of-three hitting-set conclusion.
14. Audit the negative control in `positive_critical_relaxation_audit.json`.
    Verify the displayed distance `31/45`, all six indexed zero-coordinate
    witnesses, all three common-triple equalities, and the affine local ray
    with distance `2/3+lambda/45`.  Then discard the claimed selections,
    reconstruct the lower-envelope game, and independently check the complete
    `(3,2,1)` Lmin and `(2,1,3)` Lmax traces, all twelve pinning certificates,
    and true distance `4/9`.  Treat this as a falsification of triple-only
    tangent arguments, not as a counterexample to the six-player conjecture.
15. Reproduce `positive_one_split_residue_audit.json`.  Confirm that the
    positive coarse-or-one-split neighborhood has eleven hand-net survivors,
    that the critical triples, exactness, and locally persistent cross-cell
    signs exclude nine, and that precisely indices 1442 and 2268 remain before
    the explicit Lmin directions are imposed.  Audit the two direction-count
    arguments and the direct index-1414 algebra.  Confirm that the earlier
    three-row residue was correctly withdrawn because its 1414 SAT point had
    the wrong local sign.  Check the common witness inequality
    `2x(P)+3x_r<=2` and every row of the seven-case table against the stored
    contingency tables.  In particular, do not infer a simultaneous-split
    reduction from this one-split theorem.
16. Reproduce `positive_two_sided_ablation_audit.json`.  For index 239 verify
    that the complete staged Lmin packet is retained, the displayed distance
    is `449/516`, exact closure preserves Lmin, changes Lmax, and produces true
    distance `118/387`.  For index 212 check the mirror statement with full
    staged Lmax, displayed distance `553/825`, changed Lmin, and true distance
    `53/165`.  Independently inspect both exact games, both selection
    formulations, and all 24 pinning certificates.  Decide whether these
    controls establish only that neither fixed one-sided packet is universal,
    rather than the stronger and now-withdrawn claim that both packets must be
    coupled inside every simultaneous-split support type.
17. Reproduce the fast structural checks in
    `positive_packet_ablation_census.json`, then rerun the expensive census if
    resources permit.  Confirm that all 1,659 positive refinements are decided,
    that the Lmin-only and Lmax-only SAT sets have sizes 38 and 257, and that
    their intersection is empty.  Hostilely test the proposed handover rule:
    choose Lmax for rich-player Lmax isolation or the `(1,1,2,2)` first-high-
    block exception, and Lmin otherwise.  Treat this as a separator of solver
    verdicts and a human-proof target, not as independent proof evidence.
18. Reproduce `positive_lmax_handover_directions.json` and
    `positive_lmin_handover_directions.json`.  Confirm the complete
    `230+109=339` and `901+322+97=1320` decompositions and zero unresolved
    rows.  For every reported direction, independently check efficiency,
    lexicographic improvement in the stated refined stratum, and the absence
    of a coalition that is both derivative-negative and eligible to be tight.
    Normalize directions by the `N,P,r` roles and verify the three templates
    on each side.  For the 97 menu cases, audit the fourteen directions
    `1_I-e_n-(|I|-1)e_r`, the all-directions-blocked quantifier, and the two
    exceptional tables 2597 and 3237.  Treat these exact blocker UNSAT verdicts
    as a compressed proof-discovery map, not as independent proof evidence.
    Reproduce the sharded Lmin dependency audit and reconcile the critical
    split `293+266+342`, direction split `71+14+5+232`, and menu split
    `13+64+20`.  Check carefully that removing blocker-witness inequalities
    does not remove the separate critical-triple witness system.  Treat these
    classifications as a map for abstract lemmas, not as proof objects.
    Audit the shared gap-pair classification across both sides: no feasible
    pair in `68+293` rows, exactly one pair in `146+266`, and no candidate
    surviving the third-gap comparison.  Then independently audit the promoted
    concordance/inversion lemma (34)--(35) and reproduce
    `positive_common_gap_order_lemma_audit.json`: 361 rows must have no P pair
    with the same weak relation in both payoff orders; each of the other 412
    must have one such pair and the third P player must be weakly lower in
    Lmin, weakly higher in Lmax, with strictness, relative to both pair
    members.  Check the deductions `delta_j=delta_k => x_j-x_k=z_j-z_k` and
    `delta_l<delta_j=-A` against the third comparison `delta_l>=-A`.  This is
    intended as a human proof with a combinatorial finite map, not an SMT
    infeasibility certificate.
    For the 342 coupled critical rows, verify that players are globally
    Lmin-sorted before recording the `N/P/R` word; specifically try to recreate
    the rejected mistake of placing both poor players first.  Reconcile 278
    one-pair rows, 64 three-pair rows, 470 mappings, and all eight abstract
    cases.  Check that each exporter retains only the claimed single Lmax
    relation, then replay all eight CPC proofs.
    Reproduce `positive_lmin_direction_patterns_audit.json` and confirm that
    the 322 single-direction rows yield 494 feasible-pair instances, twenty
    global-Lmin-normalized role/direction/pair patterns, and 23 minimized proof
    cases.  Hostilely check the global sort and direction permutation, every
    weak-order relation in the map, and coverage of all 494 instances.  Replay
    all 23 SMT/CPC controls and confirm Z3 UNSAT, cvc5 UNSAT, no trust markers,
    and Ethos `correct`.  Try to weaken each listed relation independently;
    distinguish subset-minimality under the deterministic deletion order from
    minimum cardinality.  Treat the finite mapping and the abstract formulas
    as separate dependencies, and do not infer a human proof from the proof
    objects alone.
    Reproduce `positive_lmin_menu_patterns_audit.json`.  Confirm that the 95
    ordinary rows use all lex-eligible members of the canonical fourteen-
    direction subset-exchange family, while indices 2597 and 3237 use exactly
    their stored exceptional menus.  Reconcile 97 rows, 161 pair instances,
    21 role/menu/pair patterns, and 22 minimized proof cases.  Audit the sole
    two-case refinement (`x_3<x_4` versus `z_3<z_4`), coverage of every mapping,
    and all direction/blocker signs.  Replay all 22 SMT/CPC controls and apply
    the same separation between finite mapping evidence, abstract implication,
    and human proof as for the single-direction layer.
19. Inspect the three representative positive-handover proof objects
    independently.  For survivor 40, confirm that the base critical system is
    feasible, direction
    `(0,0,0,-1,0,1)` lexicographically improves Lmax in that support type,
    and the blocker disjunction has the correct inequality direction for `x`
    and all six singleton witnesses, then audit the short gap calculation
    `(29)--(30)`.  Reproduce the dependency ablation:
    21 direction rows need neither distance nor witness blocker inequalities,
    80 need witnesses but not distance, and eight need both.  Survivors 40,
    200, and 504 represent those three templates, but cover only three of the
    109 single-direction Lmax rows and none of the 230 critical-algebra rows;
    do not extrapolate them to the complete branch.  For the 80-row template,
    independently verify that the sole payoff-comparison-eligible coalition
    is `N union {p}`, that the recorded `j` is below `p` in both selections,
    and that the zero-at-`p` witness plus `T_j` gives the stated disjoint-set
    contradiction.  Reproduce the promoted uniform proof and
    `positive_lmax_dominant_order_lemma_audit.json`: reconcile the 62 rows with
    two concordant pairs and the 18 with three; check that every common-pair
    alternative forces `delta_p=-A` or is excluded by gap inversion; then
    verify that only `N union {p}` can have nonnegative gap and that the unique
    low `j` makes the two disjoint witness lower bounds sum above one.  The
    order audit must perform no infeasibility solve.  For the 21-row template,
    audit the complete gap proof around direction `(31)`: the two `-2`
    players must occupy one cell and have forced common excluded-player
    triples, the `-1` player must share their Lmax level but have higher Lmin,
    and the four `(m,l)` cases must cover every coalition with negative
    derivative.  This is intended as a human direction lemma conditional on
    the finite stratum-pattern classification, not a proof of that
    classification without enumeration.
    For the eight-row boundary template, verify the shared weak coordinate
    order and the reduction to exactly the four coalitions in `(32)`.  Then
    audit each abstract SMT formula against its prose assumptions and replay
    its CPC proof.  Confirm that these formulas prove only that a displayed
    blocker forces distance at most `2/3`; the finite audit supplies the
    separate map from the eight tables to those blocker shapes.
    Finally, reproduce the `68+146+16=230` critical-algebra split.  Check that
    the first 68 use only signs/common-pair algebra, the next 146 also use the
    third triple comparison but neither distance nor witnesses, and all
    sixteen remaining rows fit the weak order in the abstract critical-boundary
    exporter.  Replay its CPC proof, while treating the 214-row payoff
    classification as finite solver evidence until uniform inequalities are
    written.  Verify the gap equivalence `(33)`: all 68 first-layer rows have
    no order-feasible equal-gap pair, while every one of the 146 second-layer
    rows has exactly one candidate pair and that pair fails only when the
    third-gap comparison is added.

Reproduce the two exact reconstruction controls from the repository root:

```bash
python3 coopgames/verifiers/s6/audit_two_packet_exactification.py \
  --output /tmp/two-packet-current.json
cmp coopgames/verifiers/s6/two_packet_exactification_audit.json \
  /tmp/two-packet-current.json
python3 coopgames/verifiers/s6/verify_two_packet_staged_certificates.py
python3 coopgames/verifiers/s6/verify_frozen_certificates.py
python3 coopgames/verifiers/s6/verify_positive_handover_certificates.py
python3 coopgames/verifiers/s6/verify_equality_checkpoint.py
python3 coopgames/verifiers/s6/audit_starved_4_2_barrier.py
python3 coopgames/verifiers/s6/audit_positive_5_1_barrier.py
python3 coopgames/verifiers/s6/audit_positive_critical_relaxation.py \
  --output /tmp/positive-critical-current.json
cmp coopgames/verifiers/s6/positive_critical_relaxation_audit.json \
  /tmp/positive-critical-current.json
python3 coopgames/verifiers/s6/audit_positive_one_split_residue.py \
  --output /tmp/positive-one-split-current.json
cmp coopgames/verifiers/s6/positive_one_split_residue_audit.json \
  /tmp/positive-one-split-current.json
python3 coopgames/verifiers/s6/audit_positive_two_sided_ablation.py \
  --output /tmp/positive-two-sided-current.json
cmp coopgames/verifiers/s6/positive_two_sided_ablation_audit.json \
  /tmp/positive-two-sided-current.json
python3 coopgames/verifiers/s6/audit_positive_packet_ablation_census.py \
  --output /tmp/positive-packet-census-current.json
cmp coopgames/verifiers/s6/positive_packet_ablation_census.json \
  /tmp/positive-packet-census-current.json

# Expensive: recomputes all 3,318 one-sided solver instances (30 s cap each).
python3 coopgames/verifiers/s6/audit_positive_packet_ablation_census.py \
  --recompute --output /tmp/positive-packet-census-recomputed.json

python3 coopgames/verifiers/s6/search_positive_handover_directions.py \
  --selected-side max --bound 3 --timeout-ms 1000 \
  --output /tmp/positive-lmax-handover-current.json
cmp coopgames/verifiers/s6/positive_lmax_handover_directions.json \
  /tmp/positive-lmax-handover-current.json
python3 coopgames/verifiers/s6/audit_positive_lmax_direction_layers.py \
  --output /tmp/positive-lmax-layers-current.json
cmp coopgames/verifiers/s6/positive_lmax_direction_layers_audit.json \
  /tmp/positive-lmax-layers-current.json

# Slower: full Lmin branch, including the canonical and exceptional menus.
python3 coopgames/verifiers/s6/search_positive_handover_directions.py \
  --selected-side min --bound 3 --max-single-directions 100 \
  --timeout-ms 30000 --allow-menus --canonical-menus \
  --output /tmp/positive-lmin-handover-current.json
cmp coopgames/verifiers/s6/positive_lmin_handover_directions.json \
  /tmp/positive-lmin-handover-current.json
python3 coopgames/verifiers/s6/reproduce_positive_lmin_handover_layers.py \
  --output /tmp/positive-lmin-layers-current.json
cmp coopgames/verifiers/s6/positive_lmin_handover_layers_audit.json \
  /tmp/positive-lmin-layers-current.json
python3 coopgames/verifiers/s6/audit_positive_common_gap_pairs.py \
  --output /tmp/positive-common-gap-current.json
cmp coopgames/verifiers/s6/positive_common_gap_pair_audit.json \
  /tmp/positive-common-gap-current.json
python3 coopgames/verifiers/s6/audit_positive_lmin_critical_boundary.py \
  --output /tmp/positive-lmin-critical-boundary-current.json
cmp coopgames/verifiers/s6/positive_lmin_critical_boundary_map.json \
  /tmp/positive-lmin-critical-boundary-current.json

(cd coopgames/verifiers/s6 && python3 coverage32.py)

python3 coopgames/verifiers/s6/audit_core_closure_reconstruction.py \
  --census coopgames/verifiers/s6/equality_triple_census.json \
  --output /tmp/core-closure-reconstruction-current.json
cmp coopgames/verifiers/s6/core_closure_reconstruction_audit.json \
  /tmp/core-closure-reconstruction-current.json

python3 coopgames/verifiers/s6/audit_equality_refinement_neighborhood.py \
  --output /tmp/equality-refinement-current.json
cmp coopgames/verifiers/s6/equality_refinement_neighborhood_audit.json \
  /tmp/equality-refinement-current.json
```

The second control reconstructs both equality-census SAT models, compresses
their singleton witnesses, forms each finite lower envelope, and recomputes
both selections with two independently formulated exact rational LP
implementations.  These are normal-form controls, not evidence that every
strict-failure configuration is infeasible.
