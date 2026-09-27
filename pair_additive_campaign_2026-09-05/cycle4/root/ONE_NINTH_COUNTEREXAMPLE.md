# A 21-player counterexample to one-sixth protection

**Theorem.** There is a complete strict three-sector assignment market with seven players per sector, nonnegative integer pair matrices with entries at most 3, total worth 15, and nonempty core, for which a player receives one ninth of its maximum core payoff under full ascending leximin. The player is already fixed at the positive first max-min level. Thus a universal one-sixth guarantee is false, even with a positive global floor.

This is a finite upper-bound witness. It establishes neither a sharp universal constant nor a family with ratios tending to zero. Priority over the literature is unconfirmed.

## Model and explicit construction

Name the sectors \(a_0,\ldots,a_6\), \(b_0,\ldots,b_6\), and \(c_0,\ldots,c_6\). Every full triple has value

\[
w_{ijk}=A_{ij}+B_{ik}+C_{jk}.
\]

Singletons and pairs produce zero. A coalition's worth is the maximum total weight of its disjoint full triples. The following are all 16 nonzero pair entries:

| Matrix | Nonzero entries |
|---|---|
| \(A\) | \(A_{01}=2,\ A_{21}=2,\ A_{55}=1,\ A_{56}=1\) |
| \(B\) | \(B_{00}=2,\ B_{03}=2,\ B_{12}=1,\ B_{25}=2,\ B_{33}=3,\ B_{54}=1,\ B_{55}=2\) |
| \(C\) | \(C_{11}=2,\ C_{13}=2,\ C_{44}=1,\ C_{64}=1,\ C_{66}=1\) |

All unspecified entries are zero. Take the perfect matching

\[
M=((0,0,0),(1,2,2),(2,1,1),(3,3,3),(4,4,4),(5,5,5),(6,6,6)).
\]

Its team weights are \((2,1,4,3,1,3,1)\), totaling 15. Two nonnegative covers of all 343 triples are

\[
\begin{array}{c|ccc}
 &a&b&c\\\hline
u& (4,1,4,1,1,7,1)/3 &(1,7,1,1,1,1,1)/3 &(1,1,1,7,1,1,1)/3\\
y& (2,0,0,3,0,1,0)&(0,4,0,0,0,0,1)&(0,0,1,0,1,2,0).
\end{array}
\]

Both have total 15. Their covers can be checked directly against the sparse matrices; [the standalone rational verifier](verify_compact_proof.py) independently reconstructs the construction and performs all 686 checks. The matching is a lower bound on the integral worth, and either cover gives an upper bound of 15. Thus the true worth is 15. Triple covers imply all coalition inequalities by summing over any coalition matching and using nonnegativity on unmatched players. In particular, both points belong to the full core

\[
P=\{p\ge0:\mathbf1^Tp=15,\quad a_i+b_j+c_k\ge w_{ijk}\ \text{for all }i,j,k\}.
\]

The vector \(u\) is used only as a floor witness. We do not assert that it is the full leximin allocation.

## A short whole-core inequality

Every triple in \(M\) is tight at every core point: the seven covers sum to the efficiency equality. Add three copies of the first matching equality and one copy of each of the other six. The right side is 19. Subtract these valid inequalities:

\[
\begin{aligned}
a_0+b_1+c_3&\ge6,& a_0+b_4+c_0&\ge2,\\
a_0+b_5+c_0&\ge2,& a_1+b_3+c_2&\ge1,\\
a_2+b_2+c_5&\ge2,& a_5+b_6+c_4&\ge3.
\end{aligned}
\]

The subtracted right sides total 16. Canceling coordinates gives, for **every** core point,

\[
a_3+a_4+a_6+3b_0+c_0+c_1+c_6\le3.\tag{1}
\]

The coefficients are nonnegative and sum to 9. Hence a common coordinate floor \(t\) satisfies \(9t\le3\). The point \(u\) attains floor \(1/3\), so the first leximin level is exactly \(\tau=1/3>0\).

On the entire first optimal face \(F=\{p\in P:p_i\ge1/3\ \forall i\}\), equality holds in (1), and every coordinate with a positive coefficient in (1) equals \(1/3\). In particular \(a_3=1/3\) throughout \(F\). Every later stage of full ascending leximin stays within \(F\), so its final target payoff is \(x_{a_3}=1/3\).

Finally, the matching equality \(a_3+b_3+c_3=3\) and nonnegativity imply \(H_{a_3}\le3\), where \(H_{a_3}=\max_{p\in P}p_{a_3}\). The point \(y\) attains 3. Therefore

\[
H_{a_3}=3,\qquad \frac{x_{a_3}}{H_{a_3}}=\frac19<\frac16.
\]

This proves the theorem without computing later selector stages.

## Audit and provenance

The original inverse LP returned a 63-player instance on the old composition's support with new weights. Restricting its two covers to the seven matching teams involved in its proof and scaling by one third gives this construction. The argument above establishes the compact market directly; it does not assume that deletion preserves the original entire core or every selector coordinate.

There are three distinct audit routes: the experiment's exact certificate checker, the root's explicit reconstruction above, and [an independent raw-core audit](../zero_face/COMPACT_AUDIT.md). The last ignores the generated budget and excludes a higher floor, a higher target on the whole first face, and a higher ideal using three exact UNSAT checks. These internal audits are not external specialist review.
