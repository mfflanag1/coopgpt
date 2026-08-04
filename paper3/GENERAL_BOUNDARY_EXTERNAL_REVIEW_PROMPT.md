# Hostile external-review prompt: balanced-trace transport and sharp thresholds

Please conduct a hostile mathematical and novelty review of the new
exact-balanced boundary framework and the sharp small-poorer boundary result.

## Primary files

- `coopgames/paper3/wrapper.pdf`: rendered manuscript; the new material is in
  Lemma 5.39 through Theorem 5.45 (numbers may shift after edits).
- `coopgames/paper3/sections_leximin.tex`: source labels
  `lem:lx-exact-balanced-slack`, `lem:lx-boundary-cover`,
  `cor:lx-boundary-defect`, `lem:lx-strict-richer-cover`,
  `cor:lx-exact-face-overload`,
  `thm:lx-balanced-trace-transport`,
  `thm:lx-integral-trace-obstruction`, `cor:lx-odd-trace-cycle`,
  `thm:lx-rooted-semigroup-obstruction`,
  `thm:lx-positive-lehman-trace-exclusion`,
  `cor:lx-lehman-internal-face`,
  `thm:lx-rank-two-trace-exclusion`,
  `thm:lx-four-rich-trace-classification`,
  `thm:lx-projective-plane-trace-exclusion`,
  `cor:lx-pg27-trace-exclusion`, and
  `thm:lx-small-poorer-threshold`.
- `coopgames/paper3/GENERAL_BOUNDARY_OBSTRUCTION.md`: expanded derivation,
  prior-art boundary, and research interpretation.
- `coopgames/paper3/N4_N5_STRUCTURAL_THRESHOLD.md`: standalone sacrifice-budget
  proof and four-generator obstruction family for every dimension at least five.
- `coopgames/paper3/N5_N6_SMALL_POORER_THRESHOLD.md`: standalone statement and
  human proof of the six-player construction.
- `coopgames/paper3/BALANCED_TRACE_TRANSPORT_PRIOR_ART.md`: focused search log,
  prior-art boundary, and cautious novelty statement.
- `coopgames/paper3/PROPERTY_I_STRICT_COVER_AUDIT.md`: primary-source comparison
  of the known property-I criterion with the quantitative strict cover.
- `coopgames/paper3/EXACT_PARTITION_CITATION_NETWORK_AUDIT.md`: reproducible
  forward-citation audit and claim-by-claim novelty matrix.
- `coopgames/paper3/INTEGRAL_TRACE_OBSTRUCTION.md`: standalone proof that
  every two-poorer failure forces a nonintegral active trace hypergraph and an
  odd balanced-matrix obstruction.
- `coopgames/paper3/RANK_TWO_TRACE_EXCLUSION.md`: standalone dimension-free
  proof that graph-like active traces cannot realize a two-poorer failure.
- `coopgames/paper3/ROOTED_SEMIGROUP_OBSTRUCTION.md`: standalone
  dimension-free theorem forbidding safe rooted integer fibres of tight
  coalition semigroups.
- `coopgames/paper3/EXACT_FACE_OVERLOAD_BUDGET.md`: real-valued internal-face
  inequality proposed as the common budget behind the four/five
  unique-richest threshold and the later rooted trace roundings.
- `coopgames/paper3/LEHMAN_TRACE_OBSTRUCTION.md`: reduction of positive Lehman
  dual rows to rooted covers and the new two-poor-label density criterion.
- `coopgames/paper3/LEHMAN_MINOR_LIFTING.md`: proof that preserving only the
  gaining-player deficit automatically removes both poor labels from every
  contracted column and lifts the Lehman conclusions to the original suffix.
- `coopgames/paper3/NONCORE_LEHMAN_LIFTING.md`: union-bound refinement that
  requires a Lehman dual selector to hit every noncore MNI row exactly once.
