# Protected results ledger for the hybrid-overlap program

Status: working theorem/dependency ledger on `codex/hybrid-overlap-facets`.
Baseline: immutable tag `paper5-arxiv-review-v1`.
Current continuation baseline: commit `7a3a409`.

This file prevents a new attack from silently replacing, weakening, or
forgetting an established part of the program.  A row marked **proved** may
be used subject to its stated hypotheses and scope.  Exact audits remain
falsification/reproducibility evidence unless the human argument is named.
Novelty and external validation are not asserted here.

## Protected mathematical inputs

| Result | Status and scope | Primary repository evidence |
|---|---|---|
| Global asymptotic divergence | **Proved.** For the normalized separation `rho=||Lmin-Lmax||_1/T`, one always has `rho<=2`, the explicit exact family approaches `2`, and therefore `sup_n s(n)=2`.  This is an asymptotic theorem, not the conjectured sharp formula for every fixed `n`. | `paper5/divergence.tex`, global bound and family sections |
| Four/five selector threshold | **Proved.** Every singleton-normalized exact game on at most four players has `Lmin=Lmax`; exact five-player games can differ.  This is an unweighted player theorem, not weighted-role coincidence. | `paper4/threshold.tex`; `paper5/divergence.tex` |
| Five-player exact-partition boundary | **Proved.** Four-player exact games have the exact-partition/Lorenz-greatest bridge used for selector coincidence; every five-player selector failure has a slack suffix, and the attempted exact-partition failure mechanism is impossible at `n=5`.  Preserve the precise suffix quantifiers from the paper. | `paper4/threshold.tex`; commit `3004fe8`; `verifiers/cc/` |
| Five-player sharp separation | **Proved at fixed n.** `s(5)=1/2`; the Lmin `(4,1)` stratum regime has the stronger `1/3` bound, and the starved player is Lmin-poor.  The fixed-dimensional proof is computer-assisted with separately formulated Lmin-optimality components. | `paper5/divergence.tex`; commit `15ff9f4`; `verifiers/s5close/` |
| Five-player certificate and configuration theorems | **Proved at fixed n.** The one-coalition certificate theorem and the extremal/starvation configuration arguments are reusable structural inputs, not merely implementation details of the census. | `paper5/divergence.tex`; `verifiers/a3check/`; `verifiers/o2/`; commits `329ff1f`, `48780d9` |
| PART/ZP structural families | **Proved constructions and boundary results in their stated parameter ranges.** Closed-form `PART(p,q)` realizations and the seven-player `ZP(2,2)` realization refute earlier restrictive conjectures; these controls must remain in any general theorem audit. | `paper4/threshold.tex`; `paper5/divergence.tex`; `verifiers/part/`; commits `df58ef4`, `fd59dce` |
| Six-player sharp bound and equality work | **Proved at fixed n.** `s(6)=2/3`, with exact equality profiles, a complete counterexample-to-SMT implication, exact infeasibility certificates, and compressed human exchange schemas.  Its packet/orbit calculations must not be promoted to an all-n theorem. | `paper5/divergence.tex`; `paper5/S6_*`; `verifiers/s6/`; `verifiers/s6_direct/` |
| Sharp family `G(p,k)` | **Proved construction.** Supplies the conjectured all-n lower examples and the equality controls the upper theorem must recover. | `paper5/divergence.tex` |
| Large-core separation control | **Proved exact example.** A five-player exact game with a large core has `Lmin!=Lmax`; therefore the large-core/PES characterization of `Lmax` cannot by itself prove selector coincidence. | `paper5/divergence.tex`, introduction and archived exact verifier |
| Sparse Lmax over-cover | **Proved dual certificate framework.** Normalization and top-stratum labels are essential. | `paper5/LMAX_OVERCOVER_COUPLING.md`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` |
| Spectral-anchor overlap theorem | **Proved dimension-free conditional lower bound.** A sparse Lmax over-cover and its optimized dispersion parameter yield the exact labelled-to-spectral overlap floor `B_theta`.  It is an effective bound, not a proof that one scalar anchor reaches the all-n target. | `paper5/LMAX_OVERCOVER_COUPLING.md`, `(SA)`; `audit_lmax_overcover.py` |
| Complete staged Lmin packet | **Proved selection/certificate framework.** Later gluing must use the complete staged packet, not a first-floor surrogate. | `paper5/divergence.tex`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` |
| Zero-floor null-player descent | **Proved dimension-free induction reduction.** If the Lmin floor is zero, exactness makes one player null; deletion preserves the core product, both selectors, total, and overlap.  Thus a minimal-dimensional counterexample to the target has positive Lmin floor. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(NPD0)--(NPDC)`; `verify_null_player_hybrid_descent.py` |
| Sharp-family shared hinge and factorization | **Proved dimension-free for `G(p,k)`.** The common hinge geometry and overlap factorization explain the lower family structurally and are mandatory equality controls for any general gluing theorem. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, shared-hinge section; `verify_balanced_family_shared_hinge.py` |
| Dispersion and staged-transport theorems | **Proved within their stated packet hypotheses.** The paired dispersion budget, projected staged-circuit theorem, first-floor Hall alternative, and sign-coherent staged lifts give exact transport structure.  Their individual unit-box/target-count strengthenings fail at seven players. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, Sections 5--6; adjacent exact audits |
| Direct/interpolation/null/root-price/common-repair reduction | **Proved components plus exact finite handover audit.** The finite census is not the missing general selection theorem. | `verifiers/divergence/audit_direct_ceiling_common_hinge_trichotomy.py` and adjacent JSON; research note |
| Ceiling-root interpolation floor | **Proved dimension-free.** The scalar floor `O/T>=t-u+u/t` closes all parameters outside an explicit positive-floor wedge.  Archived hard controls lie inside that wedge, so facet/packet charge is still required. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`; `verify_ceiling_root_interpolation.py` |
| Labelled rooted packing/cover duality | **Proved exact LP duality.** Facet price belongs to a labelled normal plus its Lmin-tight labels; it is not gauge invariant. | `verifiers/divergence/audit_labelled_facet_cover_duality.py`; research note |
| Carrier cycle or separator | **Proved structural alternative.** A carrier cycle is a sign-coherent tight-face object; the alternative alone has no quantitative target price. | commits `00ea31b`, `21b2d23`; research note |
| Strict complement payment | **Proved.** A z-tight coalition splitting an x-carrier gives strict payment on it and its complement.  One separator need not pay enough. | commit `5ac2ab8`; `audit_carrier_separator_payment.py` |
| Common carrier contraction | **Proved.** A common x/z tight-face carrier module contracts to one weighted role while preserving exactness, weighted selectors, total, and overlap. | commits `5ac2ab8`, `fc28a1a`; research note |
| Canonical block expansion | **Proved.** A nonnegative exact weighted role game expands to a singleton-normalized exact atomic game when every unit-weight role has zero singleton worth.  Weighted selectors and overlap are preserved. | commit `fc28a1a`; research note |
| Weighted coincidence through three roles | **Proved dimension-free.** The core is a box intersected with efficiency and the clipped weighted equalizer Lorenz-dominates all feasible repeated vectors. | commit `36c13c6`; `verify_weighted_three_role_coincidence.py` |
| Elementary/laminar four-role coincidence reductions | **Proved.** Weighted selectors coincide when one role total is core-constant or when at most one complementary pair slab is nonredundant.  Equal weights also suffice only when all role singleton worths vanish.  Any hard quotient has four variable roles and at least two crossing pair slabs. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, elementary four-role reductions |
| Four-role weighted divergence | **Proved sharp role threshold.** Weighted coincidence fails at four roles, including in every sufficiently large atomic dimension. | commits `569dd84`, `c5e71f8`; exact verifiers and JSON |
| Normalized constant-overlap four-role family | **Proved.** For weights `(m,1,1,1)`, `m>=5`, an exact zero-singleton role game has weighted selections `(5,1,5,1)` and `(3,3,3,3)`, hence `O/T=2/3`.  It refutes a universal `3/4` quotient bound but satisfies the atomic conjecture. | commit `7a3a409`; `verify_weighted_four_role_normalized_obstruction.py` |
| Balanced weighted seesaw face | **Proved atomic-weight-aware quotient theorem.** If both weighted selectors lie on two balanced common crossing flats, the face is `q(t)=(t,W-t,t,W-t)` and its exact selector formula plus the integer harmonic/product bound proves the full atomic target.  This includes the common face of the normalized `2/3` family and has strict target slack for `n>=6`.  The two flats are exact-partition face equalities, so no new full-cone facet is asserted. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(BWS1)--(BWS8)`; `verify_weighted_balanced_seesaw.py` |
| Endowed two-flat selector reduction | **Proved selector theorem.** On an arbitrary endowed common crossing interval, weighted Lmin and Lmax are the two middle order statistics of a `2 by 2` per-capita crossing-time matrix, and overlap is total minus twice their gap.  The atomic target is reduced exactly to `(EWS5)`, which remains open.  The bounded grid is falsification evidence only. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, `(EWS1)--(EWS5)`; `paper5/divergence.tex`; `verify_weighted_endowed_seesaw.py` |
| Complete strict carrier support | **Proved support theorem.** Normalized coefficient supply collapses to zero/nonzero support; coefficient magnitude is not invariant currency. | research note, complete strict-carrier-support section |
| Interval-packing min-max | **Proved exact combinatorial theorem** with its stated fixed-stratum algorithm and integrality boundary.  It is not a full all-cell gluing theorem. | research note, interval-packing sections |
| Mixed-colour packet and mixed-witness projection | **Proved projection frameworks.** They allow genuinely mixed x/z support; relative-cell validity does not automatically imply a full exact-cone facet. | `verify_mixed_packet_gluing.py`; `verify_mixed_witness_projection.py` and Z3 replay |
| First genuinely noncommon mixed packet | **Proved branch certificate.** The explicit two-colour packet closes its optimized hostile branch; an alternative rooted-pair shear gives an active indecomposable exact-cone facet and reaches the exact `3/4` one-witness minimum.  This is a branch theorem, not universal gluing. | `paper5/EFFECTIVE_BIPARTITION_BRIDGE.md`; `mixed_packet_gluing.json`; `mixed_witness_projection*.json` |
| Complement-star facets | **Proved dimension-free class** with exact indecomposability/facet criterion in its stated parameter range. | commit `cd5e947`; `verify_complement_star_facets.py` |
| Rectangular and saturated rooted-star facets | **Proved class criteria.** These enumerate their distinguished classes, not every exact-cone facet. | `verify_rooted_star_matrix_facets.py`; research note |
| Nonroot clone expansion of rooted-star facets | **Proved preservation theorem.** It applies to the stated nonroot clone expansion, not arbitrary marked shears. | commit `d3b4987`; `verify_clone_expanded_rooted_star_facets.py` |
| Complete-graph rooted-pair facets | **Proved dimension-free non-star class.** This is a sharp warning that clone-saturated stars do not exhaust the facet atoms. | `verify_complete_graph_rooted_pair_facets.py`; independent K4 Z3 control |
| Rooted pair-lift facet theorem | **Proved dimension-free interface.** Extreme rooted packings shear to min-semi-balanced systems of support at most `n`; the published indecomposability test decides when the resulting inequality is a full exact-cone facet.  The simultaneous `G(p,k)` lift is an indecomposable facet for every stated `p,k`. | `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`; `paper5/EFFECTIVE_BIPARTITION_BRIDGE.md`; pair-lift LP/Z3 audits |
| Relative common-hinge facet decision | **Proved exact finite decision procedure** on a fixed labelled selection cell.  It does not by itself certify a full-cone facet after cell gluing. | research note, `(CHF)` section |
| Exact fixed-stratum/fixed-n algorithms | **Proved decidability/enumeration interfaces** for the stated cells and candidate classes.  No polynomial full exact-cone enumeration claim is licensed. | research note, fixed-stratum and cellwise-pullback sections |
| Effective fractional-role decomposition | **Proved exact reduction.** The clipped fractional-role/dispersion dual and disjoint carrier packets remain valid.  The stronger effective-bipartition overlap floor they motivated is false by an exact seven-player counterexample. | `paper5/EFFECTIVE_BIPARTITION_BRIDGE.md`; `verify_n7_effective_bipartition_counterexample.py` |
| Six-player positive-residual facet atlas | **Exact finite theorem/audit.** Thirteen facets in five support orbits cover the live archived residuals; it is not an all-n class exhaustion. | `audit_n6_positive_residual_facet_atlas.py`; independent Z3 verifier |
| Seven-player hostile and equality controls | **Exact falsification controls.** Every new general lemma must pass the fixed hostile cases and both balanced equality orientations `(2,4)` and `(3,3)`. | research note and adjacent n=7 verifiers |

## Adjacent campaign results that must not be lost

These results belong primarily to the normalized-Lmin/coalitional-monotonicity
paper rather than to the hybrid `Lmin`--`Lmax` bound.  They are recorded here
because they supplied several of this program's carrier, exactness, and
dimension-threshold ideas.  They must not be silently absorbed into stronger
claims about the current overlap conjecture.

| Result | Status and scope | Primary repository evidence |
|---|---|---|
| Normalized-Lmin monotonicity boundary | **Proved.** Singleton bumps are monotone; grand-coalition resource monotonicity fails; and proper nonsingleton coalitional monotonicity fails for an exact five-player zero-singleton game, in the minimum possible dimension, with the exact bump path computed. | `paper3/sections_leximin.tex`; `verify_n5_exact_leximin_monotonicity_counterexample.py` |
| Large-core/exact-partition separation at five | **Proved.** The five-player monotonicity pair has large cores and constant `Lmax`, while `Lmin` changes; the base core has neither an exact-partition allocation nor a Lorenz-dominating element.  This makes the through-four boundary sharp. | `paper3/sections_leximin.tex`, large-core separation proposition; large-core verifier |
| Quantitative carrier dimension threshold for exact games | **Proved, computer-assisted at the finite threshold.** The carrier inequality holds for every exact game through six players and fails for an explicit exact game at every `n>=7` by null padding.  The seven-player seed has a hand-certified exact lower envelope and Lmin point. | `paper3/sections_leximin.tex`, complete dimension threshold; `verify_n7_exact_carrier_counterexample*.py`; n6 eta-dual census and replay |
| Seven-player exact outside-pair theorem | **Proved, computer-assisted.** Although the unrestricted exact carrier inequality first fails at seven players, it still holds there whenever the outside set has size at most two; outside size three is minimal for an exact seven-player obstruction. | `paper3/sections_leximin.tex`, seven-player outside-pair theorem and outside-triple obstruction; exact census/replay artifacts |
| Totally-balanced outside-pair threshold | **Proved as a sharp fixed-dimensional result.** For `n=6`, `|S|=4`, `|P|=2`, all 619 undominated eta-dual vertex orbits satisfy the carrier bound under total balancedness.  An explicit integer totally balanced, nonexact seven-player game with `|S|=5`, `|P|=2` has `(gamma,eta)=(1,0)`, so this strengthening is dimension-sharp.  It does not refute the exact seven-player outside-pair theorem. | `results/total_balanced_outside_pair_checkpoint.md`; `paper3/N7_TOTAL_BALANCED_OUTSIDE_PAIR_COUNTEREXAMPLE.md`; `verify_n7_total_balanced_outside_pair_counterexample.py` |
| Eta-dual/minimal-balanced-collection correspondence | **Proved.** After dominated columns are removed, eta-dual vertices are precisely normalized minimal balanced collections containing the target coalition, with support at most `n`.  This is the principal bridge from the carrier problem to exact-cone combinatorics. | `paper3/sections_leximin.tex`, eta-dual vertex lemma |

## Protected false lemmas and forbidden shortcuts

The following must not be silently reintroduced.

- Uniform generators or monotonicity under majorization.
- Cycle-only or full-carrier-closure selection.
- Closure by one arbitrary Lmax separator.
- Gauge-invariant rooted-facet affordability.
- Coefficient magnitude as invariant carrier currency; only normalized support
  survives the proved rescaling analysis.
- Common support as a prerequisite for mixed packet validity.
- Automatic promotion of a relative selection-cell circuit to a full
  exact-game-cone facet.
- Weighted coincidence at four roles.
- An atomic-size-independent weighted four-role overlap bound `O/T>=3/4`;
  commit `7a3a409` gives a normalized exact family at `2/3`.
- A universal `O/T>=1/2` bound for abstract endowed two-flat seesaws; the
  exact rational parameter row recorded after `(EWS5)` has ratio
  `3715/12616`.  No exact-game realization of that auxiliary row is asserted.
- Reduction of all weight vectors to `(m,1,1,1)` without proof.
- Invoking four-player rigidity on an endowed weighted quotient merely because
  its role weights are equal; the ordinary theorem requires role-level
  singleton normalization, which `(CBE)` does not require for nonunit roles.
- Treating a finite n=6/n=7 census, solver agreement, or an unsat core as a
  dimension-free theorem.

## Active dependency map

The desired all-n upper theorem currently requires all three arrows:

```text
complete staged Lmin packet + sparse labelled Lmax over-cover
                         |
                         v
direct / separator / rooted-facet / common-carrier selection theorem
              |                            |
              |                            v
              |                  atomic-weight-aware quotient bound
              |                            |
              +----------------------------+
                         |
                         v
      hybrid overlap target, equality classification, exact s(n)
                         |
                         v
 semi-balanced-system identification and full-cone facet tests by class
```

The quotient program may use the companion four-player theorem as follows:
the underlying unweighted four-role exact game has an exact-partition,
Lorenz-greatest allocation.  Unequal role multiplicities change both weighted
selectors, so this center is an additional structural witness, not an
automatic coincidence theorem.  Quantifying both weighted selectors relative
to that center is an active human-proof route.

## Current completion boundary

The main dimension-free overlap inequality, its equality characterization,
and a complete carrier/separator selection theorem remain open.  Objective A
is reduced on every common two-flat quotient to the endowed middle-gap
inequality `(EWS5)`, but no proof or exact counterexample is known for the
required atomic-weight-aware four-role target in full.  The current bounded
exact grid is only a hostile discovery check.  Success on the quotient theorem
alone would not complete the project unless the carrier/separator gluing arrow
is also proved.
