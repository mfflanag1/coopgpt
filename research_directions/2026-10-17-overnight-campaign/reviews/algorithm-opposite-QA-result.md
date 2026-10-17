Verdict: **revise**

The central algorithmic claim is credible and, with several repairs, yields an exact polynomial-bit-complexity algorithm. The submission should not be accepted as written because its prior-art identification contains a false inference, its strongest algorithmic citation was not actually verified from the primary source, and several bit-complexity details are misstated or omitted.

## Major findings

### 1. The parametric-cut derivation is essentially correct

For positive rational capacities, define

\[
f_\theta(X)=c(N(X))-\theta c(X).
\]

The network with arcs

\[
s\to v_L:\theta c_v,\qquad
u_L\to v_R:M\quad(uv\in E,\text{ both orientations}),\qquad
v_R\to t:c_v
\]

has, for a closure-respecting source side determined by \(X\subseteq V\), cut value

\[
\theta c(V\setminus X)+c(N(X))
=\theta c(V)+f_\theta(X).
\]

Thus minimizing \(f_\theta\) is one minimum-cut computation. The submitted peeling proof supports the following precise proposition:

> Let \(c_v>0\), and let \(p^*\) be the unique Huber optimizer. For \(0\leq\theta<1\), the unique inclusion-maximal minimizer of \(f_\theta\) is
> \[
> L_\theta=\{v:\min(2p_v^*,1)\leq\theta\}.
> \]
> Consequently, the breakpoints \(\theta_j<1\) and their maximal source sets recover all coordinates:
> \[
> p_v^*=\theta_j/2\quad(v\in X_j),\qquad
> p_v^*=1-\theta_j/2\quad(v\in N(X_j)),
> \]
> with all remaining nonisolated vertices priced \(1/2\), and isolated positive vertices priced \(0\).

The proof needs to state explicitly that every critical set with \(\theta<1\) consists of vertices priced below \(1/2\), hence is independent. This justifies treating \(X_j\) and \(N(X_j)\) as disjoint during peeling.

Zeros and odd cycles do not obstruct the construction: zero-capacity vertices are deleted according to the rule, while the double cover is only a closure representation and does not assert bipartiteness of the original graph.

### 2. Exact polynomial bit complexity follows, but the presentation needs repairs

After multiplying all capacities by a common denominator, let the resulting positive capacities be integers and \(C=c(V)\). Then each breakpoint is

\[
\theta_j=\frac{c(Y_j)}{c(X_j)}
\]

and hence has reduced denominator at most \(C\). Each price therefore has denominator at most \(2C\).

A valid weakly polynomial exact algorithm is:

1. Delete zero-capacity vertices and record isolated positive vertices at price zero.
2. Locate the next ratio by binary search on \([0,1]\), testing whether the minimum cut has value below the empty-set value \(\theta C\).
3. Once the interval width is below \(1/(2C^2)\), recover the unique rational with denominator at most \(C\) by rational reconstruction.
4. At that exact parameter, compute the **inclusion-maximal** minimum-cut source set.
5. Peel it together with its neighborhood and repeat.

There are at most \(n\) stages and \(O(nL)\) exact rational max-flow calls, where \(L\) is the input bit length after scaling. That establishes polynomial bit complexity without needing a strongly polynomial claim.

Necessary corrections:

- Replace “infinite” closure capacities by an explicit rational number, for example \(M=C+1\) for \(0\leq\theta\leq1\). Since a cut of capacity at most \(C\) is always available, no minimum cut crosses an \(M\)-arc.
- An arbitrary returned minimum cut need not be the maximal source-side minimum cut. State how it is obtained from the residual graph, or use an algorithm with an explicit maximal-cut tie convention.
- “All payments have denominator at most \(2C\)” is true only in the integer-scaled units. If the original reports have common denominator \(D\), converting the payments back may introduce the additional factor \(D\).
- State complexity in terms of total rational input length, not merely `log(n·c_max·D)` unless those symbols are formally defined and their encoding lengths bounded.

### 3. GGT can support a one-run parametric decomposition, but the candidate did not satisfy the primary-source requirement