- `coopgames/paper3/SCALE_SEPARATED_MNI_BRIDGE.md`: big-M refinement under
  which preservation of one objective gap forces exactness on all rich rows.
- `coopgames/paper3/UNIT_GAP_MNI_BRIDGE.md`: explicit integral-cost set-cover
  gap whose strict unit threshold is equivalent to the gaining-player deficit.
- `coopgames/paper3/DEGENERATE_MNI_TRACE_EXCLUSION.md`: human elimination of
  the exceptional degenerate-projective-plane branch of Lehman's MNI theorem.
- `coopgames/paper3/LABELED_ODD_CYCLE_OBSTRUCTION.md`: augmented balanced-
  matrix proof retaining poor labels as rows rather than side annotations.
- `coopgames/paper3/H4_FIRST_OBSTRUCTION_CLASSIFICATION.md`: human
  classification proving uniqueness of the first surviving obstruction.
- `coopgames/paper3/PROJECTIVE_PLANE_TRACE_EXCLUSION.md`: human
  simple-point counting and star-rounding exclusion for projective-plane
  incidence packets.
- `coopgames/paper3/COMPLETE_BOUNDARY_SHAPE_CLASSIFICATION.md`: standalone
  statement and proof of the complete cardinality phase diagram.
- `coopgames/paper3/COMPLETE_BOUNDARY_EXTERNAL_REVIEW_PROMPT.md`: focused
  hostile checklist for the new universal family, Lmax, and phase theorem.

## Exact verification files

- `coopgames/src/verify_exact_balanced_slack_budget.py`
- `coopgames/results/exact_balanced_slack_budget.json`
- `coopgames/src/verify_n5_small_poorer_suffix.py`
- `coopgames/results/n5_small_poorer_suffix.json`
- `coopgames/src/verify_n5_unique_richest_boundary.py`
- `coopgames/results/n5_unique_richest_boundary.json`
- `coopgames/src/verify_unique_richest_family.py`
- `coopgames/results/unique_richest_family.json`
- `coopgames/src/verify_rich_block_family.py`
- `coopgames/results/rich_block_family.json`
- `coopgames/paper3/RICH_BLOCK_HOSTILE_REVIEW_RESPONSE.md`
- `coopgames/src/verify_n6_two_poorer_suffix_counterexample.py`
- `coopgames/results/n6_two_poorer_suffix_counterexample.json`
- `coopgames/src/verify_two_poorer_rich_family.py`
- `coopgames/results/two_poorer_rich_family.json`
- `coopgames/src/verify_three_poorer_boundary_family.py`
- `coopgames/results/three_poorer_boundary_family.json`

The two `hunt_*small*boundary.py` scripts and their results are discovery-only
falsification searches.  Please do not count their no-hit output as proof.

## Claims to audit

1. Does exact balancedness, under the conventions of Csóka--Herings--Kóczy
   (2011) and Lohmann--Borm--Herings (2012), imply the slack-budget inequality
   `(SB)` with the stated sign?
2. Is the direct exact-face proof of the boundary-cover inequality `(BC)`
   valid for arbitrary nonnegative tight-coalition weights and
   `alpha>beta>=0`?  Check every inequality direction and the singleton
   normalization dependence.
3. Is the exact-balanced completion following `(BC)` correct both for
   `beta>0` and `beta=0`?  Is any hypothesis about the negative coalition or
   grand-coalition coefficient missing?
4. Is the boundary-defect program `(BD)` stated correctly, including
   attainment/finite-value issues and the conclusion that zero defect forces
   suffix tightness?
5. In the five-player monotonicity example, verify
   `1_135 + 1_345 + 1_2 - 1_35 = 1_N`, the four coalition slacks, and the claim
   that the exact boundary-defect optimum is one.
