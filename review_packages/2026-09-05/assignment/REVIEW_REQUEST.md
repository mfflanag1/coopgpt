# Specialist review request — prepared, not sent

**Author:** Maxwell Flanagan — maxwell.flanagan@gmail.com  
**Manuscript:** *Fair core selections: a sharp boundary between pairs and triples*  
**External review status:** PENDING. No response, endorsement or priority clearance is recorded.

I would value a focused correctness and priority review of the attached short manuscript. It compares full ascending leximin and descending-lexicographic-minimum payoffs on entire cores of unit-capacity matching games. Its main candidate contribution is a sharp finite pairwise distance formula and a three-sided bounded-integer construction approaching the universal distance ceiling. The bipartite half-payoff guarantee is explicitly treated as a deduction from Vazirani's existing algorithmic invariants; the paper does not claim that guarantee as an independent fairness discovery.

The attached package contains conventional proofs, an exact verification command and a claim/source ledger. Codex assisted the development, drafting and computational checks. I am seeking independent specialist judgment, rather than counting the project’s internal checks as external validation.

The most useful review would answer these bounded questions:

1. **Pairwise theorem.** Does the signed-threshold feasible-direction argument establish `x_i >= max_C y_i/2` for every nonempty graph matching core? Does the subsequent `T >= 2D+M` argument give `rho <= k/(k+1)` against every minimax point, with the stated finite-player attainment? Is this sharp quantitative statement already explicit or immediate in prior work?
2. **Three-sided construction.** Are the colored triples, integral matching/cover certificates, and both directions of the entire-core parametrization correct? Does the floor-sum argument force the unique first nonfixed leximin point without a symmetry assumption, while the root constraints force a unique minimax point? Do the payoff, player-count and distance formulas follow?
3. **Priority and representations.** Is the `rho -> 2` conclusion already contained in Quint (1991), Lucas (1995), later multisided assignment/core representations, or egalitarian selection literature? A theorem number or primary reference would be especially useful. A general polytope representation needs to preserve the entire payoff core, added player coordinates and both sorted selectors to imply this particular statement.
4. **Positioning.** Is the combined worst-case comparison a worthwhile standalone contribution given the low-dimensional, dummy-and-replication construction? Are the general-graph extension and additive benchmark appropriately described as supporting results rather than independent headline discoveries?

The ledger distinguishes sources inspected in full from previews or later citations. In particular, the original Quint and Lucas texts remain uninspected; the June 2026 Lluc Santamaria Riba implementation thesis is a further targeted follow-up. Please feel free to identify a decisive overlap or flaw without reviewing every computational artifact.

A review reply should be archived separately with its date, reviewer identity, reviewed manuscript version and scope. An informal priority suggestion, a full correctness review and an endorsement are distinct outcomes. This document is an unsent request template and records none of them.
