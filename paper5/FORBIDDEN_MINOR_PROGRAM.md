# Sparse-fidelity forbidden-minor program

Status date: 2026-08-23.  Starting checkpoint:
`434d33a9584fb01948d1e244da31ffa0a12d1cc0`.

## Frozen target

The object is a literal tuple `(v,x,z,Cx)` consisting of an exact
singleton-normalized TU game, its two staged selectors, and a fixed complete
proper-row Lmin certificate, considered modulo the PXC112 equality of the
staged tangent cones at `x` and `z`.  A sparse-fidelity failure means that
every qualifying extreme top cover gives a retained-row lift whose Lmax is
not `z`.

PXC114 already proves a dimension-free mechanism decomposition: there is a
common descent with an outside-union blocker, or there is a reciprocal pair
of cover circuits.  It does **not** prove that either mechanism has a finite
list of literal game or incidence minors.

## Candidate literal operations

For a player `i` and distinct players `i,j`, the initial audit uses:

1. deletion/restriction: `(v\i)(S)=v(S)`;
2. contraction followed by zero normalization:
   `v/i(S)=v(S+i)-v(i)`, then subtract the contracted singleton baselines;
3. relabeling by a player permutation;
4. defining-row-parallel removal: for a fixed lower-envelope presentation,
   apply deletion when `i,j` occur together or not at all in every displayed
   defining row and also satisfy `x_i=x_j` and `z_i=z_j`;
5. parallel amalgamation: replace `i,j` by a star whose presence represents
   simultaneous presence of both players;
6. selector-zero reduction: apply deletion when `z_i=0`;
7. null reduction: delete `i` when every core allocation has coordinate zero
   (equivalently, in the normalized setting, the core is `Core(v\i) x {0}`).

The parallel condition is deliberately presentation-relative: it is the
literal sparse-row operation proposed for the PXC101/PXC102 family, not an
unstated intrinsic matroid parallelism claim.  Its counterexample therefore
also defeats that particularly strong incidence-and-selector test.

Every claimed reduction must separately preserve: exactness, singleton
normalization, the two selectors and their strata, completeness of the
mapped `Cx`, the qualifying extreme-cover quantifier, and failure of every
cover lift.  Incidence resemblance alone is not a preservation proof.

## First exact no-go

The literal operations 1, 2, 4, 5, and 6 are not universally safe.

- Deleting player `a` from the six-player PXC101 lower-envelope game leaves
  the exact-game cone: the restricted characteristic function differs from
  its own core lower envelope.
- Contracting root player 0 in the PXC116 sparse failure and then
  zero-normalizing gives a five-player game whose singleton mask 1 has
  stated worth `0` but core-envelope worth `1`; contraction can
  therefore leave the exact cone inside the target failure class.
- In the seven-player PXC101 specialization, the two bottom players are
  equal in both selectors and have identical incidence in every displayed
  defining row.  Contracting either one, with zero normalization, produces
  an exact singleton-normalized divergent two-top game in which both extreme
  covers are faithful.  Literal parallel amalgamation of the pair produces
  the same selector pair and the same loss of failure.
- A second dimension-minimal six-player universal failure has `z_i=0`, but
  deleting that player is not exact.  A zero selector coordinate is therefore
  not a null certificate even inside the target failure class.

Relabeling is equivariant.  True null reduction is safe for the full core and
the two selectors, but this alone is **not** enough for sparse fidelity:
duplicate tight rows change the extreme-cover polytope.  A null extension of
PXC104 has the same exact core selectors plus a forced zero, yet has faithful
extreme covers.  Null equivalence therefore needs an additional cover-face
hypothesis and cannot currently be admitted as a safe obstruction minor.

Primary exact artifact:

```bash
python3 verifiers/divergence/verify_pxc115_minor_operation_no_go.py \
  --output verifiers/divergence/pxc115_minor_operation_no_go.json
```

## Live theorem and falsification routes

### Route A: maximal safe player reductions

Prove whether any coordinate reduction that is guaranteed to preserve the
ordinary, unweighted staged selectors of every exact singleton-normalized
instance can go beyond relabeling and core-forced null reduction.  A block
contraction naturally preserves a *weighted* selector problem; that is not
the literal PXC112 quotient and must not be substituted silently.