6. Audit the human unique-richest threshold theorem.  Does the protector
   packing exhaust all one-, two-, and three-poorer-player configurations?
   For every `m>=4`, do the four parametric generators have common total and
   define an exact lower-envelope game?  Do the four displayed coalition
   values force `Lmin=(1^m,m-2)`?  Does the circuit
   `1_{3r}+1_{4r}+sum_{i in P\{3,4}}1_i-1_r=1_N` attain the slack budget at
   equality?  Do the two pair inequalities, the convex combination
   `a*g4+(1-a)*g2`, and the averaging step prove the claimed closed-form Lmax
   and hence Lmin--Lmax separation in every dimension?  Check the endpoint
   `m=4` separately, where the coefficient of
   `e5=er` in `(m-4)e5` is zero.
7. Audit the two-parameter rich-block amplification for every `h>=1` and
   `m>=h+3`.  Check the common totals, four load-bearing values, two-stage
   Lmin proof, Lmax ceiling and convex combination, saturated circuit, and
   L1-distance formula.  Check the new indecomposability argument, including
   the exceptional `m=4,5,6` cases and the coalition interactions attaching
   later poorer players.  Assess whether an indecomposable exact family with
   normalized `h=1` separation `(m-3)/(m-1) -> 1` is already known; do not
   treat large tied blocks alone as novel because direct sums supply them.
8. Hostilely audit the new human two-poorer threshold proof.  Check the
   individual-pinning dual derivation of the dimension-free strict richer-side
   cover, including the backward large-coefficient induction across arbitrary
   poorer payoff strata; the balanced-trace transport theorem and its product
   lift to original coalitions; the integer/half-integer two-poor carrier
   argument; the forced tight triangle `{c,d}`, `{c,e}`, `{b,d,e}`; and the
   final exact-singleton efficiency contradiction.  Confirm that the old
   16-query verifier is now only an audit and that no payoff-stratum case
   enumeration remains in the proof dependency.  A focused checklist is in
   `coopgames/paper3/N5_HUMAN_BOUNDARY_EXTERNAL_REVIEW_PROMPT.md`.
   First decide whether the strict cover is merely a standard Farkas-dual
   reformulation of Arin--Kuipers--Vermeulen property I (and Mauri's antidual
   Lmin form), or whether simultaneous strict undercoverage of every poorer
   player is an additional quantitative consequence. Do not credit the
   qualitative tight-coalition characterization as new.
