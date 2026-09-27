# A stationary leaf-dilation theorem and an infinite two-hub family

Date: 2026-09-07. All-size lifting lemma with an exactly verified seed and rational realizations. Global sharp bounds remain **1/3 <= S_3 <= 2/5**. No novelty or field-level breakthrough is claimed.

## 1. Seed conditions

Let a seed label/P incidence tree have only degree-one and degree-three labels. Every P-team has three distinct labels. Write e for a seed P-node, ell_e for the number of its adjacent leaf labels, and L_(e,s) for the number of those leaves whose unique used player is in sector s.

Suppose an exact one-third deletion certificate is given, using P-teams, diagonals and same-sector transfers. For each deletion row i in sector s, assume:

- E_i=0, equivalently maximal nonroot diagonals and P weights decreasing away from its deletion root;
- sector balance: sum_{i in U_s} p_(i,e)=1 for every e;
- the additional row identity

    sum_e (ell_e-L_(e,s)) p_(i,e)=1.                 (S)

All seed unmatched players lie at leaves. The final identity is called stationarity here solely as a label for this displayed equality. Its purpose is the supply calculation in Section 4; no unproved probabilistic interpretation is used.

Let F_(i,j)>=0 be the additional opposite-pair mass at label j, beyond the diagonal mass in row i. Its possible destinations are the deletion root, sector-s-used leaves, and degree-three labels. At any other leaf its capacity is zero. The residual source supply is P_i=sum_e p_(i,e), by E_i=0. Put L_i=P_i-sum_j F_(i,j)>=0.

## 2. Expand each leaf k-fold

Fix an integer k>=1. For every seed leaf, create k leaves in its P-block, keeping its used sector. Retain the seed degree-three labels and their sector-labelled incident blocks. Replace each seed P-node e by an incidence subtree of P-teams connected through degree-two labels. If the seed P-node has ell_e leaves, the expanded block has

    r'_e=1+(k-1)ell_e

P-teams. It has k copies of every old leaf and the same degree-three boundary ports.

The expansion always exists. To add a leaf in sector s, split any P-team in the selected block. Let a,b be the other two sectors. Replace its old team with two teams: the first keeps its a-player and s-player and uses a new label in sector b; the second keeps the old b-player, uses that new label in sector a, and uses a new leaf label in sector s. The new intermediate label has exactly the used sectors a,b. This adds one P-team, one degree-two label and one leaf, preserves all external ports, and preserves the incidence-tree property. Repeating this split realizes all the required leaf copies.

## 3. Lift the row weights and pair masses

For each seed row i at leaf j, create k rows, one at each leaf copy, in the same sector s. In every such row give every P-team in block e weight p_(i,e)/k. Give every nonroot diagonal the maximal feasible mass. The root-monotonicity ordering is preserved: weights are constant inside each block, and the ordering between blocks follows the seed tree.

For a cloned row with new root j', use the following additional pair masses:

- At its own root:

      F'_(i',j')=F_(i,j)/k+(k-1)/k.

- At each copy of a seed sector-s-used leaf v in block e:

      F'_(i',v')=[F_(i,v)+(k-1)p_(i,e)]/k^2.

- At each original degree-three label v:

      F'_(i',v)=F_(i,v)/k.

No other destinations receive additional mass. Every new unmatched player at a degree-two label gets a separate deletion row consisting only of all diagonals except its own.

## 4. Capacities and the role of (S)

At a root copy, the opposite-pair capacity is 1-p_(i,e)/k, where e is its block. Since F_(i,j)<=1-p_(i,e), the root formula respects this capacity. At a sector-s-used leaf copy, capacity beyond the diagonal is p_(i,e)/k. Since F_(i,v)<=p_(i,e), its formula also respects capacity. At a degree-three label, every P load and the capacity difference beyond its maximal diagonal are scaled by 1/k, so scaling its F by 1/k is feasible.

Maximal diagonals make positive residual source capacity and positive residual pair capacity occur at disjoint labels. Thus, once total source supply dominates total pair demand in each row, ordinary rational transportation can realize all the added pairs without using a forbidden diagonal. Greedy pairing suffices because every positive source is allowed at every positive destination.

The new residual source supply is

    P'_i = sum_e r'_e p_(i,e)/k
         = P_i/k+(k-1)/k sum_e ell_e p_(i,e).

Its total destination mass is

    sum F'_i = [sum_j F_(i,j)]/k
             +(k-1)/k [1+sum_e L_(e,s)p_(i,e)].

Their difference is therefore

    P'_i-sum F'_i
      = L_i/k +(k-1)/k [sum_e(ell_e-L_(e,s))p_(i,e)-1]
      = L_i/k >=0,

using (S). This proves every lifted deletion row is feasible. Rational seed values give rational lifted values and an exact greedy realization.

## 5. Pair coverage