The freely available primary source is the authors’ Princeton technical report: [Gallo–Grigoriadis–Tarjan, *A Fast Parametric Maximum Flow Algorithm and Applications*](https://www.cs.princeton.edu/techreports/1987/105.pdf).

The relevant hypotheses are:

- only arcs leaving \(s\) and entering \(t\) depend on the parameter;
- all other capacities are constant;
- source-adjacent capacities are monotone in one direction and sink-adjacent capacities in the opposite direction, with the reverse-parameter variants explained in §2.5;
- the applicable complexity bound is Theorem 2.7;
- the all-breakpoint procedure and fractional/maximum-ratio closure application are in §3, particularly the breakpoint and fractional-programming portions.

Here \(s\to v_L\) has linear nondecreasing capacity \(\theta c_v\), \(v_R\to t\) is constant, and all closure arcs are constant, so the instance satisfies the monotonicity assumptions.

This supports computing all nested cuts in the operation bound of a parametric max-flow computation. For a complete Turing-model claim, the paper’s operation bound should be supplemented by the elementary observation that all breakpoints and intermediate capacities have polynomial encoding length. The current candidate’s admission that it relied only on secondary quotations does not meet the task’s demand to read the primary algorithmic theorem.

Hochbaum–Queyranne is also a primary source, but it does not by itself prove exact continuous output here. Its CCC formulation is initially integer-valued, while §8 gives grid-accurate continuous computation. See the problem definition at pp. 192–193, the parametric algorithm in §6, quadratic specialization in §7.1, and continuous treatment in §8 of their [freely available paper](https://hochbaum.ieor.berkeley.edu/html/pub/CCC-SIAM-2003.pdf). Exactness in this problem comes from the proved ratio structure, not from their continuous approximation result.

### 4. The claimed transversal-polymatroid identification is not valid as stated

The assertion that the matching degree vector “should be the weighted lex-optimal base” of the coverage polymatroid

\[
\rho(X)=c(N(X))
\]

is false in general. That polymatroid describes possible **left-degree vectors in the bipartite double cover**. It does not impose the symmetry equating the left and right copies of each original vertex that is inherent in an undirected fractional matching degree vector.

A concrete counterexample is the triangle with capacities \((1,1,10)\):

- the Huber/KKT fractional-matching degree vector is \((1,1,2)\), of total \(4\);
- a base of the coverage polymatroid has total
  \(\rho(V)=c(V)=12\).

Therefore the Huber degree vector cannot be a base of that polymatroid. The coincidence of the low-side parametric set family below \(\theta=1\) does not identify the full degree vector with Fujishige’s lexicographically optimal base.

Fujishige’s results themselves are accurately described in the author’s later primary survey: Theorems 18–19 identify the weighted lexicographically optimal base with the minimizer of \(\sum_e x_e^2/w_e\), and discuss principal partitions and algorithms ([Fujishige, *Theory of Principal Partitions Revisited*, pp. 14–16](https://www.kurims.kyoto-u.ac.jp/~fujishig/Preprint010208.pdf)). But an additional symmetric-flow or polymatroid-intersection formulation would be required before applying that theory to this undirected matching problem.

Remove the claimed identification unless such a formulation is supplied and proved.

### 5. The defensible closest prior-art relation is the balanced fractional-matching dual

The Fenchel dual calculation is sound when stated carefully:

\[
\max_{\lambda\ge0,\;\lambda(v)\le c_v}
\left\{
\sum_e\lambda_e-\frac14
\sum_v\frac{\lambda(v)^2}{c_v}
\right\}.
\]

The theorem’s complementary-slackness argument additionally proves that an optimal multiplier is a maximum-value fractional matching. Hence its degree vector is the unique minimizer of

\[
\sum_v\frac{d_v^2}{c_v}
\]

among maximum fractional-matching degree vectors, and

\[
p_v^*=\frac{d_v}{2c_v}
\]

at unsaturated vertices. This is legitimately a least-squares-balanced maximum fractional matching construction.

That is the closest established mathematical construction identified by the submission. It should be presented as a structural equivalence, while historical priority for this exact undirected weighted formulation remains unresolved. The approximate-core matching mechanisms are more distant: they concern integral matching and odd-cycle integrality gaps, rather than this exact fractional minimum-norm degree selection.

### 6. The rational QP observation is useful but presently unsupported

The identity

\[
h(p)=\min_{\substack{a+d=p\\0\le a,d\le1/2}}(a^2+d)
\]

is correct and gives a rational convex quadratic program. But the candidate did not verify the Kozlov–Tarasov–Khachiyan source and should not invoke it as satisfying the requested primary-source standard.

This does not damage the main result because the combinatorial parametric-cut proof already supplies exact polynomial bit complexity. Either verify a freely available primary exact-QP theorem with its input and output model, or omit this citation.

## Required revision

Acceptable revision would:

- retain and tighten Lemmas A–D and the exact parametric-cut proposition;
- explicitly handle maximal minimum cuts and finite closure capacities;
- give bit bounds in the original rational input model;
- cite and state the GGT primary hypotheses and theorem locations;
- remove the false transversal-polymatroid-base identification;
- describe the balanced fractional-matching dual as proved structure, not automatically as historically novel;
- separate the exact algorithm from optional, presently unverified generic-QP claims.

The exact-computation result itself appears provable. The submission needs revision rather than rejection because the principal construction survives, but its current prior-art and sourcing sections are not reliable enough for acceptance.