### Route B: infinite antichain — resolved for the audited universal relation

PXC117 defines an operation schema to be universally safe only when it
preserves the complete sparse-failure tuple on every applicable instance.
Among the requested literal schemata, only relabeling survives:

- restriction and selector-zero deletion preserve singleton values but can
  destroy exactness;
- zero-normalized contraction has zero singleton values by construction but
  can destroy exactness (the PXC116 root contraction), and even
  when exact can destroy selector fidelity (the PXC101 parallel-bottom
  contraction);
- deleting one of two defining-row-parallel, selector-equal elements can
  destroy exactness;
- quotient/amalgamation always preserves exactness, and preserves singleton
  normalization exactly when the amalgamated block has worth zero, but can
  destroy selector fidelity and universal cover failure even in the parallel
  equal-selector case.

Under the quasi-order generated by these universally safe audited schemata,
the non-null PXC101 games for n >= 6 form a proved infinite antichain:
relabeling cannot change ground-set cardinality, PXC112 equivalence is a
within-instance certificate quotient, and PXC102 proves a strictly positive
marginal coalition for every player. Therefore no finite forbidden-minor
list exists for this natural universal relation.

This does not settle a future **conditional** reduction with a local,
verdict-independent admissibility test. Such a relation must be defined and
the PXC101 family retested; admitting a step only after recomputing the target
failure verdict would be circular.

### Route C: conditional obstruction minors

One may instead define an operation to be admissible only when its output is
again exact, normalized, certificate-complete, cover-qualifying, and failing.
This relation is scientifically useful only if admissibility has a local
checkable characterization independent of recomputing the desired verdict.
Otherwise the definition is circular and every finite instance has a trivial
minimal descendant.

## Calibration and promotion gates

- PXC101/PXC102 must remain a common-direction failure in every audited
  dimension; PXC104/PXC106 must remain reciprocal-pair failures.
- PXC90 must remain the full-rank faithful control.
- Every negative preservation claim needs an explicit rational witness, not
  a floating search result.
- An independent implementation must reconstruct the counterexamples without
  importing the primary selector, cover, or lower-envelope code.
- No finite forbidden-minor theorem may be claimed until either a well-founded
  safe reduction proves finite primitives, or an infinite-antichain theorem
  proves that such a list cannot exist.
- Prior-art review must separately cover cooperative-game restriction and
  contraction, amalgamation/quotient games, weighted lexicographic solutions,
  oriented-matroid minors, and antichain/well-quasi-order results.

Current evidence tier: a conventional dimension-free natural-operation
impossibility theorem and infinite antichain (PXC117), exact rational
counterexamples to every unsafe universal schema, positive relabeling and
quotient-exactness proofs, and dimension-minimal exact falsifiers of literal
canonicality in both PXC114 branches. A stronger locally admissible
conditional reduction remains open.

## Minimal-primitive classification status

The common-branch proposal is already false.  The six-generator total-18
game pinned by the PXC115 verifier has unique complete `Cx={19,43}`, five
qualifying extreme covers, and common direction `(0,0,0,1,0,-1)` cut only by
row `39`.  PXC101 has two extreme covers.  Cover count is invariant under
relabeling, and PXC100 excludes every smaller-dimensional failure, so this is
a smallest dimension-minimal common obstruction not relabeling-equivalent to
PXC101. Because ordinary deletion is not a safe operation, no stronger
player-deletion minimality is asserted.

The reciprocal-branch analogue is also false.  PXC118 adjoins the common
row `ajk>=7` to PXC104, remains exact and singleton-normalized with the same
selectors, and has exactly two complete `Cx` classes and four qualifying
extreme covers. Every one of the eight certificate-cover lifts fails, both
certificate classes have empty common descent intersection, and the two
rank-three covers retain the reciprocal cross-blocker pair. PXC104 has only
three covers, so the two games are not relabeling-equivalent. PXC100 again
makes the new realization dimension-minimal; as above, no unsafe literal
deletion is invoked to claim a stronger minor-minimal statement.
