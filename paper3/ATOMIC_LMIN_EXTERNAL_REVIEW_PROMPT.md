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
- `paper3/TWO_SIDED_TRACE_COUPLING.md`
- `src/verify_atomic_lmin_obstruction.py`
- `src/verify_rooted_deficit_completion.py`
- `src/verify_block_star_facet.py`
- `src/verify_two_sided_trace_coupling.py`
- `results/atomic_lmin_obstruction.json`
- `results/rooted_deficit_completion.json`
- `results/block_star_facet.json`
- `results/two_sided_trace_coupling.json`
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
18. Audit the two-sided trace-coupling normal form coordinate by coordinate.
    Check that the treatment of coalitions coinciding with rooted spokes is
    unambiguous, that `alpha>=0` follows without an omitted coverage
    hypothesis, and that the claimed linear bijection really identifies the
    extreme rays of the nonnegative rooted-relation cone with extreme
    coupling rays.  Look for degeneracies at `alpha=0`, `beta=0`, empty rich
    traces, and repeated coalition columns.
19. Search balanced-hypergraph, exact-cover, oriented-matroid, and
    exact-game literature for an equivalent two-block coupling formulation.
    The coordinate split itself is elementary; assess novelty only for the
    Lmin-selected obstruction cone and any later classification of its
    extreme rays.
20. Audit the single-packet Lmin star-or-trace reduction.  Check that deleting every
    `H`-disjoint tight coalition preserves a strict cover, that conformal
    circuit reduction cannot reintroduce a deleted coalition, and that every
    remaining non-spoke term has a nonempty rich trace.  Verify that the
    `alpha=0` branch then collapses exactly to the block star, including
    degeneracies caused by a coalition serving simultaneously as a tight
    protector and a rooted completion spoke.
21. Check the canonical rooted-excess argument independently.  Verify
    boundedness of the nonempty-trace exact-cover polytope, the lifted extreme
    packet decomposition, convexity of
    `delta(r)=1+(m-1)max_i r_i-sum_i r_i`, strict positivity at the averaged
    poorer load, every coefficient in the canonical completion identity, and
    the Jensen step selecting one positive-excess packet.  Finally check that
    a conformal circuit's non-spoke traces form a balanced subcollection and
    minimality forces the entire packet, including repeated-trace and
    full-trace degeneracies.
22. Audit the canonical packet slack-transfer theorem. Starting from the
    completed packet relation, verify the direction of the exact-balancedness
    inequality and every sign in
    `delta s(H) <= sum_i (b-r_i)s(H union {i})`. Check that `b<1` forces a
    strictly larger completion slack, and that the two-poorer specialization
    has the exact factor `(1-r_a)/(r_b-r_a)`. Independently recompute the
    saturated factors `2` and `3/2` in the three-column and four-co-singleton
    examples. Verify the equivalent marginal-deficit formula and its strict
    sign. Assess whether this invariant or an equivalent slack-ascent
    lemma already appears in exact-balanced, exact-partition, or egalitarian
    solution theory.

Please report fatal errors first, then repairable gaps, then novelty risks.
State whether the result is (a) correct as written, (b) correct after named
repairs, or (c) false, and identify the exact equation or implication at
issue.
