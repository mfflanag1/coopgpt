# Specialist review brief — prepared, not sent

Please assess the mathematical correctness and prior art of SIMULTANEOUS_PROTECTION.md, with SOURCE_STATUS.md controlling attribution. This is a strengthening of an existing project construction, not a new independently discovered family.

Main proposed contribution: among strict full-team, equal-size, nonnegative pair-additive assignment markets with nonempty entire core, the optimal size-independent simultaneous fraction of all individual core maxima is 1/K on each K-sector tree and zero on every cyclic allowed graph. The triangle witness has exact best protection 1/(2q+3), integer pair entries at most 2, positive core, and an explicit entire-core simplex description.

The key distinction from the prior project result is the quantifier over every core allocation. The poorly protected player can depend on the allocation. Each individual still has an ideal-attaining core point.

Focused questions:

1. Does the simplex representation in Section 4 capture the entire strict core in both directions? In particular, check the weak-a equality argument, the E/N inequalities, and the four strong-a mixed-team cases.
2. Does Section 5 prove every claimed ideal and provide matching primal and dual certificates for rho=1/(2q+3)?
3. Does the cyclic extension legitimately use preserved lower ideal witnesses and a unit residual matching budget, without assuming the enlarged cores are isomorphic?
4. Is this impossibility already implied by a published result on multisided assignment, proportional core sections, or the bilateral half-optimal core? The free Núñez–Rafels 2004 original is explicitly credited. Quint, Lucas and Stuart full-original comparisons remain incomplete.

Evidence: all-parameter conventional proof; 2,553,912 rational cover checks; 16 raw-core SMT UNSAT queries on bounded instances; three negative controls. No new external or paid cross-model review has occurred, and the computational evidence is not a proof-assistant formalization.
