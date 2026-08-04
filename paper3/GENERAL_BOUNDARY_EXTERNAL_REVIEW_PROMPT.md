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
  `lem:lx-odd-cycle-overload-footprint`,
  `thm:lx-labeled-odd-cycle`,
  `cor:lx-unconditional-labeled-obstruction`,
  `thm:lx-positive-lehman-trace-exclusion`,
  `cor:lx-convex-lehman-row`,
  `eq:lx-lehman-residual-transport`,
  `lem:lx-three-column-lehman-separation`,
  `lem:lx-four-column-odd-lehman-separation`,
  `prop:lx-thin-four-label-normal-form`,
  `cor:lx-three-gaining-column-exclusion`,
  `cor:lx-subset-lehman-face-budget`,
  `cor:lx-lehman-internal-face`,
  `thm:lx-rank-two-trace-exclusion`,
  `thm:lx-four-rich-trace-classification`,
  `thm:lx-projective-plane-trace-exclusion`,
  `cor:lx-projective-plane-all-orders`, and
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
- `coopgames/paper3/RANK_TWO_TRACE_EXCLUSION.md`: corrected dimension-free
  exclusion for graph-like packets, using a real overload when untouched
  odd-cycle components retain half weights.
- `coopgames/paper3/ROOTED_SEMIGROUP_OBSTRUCTION.md`: standalone
  dimension-free theorem forbidding safe rooted integer fibres of tight
  coalition semigroups.
- `coopgames/paper3/EXACT_FACE_OVERLOAD_BUDGET.md`: real-valued internal-face
  inequality proposed as the common budget behind the four/five
  unique-richest threshold and the later rooted trace roundings.
- `coopgames/paper3/LEHMAN_TRACE_OBSTRUCTION.md`: reduction of positive Lehman
  dual rows to rooted covers and the new two-poor-label density criterion.
- `coopgames/paper3/CONVEX_LEHMAN_ROW.md`: real-valued interpolation between
  the uniform packet and a dual row, yielding the two-sided Lehman row band.
- `coopgames/paper3/LEHMAN_RESIDUAL_TRANSPORT.md`: exact transpose transport
  of the label-residual vector and zero local balance on neutral traces.
- `coopgames/paper3/THREE_COLUMN_LEHMAN_SEPARATION.md`: dimension-free
  capacity-parity proof that every three dual columns have a simple row and
  the resulting exclusion through three gaining labels.
- `coopgames/paper3/FOUR_COLUMN_RESIDUAL_NORMAL_FORM.md`: reduction of the
  first open thin label cardinality to six local neutral-trace tiles.
- `coopgames/paper3/SUBSET_LEHMAN_FACE_BUDGET.md`: multi-row extension that
  converts aggregate label residual into a quantitative internal-face slack
  bound.
- `coopgames/paper3/LEHMAN_MINOR_LIFTING.md`: proof that preserving only the
  gaining-player deficit automatically removes both poor labels from every
  contracted column and lifts the Lehman conclusions to the original suffix.
- `coopgames/paper3/NONCORE_LEHMAN_LIFTING.md`: union-bound refinement that
  requires a Lehman dual selector to hit every noncore MNI row exactly once.
- `coopgames/paper3/SCALE_SEPARATED_MNI_BRIDGE.md`: big-M refinement under
  which preservation of one objective gap forces exactness on all rich rows.
- `coopgames/paper3/PARALLELIZED_RELATIVE_MNI.md`: exact conversion of the
  weighted gap to an unweighted clone parallelization, together with the
  denominator and row-geometry reasons this shortcut does not lift Lehman
  structure back to the exact game.
- `coopgames/paper3/UNIT_GAP_MNI_BRIDGE.md`: explicit integral-cost set-cover
  gap whose strict unit threshold is equivalent to the gaining-player deficit.
- `coopgames/paper3/DEGENERATE_MNI_TRACE_EXCLUSION.md`: human elimination of
  the exceptional degenerate-projective-plane branch of Lehman's MNI theorem.