9. Audit the integral-trace theorem without relying on the small-cardinality
   classification.  Check that the restricted active-trace polytope is
   nonempty and bounded; that integrality makes every packet a set partition;
   that the conditional product lift preserves the original cover; and that
   a unique gaining poor coordinate forces integer packet load at least one,
   contradicting strict undercoverage.  For two poorer players, verify that
   the unique-gainer hypothesis is automatic and that Berge's balanced-matrix
   theorem really yields the stated odd submatrix.  In the `h>=4` family,
   verify symbolically that every co-singleton trace is active and that the
   displayed `3x3` odd-cycle submatrix is present.
   Audit the rooted-semigroup theorem independently of all three applications:
   check the incidence identity `(SRC)`, exactification of the root singleton,
   both possible nonzero zero-one poor-load vectors, and the strict inequality
   `k phi_d>phi_j`. Decide whether “rooted fibre” or an established
   affine-semigroup term is the correct language (the draft deliberately does
   not claim these fibres are semigroup holes without a saturation proof), and whether the
   theorem is a genuinely useful general obstruction rather than a renamed
   repetition of the exact-singleton argument.
   First audit the stronger exact-face overload budget: derive it both from
   the boundary-cover inequality and by exactifying an arbitrary nonempty
   `D subset H`; check all inequality directions when poorer loads are raised
   to one. Verify that the fractional protector-packing inequality and the
   safe rooted theorem are genuinely specializations. Assess whether this
   unification is mathematically informative or only a repackaging of the
   already stated boundary-cover inequality.
   Then audit the positive-Lehman theorem. Check the orientation of
   `A B^T=J+kI`, row/column regularity, the lower bound on dual rows meeting
   `V` exactly once, the upper bound forced by two `U` labels, and the
   column-linear corollary. Confirm independently that odd cycles and
   self-dual projective planes are instances, while `J-I` has the opposite
   sign. Determine whether the labeled density argument or its exact-game
   use already appears in the Lehman/minimally-nonideal literature.
   Audit the canonical internal-face corollary separately: check
   `k+1<=s`, the strict count `s|V|<|H|`, construction of the row set `D`,
   both poor loads after averaging, and every factor of `|D|` in `(LH-F)`.
   Then check the new strict lower bound: for every dual row outside `D`,
   verify the displacement inequality, positivity of its root coordinate,
   strict negativity of `Delta(D)`, and the conversion
   `v(D)<=z(D)` into slack amplification.
   Audit the deficit-preserving minor lift separately. Check the algebra
   from (LM-1) and (LM-4) to `t_a=t_b=0` and `|U|<|V|<r`; check that adding
   the contracted columns produces exactly the claimed rich load; and check
   that their tightness and disjoint traces suffice for the strict lower
   bound in (LM-3). Decide whether reducing label preservation to one scalar
   deficit is genuinely useful or merely repackages the unresolved step.
   Explicitly distinguish an exact-cover Lehman lift from a general MNI
   minor whose uniform fractional core may overcover noncore rich rows. Check
   that no current statement silently assumes those rows away, and assess
   whether their aggregate excess can be controlled by the unit-gap objective
   or exact-face overload budget.
   Audit the noncore-aware criterion: verify that blocker-core rows really
   meet every retained noncore clutter row, that `s|W|-n` bounds every
   double-hit event, including the identity `n=rs-k`, and that the union
   bound yields unit load on all rich rows after contraction lifting.
   Identify any domination or matrix-
   orientation issue when transferring this statement to active traces.
   Audit the unit-gap bridge: verify the fractional cost identity, the split
   between overlapping integral covers and exact partitions, and the use of
   the displacement inequality to force every integral partition to contain
   the gaining player. Assess whether standard cost-aware MNI reductions
   preserve this particular gap or whether a new relative-minor theorem is
   still required.
   Audit the scale-separated refinement independently. Check that choosing
   `Lambda` above the original active-column count implies `Lambda/r>1` for
   every surviving Lehman core, that any positive overcoverage is at least
   `1/r`, and that exactness really forces disjoint contractions and survivor
   avoidance. Check the transport step eliminating both contracted poor
   labels and that the original scaled costs survive the proposed lift.
   Determine whether a standard MNI/minor-compatible theorem actually
   preserves this objective; the manuscript does not claim that it does.
   Compare this carefully with Király--Pap (2016), DOI
   `10.1016/j.dam.2015.07.035`: determine whether their minor-compatible
   covering/packing pairs or ideal unit-increasing set functions already
   encode the unit-gap or one-label augmented systems, and whether their MNI
   theorem supplies the missing cost-preserving reduction.
   Audit the degenerate-MNI exclusion: verify the unique fractional weights,
   the deduction `r_a<r_b<1`, both cases `v_0=0,1`, and that the chosen pair
   `R_0,R_i` always has exactly one duplicated rich row and safe nonzero poor
   load. Confirm the matrix orientation agrees with the classical exception.
   Audit the labeled odd-cycle theorem: check `r_a<r_b<1`, feasibility of the
   two dummy weights, the claim that every integral exact cover has gaining
   dummy coordinate zero, and the balanced-matrix contrapositive. Check that
   dummy columns truly cannot enter the forbidden odd submatrix, and identify
   precisely what label or spanning information the resulting cycle may
   still omit. Then audit the two one-label strengthenings separately,
   especially the convex-decomposition argument for the losing-row matrix.
   Assess whether this certificate is strong enough to support a recursive
   minor-lifting theorem or is only a weak necessary inequality.
   Then audit the rank-two trace exclusion: prove the extreme-point support
   decomposition into singleton blocks, isolated edges, and half-weight odd
   cycles; check the half-integer poor-load argument; and verify that
   alternating rounding really gives load `1_H+e_d+e_b` before the exact
   singleton/efficiency contradiction. Look for a hidden problem caused by
   multiple odd-cycle components or by lifting duplicate traces to original
   coalitions.
   Also audit the `|H|=4` first-obstruction theorem: independently derive the
   five fractional vertex types in `(FO-2)`, verify that the list is exhaustive
   without trusting a search, and check every safe root rounding and the
   type-D poor-label argument. Confirm that slack really forces the
   four-co-singleton `1/3` vertex, not merely the presence of its columns.
   Finally audit the projective-plane density barrier: verify the two
   incidence identities, the lower bound `n_1>=b(q+2-b)`, the injection of
   simple points into `C x D` or pairs of `D=A setminus B` under failure of
   safe rounding, and the local deduction `|D|>=2(q+2-|B|)` from a line in
   `B setminus A`. Then verify
   the load `1_H+q e_d` from the pencil through `d`. Check especially that
   exactifying only singleton `d` suffices when its multiplicity is `q`.
   For the order-seven `(a,b)=(6,7)` case, check the exact simple-point
   identity, the deductions that both line families are in general position,
   the dual tangent/secant translation, the use of Segre's `q`-arc extension
   theorem, and the bound of five (or three) concurrent secants of a six-arc.
   Confirm that this closes only `PG(2,7)` and does not silently assume an
   arbitrary projective plane is Desarguesian.
