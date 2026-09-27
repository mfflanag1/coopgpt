# A necessary size-growth condition for first-face amplification

This is a conventional consequence of LP duality, vertices, and the Hadamard determinant bound. It is a certificate-size observation, not a claim of methodological novelty or a size-independent fairness theorem.

Let a strict three-uniform assignment game have n players, nonnegative values, positive integral worth T, and nonempty core P. Put tau=max_(p in P) min_i p_i>0. Suppose coordinate i is fixed to tau throughout the first optimal face F={p in P:p>=tau}. Then

    H_i / tau <= n * 3^((n-1)/2).

Consequently a family of such first-face targets with tau/H_i tending to zero must have unbounded player count. Varying only the weights on a fixed finite player set cannot suffice. The bound is deliberately crude and does not depend on pair additivity.

## Proof

Let E be the triple-by-player incidence matrix. The residual cover LP has primal variables q=p-tau*1>=0, constraints Eq>=w-3*tau, and minimum total T-n*tau. Its dual is

    maximize lambda.(w-3*tau), subject to lambda>=0, E^T lambda<=1.

The optimum equality follows from a floor-attaining core point and the lower bound obtained by summing a residual cover over an optimal integral matching. Positive first floor forces every optimal matching to cover all players: its team covers already spend T, so a positive unmatched payoff would contradict efficiency. Every residual primal optimum corresponds to F. Write r=w-3*tau and L=T-n*tau. Maximize q_i subject to Eq>=r, q>=0, sum(q)=L. Its optimum is zero by the hypothesis on i. The dual has alpha>=0 and a free scalar mu, with

    mu*1 - E^T alpha >= e_i,
    minimum objective mu*L - alpha.r = 0.

Since E and alpha are nonnegative, the target inequality implies mu>=1. Therefore lambda=alpha/mu is an optimal residual dual, with positive deficit d_i=1-(E^T lambda)_i>=1/mu. This is a direct strong-duality argument; strict complementarity is not needed.

The residual dual feasible polytope is compact: every lambda_e is between zero and one. An optimal vertex with d_i>0 exists by decomposing the preceding optimal dual into optimal vertices.

Let S be the positive support of that vertex, with k=|S|. The tight player-load rows restricted to S have rank k; otherwise a sufficiently small nonzero two-sided perturbation on S preserves those equalities, the positive variables, and all remaining strict load bounds, contradicting extremality. Since row i is not tight, k<=n-1. Choose k independent tight rows R. Then

    E^T_(R,S) lambda_S = 1.

This is a nonsingular k-by-k zero-one system. Write D for its nonzero integer determinant. Every column contains at most three ones, so |D|<=3^(k/2) by Hadamard. Cramer's rule implies that the positive number d_i is an integer multiple of 1/|D|. Thus d_i>=1/|D|. The k=0 vertex has d_i=1 and is handled by D=1.

For every full-core y, strong duality gives the exact identity

    sum_j d_j y_j + sum_e lambda_e (sum_(j in e) y_j - w_e)
      = tau * sum_j d_j.

All terms on the left are nonnegative. Hence H_i<=tau*sum(d)/d_i. Since 0<=d_j<=1, this is at most tau*n*|D|, which is at most tau*n*3^((n-1)/2).

This proves only a fixed-size, first-global-face bound. It does not handle arbitrary later positive stages with previously frozen payoffs, does not prove c_pair>0, and does not exclude unbounded-size families with bounded individual pair entries. The cycle4 example meets the hypotheses and is consistent with the bound.
