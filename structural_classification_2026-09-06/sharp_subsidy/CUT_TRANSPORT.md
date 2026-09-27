# Cut weights on incidence trees: exact identities, certificates and limitation

Date: 2026-09-07. Global sharp-constant bounds remain 1/3 <= S_3 <= 2/5. This is an all-size structural lemma with fixed-pattern certificates and an exact limitation; it is not a universal one-third theorem.

## 1. Tree cut weights

Let the bipartite incidence graph of diagonal labels and P-teams be a tree. Write r=|P|, m=2r+1, h=m-r=r+1, and u=3h. Deleting a P-team node e leaves three components. Let c_e(j) be the number of unmatched players in the component containing label j. Every component has a positive such count: if it contains r' other P-teams, it has 2r'+1 labels and 3r'+2 unmatched players. Thus c_e(j)>=2.

For deletion row i set

    p_{i,e}=2/u + 1/(3 c_e(label(i))).                   (1)

The three components partition U. Summing (1) over all unmatched rows gives exactly three copies of each P-team. These weights are a two-thirds uniform, one-third inverse-component-size mixture.

For each label j other than label(i), let M_{i,j} be the largest P load of its three players and set d_{i,j}=1-M_{i,j}. At the excluded label set d=0. This is the maximal feasible diagonal mass for the chosen P weights.

## 2. Two exact tree identities

Root the incidence tree at label(i). At any other label j, its largest incident P weight is the weight on the edge toward the root. The component containing the root after deleting that edge is contained in the corresponding root components for the other incident edges; reciprocals therefore have the required ordering. Every P-node has exactly two child labels. Consequently

    sum_{j != label(i)} M_{i,j}=2 sum_e p_{i,e}.

The remaining supply of sector-i players after diagonal placement is therefore

    R_i=m-1-sum_e p_{i,e}-sum_j d_{i,j}=sum_e p_{i,e}.    (2)

There is also an aggregate identity. Let k_j=3-d_j^used be the number of unmatched players at label j. The 2d_j^used outward components beyond its incident P-nodes partition U outside label j. On each such component, the maximum reciprocal contributing to M has sum one over its unmatched players. Hence

    sum_i d_{i,j}
      =(u-k_j)(1-2/u) - 2d_j^used/3
      =u-4-k_j(h-2)/(3h).                              (3)

The notation d^used refers to incidence degree; d_{i,j} refers to diagonal packing mass.

Thus to reach one-third coverage, the residual demand at label j in each sector is

    a_j=k_j(h-2)/(3h).                                 (4)

The total demand per sector is h-2, since sum_j k_j=3h.

## 3. Exact transportation realization when feasible

For row i in sector s, let A_{i,j} be its remaining sector-player capacity before diagonal placement and B_{i,j} the remaining opposite-sector pair capacity, as in VARIABLE_P_DIRECTION.md. Let

    r_{i,j}=A_{i,j}-d_{i,j},
    b_{i,j}=B_{i,j}-d_{i,j}.

When j is not the excluded label, positive r means another sector has strictly larger P load than s, so b=0. Positive b means s has the strictly largest load, so r=0. At the excluded label r=0 as well. The residual source and destination labels are therefore disjoint.

For each sector, send row supply R_i through edges of capacity b_{i,j} to label demands a_j. If this fractional transportation problem is feasible, its row-to-label flows can be completed by greedily pairing each row's destination mass with its residual source players. Disjoint support prevents a forbidden diagonal entry. Add the P-teams and diagonal masses to obtain the deletion matchings.

This construction uses standard rational max flow, not a market-weight optimization. Identities (2)–(4) are proved for every incidence tree; feasibility of the three transportation problems is not asserted for every tree.

## 4. Exact successful configurations

cut_transport.py constructs the certificates for the existing junctions(2), junctions(8), and junctions(16) patterns, at m=11,35,67. All flows and packing coefficients are rational from the start; no numerical LP or rounding step is used.

verify_cut_transport.py independently checks 20,073 packing entries, all player capacities and exclusions, same-sector support, exactly three aggregate P copies, and pair coverage (u-4)mu+3P. It also verifies each graph's specified junction count and tree property. Thus these fixed obstructions are at most T/3 for all admissible nonnegative pair weights. Other matchings in those markets, and arbitrary incidence trees, are outside that conclusion.

The cut-mixture numerical probe first optimized a common mixing parameter and returned approximately 0.30319, 0.32404 and 0.32854 for the same junction counts. Those numerical optima are discovery only. The retained exact construction fixes the mixture at one-third and is verified independently.

## 5. Exact failure under sector imbalance

For r>=2 take m=2r+1 and

    P_j=(r+1+j,j,j+1),       j=0,...,r-1.

This is a valid incidence tree: its added r leaves use sector A, while the chain labels connect sectors B and C. Each sector has h=r+1 unmatched players.

For edge j, the three cut-component sizes are 2, 3j+2, and 3(r-1-j)+2. The isolated A-leaf component has no unmatched A-player. Using (1), total sector-A residual supply from (2) is

    sum_{i in U_A} R_i
      =8r/9 + (2/9) sum_{j=0}^{r-1} 1/(3j+2).

Demand from (4) is r-1. At r=12 the exact shortfall is

    6560707/129718160 > 0.

The independent verifier reconstructs the components and confirms this value.

This shortfall cannot be repaired just by choosing smaller diagonal masses. For any same-sector block certificate with these fixed P weights, sector A's total q mass is at most sum_i A_i, while its required q mass is at least m(u-4) minus the diagonal mass in the other two deletion sectors. The maximal diagonals used above maximize that latter contribution. Reducing them can only worsen this necessary inequality. Consequently the fixed weights (1) cannot attain one-third coverage on this tree with any same-sector block transfers.

This is a limitation of the fixed weights, not a counterexample to S_3<=1/3. The earlier uniform one-third theorem already covers the appropriate chain classes.

## 6. Next proof obligation

The cut mixture handles junction patterns that defeated the local rule, and the exact imbalance obstruction identifies what its global averaging misses. The next mechanism must account for sector supply when choosing weights—rather than trying another constant mixture of the same two formulas—and may use the tree identities as constraints. Cyclic incidence patterns and actual markets above one-third remain live as well. Novelty, sharpness, and the remaining free-original comparisons are still unresolved.