10. For the six-player upper bound, verify directly that the six displayed
   integer allocations have common total, that their lower envelope is exact,
   and that the five displayed coalition inequalities prove
   `Lmin=(1,1,2,2,2,2)` without an unstated assumption.
11. Confirm that `v({3,4,5,6})=6<8=Lmin({3,4,5,6})`, establishing sharp failure
   of the small-poorer conclusion at six.
12. Audit the dimension-free internal-sacrifice family for every `m>=2` and
    `h>=4`: common generator totals, singleton normalization, all displayed
    worths, the summed Lmin argument (including the aggregate excess on the
    additional poorer players), the Lmax ceiling argument, and the internal
    circuit.  In
    particular, confirm that the richer suffix is slack although Lmin=Lmax,
    and assess whether this is already known as a replication construction or
    as a counterexample to necessity of the exact-partition condition.
13. Audit the universal three-poorer family for every `m>=3,h>=2`: common
    totals, singleton normalization (including the endpoint `h=2`), the four
    displayed load-bearing values, and each progressive Lmin pinning step.
    Confirm that the proof establishes the claimed `(m-1,1,h)` strata and
    unit richer-suffix slack without relying on the finite verifier.  Check
    the dimension-free core-feasibility argument for the displayed Lmax,
    including both coalition-difference formulas and the endpoint `h=2`.
    Check every successive Lmax forcing face and the `4h/(h+1)` distance.
    Check
    the indecomposability proof separately for `Q` nonempty and for the
    endpoint `m=3`, including the strict four-player interaction attaching
    `p2`.
14. Check the complete boundary-cardinality phase diagram:
    `m_min(1)=4`, `m_min(2)=m_min(3)=3`, and `m_min(h)=2` for `h>=4`.
    Verify that the lower bounds cover every excluded pair, the three
    dimension-free families cover every admitted pair, and the theorem is
    about an arbitrary strict Lmin boundary rather than only two-stratum
    allocations.  Check that no normalization or quantifier is lost.

## Novelty questions

Please separately assess whether any of the following already appears in the
exact-game, exact-balancedness, egalitarian-core, exact-partition, or Lorenz
core literature:

- the quantitative slack-budget reading `(SB-H)`;
- the protector-completion/boundary-cover inequality `(BC)`;
- the canonical boundary-defect LP `(BD)`;
- the sacrifice-budget interpretation and sharp unique-richest threshold;
- the four-generator integral family with `Lmin=(1^m,m-2)` for every `m>=4`,
  its closed-form Lmax, and whether it is merely a padding or replication of a
  known example;
