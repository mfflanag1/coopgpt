# Hostile external review: atomic Lmin obstruction reduction

Please review the claimed dimension-free reduction and its circuit proof of
the four/five threshold as if deciding whether the manuscript is safe to
submit.  Do not infer correctness from passing scripts.

## Commit and files

Review the commit identified in the accompanying GitHub pull request, with
special attention to:

- `paper3/ATOMIC_LMIN_OBSTRUCTION_REDUCTION.md`
- `paper3/sections_leximin.tex`, Theorem `atomic Lmin obstruction reduction`
  and Corollary `circuit proof of the four/five threshold`
- `paper3/TWO_COLUMN_LMIN_OBSTRUCTION.md`
- `paper3/TIGHT_DEFICIT_COMPLETION_THEOREM.md`
- `src/verify_atomic_lmin_obstruction.py`
- `results/atomic_lmin_obstruction.json`
- `paper3/wrapper.pdf`

## Questions requiring explicit answers

1. Does the conformal circuit decomposition apply exactly as used after
   quotienting by `span{1_N}`?  In particular, does it guarantee a circuit
   whose negative support is exactly the exceptional coalition `H`?
2. Is a circuit of projected proper-coalition incidence vectors equivalent
   here to a *pure minimal semi-balanced system* in the terminology of
   Studeny and Kratochvil?
3. Is the support bound `|A|<=|N|` correct, including all degenerate cases?
4. Does exact balancedness applied to the lifted circuit force the atom to
   contain a positive-slack deficit singleton, as claimed?
5. In the four-player corollary, does removing the unique singleton term
   necessarily leave a strict two-column tight cover, so that the broken-
   diamond theorem applies without an omitted sign or positivity condition?
6. Is the proof genuinely free of payoff-stratum enumeration and sufficient
   to replace the earlier finite classification as the conceptual proof of
   the `4/5` threshold?
7. Search specifically for prior work combining Lmin stagewise tight covers
   with minimal semi-balanced/oriented-matroid circuits.  Separate prior art
   for conformal decomposition and exact-game facets from any prior art for
   this Lmin-selected reduction.
8. Audit the stronger facet-avoidance corollary: does the costly singleton
   always make `E=H union {i}` a proper coalition outside the atom, and does
   `1_H+1_{i}-1_E=0` prove decomposability under the exact published
   definition?  Does the cited facet theorem then justify the conclusion
   that no selected atom is facet-defining?

Please report fatal errors first, then repairable gaps, then novelty risks.
State whether the result is (a) correct as written, (b) correct after named
repairs, or (c) false, and identify the exact equation or implication at
issue.
