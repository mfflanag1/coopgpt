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
| Four/five selector threshold | **Proved.** Every singleton-normalized exact game on at most four players has `Lmin=Lmax`; exact five-player games can differ.  This is an unweighted player theorem, not weighted-role coincidence. | `paper4/threshold.tex`; `paper5/divergence.tex` |
| Five-player sharp classification | **Proved at fixed n.** Includes the dimension-five separation classification and sharp failure mechanisms. | `paper5/divergence.tex`; `verifiers/s5close/`; hostile external reviews archived in the campaign |
| Six-player sharp bound and equality work | **Proved at fixed n** with the evidence qualifications stated in the paper.  Its packet/orbit calculations must not be promoted to an all-n theorem. | `paper5/divergence.tex`; `paper5/S6_*`; `verifiers/s6/` |
| Sharp family `G(p,k)` | **Proved construction.** Supplies the conjectured all-n lower examples and the equality controls the upper theorem must recover. | `paper5/divergence.tex` |
| Sparse Lmax over-cover | **Proved dual certificate framework.** Normalization and top-stratum labels are essential. | `paper5/LMAX_OVERCOVER_COUPLING.md`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` |
| Complete staged Lmin packet | **Proved selection/certificate framework.** Later gluing must use the complete staged packet, not a first-floor surrogate. | `paper5/divergence.tex`; `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md` |
| Direct/interpolation/null/root-price/common-repair reduction | **Proved components plus exact finite handover audit.** The finite census is not the missing general selection theorem. | `verifiers/divergence/audit_direct_ceiling_common_hinge_trichotomy.py` and adjacent JSON; research note |
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
| Complete strict carrier support | **Proved support theorem.** Normalized coefficient supply collapses to zero/nonzero support; coefficient magnitude is not invariant currency. | research note, complete strict-carrier-support section |
| Interval-packing min-max | **Proved exact combinatorial theorem** with its stated fixed-stratum algorithm and integrality boundary.  It is not a full all-cell gluing theorem. | research note, interval-packing sections |
| Mixed-colour packet and mixed-witness projection | **Proved projection frameworks.** They allow genuinely mixed x/z support; relative-cell validity does not automatically imply a full exact-cone facet. | `verify_mixed_packet_gluing.py`; `verify_mixed_witness_projection.py` and Z3 replay |
| Complement-star facets | **Proved dimension-free class** with exact indecomposability/facet criterion in its stated parameter range. | commit `cd5e947`; `verify_complement_star_facets.py` |
| Rectangular and saturated rooted-star facets | **Proved class criteria.** These enumerate their distinguished classes, not every exact-cone facet. | `verify_rooted_star_matrix_facets.py`; research note |
| Nonroot clone expansion of rooted-star facets | **Proved preservation theorem.** It applies to the stated nonroot clone expansion, not arbitrary marked shears. | commit `d3b4987`; `verify_clone_expanded_rooted_star_facets.py` |
| Complete-graph rooted-pair facets | **Proved dimension-free non-star class.** This is a sharp warning that clone-saturated stars do not exhaust the facet atoms. | `verify_complete_graph_rooted_pair_facets.py`; independent K4 Z3 control |
| Relative common-hinge facet decision | **Proved exact finite decision procedure** on a fixed labelled selection cell.  It does not by itself certify a full-cone facet after cell gluing. | research note, `(CHF)` section |
| Exact fixed-stratum/fixed-n algorithms | **Proved decidability/enumeration interfaces** for the stated cells and candidate classes.  No polynomial full exact-cone enumeration claim is licensed. | research note, fixed-stratum and cellwise-pullback sections |
| Six-player positive-residual facet atlas | **Exact finite theorem/audit.** Thirteen facets in five support orbits cover the live archived residuals; it is not an all-n class exhaustion. | `audit_n6_positive_residual_facet_atlas.py`; independent Z3 verifier |
| Seven-player hostile and equality controls | **Exact falsification controls.** Every new general lemma must pass the fixed hostile cases and both balanced equality orientations `(2,4)` and `(3,3)`. | research note and adjacent n=7 verifiers |

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
is also open: no proof or exact counterexample is known for the required
atomic-weight-aware four-role target.  The current exact searches are only
hostile discovery checks.  Success on the quotient theorem alone would not
complete the project unless the carrier/separator gluing arrow is also proved.
