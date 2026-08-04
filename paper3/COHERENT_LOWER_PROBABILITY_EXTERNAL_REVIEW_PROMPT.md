# External-review request: sharp credal Lorenz threshold

Please review the candidate theorem in:

```text
paper3/COHERENT_LOWER_PROBABILITY_THRESHOLD.md
```

and its exact audit:

```text
src/verify_credal_four_five_threshold.py
results/credal_four_five_threshold.json
```

The supporting cooperative-game theorem is Corollary
`cor:lx-circuit-four-five-threshold` in:

```text
paper3/sections_leximin.tex
```

Please assess four questions hostilely:

1. Does the atom-removal affine bijection cover every finite coherent lower
   probability under the stated definition, including the `R=0` case?
2. Does exact-partition/Lorenz prior art really imply the through-four credal
   claim after the affine transformation, or is an order-theoretic step
   missing?
3. Do the two crossing Lorenz curves and uniqueness of leximin suffice to
   exclude every Lorenz-dominating point in the five-state credal set?
4. Is the sharp four/five theorem already known in coherent lower
   probabilities, credal-set selection, majorization, or base-polyhedron
   theory? Please identify the closest theorem and exact citation.

Reproduction command from the `coopgames` directory:

```bash
/Users/maxf/miniforge3/bin/python3 \
  src/verify_credal_four_five_threshold.py \
  --output /tmp/credal-four-five.json
cmp /tmp/credal-four-five.json \
  results/credal_four_five_threshold.json
```

Please treat the script as a bug-detecting audit only. The claimed proof is
the human affine reduction plus the already documented structural
four-player theorem. No novelty or field-level significance should be
accepted without a literature-based specialist judgment.
