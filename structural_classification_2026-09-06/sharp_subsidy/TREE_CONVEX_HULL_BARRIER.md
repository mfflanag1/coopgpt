# Averaging integral deletion matchings does not remove the tree barrier

Date: 2026-09-07. All-size extension of TREE_INTEGRAL_BARRIER.md. Global sharp bounds remain 1/3 <= S_3 <= 2/5. No novelty or universal subsidy conclusion is asserted.

## Statement

Consider the same-sector certificate model on a label/P incidence tree. Assume maximal diagonals and P weights decreasing away from each deletion root (equivalently E_i=0), and sector balance sum_{i in U_s}p_(i,e)=1.

If the tree has at least four degree-two labels, a t=1 certificate **cannot have every deletion row in the convex hull of integral deletion matchings**. This remains true even though the averaged P coefficients may be fractional and the individual integral components need not obey sector balance. It is strictly broader than requiring the final P coefficients to be binary.

Here the support consists of P-teams, diagonal teams, and transfers in the deleted player's sector. If a putative decomposition includes other teams, their coefficients must be zero in every positive-weight component because the target row has zero coefficient there. Thus considering larger integral supports cannot conceal such a decomposition.

## 1. A linear inequality on the E=0 face of the integral hull

Fix deletion row i in sector s and root the incidence tree at its label. At each degree-two label j with a used sector-s player, let child_i(j) be the P-node farther from the root. Such a label cannot be the root, because i is globally unmatched by P. Define the linear expression

    K_i(p) = sum_{j: degree(j)=2, sector s used at j} p_(i,child_i(j)).

Every integral same-sector deletion matching on the face E_i=0 satisfies

    L_i >= K_i(p).                                   (1)

Indeed its P coefficients are binary, and E_i=0 makes them root-monotone with maximal diagonals. At a degree-two label, selecting the child P-node also selects the parent. When the deletion sector is one of the two used sectors at that label, this is one of the capacity-consuming joins counted in Section 1 of TREE_INTEGRAL_BARRIER.md. That argument proves L_i at least the number of all such joins. Restricting to degree-two labels gives (1).

The equality E_i=0 passes to each component of any convex decomposition. To see this, E_i=m-1-D_i-2P_i is affine and nonnegative on every feasible deletion matching by TREE_SLACK_IDENTITY.md. A convex average can equal zero only if each positive-weight component equals zero. Consequently (1), which is linear in all row coefficients, holds for every row in the integral hull with E_i=0.

This is a valid inequality for the specified face and support. It is not claimed for arbitrary fractional matchings; the verified fractional certificate below violates it.

## 2. Degree-two coverage requires sum K_i >= n_2

At a degree-two label j, call its two incident P-teams e and f, using sectors a and b, and let i0 be its unmatched sector-c player.

For an integral E=0 deletion row rooted at j, the opposite-pair mass q_(i0,j) is zero: if any P-team is selected, root connectivity uses an opposite player; if none is selected, all other sector-c players are occupied by their maximal diagonals, leaving no source for the root pair. Therefore q_(i0,j)=0 also in every convex combination of such rows.

For every other sector-c row, the opposite-pair capacity at j equals the maximal diagonal mass, because there is no used sector-c player there. Thus the pair missing c receives only aggregate diagonal coverage. For fractional averaged P weights, put

    O = sum_i min(p_(i,e),p_(i,f)),
    M = max(p_(i0,e),p_(i0,f)) <= 1.

Using max(x,y)=x+y-min(x,y) and total P coefficients three gives

    C_(j,c) = sum_i d_(i,j) = u-7+O+M.

The t=1 target implies O+M>=3, hence O>=2. Sector balance implies

    sum_{i in U_c} min(p_(i,e),p_(i,f)) <= 1.

So the overlap contributed by U_a and U_b is at least one. In each such row j is not the root, and root monotonicity makes min(p_(i,e),p_(i,f)) exactly the child P-weight counted in K_i. Summing over degree-two labels yields

    sum_i K_i >= n_2.                                (2)

Sector balance is needed only for the averaged certificate, not its individual integral components.

## 3. Contradiction and explicit separation

If all rows were in the integral hull, (1) and (2) would give sum_i L_i>=n_2. The slack identity with E_i=0 and t=1 gives G_1+sum_i L_i=3, so n_2<=3. This proves the theorem.

On the r=5 chain from TREE_INTEGRAL_BARRIER.md, the closed-form fractional certificate has 570 entries and meets t=1, E_i=0 and sector balance. Twelve of its deletion rows satisfy

    L_i=0,       K_i=2/3.

Each therefore lies outside the integral matching hull, with an exact linear separation of 2/3. This is a statement about the certificate rows, not a new actual-market subsidy bound.

verify_tree_convex_hull.py exhausts all binary P states in each row, retaining the 148 states satisfying root monotonicity. It bounds available opposite-pair capacity and verifies (1) for every retained state, without choosing transfer coefficients. It then reconstructs the fractional control, independently checks its full pair domination, verifies E=0 and sector balance, and checks all twelve stated violations. The all-size theorem rests on the conventional argument; the exhaustive check concerns this specified chain.

Run `python3 -O verify_tree_convex_hull.py` with the existing helper verifiers and uniform_template.py alongside it. No optimizer is needed.

## Consequence for the research program

A randomized construction whose output is an average of integral deletion matchings cannot supply the desired sector-balanced, E=0 certificate on these trees. Work directly with fractional packing capacity: merely randomizing an integral assignment does not preserve the needed generality. Removing sector balance or allowing positive E could change the conclusion, but those alternatives remain unproved routes. The full original sharp-subsidy goal, including cyclic patterns, remains active.
