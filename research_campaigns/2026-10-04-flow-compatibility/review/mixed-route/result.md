## Report: mixed bimatroid inequality and its obstruction

Let \(I\) be row players and \(J\) column players, with capacities \(r_i,c_j\ge 0\) and public pair capacities \(p_{ij}\ge 0\). For \(Q\subseteq I\), \(R\subseteq J\), define

\[
w(Q,R)=\max\left\{\sum_{ij}f_{ij}:
\sum_jf_{ij}\le r_i\ (i\in Q),\
\sum_if_{ij}\le c_j\ (j\in R),\
0\le f_{ij}\le p_{ij}\right\}.
\]

Absent pairs may be represented by \(p_{ij}=0\). This is the unweighted capacitated transportation game arising from the prerequisite transfer. It is not an arbitrary weighted assignment game.

### Lemma: mixed source/sink uncrossing

For all \(Q,Q'\subseteq I\) and \(R,R'\subseteq J\),

\[
\boxed{
w(Q,R)+w(Q',R')
\ge
w(Q\cap Q',\,R\cup R')
+
w(Q\cup Q',\,R\cap R').
}
\tag{M}
\]

Thus \(w\) is submodular on the product lattice in which the column coordinate is ordered oppositely. This is genuinely mixed: it is stronger than merely asserting submodularity separately on rows and columns.

#### Proof

The max-flow/min-cut formula is

\[
w(Q,R)=
\min_{\substack{X\subseteq Q\\Y\subseteq R}}
\left[
r(Q\setminus X)+p(X,R\setminus Y)+c(Y)
\right],
\tag{1}
\]

where \(r(U)=\sum_{i\in U}r_i\), \(c(V)=\sum_{j\in V}c_j\), and
\(p(U,V)=\sum_{i\in U,j\in V}p_{ij}\).

Choose minimizing cuts \((X,Y)\) for \((Q,R)\) and \((X',Y')\) for \((Q',R')\). For the two crossed coalitions use the feasible cuts

\[
(X\cap X',\,Y\cup Y')
\quad\text{and}\quad
(X\cup X',\,Y\cap Y').
\]

The row-cut terms satisfy the exact coordinatewise identity

\[
r(Q\setminus X)+r(Q'\setminus X')
=
r((Q\cap Q')\setminus(X\cap X'))
+r((Q\cup Q')\setminus(X\cup X')).
\tag{2}
\]

Likewise,

\[
c(Y)+c(Y')=c(Y\cup Y')+c(Y\cap Y').
\tag{3}
\]

For every pair \((i,j)\), direct inspection of its four membership indicators gives

\[
\begin{aligned}
&1_{i\in X}1_{j\in R\setminus Y}
+1_{i\in X'}1_{j\in R'\setminus Y'}\\
&\quad\ge
1_{i\in X\cap X'}1_{j\in (R\cup R')\setminus(Y\cup Y')}
+
1_{i\in X\cup X'}1_{j\in (R\cap R')\setminus(Y\cap Y')}.
\end{aligned}
\]

Multiplication by \(p_{ij}\ge0\) and summation yield the corresponding inequality for the middle-cut terms. Combining this with (2)–(3), the sum of the two original minimum-cut values is at least the sum of the two displayed crossed-cut values. Each crossed-cut value is at least the relevant minimum in (1), proving (M). ∎

The proof allows arbitrary rational row, column, and public pair capacities. It also works over the nonnegative reals.

### Exact obstruction to the intended tight-set mechanism

Although (M) is the natural bimatroid inequality, its direction is unsuitable for the usual core tight-set uncrossing.

For a core payoff \((x,y)\), modularity gives

\[
[x(Q)+y(R)]+[x(Q')+y(R')]
=
[x(Q\cap Q')+y(R\cup R')]
+[x(Q\cup Q')+y(R\cap R')].
\tag{4}
\]

If the two left coalitions are tight, (M) says only that their total worth is **at least** the total crossed worth. Consequently (4) permits positive slack in the crossed constraints. It does not imply that crossed coalitions are tight, so it supplies neither the usual lattice of tight constraints nor an exchange step producing a common upper source payoff.

This failure is strict in the smallest conventional transportation example. Take one row \(i\) of capacity \(1\), two columns \(j_1,j_2\), each of capacity \(1\), and pair capacities \(p_{ij_1}=p_{ij_2}=1\). Then

\[
w(\{i\},\{j_1\})+w(\{i\},\{j_2\})=2,
\]

whereas

\[
w(\{i\},\{j_1,j_2\})+w(\{i\},\varnothing)=1.
\]

The core point \(x_i=1,\ y_{j_1}=y_{j_2}=0\) makes both singleton-pair coalitions tight. After mixed uncrossing, the union coalition remains tight but the row-only coalition has payoff \(1\) and worth \(0\). Thus one full unit of slack appears.

The reverse inequality that tight-set uncrossing would need,

\[
w(Q,R)+w(Q',R')
\le
w(Q\cap Q',R\cup R')+
w(Q\cup Q',R\cap R'),
\]

is therefore false even for a one-row, two-column unweighted transportation game.

### Consequence and unresolved point

The prerequisite transfer legitimately exposes a bimatroid-style mixed rank structure, namely (M). However, that structure alone does not furnish the missing source-projection directedness argument: its strict-slack behavior blocks the standard “uncross tight constraints, then exchange coordinates” route. The supplied coordinatewise-maximum obstruction is consistent with this diagnosis; additional source coordinates may have to increase, while (M) provides no rule selecting or financing those increases.

I found no error in the supplied transfer or embedding arguments relevant to this lemma. A useful verification target for any continuation is an additional inequality controlling the **slack**

\[
\Delta =
w(Q,R)+w(Q',R')
-w(Q\cap Q',R\cup R')
-w(Q\cup Q',R\cap R'),
\]

by the endpoint payoff adjustment needed to dominate two source projections. Inequality (M) controls only \(\Delta\ge0\), which the example shows is insufficient for tight-set closure.

**Status:** UNKNOWN for universal endpoint directedness. The proved contribution is the exact mixed transportation-rank inequality (M), together with a conventional analytic obstruction showing why its ordinary uncrossing consequence is insufficient. No claim of novelty or universal compatibility is made.