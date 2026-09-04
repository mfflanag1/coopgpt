# Coalition closure of the abstract near-extremizer

This note records a negative control for the research campaign. It makes no
novelty claim. All statements below follow directly from coalition inequalities;
the argument does not depend on numerical reconstruction.

Let \(n\ge4\), \(q=1/(n-1)\), \(0\le a\le q/2\), and

\[
x=(1-(n-1)a,a,\ldots,a),\qquad
z=(q,0,q,\ldots,q),\qquad
K=\operatorname{conv}\{x,z,e_1,e_3\}.
\]

Define \(v(S)=\min_{w\in K}w(S)\). This lower-envelope game is exact and
singleton-normalized: every generating point lies in its core, every coalition
minimum is attained at a generator, and the two unit vectors supply a zero
coordinate witness for every player. Write \(B=\{4,\ldots,n\}\) and \(k=n-3\).

## Exact core description

The coalition-defined core is

\[
C=\left\{y\ge0:\ \sum_i y_i=1,\quad y_2\le a,\quad
y_2+y_j\le q\quad(j\in B)\right\}.                 \tag{1}
\]

If a coalition omits either player 1 or player 3, its worth is zero, so its
inequality follows from nonnegativity. Otherwise its complement is a subset

\[
Q\subseteq\{2\}\cup B.
\]

Efficiency converts its coalition inequality into

\[
y(Q)\le\max\{a|Q|,\ q|Q\cap B|\}.                \tag{2}
\]

For \(Q=\{2\}\), this gives \(y_2\le a\). For

\[
Q=\{2\}\cup J,\qquad \varnothing\ne J\subseteq B,
\]

the assumption \(a\le q/2\) implies \(a(|J|+1)\le q|J|\), so (2) becomes

\[
y_2+y(J)\le q|J|.
\]

Its singleton instances are precisely \(y_2+y_j\le q\). Conversely, summing
these singleton instances gives

\[
|J|y_2+y(J)\le q|J|,
\]

which implies the required inequality because \(y_2\ge0\). If \(Q\subseteq B\),
(2) is \(y(Q)\le q|Q|\), also implied by (1). This proves (1) in both directions.

## Complete selectors

Here Lmin maximizes the increasingly sorted payment vector lexicographically;
Lmax minimizes the decreasingly sorted payment vector lexicographically.

Put

\[
b=q+\frac{n-4}{2}a.
\]

Then

\[
\mathrm{Lmin}(v)=(b,a,b,(q-a)^{n-3}).              \tag{3}
\]

Indeed \(y_2\le a\) bounds the common floor by \(a\). The displayed allocation
is feasible, and its other coordinates are at least \(a\), because

\[
q-a\ge a,\qquad b\ge q.
\]

Thus a lexicographic optimum has \(y_2=a\). On this face every coordinate in \(B\) is bounded above by \(q-a\). The displayed allocation attains all these upper
bounds while leaving both remaining coordinates at least \(q-a\). Consequently
lexicographic maximization fixes every coordinate in \(B\) at \(q-a\). The last
two coordinates have a fixed sum and are therefore equalized at \(b\). The
same argument includes \(a=0\) and \(a=q/2\), with coincident stages allowed.

For \(n\ge5\),

\[
\mathrm{Lmax}(v)=z.                                \tag{4}
\]

To see this, (1) gives

\[
y_2+\sum_{j\in B}y_j\le kq-(k-1)y_2\le kq.
\]

If all coordinates are at most \(M\), efficiency therefore implies

\[
1\le2M+kq,
\]

so \(M\ge q\). The point \(z\) attains this ceiling. At equality \(M=q\), and
with \(k\ge2\), the preceding inequalities force \(y_2=0\). Efficiency then
forces every other coordinate to equal \(q\). Thus the first minimax optimum
is unique, proving the complete selector claim.

For \(n=4\), the complete selectors instead coincide:

\[
\mathrm{Lmax}(v)=\mathrm{Lmin}(v)=(q,a,q,q-a).       \tag{5}
\]

The minimum ceiling remains \(q\), but its face is

\[
y_1=y_3=q,\qquad y_2+y_4=q,\qquad0\le y_2\le a.
\]

Since \(a\le q/2\), the next descending lexicographic stage minimizes

\[
\max\{y_2,y_4\}=q-y_2
\]

by choosing \(y_2=a\), proving (5).

## Effect on the original near-disjoint pair

For \(a=n^{-3}\), the original set \(K\) has unique maximin point \(x\): its
second coordinate reaches \(a\) only at \(x\). It also has unique minimax
point \(z\): every other displayed vertex has coordinate sum on \(\{1,3\}\) strictly greater than \(2q\). Thus every non-\(z\) convex combination has a
coordinate greater than \(q\). These unique first-stage optima certify the
full lexicographic selectors on \(K\).

Their overlap on \(K\) is \(q+(n-2)a\), so their normalized divergence

\[
\rho_K=\|x-z\|_1=2-2\{q+(n-2)a\}
\]

approaches two. Coalition closure changes the leximin allocation to (3).
For \(n\ge5\), direct coordinate subtraction from (4) gives

\[
\boxed{\rho(v)=2(n-3)a.}                           \tag{6}
\]

For \(a=n^{-3}\), this is \(2(n-3)/n^3\), which tends to zero. At \(n=4\),
the divergence is exactly zero by (5); formula (6) is specifically for \(n\ge5\).

This control shows that the selected pair on a convex hull need not survive
coalition closure, even when that hull attains zero in every coordinate. It
does not obstruct other exact-game constructions attaining asymptotic
coefficient two.