- `coopgames/paper3/LABELED_ODD_CYCLE_OBSTRUCTION.md`: augmented balanced-
  matrix proof retaining poor labels as rows rather than side annotations.
- `coopgames/paper3/CANONICAL_LABELED_CIRCUIT.md`: proof that the same
  original-row packet is a fractional vertex and a support-minimal linear
  circuit, without an MNI reduction.
- `coopgames/paper3/ODD_CYCLE_OVERLOAD_FOOTPRINT.md`: exact-face budget for
  alternating odd-cycle roundings and the singleton-to-pair transition at
  the sharp `2|3` versus `2|4` boundary.
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
   Audit the two-sided convex Lehman-row corollary separately.  Recompute
   `F_d=(r-p)w_d+p-ell-(r-ell)u_d`.  For the positive band, check
   `t=(r-ell)/(r w_d-ell)`, the losing load
   `[p(w_d-1)+u_d(r-ell)]/(r w_d-ell)`, and the equivalences with
   `a_d<=1`, `t k>=1-a_d`.  For the negative band, check
   `t_hat=(r-p)/(r u_d-p)`, the gaining load
   `[ell(u_d-1)+w_d(r-p)]/(r u_d-p)`, and the equivalences with
   `b_d<=1`, `t_hat k>=1-b_d`.  Check both equality endpoints and the
   strict comparisons `phi_d>phi_a,phi_b`.  Independently derive the residual
   conservation identity `sum_d F_d=k(ell-p)` and its overshoot consequence.
   Before summing, audit the stronger vector identity
   `A^T F=k[(r-p)1_V-(r-ell)1_U]`: check the cancellation of the all-ones
   coefficient, every overlap case `U intersect V`, the neutral-column zero
   balance, and the derivation of the scalar law by left multiplication.
   Determine whether either interpolation has an antecedent in Lehman-matrix
   or blocking-polyhedra literature.
   Audit the three-column separation lemma independently.  Assuming no row
   meets a chosen triple `V` exactly once, verify that
   `A^T B 1_V=3 1+k 1_V` forces every outside `A`-column to meet exactly one
   load-three row; check `n-3<=r x`, `n=rs-k`, `k+1<=r`, the rounding to
   `x>=s-1`, and the parity argument from `3(s-x)`.  Check that `x=s` really
   makes the three `B`-columns identical.  Then audit every `u=0,1,2` case
   in `F=(r-3)(1-u)` and the conclusion that survivors require
   `|V|>=4,r>=5`.  Search specifically for an antecedent in the Lehman-matrix
   and regular-covering-design literature.
   Then audit the odd-multiplier four-column lemma: under the no-simple-row
   assumption, check why a load-three row cannot place all `r>=5` entries of
   its `A`-row inside `V`, and why the resulting even load vector contradicts
   `4+k` on a labeled column.  For `k=1,ell=4`, recompute the parameter
   reduction `r>=6,p=3,|U intersect V|<=1`, both simple-row implications, the
   neutral-trace totals `(4,3)`, every allowed row type, and exhaustiveness of
   the six displayed tiles.  Confirm that the result is only a local normal
   form and does not assert global incompatibility.
   Audit the subset residual face budget separately.  For a row set `D`,
   recompute the averaged rich load `1_H+(k/|D|)1_D`; verify the two
   interpolation parameters and the identities
   `1-a_D=F(D)/(rW_D-|D|ell)` and
   `1-b_D=-F(D)/(rU_D-|D|p)`.  Check both cleared-denominator face bounds,
   all positivity conditions, and the assertion that zero residual forces
   `D` tight.  Confirm that singleton `D` recovers the two row bands and that
   the canonical `|D|=s ell` construction recovers `(LH-F)` without a missing
   factor of `r-ell`.
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
   Check the parallelization identities for both integer and fractional
   covering numbers, including the clone-symmetrization argument. Then audit
   the stated failure of the shortcut: MNI core rows are clone-variant
   clutter members rather than rich players, and clone averaging introduces
   denominators `c_T r`. Determine whether some stronger symmetry-preserving
   minor theorem avoids this loss; do not infer it from an arbitrary MNI
   minor.
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
   For the circuit strengthening, verify that minimal balanced support makes
   the rich trace columns linearly independent, that lifting and adding dummy
   columns preserve independence, that every coefficient in the all-ones
   representation is strictly positive, and hence that adjoining the right-
   hand side gives a minimally dependent set. Distinguish this linear-circuit
   minimality from minimally nonideal, facet, and deletion/contraction
   minimality; the manuscript claims none of the latter.
   Assess whether this certificate is strong enough to support a recursive
   minor-lifting theorem or is only a weak necessary inequality.
   Audit the odd-cycle overload footprint separately: verify the alternating
   load on the cycle rows, the construction of the full footprint from
   external rows, and the specialization of the exact-face budget. For the
   `h=4` family, recompute the selected two co-singletons, their safe poor
   load, `F={r_2,k_2}`, and the equality `s_phi(F)=phi_{p_2}`. Decide whether
   this genuinely explains the `2|3` versus `2|4` transition or merely
   restates the existing four-row classification.
   Then audit the corrected rank-two trace exclusion: prove the extreme-point support
   decomposition into singleton blocks, isolated edges, and half-weight odd
   cycles; check the half-integer poor-load argument; and verify that
   only the uniquely labeled odd-cycle component is rounded while all other
   components retain their original exact-cover weights. Check the resulting
   real load `1_H+e_d+e_b` and the singleton budget contradiction
   `phi_d<=phi_a`. Confirm that this is not called an integer semigroup fibre
   when untouched odd cycles retain half weights.
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
   Then audit the all-orders projective-plane corollary.  Check that
   `1<=ell<=q` forces a point on exactly one gaining line, that its residual
   is `(q+1-ell)(1-u)`, and that `u<=1` invokes the positive band while
   `u>=2` invokes the negative band through
   `(q+1-ell)(u-1)<=q(q+1-p)`.  Confirm that this covers every finite order,
   every overlap between the two line sets, and uses no Desarguesian theorem.
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
- the canonical original-row labeled-cover circuit, including whether its
  support-minimal vertex formulation has a known antecedent in balanced
  hypergraphs, oriented matroids, or exact-game tight-coalition systems;
