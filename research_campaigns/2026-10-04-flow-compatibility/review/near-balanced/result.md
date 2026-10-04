Result: a genuine partial structural lemma. The general least-loss question remains UNKNOWN, but it is resolved for a nonempty generic family characterized by one dominant source.

### Audit of the reduction

The derivation in [NEAR_BALANCED_ROUTE.txt](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261003-213302-dec015cf/workspace/research_campaigns/2026-10-04-flow-compatibility/NEAR_BALANCED_ROUTE.txt:7) is correct, subject to these quantifier details:

- Before mapping arbitrary original core points into \(K\), choose one global \(\epsilon\) preserving every strict comparison \(a(S)<b(R)\). Finiteness and the no-ties assumption provide it.
- Constraints with \(a(S)>b(R)\) are eventually satisfied only for each fixed finite \((z,t)\), not uniformly over \(K\). The text uses them only for finitely many minimizing witnesses, so this is sufficient.
- The claim that each minimum is attained is valid: \(K\) is a nonempty closed polyhedron, \(z_i\ge1\), and a finite linear-programming infimum over a polyhedron is attained.
- Thus lines 26–32 are valid once the two different small-\(\epsilon\) quantifiers are kept distinct.

### Dominant-source lemma

Let \(m=|I|\ge2\), \(n=|J|\ge2\), and suppose some source \(k\) satisfies
\[
A:=\sum_{i\ne k}a_i<\min_{j\in J}b_j.
\tag{D}
\]
Then \(K(a,b)\) has the componentwise least source-loss vector
\[
h_i=1\quad(i\ne k),\qquad
h_k=(n-1)(m-1)+1.
\]

Indeed, (D) completely determines the weighted subset comparisons:

- If \(S\subseteq I\setminus\{k\}\) and \(\varnothing\ne R\subsetneq J\), then
  \[
  a(S)\le A<\min_jb_j\le b(R).
  \]
- If \(k\in S\) and \(R\subsetneq J\), then
  \[
  a(S)\ge a_k=T-A>T-\min_jb_j\ge b(R).
  \]
- For \(R=J\), every proper \(S\subsetneq I\) has \(a(S)<T=b(J)\).

Put \(Z_-=\sum_{i\ne k}z_i\). The full-sink constraints, together with efficiency, are equivalent to \(z_i\ge1\) for every source. Because these make all \(z_i\) positive, the strongest constraint for each nonempty proper \(R\) is
\[
t(R)\ge Z_-.
\]
In particular, every singleton gives \(t_j\ge Z_-\). Hence
\[
z_k+Z_--1=\sum_jt_j\ge nZ_-,
\]
or
\[
z_k\ge(n-1)Z_-+1.
\tag{1}
\]

Conversely, if all \(z_i\ge1\) and (1) holds, choose \(t_j\ge Z_-\) with total \(z_k+Z_--1\). This satisfies every constraint of \(K\). Therefore the source projection is exactly
\[
z_i\ge1,\qquad z_k\ge(n-1)\sum_{i\ne k}z_i+1.
\]
Its displayed least vector follows immediately. This proof uses the capacity-induced subset order, rather than generic balancedness or a lattice assertion.

### Explicit rational flow certificate

Take
\[
a=(1,2,10),\qquad b=(4,9),\qquad \delta=(1,0,0).
\]
Here \(T_0=13\), \(A=3<4=\min b_j\), and the source subset sums
\[
1,2,3,10,11,12
\]
avoid the sink subset sums \(4,9\). Thus the hypotheses are rational, generic, and nonempty.

The lemma gives
\[
h=(1,1,3),\qquad t=(2,2).
\]
For any rational \(0<\epsilon<1/10\), form the actual two-hop network with source capacities
\[
(1+\epsilon,\,2,\,10)
\]
and sink capacities \((4,9)\). The common source-ideal core payoff furnished by the reduction is
\[
x=(1,\ 2-\epsilon,\ 10-3\epsilon),\qquad
y=(2\epsilon,\ 2\epsilon).
\]
Its total is \(13\). The minimum strict unperturbed subset gap is \(1\); the crude bound
\[
|\delta(S)-z(S)+t(R)|\le10
\]
shows that \(\epsilon<1/10\) preserves every required strict-side coalition inequality. Positivity is immediate.

Thus this is an exact analytic family where the apparently competing coordinate minima do coexist, and the weighted comparison structure forces the compensating loss onto the dominant source.

Limitation: this mechanism does not establish directedness or leastness outside condition (D), nor produce an obstruction in the remaining capacity-order regimes. The unrestricted question in line 37 therefore remains **UNKNOWN**.