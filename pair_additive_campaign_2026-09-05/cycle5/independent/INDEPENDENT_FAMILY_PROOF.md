# Independent audit of the vanishing-protection family

**Audit verdict: valid for every integer q>=1.** The family has complete strict triples, three equal sectors, nonnegative integer pair entries in {0,1,2}, a nonempty full core, and a positive first leximin floor. For its designated player, the complete ascending leximin payoff divided by the true whole-core ideal is exactly 1/[3(q+1)]. Thus no positive dimension-independent ideal-payoff protection constant exists in this class.

This is a mathematical audit of the supplied construction. No historical priority, novelty, smallest-size, distance, or complete-selector-vector claim is made.

## 1. Market, payoffs and counts

Let the team labels be L_0 and L_s,R_s,O_s for 1<=s<=q. Each sector has one player for each label, with payoffs a_t,b_t,c_t. There are m=3q+1 players per sector, hence n=9q+3 players altogether. All triples (i,j,k) are available and have worth A_ij+B_ik+C_jk. Singletons and pairs have zero worth. A coalition earns the maximum weight of its disjoint full triples.

All unspecified pair entries are zero. The positive entries are

\[
\begin{aligned}
C_{L_s,L_s}&=1 &&(0\le s\le q),\\
C_{R_s,R_s}=C_{R_s,L_s}=C_{L_{s-1},O_s}&=1 &&(1\le s\le q),\\
A_{O_s,O_s}=A_{O_s,R_s}=B_{O_s,O_s}=B_{O_s,L_s}&=2
&&(1\le s\le q).
\end{aligned}
\]

These are 8q+1 distinct positive entries. The diagonal matching has value 1 on every L_s and R_s team, and value 4 on every O_s team. Its total is 6q+1.

Put t=1/[3(q+1)]. Consider the following two vectors, with each triple displaying its (a,b,c) payoffs:

\[
\begin{array}{c|c|c}
\text{team}&u&y\\\hline
L_s&(t,\ 1-(3s+2)t,\ (3s+1)t)&(0,0,1)\\
R_s&(t,\ 1-2t,\ t)&(0,1,0)\\
O_s&(4-(3s-1)t,\ t,\ (3s-2)t)&(3,0,1).
\end{array}
\]

Here L_s includes s=0; R_s,O_s use 1<=s<=q. Every u coordinate is at least t: the smallest L-sector b payoff occurs at s=q and equals t; the smallest L-sector c payoff occurs at s=0 and equals t; the smallest O-sector c payoff occurs at s=1 and equals t. Also 0<t<=1/6, 1-2t>=t, and every O-sector a payoff is at least 3+4t. The vector y is nonnegative. Each vector makes every diagonal team tight, so both have total 6q+1.

## 2. Complete all-triple cover proof

The following split covers every possible triple, including all incidental triples.

First suppose its first-sector label is an L or R label. That player has no incident positive A or B entry, so the triple's value is the C-pair value, either zero or one. All positive C pairs are in this table:

\[
\begin{array}{c|c|c}
(j,k)&u_{b_j}+u_{c_k}&y_{b_j}+y_{c_k}\\\hline
(L_s,L_s)&1-t&1\\
(R_s,R_s)&1-t&1\\
(R_s,L_s)&1+(3s-1)t&2\\
(L_{s-1},O_s)&1-t&1.
\end{array}
\]

Adding the first-sector payoff t for u, or zero for y, covers all these one-unit values. Nonnegativity covers a zero C pair.

Now suppose its first-sector player is O_s. If zero or one of its incident A and B pair entries is positive, the triple's value is at most 3, because each such incident positive entry is 2 and C entries are at most 1. Its first-sector payoff alone is at least 3+4t under u and equals 3 under y.

If both incident entries are positive, there are exactly four possibilities:

\[
\begin{array}{c|c|c|c}
(j,k)&w_{O_s,j,k}&u_{a_{O_s}}+u_{b_j}+u_{c_k}&y_{a_{O_s}}+y_{b_j}+y_{c_k}\\\hline
(O_s,O_s)&4&4&4\\
(O_s,L_s)&4&4+3t&4\\
(R_s,O_s)&4&5-3t&5\\
(R_s,L_s)&5&5&5.
\end{array}
\]