- the arbitrary-richest-block amplification, its asymptotic Lmin--Lmax gap,
  and the extent to which these are consequences of known replication theory;
- the sharp result that a richer Lmin suffix with at most two poorer players is
  tight through five players but can be slack at six;
- the dimension-free necessity of a nonintegral active trace polytope and odd
  balanced-matrix obstruction at every two-poorer failure;
- the exact-face rooted-semigroup obstruction and its interpretation as a
  family of forbidden integer fibres, including prior terminology from
  normal hypergraphs, Hilbert bases, and affine semigroups;
- the real-valued exact-face overload budget and its claimed unification of
  the unique-richest threshold with the trace-rounding hierarchy;
- the positive-Lehman trace exclusion and the proposed positive-versus-
  negative structural divide;
- the dimension-free rank-two trace exclusion, equivalently that every
  two-poorer failure requires an active trace of size at least three;
- the uniqueness of the four-co-singleton `1/3` packet at the first feasible
  `2|4` obstruction;
- the projective-plane simple-point density barrier and safe-star exclusion,
  including whether this exact-face application is already known in the
  finite-geometry, balanced-hypergraph, or cooperative-game literature;
- the fixed six-player integer lower-envelope construction.
- the integral `m>=2,h>=4` internal-sacrifice family, the internal/external
  sacrifice dichotomy, and the observation that exact partition is not
  necessary for Lmin--Lmax equality.
- the universal `m>=3,h>=2` family and the synthesis of all three mechanisms
  into the complete boundary-cardinality phase diagram, including its
  closed-form Lmax and dimension-free Lmin--Lmax separation.

The manuscript already treats the exact-balancedness characterization, the
Arin--Iñarra transfer-blocking property, and the Arin--Kuipers--Vermeulen
property-I criterion (including Mauri's Lmin form) as prior art. Please flag any remaining
novelty overstatement.
It also records the known theorem that exact games with at most four players
are PES stable.  Check whether the new exact-partition-at-Lmin result is truly
a stronger statement and whether that strengthening already appears under
different terminology.

## Reproduction

From `coopgames/` run:

```bash
python src/verify_exact_balanced_slack_budget.py \
  --output results/exact_balanced_slack_budget.json
python src/verify_n5_small_poorer_suffix.py \
  --output results/n5_small_poorer_suffix.json
python src/verify_n5_unique_richest_boundary.py \
  --output results/n5_unique_richest_boundary.json
python src/verify_unique_richest_family.py \
  --max-players 12 --exact-lmin-through 7 --exact-lmax-through 6 \
  --output results/unique_richest_family.json
python src/verify_rich_block_family.py \
  --max-rich-block 4 --extra-poorer 4 \
  --exact-replay-through-players 7 \
  --output results/rich_block_family.json
python src/verify_n6_two_poorer_suffix_counterexample.py \
  --output results/n6_two_poorer_suffix_counterexample.json
python src/verify_two_poorer_rich_family.py \
  --max-poorer-block 5 --max-rich-block 10 --exact-replay-m2-h4 \
  --output results/two_poorer_rich_family.json
python src/verify_three_poorer_boundary_family.py \
  --max-poorer-side 6 --max-richer-suffix 6 \
  --exact-replay-through-players 6 \
  --output results/three_poorer_boundary_family.json
cd paper3
latexmk -pdf -interaction=nonstopmode -halt-on-error wrapper.tex
```

## Requested verdict

Return `verified`, `verified with qualifications`, or `not verified`; list
every issue with exact file and line references; classify it as fatal,
repairable, or expository; report the commands actually run; and give a
separate prior-art/novelty assessment.  Please do not treat solver agreement,
unsatisfiable cores, or random-search no-hit results as independent proof.
