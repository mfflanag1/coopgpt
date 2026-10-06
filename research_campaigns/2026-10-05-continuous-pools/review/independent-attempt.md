I found an exact obstruction to a natural arbitrary-real extension, not an impossibility result for the target problem.

Define, for any altered pool \(j\) with total \(C_j=\sum_{i\in N_j}c_i\),
\[
z_j=C_j/r,
\]
and the generalized one-pool vector
\[
R_i^j=
\begin{cases}
(1-z_j)c_i,&i\in N_j,\\[2mm]
z_j/(k-1),&i\notin N_j.
\end{cases}
\]
Consider the candidate that uses the existing all-unit boundary, \(R^j\) when only \(j\) is altered, and \((R^j+R^\ell)/2\) when exactly two pools \(j,\ell\) are altered.

Each \(R^j\) does cover the actual game. For a coalition \(S\), put
\[
s=\sum_{i\in S\cap N_j}c_i,\qquad
n=\min_{\ell\ne j}|S\cap N_\ell|.
\]
Its payment under \(R^j\) is at least
\[
(1-z_j)s+z_j n\ge \min(s,n).
\]
Replacing outside capacities by \(1\) can only increase coalition values, so \(R^j(S)\ge v(S)\). Hence the two-pool average also covers. Moreover,
\[
R^j(N)=(1-C_j/r)C_j+C_j=C_j(2-C_j/r)\le2C_j.
\]

However, own-report monotonicity fails at an exact rational interior edge. Take \(k=r=2\), with
\[
N_1:(1,3/4),\qquad N_2:(1,1/2).
\]
Increase the second owner in \(N_1\) from \(3/4\) to \(7/8\); both endpoint profiles retain exactly two altered pools.

Before the increase, \(C_1=7/4\), \(z_1=7/8\), and that owner receives
\[
\frac12(1-z_1)\frac34+\frac12\frac{z_2}{k-1}
 =\frac12\frac{3}{32}+\frac12\frac34
 =\frac{27}{64}
 =\frac{108}{256}.
\]
Afterward, \(C_1=15/8\), \(z_1=15/16\), and the payment is
\[
\frac12(1-z_1)\frac78+\frac12\frac34
 =\frac12\frac7{128}+\frac38
 =\frac{103}{256}.
\]
Thus the changing owner’s payment strictly falls by \(5/256\).

The obstruction is structural:
\[
c_i(1-C_j/r)
\]
need not be nondecreasing in \(c_i\), because both factors change. With the other reports fixed and sum \(A\), its derivative is
\[
1-\frac{A+2c_i}{r},
\]
which becomes negative near the upper boundary.

The load-bearing binary restriction occurs at [TWO_POOL_THEOREM.txt:67](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261005-205404-21720f37/workspace/research_campaigns/2026-10-05-two-altered-pools/TWO_POOL_THEOREM.txt:67): every permitted increase jumps a report directly from \(1/r\) to \(1\), allowing the discrete ratio identity used at lines 71–91. Intermediate increases have no corresponding ratio argument. The “real \(x\)” interpolation at line 55 concerns only the aggregate cost formula, not arbitrary real owner reports. A suitable verification is to symbolically differentiate every proposed within-pool payment while holding the other reports fixed, then separately check transitions to the one-altered boundary.

This counterexample rules out only the stated generalized-\(R\), equal-mixture candidate. It does not rule out capacity-dependent mixing, different within-pool allocations, revised boundary payments, or a uniform-constant construction. The arbitrary-real target remains unresolved.