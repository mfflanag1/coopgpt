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
paper3/sections_leximin.tex
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

Reproduce the four-state arithmetic from the `coopgames` directory with:

```bash
/Users/maxf/miniforge3/bin/python3 \
  src/verify_credal_lorenz_phase_diagram.py \
  --output /tmp/credal-phase.json
cmp /tmp/credal-phase.json results/credal_lorenz_phase_diagram.json
```

Treat the verifier as a bug audit only. Do not accept novelty from keyword
searches or from the fact that the formulation crosses disciplinary language.