Every new P-team receives three aggregate copies: the k clones divide each seed row's weight by k. Sector balance is preserved as well. Let u' be the number of new deletion rows.

At a new degree-two label, all its incident P-teams belong to the same block. Its own deletion row has zero P weights, so its aggregate diagonal mass is exactly u'-4. No added pair mass is needed there.

At an original degree-three label, the aggregate maximum P load is unchanged: k row clones each contribute 1/k of the old maximum. Its diagonal coverage changes only by u'-u, and aggregate added pair mass is unchanged. Thus the old one-third coverage requirement remains satisfied.

For a leaf j in block e, let i_1,i_2 be its two seed unmatched players. The deficit beyond the new aggregate diagonals at each leaf copy is

    1-[p_(i_1,e)+p_(i_2,e)]/k
      = (k-1)/k + [1-p_(i_1,e)-p_(i_2,e)]/k.

Each incident pair receives the scaled old root mass plus (k-1)/k, which covers this deficit. For the residual pair missing the leaf's used sector s, summing the new leaf formula over the k clones of all seed sector-s rows gives

    (1/k) sum_{i in U_s} F_(i,j)
      +(k-1)/k sum_{i in U_s} p_(i,e).

The second sum is one by sector balance, so this also covers the required deficit. The reasoning remains valid if the old deficit is negative; actual pair masses are nonnegative and the inequality still holds.

Thus all new diagonal pairs receive at least u'-4 copies and every new P-pair receives at least three. The established deletion argument yields J(M,P)<=T/3 for every admissible pair-additive market with this optimal diagonal matching and this dilated obstruction P. Ideals remain those of the original entire core.

## 6. Exact two-hub seed

STATIONARY_EXACT_SEED.json supplies a seed with m=11 and

    P={(0,1,2),(3,0,4),(5,6,0),(1,7,8),(9,10,1)}.

It has two degree-three labels and nine leaves, three used in each sector. Its 366 rational packing entries satisfy the one-third coefficient bound, E_i=0, sector balance and (S). The seed's flow metadata is checked against the packing entries themselves.

The optional numerical discovery first finds stationary marginals. Exact recovery fixes the active affine conditions on the 90 P variables, leaving 18 free variables, and solves the other 72 exactly after rational rounding of those free variables. Root monotonicity and all affine equalities are rechecked. The diagonal masses are then reconstructed exactly, and rational max flow supplies a verified seed. The final verifier does not trust numerical solver status, active-set selection or tolerances.

For this seed the expansion has, for every k>=1,

    m=18k-7,      |P|=9k-4,
    degree-three labels=2,
    degree-two labels=9(k-1),
    leaves=9k.

This is an infinite two-hub family with a constructive one-third obstruction bound. It does not exhaust all two-hub trees, all leaf-count patterns, or cyclic patterns.

## 7. Reproduce and interpret

Run `python3 -O leaf_dilation.py` to regenerate the retained k=1,2,3,5 certificates, then `python3 -O verify_leaf_dilation.py`. The verifier checks the seed identities, topology, block and leaf-copy maps, all deletion capacities and exclusions, and all aggregate pair coefficients. It verifies 26,627 lifted packing entries and rejects an empty certificate. No numerical optimizer is needed for this verification or lifting.

The all-size statement follows from the lifting proof and exactly verified seed, not from extrapolating the four finite checks. Optional discovery/stationary_probe.py and discovery/stationary_recover.py regenerate a candidate seed with SciPy and SymPy; accept it only after the independent seed checks pass.

The next live question is whether arbitrary low-dimensional block counts can be handled, rather than uniformly duplicating every leaf. The additional balance identities have not been proved feasible for every seed, and this lift does not cover arbitrary two-hub trees. The full sharp-subsidy goal remains active with its original scope.

## 8. Why degree-two links can be contracted in the leaf-only model

A related necessary identity motivates the block formulation. In any E=0 one-third tree certificate with three copies of P, suppose every deletion row rooted at a degree-two label has zero P weights. At a degree-two label j joining P-nodes e,f, the opposite pair of its unmatched sector receives only diagonal coverage: all nonroot rows have that pair's capacity equal to the maximal diagonal mass, while the root row has zero residual supply.

Its coverage is therefore u-1-sum_i max(p_(i,e),p_(i,f)); the root row has both weights zero. The target u-4 requires the maximum sum to be at most three. Each of the two P columns sums to three, so this is possible only if p_(i,e)=p_(i,f) in every row. Thus P weights must be constant across every connected block obtained by contracting degree-two labels.

If there are g degree-three labels, tree counting gives n_2=r-2g-1. Contracting those n_2 links among the r P-nodes leaves exactly 2g+1 blocks. This is a reduction of the specified leaf-only certificate model, not a proof that the restriction is without loss for the original sharp problem. Numerical tests on three 24-edge random trees reached t=1 under that restriction; they remain discovery evidence only.
