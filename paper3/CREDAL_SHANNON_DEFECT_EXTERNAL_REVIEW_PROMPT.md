# Hostile review: Shannon upper-entropy defect bound

Please audit:

```text
paper3/CREDAL_SHANNON_DEFECT_BOUND.md
paper3/CREDAL_DEFECT_STABILITY_THEOREM.md
paper3/sections_leximin.tex
```

Exact audit:

```text
src/verify_credal_shannon_stability.py
results/credal_shannon_stability.json
```

Please answer hostilely:

1. Does the approximate-majorization theorem provide `q` with total
   variation at most `epsilon` in the required Lorenz direction?
2. Is the Fannes--Audenaert inequality applied with the correct factor of two
   between total variation and `l1` distance?
3. Is `h(t)+t log(n-1)` maximized over `0<=t<=epsilon` at
   `min{epsilon,1-1/n}`?
4. Does Schur concavity give `H(q)<=H(phi)` under the manuscript's Lorenz
   convention?
5. Does the two-point family attain the global geometric constant, and is the
   caveat that `phi` is not its inc-max point stated prominently enough?
6. Is the displayed `Q(sqrt(43))` point in the full five-state credal core?
7. Do the two active constraints, positivity, strict concavity, and the KKT
   product identity prove that it is the unique Shannon maximizer of the full
   core rather than merely of a relaxation?
8. Is the composed binding-defect-to-upper-entropy theorem already known in
   imprecise probability, robust entropy maximization, approximate
   majorization, or cooperative games? Give the closest exact citation.

Reproduce from `coopgames`:

```bash
/Users/maxf/miniforge3/bin/python3 \
  src/verify_credal_shannon_stability.py \
  --output /tmp/credal-shannon-stability.json
cmp /tmp/credal-shannon-stability.json \
  results/credal_shannon_stability.json
```

Treat Shannon entropy, Schur concavity, the Fannes--Audenaert inequality,
approximate majorization, and coherent lower probabilities as prior art. The
candidate novelty is only the bridge from canonical binding-event defect
budgets to a sharp-form upper-entropy regret guarantee.
