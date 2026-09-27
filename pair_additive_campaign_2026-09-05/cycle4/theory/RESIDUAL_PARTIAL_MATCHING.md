# First-stage residual partial-matching reduction

This is a standard LP reduction retained as a useful certificate interface. It does not use pair additivity and carries no novelty claim. The hoped-for universal six-deficit bound is false by the independently audited 63-player example.

Let E be the triple-versus-player incidence matrix of a strict assignment market with n players, nonempty full core P, and optimal grand-coalition matching value T. Write

\[
P=\{p\ge0:Ep\ge w,\ \mathbf1^Tp=T\},\qquad
\tau=\max_{p\in P}\min_i p_i.
\]

Assume tau>=0. At this first optimal floor, substitute p=tau*1+q. Consider

\[
\begin{aligned}
\min\;&\mathbf1^Tq\\
\text{s.t. }& Eq\ge w-3\tau\mathbf1,\quad q\ge0.
\end{aligned}
\tag{R}
\]

Its dual is a fractional partial-matching problem:

\[
\max\{\lambda^T(w-3\tau\mathbf1):\lambda\ge0,
\ E^T\lambda\le\mathbf1\}.
\tag{D}
\]

**Lemma.** The optimum is T-n*tau. If lambda is dual optimal and d=1-E^T lambda, then for every full-core y,

\[
\sum_i d_i y_i+\sum_e\lambda_e((Ey)_e-w_e)
=T-\lambda^Tw=\tau\sum_i d_i.
\tag{1}
\]

In particular, for d_i>0,

\[
H_i\le\tau\frac{\sum_j d_j}{d_i}.
\tag{2}
\]

**Proof.** A max-min optimal core vector supplies a feasible q with objective T-n*tau. Conversely, any feasible q makes p=tau*1+q a nonnegative triple cover. Summing cover inequalities over an optimal integral matching and using nonnegativity for any unmatched players gives sum(p)>=T. Hence every residual feasible objective is at least T-n*tau. Strong LP duality applies.

At an optimal lambda, the equality lambda^T(w-3*tau*1)=T-n*tau implies T-lambda^Tw=tau*(n-3*sum(lambda))=tau*sum(d), because each triple has three players. For any core y, expand the left-hand side of (1); terms E^T lambda cancel and sum(y)=T. All terms on that left side are nonnegative. Dropping all except d_i*y_i proves (2). QED.

Every primal optimum of (R) corresponds exactly to a point of the max-min face F={p in P:p>=tau*1}. Complementary slackness therefore gives two useful support statements: lambda can be positive only on triples tight throughout F, and a positive deficit d_i implies p_i=tau throughout F. Conversely, if p_i=tau throughout F, standard strict complementarity for finite linear programs supplies an optimal dual lambda with d_i>0. The converse is a support-existence fact; it provides no bound on the deficit ratio.

For tau>0, a certificate with sum(d)/d_i<=C would establish H_i<=C*tau for that first-stage fixed player. Finding such certificates can be structurally informative. It is only a sufficient route to a proposed uniform constant, and it must not require a separate ideal-payoff LP certificate to be tight at the leximin point.

In the cycle4 counterexample, one explicit optimal lambda has total deficit 3 and target deficit 1/3, giving ratio 9. The target ideal payoff 9 at tau=1 proves that every optimal certificate with positive target deficit has ratio at least 9. Thus a claimed six-deficit certificate for every first-stage player would be incorrect.

At tau=0, formula (2) implies H_i=0 for every coordinate fixed to zero throughout the first max-min face. This covers only such first-stage fixed-zero coordinates. A later positive leximin stage with previously fixed coordinates requires an extended residual formulation; no extension is asserted here.