Since t<=1/6, all four are covered. There are no other pairs of positive incident entries. This completes the all-triple proof for both vectors.

## 3. True integral worth and the full core

The diagonal matching supplies the lower bound T>=6q+1 on the true integral matching optimum. Any nonnegative triple cover upper-bounds every disjoint integral matching by its total payoff. Either u or y therefore gives T<=6q+1. Thus the actual integral worth is exactly T=6q+1; no substitution of a fractional optimum is used.

For any coalition, sum the cover inequalities over its optimal disjoint triples and use nonnegativity on its unmatched players. This proves every coalition inequality. Consequently both displayed vectors belong to the whole labeled payoff core

\[
P=\{p\ge0:\sum_vp_v=6q+1,\ a_i+b_j+c_k\ge w_{ijk}
\text{ for every full triple}\}.
\]

In particular P is nonempty and compact. Since u is positive on every coordinate, no coordinate has zero ideal, and no player is being silently discarded.

## 4. An integral partial matching gives the first-stage budget

For each 1<=s<=q, select the two triples

\[
N_s=(O_s,R_s,L_s),\qquad E_s=(L_{s-1},L_{s-1},O_s).
\]

Their values are respectively 5 and 1. They are pairwise player-disjoint: N_s consumes a_{O_s},b_{R_s},c_{L_s}; E_s consumes a_{L_{s-1}},b_{L_{s-1}},c_{O_s}. Within each sector these lists contain no repetition. They form an actual partial matching of total value 6q.

The unmatched player set is exactly

\[
U=\{c_{L_0},a_{L_q},b_{L_q}\}
\cup\bigcup_{s=1}^{q}\{a_{R_s},b_{O_s},c_{R_s}\},
\qquad |U|=3q+3.
\]

Every core allocation p must allocate at least 6q to the selected partial matching. Efficiency therefore gives the whole-core inequality

\[
\sum_{v\in U}p_v\le1.\tag{1}
\]

No equality between leaf payoffs, floor assumption, or local-face restriction was used to derive (1).

If every coordinate of p is at least r, (1) gives (3q+3)r<=1. The vector u achieves r=t, so the true first leximin floor is t. Every player in U receives t at u, and at every point of the entire first optimal face p>=t the same must hold: their lower bounds already sum to 1, leaving no room to increase any one of them in (1).

Therefore the target c_{L_0} equals t throughout the first optimal face. Every complete ascending leximin allocation stays in that face, so its final target payoff is t. Later selector stages need not be computed, and the displayed u is not asserted to be the whole final selector.

## 5. Exact ideal and limiting conclusion

At every core point the diagonal L_0 team is tight: all diagonal triple inequalities sum to the efficiency equality. Hence

\[
a_{L_0}+b_{L_0}+c_{L_0}=1.
\]

Nonnegativity gives H_{c_{L_0}}<=1, while the already verified full-core vector y attains c_{L_0}=1. Thus H_{c_{L_0}}=1 exactly. For the full ascending leximin allocation x,

\[
\frac{x_{c_{L_0}}}{H_{c_{L_0}}}=\frac1{3(q+1)}\longrightarrow0.
\]

Since all ratios with positive ideal are nonnegative, the infimum of these protection ratios over the stated class is zero.

## Independent finite reproduction

`verify_family.py` reconstructs all pair entries directly from this description, imports no other campaign code, and uses Fraction arithmetic to check q=1,2,3,4 against every raw full triple for both covers. It independently checks the partial matching's disjointness, value, exact unmatched set, and target certificates. Assertions are not used as proof gates.

With `--smt`, three additional Z3 queries at q=4 use only the raw complete core constraints: a larger common floor, a larger target on the whole first optimal face, and an ideal above one. All return UNSAT. The recorded run used Z3 5.1.0 and passed under Python `-O`; results are in `FAMILY_AUDIT.json`.

These finite replays supplement the all-parameter proof above. The q=2 member has T=13, so it is not being confused with the older 21-player, T=15 finite witness. Neither exact arithmetic nor this internal independent audit establishes global literature priority.
