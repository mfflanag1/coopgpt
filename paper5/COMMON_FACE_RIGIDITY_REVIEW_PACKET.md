# External review packet: weighted common-face rigidity

## Claim to review

Let a compact four-role core have positive integer role weights.  If two points that
are Lorenz-undominated after repeating each role per-capita payoff by its
weight lie on the same endpoint of one complementary pair-sum slab, then
either they coincide or they lie on the same endpoint of a second independent
pair-sum slab.

Applied to weighted Lmin and weighted Lmax, this closes both common-face
transition types I and II.  The already proved atomic common-two theorem then
gives the target overlap bound whenever the selectors share even one pair
endpoint.  Opposite-endpoint face-changing types III and IV remain open.

This is a structural theorem about the core geometry.  It does not require
exactness, singleton normalization, or a solver.  No novelty
or external validation is claimed.

## Human proof map

The full proof is in:

- `paper5/divergence.tex`, Theorem `common-face-rigidity`, equations
  `(FEC5)--(FEC8)`;
- `paper5/HYBRID_OVERLAP_FACET_PROGRAM.md`, equations `(FEC6)--(FEC9)`.

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

## Exact audits

The identity audit checks 1,584 exact within-pair contractions, 12,480 exact
block-diagonal Lorenz contractions, all four orthant-normal rows, and 5,000
exact rational dispersion polygons, including 2,709 nonsingleton Pareto
frontiers:

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
theorem and not a parametric-weight proof of Types III--IV.

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
6. Please distinguish an error in this theorem from the still-open
   opposite-endpoint Types III--IV; the latter are not claimed closed by the
   human argument or the finite audit.
