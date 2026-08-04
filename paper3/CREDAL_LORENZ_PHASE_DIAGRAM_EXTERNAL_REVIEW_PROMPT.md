# Hostile external review: credal Lorenz phase diagram

Please review the theorem and human proof in:

```text
paper3/CREDAL_LORENZ_PHASE_DIAGRAM.md
```

The exact four-state replay is:

```text
src/verify_credal_lorenz_phase_diagram.py
results/credal_lorenz_phase_diagram.json
```

The atom-vacuous five-state half and supporting four-player structural theorem
are in:

```text
paper3/COHERENT_LOWER_PROBABILITY_THRESHOLD.md
src/verify_credal_four_five_threshold.py
results/credal_four_five_threshold.json
paper3/sections_leximin.tex
```

The separate dimension-free extension beyond global 2-monotonicity is in:

```text
paper3/CREDAL_BINDING_EVENT_SELECTOR_THEOREM.md
paper3/CREDAL_BINDING_EVENT_EXTERNAL_REVIEW_PROMPT.md
src/verify_lmin_uncrossing_domain.py
results/lmin_uncrossing_domain.json
```

Please answer hostilely:

1. Is every credal set on at most three states exactly the stated coordinate
   box slice?
2. Is `f(A)=ell(A)+min{(u-ell)(A),R}` a valid submodular rank function whose
   base is exactly that box slice, including boundary and degenerate cases?
3. Does the cited lexicographically optimal-base theorem yield a unique
   Lorenz-dominating point under the manuscript's order convention?
4. Do the two inequalities in the four-state witness correctly certify the
   two lexicographic selections, and does their Lorenz crossing exclude every
   possible dominator?
5. Is either sharp threshold already known in exact capacities, coherent
   lower probabilities, credal-set selection, majorization, or polymatroid
   theory? Please provide the closest exact theorem and citation.
6. Is the equivalence between Lorenz dominance and simultaneous maximization
   of every Schur-concave uncertainty functional stated with the correct
   order convention and quantifiers? In particular, do the partial-sum
   functionals `L_k` give the converse without extra regularity assumptions?
7. Is the resulting `3/4` and atom-vacuous `4/5` phase diagram for a universal
   maximum-uncertainty representative already known in the credal-set,
   maximum-entropy, majorization, or robust-Bayesian literature?

Reproduce the four-state arithmetic from the `coopgames` directory with:

```bash
/Users/maxf/miniforge3/bin/python3 \
  src/verify_credal_lorenz_phase_diagram.py \
  --output /tmp/credal-phase.json
cmp /tmp/credal-phase.json results/credal_lorenz_phase_diagram.json
/Users/maxf/miniforge3/bin/python3 \
  src/verify_credal_four_five_threshold.py \
  --output /tmp/credal-four-five.json
cmp /tmp/credal-four-five.json results/credal_four_five_threshold.json
```

Treat the verifier as a bug audit only. Do not accept novelty from keyword
searches or from the fact that the formulation crosses disciplinary language.

Friedland, Gheorghiu, and Gour (2013), *Universal Uncertainty Relations*, is
cited only for the established interpretation of nonnegative Schur-concave
functions as uncertainty measures under monotonicity under random relabeling.
Skulj (2022), *Normal Cones Corresponding to Credal Sets of Lower
Probabilities*, is adjacent credal-polytope geometry; its full text contains
no `majoriz`, `Lorenz`, `lexic`, or `entropy` occurrence. Please do not infer
novelty from that negative search. The review question is whether the sharp
state thresholds, as opposed to the standard majorization equivalence, are
new.

Cuzzolin (2022), *The Intersection Probability: Betting with Probability
Intervals*, proposes a different single representative for probability-
interval credal sets. Please check whether its geometry, or earlier work it
cites, implies the universal Schur-concave selector claimed here; the present
audit found no such statement.
