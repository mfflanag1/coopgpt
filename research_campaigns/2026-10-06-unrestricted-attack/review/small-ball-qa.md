## Verdict: revise

The central result survives audit: the exact pairwise inequality is valid for all \(\rho\ge2\), including \(\rho=2\), unequal owner counts, and zero coefficients. It yields the all-profile budget
\[
Q(k)=2+\int_2^\infty \min\{1,(k-1)q(s)\}\,ds,
\]
and the analytic comparison \(Q(k)<U(k)\) is correct for every \(k\ge2\).

However, the candidate should be revised because its claimed heuristic
\[
U(k)-Q(k)=1.5+o(1)
\]
is unsupported and likely false without accounting for floor/fractional-part effects.

### Checked core argument

Let
\[
X_j=\sum_i a_iU_i,\qquad 0\le a_i\le1,\qquad \sum_i a_i=\rho\ge2.
\]

1. **Convexity of \(F_j\) on \([0,1]\).**  
   This is correct. A sum of independent uniform variables has a symmetric unimodal density about \(\rho/2\); hence its density is nondecreasing to the left of \(\rho/2\), so its CDF is convex there. Since \([0,1]\subseteq(-\infty,\rho/2]\), \(F_j\) is convex on the needed interval.

   The candidate’s elementary convolution proof can be simplified. If \(Z\) has symmetric unimodal density \(f\) about \(c\) and \(W\sim\mathrm{Unif}[0,a]\), then
   \[
   F_{Z+W}'(x)=\frac{F_Z(x)-F_Z(x-a)}a,
   \quad
   F_{Z+W}''(x)=\frac{f(x)-f(x-a)}a
   \]
   almost everywhere. For \(x\le c+a/2\), symmetry and monotonicity imply \(f(x)\ge f(x-a)\). This proves convexity directly and also handles the endpoint \(\rho=2\).

2. **Jensen step.**  
   For a shortest pool,
   \[
   X_s=\sum_i b_iU_i,\qquad b_i\ge0,\qquad\sum_i b_i=1.
   \]
   Thus
   \[
   F_j(X_s)\le\sum_i b_iF_j(U_i).
   \]
   Independence and continuity give
   \[
   \Pr(X_j<X_s)
   =\mathbb E F_j(X_s)
   \le\int_0^1F_j(u)\,du
   =\mathbb E(1-X_j)_+.
   \]
   This uses no equality of owner counts.

3. **Coefficient maximization.**  
   The map
   \[
   a\longmapsto\mathbb E\Bigl(1-\sum_i a_iU_i\Bigr)_+
   \]
   is convex. Therefore its maximum over
   \[
   \{a\in[0,1]^m:\ \sum_i a_i=\rho\}
   \]
   occurs at a vertex. Such vertices have \(n=\lfloor\rho\rfloor\) unit coordinates, one coordinate \(\theta=\rho-n\) when \(\theta>0\), and all remaining coordinates zero. This correctly covers arbitrary owner counts and zero capacities.

4. **Exact sharp formula.**  
   At that vertex,
   \[
   q(n)=\frac1{(n+1)!},
   \]
   and, for \(0<\theta<1\),
   \[
   q(n+\theta)
   =\frac{1-(1-\theta)^{n+2}}{\theta(n+2)!}.
   \]
   The limits at \(\theta=0,1\) agree with the adjacent integer formulas. Coupling shows that \(q\) is strictly decreasing. Equality is attained by a singleton shortest pool and the extremal coefficient vector, so the pairwise inequality is sharp.

### Budget comparison

For \(s\ge2\),
\[
\Pr(\rho_W>s)\le \min\{1,(k-1)q(s)\},
\]
because a shortest pool has normalized total \(1\) and therefore cannot be counted when \(s\ge2\). Hence
\[
\mathbb E\rho_W\le Q(k).
\]

Writing \(n=\lfloor s\rfloor\),
\[
q(s)\le q(n)=\frac1{(n+1)!}
<\left(\frac e{n+1}\right)^{n+1}
\le\left(\frac es\right)^s.
\]
The last inequality follows because \(x\mapsto(e/x)^x\) is decreasing for \(x>1\).

Therefore,
\[
\begin{aligned}
Q(k)
&\le e+\int_e^\infty\min\{1,k(e/s)^s\}\,ds\\
&=R_k+\int_{R_k}^\infty k(e/s)^s\,ds\\
&\le R_k+\frac1{\log R_k}=U(k).
\end{aligned}
\]
The inequality is strict because \(q(s)<(e/s)^s\) throughout the nonempty tail \((R_k,\infty)\). Thus
\[
\boxed{Q(k)<U(k)\quad\text{for every }k\ge2.}
\]

### Required correction

The assertion
\[
U(k)-Q(k)\approx1.5+o(1)
\]
should be deleted or substantially qualified. For fixed \(0<\theta<1\),
\[
q(n+\theta)\sim\frac1{\theta(n+2)!},
\]
whereas at the integer endpoint \(q(n)=1/(n+1)!\). Consequently, the crossing of \((k-1)q(s)=1\) can retain an \(O(1)\) dependence on its position inside \([n,n+1]\). The proposed \(1.5+o(1)\) estimate ignores this lattice/fractional-position effect. No calculation in the candidate proves that these oscillations vanish.

The hand-computed numerical values were not independently reproduced here. They are illustrations only and are unnecessary for the theorem.

Established probability ingredients are convolution closure of symmetric unimodality, Jensen’s inequality, convex maximization on a polytope, and the uniform-sum simplex formula. The application of these ingredients to obtain the sharp \(q(\rho)\), \(Q(k)\), and \(Q(k)<U(k)\) is the proposed contribution. This audit makes no novelty or field-level breakthrough claim.