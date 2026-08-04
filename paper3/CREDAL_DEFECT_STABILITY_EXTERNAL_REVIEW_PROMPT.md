# Hostile review: defect-to-uncertainty stability theorem

Please audit the theorem and proof in:

```text
paper3/CREDAL_DEFECT_STABILITY_THEOREM.md
paper3/sections_leximin.tex
```

The exact arithmetic audit is:

```text
src/verify_credal_defect_stability.py
results/credal_defect_stability.json
```

The Shannon-entropy specialization and its separate hostile review are:

```text
paper3/CREDAL_SHANNON_DEFECT_BOUND.md
paper3/CREDAL_SHANNON_DEFECT_EXTERNAL_REVIEW_PROMPT.md
src/verify_credal_shannon_stability.py
results/credal_shannon_stability.json
```

Please answer the following questions hostilely.

1. Does concavity of the upper Lorenz curve interpolate the richer-stratum
   boundary inequalities with no missing boundary, tie, or ordering case?
2. Is the resulting bound `L_k(p)<=L_k(phi)+epsilon` correctly oriented?
3. Does the established `l1` approximate-majorization formula give a point
   Lorenz-dominated by `phi` within distance `2 epsilon` under the paper's
   increasing-order convention?
4. Does the direct lower-tail-to-upper-tail mass-transfer proof cover zero
   coordinates, ties, and the case where several coordinates are exhausted?
5. Is the `2M epsilon` regret bound valid for every `M`-Lipschitz
   Schur-concave functional without assuming concavity or differentiability?
6. Does the uncrossing-defect budget apply to a rational Lmin strict cover at
   every strict boundary and yield the displayed normalized bound?
7. Do the five-state calculations really attain both constants `epsilon` and
   `2 epsilon`?
8. Does the inert positive-defect example correctly show why one cannot use
   the maximum defect over all binding pairs?
9. Is the suffix-slack-to-approximate-majorization bridge, or its combination
   with an uncrossing-defect budget, already known in cooperative games,
   credal sets, approximate majorization, or robust uncertainty selection?
   Give the closest exact theorem and citation.

Reproduce from the `coopgames` directory:

```bash
/Users/maxf/miniforge3/bin/python3 \
  src/verify_credal_defect_stability.py \
  --output /tmp/credal-defect-stability.json
cmp /tmp/credal-defect-stability.json \
  results/credal_defect_stability.json
```

Treat approximate majorization, Schur concavity, Lorenz curves, coherent
lower probabilities, exact games, and set-family uncrossing as prior art.
The candidate novelty is only the quantitative bridge among canonical
suffix slacks, binding-event defect budgets, and simultaneous uncertainty
regret. The 51,989-pair rational grid is a bug audit, not proof evidence.
Negative keyword searches are not novelty proof.
