# Tree core representation and path protection: candidate proof

Status: conventional proof; Claude found no correctness defect in the reviewed argument, and finite raw-core equivalence and explicit path-cycle checks pass. No novelty claim. Model: k>=2 fixed sectors of equal size m>=1, complete k-tuples only productive, nonnegative pair matrices on the edges of a connected tree, and positive total worth T. Coalition values use integral matchings. Root the tree at vertex 0 and orient every edge parent a to child b, with matrix A_ab(parent label, child label). Define c(G) as the infimum of x_i/H_i over all admissible markets on fixed G and players with positive full-core ideal H_i. Zero-ideal coordinates remain in the full leximin optimization; their ratios are not formed.

## Integral worth and simultaneous diagonalization

Choose an optimal perfect matching for each edge. Root-label the players and propagate labels along each chosen matching. There is no conflicting propagation because the sector graph is a tree. All chosen edge matchings are now diagonal. Write d_ab(j)=A_ab(j,j). Any full-team matching projects to edge matchings, so its worth is at most the sum of their optima. The diagonal full-team matching attains this bound. Thus T=sum_j sum_edges d_ab(j). Nonnegative weights and equal sizes allow completion of partial matchings without loss. Assume T>0.

The core is precisely p>=0, sum p=T, and all full-team covers: singleton and team coalitions imply necessity, and summing team inequalities over any integral coalition matching, with nonnegative unmatched payoffs, proves sufficiency. Every diagonal team is tight at every core point because summing its inequalities exhausts T. Put s(j)=sum_edges d_ab(j); then sum_v p_v(j)=s(j).

## Exact cut-variable representation

For each nonroot vertex b, let S_b be its descendant subtree, and define

    U_b(j) = sum_{v in S_b} p_v(j) - sum_{edges internal to S_b} d_edge(j).

Set U_0(j)=0. The entire core is affinely represented by

    U_b(i)-U_b(j) >= A_ab(j,i)-d_ab(j)       (a parent of b; all i,j),
    p_v(j)=U_v(j)-sum_{b child of v} U_b(j)+sum_{b child of v} d_vb(j) >=0.

Necessity: use the full team with label i on S_b and label j on its complement. Subtract the tight diagonal team j. The only edge crossing the cut is ab. Internal diagonal terms cancel after substituting the definition of U_b, leaving the claimed difference inequality. The formula for p is immediate by subtracting child-subtree sums from the parent-subtree sum. At the root it follows from the tight diagonal identity.

Sufficiency: start with arbitrary U satisfying these constraints and reconstruct p by the displayed formula. Summing over vertices at a common label j telescopes to s(j), giving efficiency. For an arbitrary full team with label i_v at vertex v, sum its payoffs:

    sum_v p_v(i_v)
      = sum_{a->b} [U_b(i_b)-U_b(i_a)+d_ab(i_a)]
      >= sum_{a->b} A_ab(i_a,i_b).

This proves every team cover. The transformation is invertible: descendant sums of the reconstructed p recover each U_b. The representation thus preserves labeled coordinates and their full-core ideals.

Nonemptiness is classical matching duality: sum nonnegative optimal bilateral vertex covers over incident edges to obtain full-team covers with total T. This observation and the cut algebra are not asserted to be new.

## Path theorem

For the path 0-1-...-(k-1), rooted at 0, the representation is a potential network. Use nodes (r,j), 1<=r<=k-1, and a single anchor of potential zero. Node (r,j) has potential U_r(j). An arc tail->head of constant c has slack c+U_tail-U_head.

Payoff arcs at each label j:

    anchor -> (1,j), constant d_01(j), payoff p_0(j);
    (r,j) -> (r+1,j), constant d_r,r+1(j), payoff p_r(j), 1<=r<k-1;
    (k-1,j) -> anchor, constant 0, payoff p_{k-1}(j).

Structural arcs stay inside one layer r: (r,i)->(r,j), constant d_(r-1),r(j)-A_(r-1),r(j,i). Their nonnegative slacks are exactly the cut inequalities. Omit i=j zero-slack self-loops, which impose no restriction.

The nonempty core is compact since p>=0 and sum p=T. Each sorted coordinate is continuous, so successive maximization on nested compact sets gives full leximin existence. For uniqueness, if two distinct labeled vectors have the same optimal sorted vector, their average preserves all coordinates below the smallest level at which they differ and reduces the multiplicity of that level, a contradiction to optimality. Thus x is well-defined.

Apply the selected-payoff-slack argument (classical slack-balancing ingredient): for each payoff arc e at full leximin x, a simple directed cycle through e exists whose structural arcs are tight and whose payoff arcs f satisfy x_f<=x_e. To prove it, let eligible arcs be tight structural arcs and payoff arcs with value at most alpha=x_e, and let R be the vertices reaching tail(e) through eligible arcs. If head(e) lies in R, take a simple path from head(e) to tail(e). This path cannot use e because it first reaches tail(e) at its endpoint. Adding e gives the required simple cycle.

Otherwise increase potentials on R by epsilon>0, then subtract the new anchor potential from every potential. No eligible arc enters R from outside, so all eligible slacks weakly increase; e strictly increases. Any omitted structural slack was strictly positive. Any omitted payoff slack exceeded alpha. Finiteness permits epsilon small enough to preserve feasibility and keep every previously higher payoff strictly above alpha. To see strict lexicographic improvement, either an entry below alpha increases, in which case the smallest such changed level has reduced multiplicity and no lower change, or all lower entries stay unchanged and increasing e reduces the multiplicity of alpha. The sorted vector strictly improves, a contradiction.

Any directed cycle containing a payoff arc advances through every layer and the anchor. A simple cycle visits the anchor only once; structural arcs do not change layers, and payoff arcs advance one layer. It therefore has exactly k payoff arcs. On the cycle, slack sums telescope to a fixed constant. At x this is the sum of its payoff entries because structural slacks vanish. For any other feasible y, all slacks are nonnegative, so

    y_e <= sum_cycle constants = sum_{payoff f in cycle} x_f <= k*x_e.

Taking the full-core maximum gives H_e<=k*x_e, including the case x_e=0. This uses all lexicographic stages, not merely the first floor. For m=1 and total edge value 1, the strict core is the k-player unit simplex, whose leximin is uniformly 1/k and each ideal is 1. Hence c(path_k)=1/k for every k>=2.

## Historical scope update, September 7, 2026

The path slack-cycle proof alone does not settle branching. The subsequent ALL_TREES.md clipping argument proves every tree, and GRAPH_DICHOTOMY.md now settles cyclic allowed graphs. The full-core representation above remains the load-bearing dependency; its mathematical proof is unchanged. Earlier open-status statements are superseded.
