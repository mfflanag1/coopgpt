# Breakthrough-goal checkpoint — 2026-08-04

## Decision at this checkpoint

Pause research here. The current branch contains a coherent theorem chain,
reproducible exact audits, a built paper, and an explicit prior-art correction.
Starting another search or another corollary before external review would risk
optimizing presentation around an untested novelty claim.

The defensible assessment is:

> advanced, research-level mathematics with an apparently new sharp
> classification in a specialized part of cooperative game theory, plus a
> dimension-free robust credal-set extension; not yet a major field
> breakthrough.

## What has been achieved

### Structural cooperative-game core

1. Exact games with at most four players are proved to have the exact-partition
   property at Lmin; a five-player exact game gives sharp failure.
2. A human structural mechanism explains the threshold through strict Lmin
   covers, active traces, uncrossing, and the first realizable broken tight
   diamond. The complete poorer/richer boundary staircase is
   `m_min(1)=4`, `m_min(2)=m_min(3)=3`, and `m_min(h)=2` for `h>=4`.
3. Dimension-free local theorem: supermodularity only on pairs of events
   binding at the selected point suffices for a universal Lorenz selector;
   every failure exposes a crossing binding pair with positive defect.

The exact-partition condition and its exact implication to Lorenz dominance
are prior art. The low-dimensional classification, sharp five-player failure,
and the structural obstruction mechanism are the central candidate
contributions.

### Quantitative robustness and information theory

For a compact credal set and candidate `phi`, let `epsilon` be the largest
richer-stratum face slack. The current theorem proves:

```text
each Lorenz-coordinate regret <= epsilon,
distance to a point Lorenz-dominated by phi <= 2 epsilon in l1,
regret of every l1-M-Lipschitz Schur-concave F <= 2 M epsilon.
```

Binding-event uncrossing defects give an upstream bound on `epsilon`. The
five-state obstruction attains both geometric constants. A separate Shannon
corollary gives the sharp-form Fannes--Audenaert bound, and the exact entropy
maximizer of the five-state core is computed over `Q(sqrt(43))`.

### Prior-art correction made at this checkpoint

Sanchez-Soriano, Branzei, Llorca, and Tijs (2010), Proposition 2, already
prove the exact cooperative-game block-prefix-to-Lorenz implication and apply
it to Dutta--Ray and equal-split-off allocations. The manuscript now cites
this primary source and no longer treats the zero-slack endpoint/block
argument as candidate novelty.

The narrower candidate contribution is the additive-error theorem: richer-face
slack controls Lorenz regret and the exact `2 epsilon` approximate-majorization
radius, while binding-event defect budgets control that slack.

## Verification and review status

### Internally verified

- Exact rational verifiers recompute the selectors, sharp examples, defects,
  Lorenz regret, and distance constants.
- The defect-stability audit checks 51,989 ordered rational-vector pairs
  through five states as a bug audit, not proof evidence.
- The Shannon audit checks full-core feasibility, the quadratic-field KKT
  identity, entropy values, and the continuity bound.
- The LaTeX paper builds reproducibly and is checked for warnings and rendered
  layout at release checkpoints.

### Externally reviewed

Earlier hostile reviews materially corrected the four-player bridge,
five-player verifier, exact-partition attribution, domain quantifiers,
concavity/Lorenz exposition, and the two-parameter obstruction family. Those
reviews improved the project but do not constitute journal peer review.

### Not yet externally reviewed

The three newest results still require independent specialist review:

1. binding-event universal-selector theorem;
2. defect-to-uncertainty stability theorem and sharpness;
3. Shannon defect-to-entropy corollary and exact five-state entropy optimizer.

No external reviewer has yet certified the complete current theorem chain or
its novelty. Negative literature searches are not novelty proof. The closest
unavailable gap remains the full text of Yanovskaya (2023), *Rich Extensions
of the Core and the Equal Split Off Set*.

## Mathematical level

The work is at a strong research PhD/postdoctoral level. It combines
polyhedral cooperative game theory, leximin/dec-min geometry, balanced and
semi-balanced set systems, uncrossing, majorization, exact arithmetic, and
entropy continuity. The proofs are not routine computations: the sharp
four/five threshold and dimension-free binding-event theorem are genuine
structural mathematics.

The deepest current content is the structural classification and local
binding-event theorem. The entropy result is a rigorous and useful
cross-field consequence, but its final step composes established approximate
majorization and Fannes--Audenaert theory; it should not be sold as the main
breakthrough.

## What prevents “major field breakthrough” status

1. Specialist correctness and novelty review is incomplete.
2. The main theorem resolves a narrow solution-theory question, even though
   the credal formulation broadens its audience.
3. Several ingredients are classical, and the manuscript must keep separating
   the new bridges from exact-partition, Lorenz, uncrossing, majorization, and
   entropy prior art.
4. The current manuscript is long. A field-level result needs a short,
   memorable structural theorem and proof, not only a large dependency chain.
5. The work does not yet give a dimension-free classification of all failures
   or a standard-object characterization that other researchers can reuse.

## Best next steps after review

### 1. Seek a forbidden-configuration theorem

The highest-upside direction is to prove that failure of the Lmin
exact-partition property is equivalent, after contraction/deletion or a
precise face reduction, to a small rooted nonintegral trace circuit or broken
tight diamond. This would turn the four/five threshold from one classification
into the first case of a dimension-free obstruction theory.

### 2. Compress the proof into a structural centerpiece

Extract a short theorem chain:

```text
strict Lmin boundary
  -> minimal rooted trace circuit
  -> exact-face capacity obstruction
  -> no obstruction on four players
  -> unique first obstruction on five
  -> quantitative defect/majorization stability.
```

A clean 15–25 page paper centered on this chain has a better chance of being
recognized than a 100-plus-page omnibus manuscript.

### 3. Obtain three targeted hostile reviews before adding corollaries

- cooperative-game/exact-partition specialist: central 4/5 theorem and
  terminology;
- combinatorial-optimization specialist: rooted trace, uncrossing, and
  forbidden-configuration mechanism;
- majorization/imprecise-probability specialist: additive-error and credal
  selector results.

### 4. Use a hard go/no-go test

Resume theorem search only if review confirms that at least one of these is
both correct and absent from the literature:

- the sharp Lmin exact-partition 4/5 classification;
- the binding-only universal-selector theorem;
- the richer-face/defect quantitative stability bridge.

If all three survive, pursue the forbidden-configuration theorem. If the
first is known but the latter two survive, split off a credal/majorization
paper. If the quantitative bridge is known, refocus entirely on the sharp
structural classification.

## Reproduction entry points

```bash
python src/verify_credal_defect_stability.py \
  --output /tmp/credal-defect-stability.json
cmp /tmp/credal-defect-stability.json \
  results/credal_defect_stability.json

python src/verify_credal_shannon_stability.py \
  --output /tmp/credal-shannon-stability.json
cmp /tmp/credal-shannon-stability.json \
  results/credal_shannon_stability.json

cd paper3
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
```

Reviewer entry points:

```text
paper3/N4_LMIN_LMAX_REVIEW_PACKET.md
paper3/CREDAL_BINDING_EVENT_EXTERNAL_REVIEW_PROMPT.md
paper3/CREDAL_DEFECT_STABILITY_EXTERNAL_REVIEW_PROMPT.md
paper3/CREDAL_SHANNON_DEFECT_EXTERNAL_REVIEW_PROMPT.md
paper3/EXACT_PARTITION_CITATION_NETWORK_AUDIT.md
paper3/wrapper.pdf
```
