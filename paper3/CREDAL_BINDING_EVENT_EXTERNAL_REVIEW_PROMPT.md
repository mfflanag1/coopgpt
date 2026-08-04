# Hostile review: dimension-free binding-event credal selector

Please review the theorem and proof in:

```text
paper3/CREDAL_BINDING_EVENT_SELECTOR_THEOREM.md
paper3/sections_leximin.tex
```

The exact arithmetic audit is:

```text
src/verify_lmin_uncrossing_domain.py
results/lmin_uncrossing_domain.json
```

The quantitative stability extension and its separate hostile-review packet
are:

```text
paper3/CREDAL_DEFECT_STABILITY_THEOREM.md
paper3/CREDAL_DEFECT_STABILITY_EXTERNAL_REVIEW_PROMPT.md
src/verify_credal_defect_stability.py
results/credal_defect_stability.json
```

Please answer hostilely:

1. Under atom-vacuity, is the ordinary increasingly maximal credal
   distribution exactly the singleton-normalized game's Lmin allocation?
2. Does supermodularity only on pairs of binding events force their
   intersection and union to bind, including empty-intersection and full-union
   cases?
3. Does the minimum-energy uncrossing argument prove every strict richer-side
   boundary binds without silently assuming global 2-monotonicity?
4. Does exact partition plus the cited published theorem give the Lorenz-
   dominating point with the manuscript's order convention?
5. Is Lorenz dominance correctly equivalent to simultaneous maximization of
   every Schur-concave uncertainty functional, with the partial-sum functions
   providing the converse?
6. Does absence of a universal selector really force the stated crossing
   binding pair and positive broken-diamond defect?
7. Does the normalized positive example genuinely lie outside the globally
   2-monotone class while satisfying the binding-only condition?
8. Is this binding-only theorem already known under another name in coherent
   lower probabilities, upper entropy, generalized permutahedra, exact games,
   or submodular optimization? Give the closest exact theorem and citation.

Reproduce from the `coopgames` directory:

```bash
/Users/maxf/miniforge3/bin/python3 \
  src/verify_lmin_uncrossing_domain.py \
  --output /tmp/credal-binding-event.json
cmp /tmp/credal-binding-event.json results/lmin_uncrossing_domain.json
```

Treat the verifier only as a bug audit. Uncrossing, base polyhedra,
2-monotonicity, exact partition, and majorization/Schur concavity are prior
art. The novelty question is narrowly whether local supermodularity only on
constraints binding at the canonical inc-max distribution suffices for a
universal credal selector, and whether every failure has the stated local
broken-diamond certificate.

Mandatory adjacent sources to compare include Abellan and Moral (2003),
Fujishige (1980/2005), Frank and Murota (2022), Studeny and Kratochvil (2017),
and Vu, Destercke, and Pichon (2026). Negative keyword searches are not a
novelty proof.
