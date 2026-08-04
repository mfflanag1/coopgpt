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
- `paper3/MARGINAL_CORE_FACTORIZATION.md`
- `paper3/ROOTED_DEFICIT_COMPLETION.md`
- `paper3/BLOCK_STAR_FACET_THEOREM.md`
- `src/verify_atomic_lmin_obstruction.py`
- `src/verify_rooted_deficit_completion.py`
- `src/verify_block_star_facet.py`
- `results/atomic_lmin_obstruction.json`
- `results/rooted_deficit_completion.json`
- `results/block_star_facet.json`
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
9. Audit the marginal-core factorization.  Does exactifying `H` really imply
   that `w_H(Q)=v(H union Q)-v(H)` is balanced, and is
   `H tight at phi` equivalent to `phi_L in Core(w_H)` with no omitted
   normalization, monotonicity, or superadditivity hypothesis?
10. Is rooted deficit completion strictly the earlier exact-balanced
    incidence inequality after the substitution
    `1_Q=1_{H union Q}-1_H`?  Check every coefficient, the marginal-slack
    identity, finiteness of the rooted LP, and the claim that its optimum is
    bounded above by the unrooted completion cost.
11. Check the rooted atomic reduction, especially why all rooted singletons
    are proper and why at least one must be slack.  Confirm independently
    that the five-player rooted system is indecomposable while the
    seven-player rooted system has the displayed residual decomposition.
12. Search marginal-game, reduced-game, exactness, balancedness, and
    fractional-cover literature for the combined equivalence and rooted
    functional.  Treat the marginal-contribution operation itself as prior
    art and assess novelty only for the exact-face/Lmin assembly.
13. Audit the claim that selector recursion fails: independently recompute
    ordinary and normalized Lmin of both marginal games and compare them
    with the uniformly efficiency-repaired restriction.
14. Audit the two-facet factorization of the full three-trace family,
    including both incidence identities, the block-pattern proofs of
    indecomposability, the appeal to the exact-cone facet theorem, and the
    slack sandwich forcing both factors to be saturated.
15. Audit the dimension-free block-star theorem.  In particular, check the
    unique-dependence/minimality argument, the claim that a prospective new
    exceptional coalition must be a union of whole incidence-row blocks,
    every case in equation `(BSD)`, and the appeal from indecomposability to
    an exact-cone facet.  Check whether this system or equivalent terminology
    already appears explicitly in the exact-game literature.
16. Independently recompute the block-star slack equality in the complete
    two-column family and the universal three-poorer family.  Assess whether
    identifying the same saturated exterior facet in those two families and
    the complementary factor of the three-trace family is a substantive
    Lmin-specific structural contribution or merely a relabeling of a
    standard exact-game facet.
17. Treat the proposed next statement---that every saturated rooted Lmin
    atom factors into block stars and lifted internal balanced facets---only
    as an open conjecture.  Look aggressively for a counterexample before
    recommending that it be promoted to a theorem.

Please report fatal errors first, then repairable gaps, then novelty risks.
State whether the result is (a) correct as written, (b) correct after named
repairs, or (c) false, and identify the exact equation or implication at
issue.
