# External review packet: weighted four-role edge confinement

## Claim to review

Let a compact four-role core have positive integer role weights.  If two points that
are Lorenz-undominated after repeating each role per-capita payoff by its
weight lie on the same endpoint of one complementary pair-sum slab, then
either they coincide or they lie on the same endpoint of a second independent
pair-sum slab.

Applied along a connected positive-Lorenz continuation from weighted Lmin to
weighted Lmax, this also rules out turns between incident pair-box edges.
Consequently the selectors coincide or share two pair endpoints.  The proved
common-two theorem then establishes the atomic overlap target for every
four-role quotient satisfying objective A's hypotheses.  This completes
objective A; carrier/separator gluing and full equality/facet classification
remain open.

This is a structural theorem about the core geometry.  It does not require
exactness, singleton normalization, or a solver.  No novelty
or external validation is claimed.

## Human proof map

The full proof is in:

- `paper5/divergence.tex`, Theorem `common-face-rigidity`, equations
  `(FEC5)--(FEC9)`, and Theorem `four-role-confinement`;
- `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, equations `(FEC6)--(FEC10)`.

Fix the common pair total and write

```text
q=(s,W-s,t,T-W-t).
```

1. The two fixed-total role pairs have weighted-equality splits `s_*` and
   `t_*`.  Their absolute split deviations `d_1,d_2` are Lorenz dispersion
   coordinates: moving either toward zero is a Pigou--Dalton transfer between
   clone blocks.  Componentwise dispersion reduction therefore strictly
   Lorenz-improves the repeated vector.
2. Convexity puts every pair of Lorenz-undominated points in a common closed
   orthant about `(s_*,t_*)`.  If a segment crosses an equality axis, its
   crossing has zero dispersion in that coordinate and no more than the
   larger endpoint dispersion in the other, so it dominates one endpoint.
3. In one orthant, singleton/complement bounds are coordinate intervals in
   `(d_1,d_2)`.  The two remaining pair-slab normals are
   `(epsilon_1,epsilon_2)` and `(epsilon_1,-epsilon_2)`.  Exactly one has
   equal signs.  Coordinate boundaries and the opposite-sign strip have no
   negative-slope edge, so each contains at most one Pareto-minimal point.
   A non-singleton lower convex frontier must be the unique inward endpoint
   of the equal-sign strip.  Thus all distinct undominated points share that
   second pair endpoint.
4. The repeated-payoff Lorenz partial sums are continuous concave polyhedral
   functions.  Lmin and Lmax uniquely maximize two strictly positive
   scalarizations of these sums.  Along the segment between the coefficient
   vectors, each argmax fiber is compact and convex.  The argmax graph is
   connected: a separation would have overlapping parameter projections and
   would disconnect one fiber.  Its projection is therefore a connected set
   of Lorenz-undominated core points containing both selectors.
5. The two-active-crossing proof applies to every point in that continuation,
   placing it in the pair-box one-skeleton.  A connected subset spanning two
   edges must use two incident edge interiors.  Such points share exactly one
   pair endpoint, which common-face rigidity forbids.  The continuation lies
   on one edge, so the selectors share its two defining endpoints.

## Exact audits

The identity audit checks 1,584 exact within-pair contractions, 12,480 exact
block-diagonal Lorenz contractions, all four orthant-normal rows, and 5,000
exact rational dispersion polygons, including 2,709 nonsingleton Pareto
frontiers.  It also enumerates all 4,095 nonempty subsets of the 12-edge pair
box; among 2,433 connected subsets, exactly the 12 singleton edges satisfy
the no-turn consequence of common-face rigidity:

```bash
python verifiers/divergence/verify_weighted_common_face_rigidity.py \
  --output /tmp/weighted_common_face_rigidity.json
cmp verifiers/divergence/weighted_common_face_rigidity.json \
  /tmp/weighted_common_face_rigidity.json
```

The separate quantified-LRA hostile audit represents the whole four-role
core by coordinate intervals and three pair slabs and defines both selectors
by universal max-min/min-max fairness.  Across every ordered positive weight
row of total 4 through 7 it reports 105 UNSAT canonical Type II--IV cells and
no unknowns:

```bash
python verifiers/divergence/audit_noncommon_transition_z3.py \
  --min-n 4 --max-n 7 --types II,III,IV --timeout-ms 300000 \
  --output /tmp/noncommon_transition_z3_n4_n7.json
cmp verifiers/divergence/noncommon_transition_z3_n4_n7.json \
  /tmp/noncommon_transition_z3_n4_n7.json
```

The LRA audit reuses the fairness formulation of the earlier common-two
audit; it is a hostile finite control, not independent proof of the human
edge-confinement theorem.  The parametric exclusion of Types III--IV comes
from connected Lorenz continuation, not from this finite audit.

The fixed seven-player hostile branch and both sharp equality orientations
remain unchanged under the existing common-hinge/rooted-hinge replay:

```bash
python verifiers/divergence/verify_common_hinge_root_reduction.py \
  --output /tmp/common_hinge_root_reduction.json
python verifiers/divergence/verify_rooted_hinge_projection.py \
  --output /tmp/rooted_hinge_projection.json
```

Those controls audit the surrounding carrier/facet architecture; they are
not additional evidence for common-face rigidity itself.

## Requested hostile review

1. Does blockwise reduction of the two fixed-total dispersion coordinates
   indeed imply Lorenz dominance of the concatenated repeated vector?
2. Is the segment argument sufficient to place any two undominated points in
   one closed orthant, including equality-axis boundary cases?
3. In the two-dimensional convex polygon, can two distinct Pareto-minimal
   pieces evade the unique negative-slope equal-sign pair boundary?
4. Does every four-role core restricted to a pair endpoint reduce exactly to
   coordinate intervals plus the two stated pair strips, with no omitted
   coalition inequality?
5. Is the application from Lorenz undominance to both weighted canonical
   selectors stated with the correct repeated-payoff convention?
6. Does finite polyhedral lexicographic optimization indeed provide strictly
   positive Lorenz-sum scalarizers uniquely selecting both Lmin and Lmax?
7. Is the compact-graph/connected-fiber argument sufficient to make the union
   of intervening argmax sets connected?
8. Does the two-active-crossing proof extend to every Lorenz-undominated
   continuation point, including a possible Lorenz-greatest point?
9. Can a connected subset of the clipped box one-skeleton pass between edges
   without creating two points on incident edge interiors, including
   zero-width or three-flat degeneracies?
10. Please distinguish an error in edge confinement from the quantitative
    common-two theorem: the latter still has a computer-assisted six-row
    component and does not by itself classify every equality core.