- the odd-cycle overload-footprint budget and its interpretation of the first
  feasible obstruction as a singleton-to-pair internal-face transition;
- the exact-face rooted-semigroup obstruction and its interpretation as a
  family of forbidden integer fibres, including prior terminology from
  normal hypergraphs, Hilbert bases, and affine semigroups;
- the real-valued exact-face overload budget and its claimed unification of
  the unique-richest threshold with the trace-rounding hierarchy;
- the positive-Lehman trace exclusion and the proposed positive-versus-
  negative structural divide;
- the convex Lehman-row interpolation, including whether the two-sided band
  or its exact-face application is already known;
- the local residual transport identity, including whether this labeled
  formulation or its use on neutral traces already occurs in Lehman theory;
- the three-column capacity-parity separation and its exact-game consequence,
  including whether the incidence lemma is already known for Lehman pairs;
- the odd-multiplier four-column separation and six-tile thin normal form,
  including whether comparable local configurations occur in Lehman theory;
- the subset Lehman residual face budget, its unification of the singleton
  bands and canonical internal face, and whether its proposed recursive
  interpretation is genuinely new;
- the dimension-free rank-two trace exclusion via a real tight-cover
  overload, including the distinction from an integer rooted fibre;
- the uniqueness of the four-co-singleton `1/3` packet at the first feasible
  `2|4` obstruction;
- the projective-plane simple-point density barrier and safe-star exclusion,
  the incidence-theoretic all-orders closure, and whether this exact-face
  application is already known in finite geometry, balanced hypergraphs, or
  cooperative games;
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
