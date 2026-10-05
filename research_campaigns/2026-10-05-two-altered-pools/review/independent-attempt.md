A natural boundary-preserving extension works for coverage and budget, but fails retained-edge monotonicity exactly when the identity of the minimum pool changes.

Let \(T_j=h_j+(r-h_j)/r\) for each altered pool \(j\). Choose an altered pool \(p\) having minimum \(T_j\), breaking ties deterministically. Apply the original one-altered formula with \(p\) special:

\[
z_p=T_p/r,\qquad
a_p=\frac{((r-h_p)/r-z_p)_+}{r-h_p},\qquad
b_p=1-z_p,\qquad
c_p=\frac{z_p}{k-1}.
\]

Pay \(a_p\) or \(b_p\) to low or high owners in \(p\), respectively, and \(c_p\) to every owner outside \(p\). At \(H\), retain \(1/k\) per owner.

This exactly preserves all zero/one-altered payments.

Coverage still holds even when the second altered pool contains low owners. For any coalition, let \(b+s\) be its capacity in \(p\), and let \(n\) be the minimum selected-owner count outside \(p\). Its value is at most \(\min(b+s,n)\), since every outside capacity is at most one. Its payment is at least

\[
b(1-z_p)+s(1-z_p/\delta_p)_+ + nz_p,
\]

so the original proof applies unchanged.

The budget is also unchanged by the second pool’s reports:

\[
B=h_p(1-z_p)+(\delta_p-z_p)_+ +rz_p\le 2T_p.
\]

Because \(p\) is minimum-total, \(T_p=T\), hence \(B\le2T\).

However, the formula is not monotone for all retained edges. Take \(r=2\), \(k\ge4\), and two fully low pools \(A,B\). Both have \(T_A=T_B=1\), \(z=1/2\), and the selected special pool’s low owners receive

\[
a_0=\frac14.
\]

Whichever pool the tie rule selects, raise one of its owners from \(1/2\) to \(1\). The other fully low pool becomes the unique minimum and hence special. The raised owner is now outside the special pool and receives

\[
c_0=\frac{1}{2(k-1)}<\frac14 \qquad(k\ge4).
\]

Thus its own-report increase strictly decreases its payment. This counterexample applies to every deterministic tie-breaking rule.

Consequently, minimum-pool selection gives a boundary-preserving \(2T\) cover but not the requested finite-family mechanism. It does not establish an impossibility for other two-pool formulas, nor any mechanism or obstruction on all real reports.

Review note: the supplied one-pool proof itself remains valid. Its explicit limitation at [FINITE_FAMILY_ESCAPE.txt:47](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261005-183312-86463ec3/workspace/research_campaigns/2026-10-05-beyond-thresholds/FINITE_FAMILY_ESCAPE.txt:47) is exactly where this new switching edge enters. Any proposed extension should be checked first against the \(r=2,\ k=4\), two-fully-low tie profile above. No external sources were used; this is an original finite-family derivation.