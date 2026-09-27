# Vanishing leximin protection with nonnegative pair-additive triples

**Theorem.** For every integer q>=1 there is a complete strict three-sided assignment market with 9q+3 players, nonnegative pair entries in {0,1,2}, positive integral worth 6q+1, and nonempty full core, such that one player's full ascending-leximin payoff is 1/[3(q+1)] and its maximum whole-core payoff is 1. The target is fixed at the positive first global leximin level. Consequently the best size-independent protection fraction for this class is

\[
c_{\mathrm{pair}}=0.
\]

Every induced triple has integer value at most 5. There are no permanently zero-ideal players: the core contains an allocation positive in every coordinate. This proves the mathematical vanishing-family target. It does not prove priority, minimum market size, optimal finite-size ratios, or a new selector-distance result.

## Construction

Use the common team-label set

\[
\mathcal T=\{L_0\}\cup\{O_s,L_s,R_s:1\le s\le q\}.
\]

For every label t, create players a_t,b_t,c_t in the three respective sectors. Thus each sector has 3q+1 players. Every full triple has value

\[
w(a_t,b_u,c_v)=A_{tu}+B_{tv}+C_{uv}.
\]

Only full triples produce output. Coalition worth is maximum integral disjoint-triple output. Define the pair matrices by the following nonzero entries, and set every other entry to zero:

| Entries | Range | Value |
|---|---|---|
| \(C_{L_s,L_s}\) | \(0\le s\le q\) | 1 |
| \(C_{R_s,R_s}\) | \(1\le s\le q\) | 1 |
| \(A_{O_s,O_s},\ B_{O_s,O_s}\) | \(1\le s\le q\) | 2 |
| \(A_{O_s,R_s},\ B_{O_s,L_s}\) | \(1\le s\le q\) | 2 |
| \(C_{R_s,L_s},\ C_{L_{s-1},O_s}\) | \(1\le s\le q\) | 1 |

There are 8q+1 nonzero pair entries. The diagonal perfect matching consists of all teams \((a_t,b_t,c_t)\). Each L or R team has value 1 and each O team value 4. Its total is

\[
T=1+6q.
\]

## Two complete core covers

Put \(\tau=1/[3(q+1)]\). In (a,b,c) order define a floor witness u and an ideal witness y by

\[
\begin{array}{c|c|c}
\text{team}&u&y\\\hline
L_s&\bigl(\tau,\ 1-(3s+2)\tau,\ (3s+1)\tau\bigr)&(0,0,1)\\
R_s&\bigl(\tau,\ 1-2\tau,\ \tau\bigr)&(0,1,0)\\
O_s&\bigl(4-(3s-1)\tau,\ \tau,\ (3s-2)\tau\bigr)&(3,0,1).
\end{array}
\]

Use 0<=s<=q for L and 1<=s<=q otherwise. Every coordinate of u is at least tau. For instance, its smallest L-side b payoff occurs at s=q and equals tau; its smallest O-side c payoff occurs at s=1 and equals tau. Each diagonal team's payoff sum equals its value, at both points, so both totals are T.

We verify **every** mixed triple. If its a-player is from an L or R team, it has no positive A or B pair entry, and the triple value is its C entry. The possible positive C pairs and their u-payoff sums are

\[
\begin{array}{c|c|c}
(b,c)\text{ labels}&u_b+u_c&y_b+y_c\\\hline
(L_s,L_s)&1-\tau&1\\
(R_s,R_s)&1-\tau&1\\
(R_s,L_s)&1+(3s-1)\tau&2\\
(L_{s-1},O_s)&1-\tau&1.
\end{array}
\]

Each corresponding C entry is 1. Adding u_a=tau or y_a=0 proves the cover. Zero C entries follow from nonnegativity.

If the a-player is a_(O_s), its only positive pair entries are the two specified A entries and two specified B entries, all of value 2. With at most one such entry, the triple value is at most 3, covered by

\[
u_{a_{O_s}}\ge3+4\tau,\qquad y_{a_{O_s}}=3.
\]

With both entries positive, exactly four cases remain:

\[
\begin{array}{c|c|c|c}
(b,c)\text{ labels}&w&u_a+u_b+u_c&y_a+y_b+y_c\\\hline
(O_s,O_s)&4&4&4\\
(O_s,L_s)&4&4+3\tau&4\\
(R_s,O_s)&4&5-3\tau&5\\
(R_s,L_s)&5&5&5.
\end{array}
\]

Since tau<=1/6, all these are covers. This exhausts all triples and also proves w<=5.

The integral matching gives worth at least T, while either complete nonnegative cover bounds every integral matching by T. Thus the actual integral worth is T. Summing triple covers over arbitrary coalition matchings proves all coalition inequalities, including unmatched players by nonnegativity. Both u and y belong to the entire core, and its raw triple-cover description is exact. No fractional matching value is substituted for T.

## A near-optimal partial matching fixes the target

For each s take the two triples

\[
N_s=(a_{O_s},b_{R_s},c_{L_s}),\qquad
E_s=(a_{L_{s-1}},b_{L_{s-1}},c_{O_s}).
\]

Their values are respectively 5 and 1. These 2q triples are pairwise player-disjoint: the used a labels are the O labels and L_0,...,L_(q-1); the used b labels are the R labels and L_0,...,L_(q-1); the used c labels are L_1,...,L_q and the O labels. They form an actual partial matching of value 6q.

Its unmatched player set is

\[
U=\{c_{L_0},a_{L_q},b_{L_q}\}
\cup\{a_{R_s},b_{O_s},c_{R_s}:1\le s\le q\},
\]

with exactly 3q+3 players. At every core point p, summing the partial-matching covers and subtracting from efficiency gives

\[
\sum_{i\in U}p_i\le T-6q=1.\tag{1}
\]

Hence a common payoff floor is at most 1/(3q+3). The point u attains this bound, so it is exactly the first global leximin level tau. On the whole first optimal face, all coordinates are at least tau. Since |U|tau=1, inequality (1) forces every U coordinate to equal tau there. In particular, the target c_(L_0) remains tau through every subsequent refinement of full leximin. No claim that u is the entire final selector is needed.

The diagonal L_0 team is tight at every core point, so nonnegativity gives H_(c_(L_0))<=1. The cover y attains target payoff 1. Therefore

\[
H_{c_{L_0}}=1,\qquad
x_{c_{L_0}}=\frac1{3(q+1)},\qquad
\frac{x_{c_{L_0}}}{H_{c_{L_0}}}=\frac1{3(q+1)}\longrightarrow0.
\]

The first-face statement follows from the entire-core inequality, rather than the output of a finite numerical selector computation. For each desired epsilon>0, choosing an integer q with 3(q+1)>1/epsilon supplies the required market, proving c_pair=0.

## Evidence and priority boundary

The construction route supplies an all-parameter proof and exact finite calibrations; root independently derived the cover cases and a telescoping version of (1). The construction route then identified the simpler disjoint partial-matching certificate, which root and the independent audit checked separately. Finite checks corroborate the formulas; they are not the proof of the limit.

The earlier 21-player example and this family's q=2 market are distinct constructions. The latter has pair entries at most 2 and 17 positive pair entries, while the earlier example has entries at most 3 and 16 positive pair entries. No isomorphism or player-minimality claim is made.

Coordinate-ideal protection and vanishing protection in broader games have prior precedents. The surviving priority question is the realization in complete, fixed three-sector, nonnegative pair-additive strict markets. See the cycle's claim-priority audit before asserting novelty or field-level significance. External specialist review remains pending.
