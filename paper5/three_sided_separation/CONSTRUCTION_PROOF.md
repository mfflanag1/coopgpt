# A bounded-integer three-sided assignment family with separation tending to two

## Theorem

For every integer L >= 1 and R >= 0, there is a standard complete three-sided
assignment game with equally many players in the three sectors, all weights in
{0,1,2,3}, a nonempty entire core, and

    n = 9(L+R)+12,   T = 3(L+R+2).

Its full leximin and full leximax-min allocations satisfy

    rho = ||x-z||_1/T
        = 2[((R+2) 2^L - 1)] / [(2^L+2)(L+R+2)].

Consequently rho tends to 2 when R=L^2 and L tends to infinity. Since two
nonnegative allocations of total T always have distance at most 2T, the sharp
supremum over nonempty entire cores of three-sided assignment games is 2.

Moreover, a top-level V coordinate has leximin payoff 2/(2^L+2) and maximum
core payoff 1. Thus no positive dimension-independent coordinate fraction
holds, even when R=0. The coordinate conclusion and the distance conclusion
follow from separate calculations; neither is inferred from the other.

## Raw triples and colors

Colors are 0,1,2 modulo 3, representing the three sectors. Include three global
players G_i of colors i. For every level l=0,...,L and i=0,1,2, introduce
U[l,i], V[l,i], D[l,i]. If l is even, their colors are i,i+1,i+2; if l is odd,
the U and V colors are swapped and the D color is still i+2.

The pair total is s_0=2 and s_l=1 for l>=1. Assign value s_l to both triples

    (U[l,i], V[l,i], D[l,i]),
    (U[l,i], V[l,i], G[i+2]).

For every root U[0,i], give its triple with the two global players of the other
colors value 1. For l>=1 and {j,k}={0,1,2}\{i}, give the triples

    (U[l,i], V[l-1,j], V[l-1,k]) value 2,
    (V[l,i], U[l-1,j], U[l-1,k]) value 3 if l=1, otherwise 1.

These are properly colored because consecutive levels swap the U/V color
orientations. Now introduce R copies of each of the three top-level pairs.
Each copy U'[r,i],V'[r,i],D'[r,i] has the top-level color orientation, pair
value 1 with its own D and with G[i+2], and the additional value-1 triples

    (U'[r,i], V[L,i], G[i+2]),
    (V'[r,i], U[L,i], G[i+2]).

All triples not explicitly listed have value zero. The executable generator
`triple_recurrence_family.py` specifies these raw weights without using a
reduced core or an optimization oracle.

## Integral matching and entire-core characterization

The disjoint triples containing each pair and its own D form an integral
matching of total T=6+3L+3R. The proposed allocation z below is nonnegative,
has total T, and covers every raw weighted triple. Consequently every integral
matching has value at most T, so this displayed matching is optimal and the
core is nonempty. The three unused global players may be added as a zero-value
triple to obtain a perfect matching if desired.

For any core allocation, sum the inequalities of the displayed disjoint
matching. Efficiency and nonnegativity force every G to zero and every local
matching triple to equality. The alternative pair triple containing G then
forces every D to zero and each U+V=s_l exactly. Write

    U[0,i] = 1+q[0,i],  V[0,i] = 1-q[0,i],
    U[l,i] = q[l,i],    V[l,i] = 1-q[l,i]  (l>=1).

The root lower triples imply q[0,i]>=0, and root V nonnegativity implies
q[0,i]<=1. The two recurrence inequalities are oppositely directed and give

    q[l,i] = q[l-1,j] + q[l-1,k].

Equivalently q_l=M q_{l-1}, where M=J-I is the 3-by-3 matrix with zero diagonal
and ones elsewhere. Copy cross-triples force U'[r,i]=q[L,i] and
V'[r,i]=1-q[L,i]. Nonnegativity requires 0<=q[l,i]<=1 for all levels. Conversely,
any q_0 satisfying these bounds, with q_l=M^l q_0, gives a core allocation:
every positive triple inequality just listed is an equality or the root lower
bound, and all omitted zero-value inequalities follow from nonnegativity.

Thus this parameterization is the entire core, not merely an embedded face or
an Owen set. In particular, q_0=0 is feasible. Its allocation z assigns 1 to
both root U and root V, 0 to every subsequent U, 1 to every subsequent V, and
0 to every dummy. This also proves the upper matching certificate above.

## Full leximax-min allocation

Every root U is at least 1, so the smallest possible maximum payoff is at least
1. At q_0=0 all payoffs are at most 1. Any core allocation with maximum at most
1 has U[0,i]=1+q[0,i]<=1 and q[0,i]>=0, so q_0=0. Recurrences and copy equalities
then determine the whole allocation. Hence z is the unique minimax allocation,
and therefore also the full leximax-min allocation.

## Full leximin allocation without a symmetry assumption

All G and D coordinates are forced zero. All other coordinates can be made
strictly positive: take q_0=t(1,1,1) with 0<t<2^-L. Therefore a full leximin
procedure first fixes exactly the dummy coordinates at zero and next maximizes
the common lower bound eta of every remaining coordinate.

If eta is feasible, the three level-1 U coordinates yield

    q[1,i]>=eta, so 2 sum_i q[0,i] >= 3 eta.

The three top-level V coordinates yield

    q[L,i]<=1-eta, so 2^L sum_i q[0,i] <= 3(1-eta).

Combining these two inequalities gives eta <= 2/(2^L+2). This bound is attained
by

    t = 1/(2^L+2),  q[l,i] = 2^l t.

Indeed, the least U payoff beyond the root is 2t, the least V payoff is the
top payoff 1-2^L t=2t, root U is 1+t, and root V is 1-t. Copies repeat the top
payoffs. Equality in the bound forces every q[1,i]=eta, and M is invertible
(eigenvalues 2,-1,-1), so q_0=t(1,1,1) is the only maximizing allocation.
The full leximin allocation x is therefore already uniquely determined at this
first positive floor. Fixed zero coordinates are explicitly retained throughout.

## Distance and coordinate guarantee

Every level-l pair changes between x and z by (+2^l t,-2^l t), including the
root pair where l=0. Every copied top pair changes by (+2^L t,-2^L t). Thus

    ||x-z||_1 = 6t [sum_{l=0}^L 2^l + R 2^L]
              = 6 [(R+2)2^L-1]/(2^L+2).

Dividing by T proves the formula. For R=L^2, both (R+2)/(L+R+2) and
2^L/(2^L+2) tend to 1, so rho tends to 2. For example L=4,R=16 gives
rho=287/198 > 4/3. The exact lower-bound construction therefore rules out any
uniform bound below 2.

Every top-level V has maximum core payoff 1, attained by z, because its U
complement is nonnegative and its pair total is 1. Its payoff at x is
2/(2^L+2), tending to zero. L=3 already gives 1/5 < 1/3.

## Optional every-dimension quantitative corollary

For every integer n>=30, put k=floor((n-12)/9), L=ceil(log2 k), and R=k-L.
Then L>=1 and R>=0, and the displayed construction has 9k+12<=n players. Add
the remaining at most eight players with all incident weights zero. The old
optimal matching and efficiency force these new players to zero throughout the
core, so neither full selector nor rho changes.

Writing S_n for the supremum for total dimension n (over all three sector sizes),
we obtain

    2-S_n <= [2 ceil(log2 k)+4]/(k+2) + 2/(k+2)^2
            = O(log n/n).

To verify the bound directly, use 2^L>=k in

    2-rho = 2L 2^L/[(2^L+2)(k+2)]
            + 4/(2^L+2) + 2/[(2^L+2)(k+2)].

No sharp finite-n constant or matching O(1/n) rate is asserted. The elementary
universal upper bound rho<=2 is sufficient for the sharp-supremum theorem.

## Negative controls and limits of the argument

1. With R=0 and L tending to infinity, the coordinate fraction still tends to
   zero but rho tends to zero as well. Coordinate failure alone does not imply
   large normalized distance.
2. With fixed L and R tending to infinity, rho tends to 2^(L+1)/(2^L+2), which
   remains strictly below 2. Amplification depth must grow as well as replicated
   mass.
3. If the root baseline shift and root lower triples are removed and every pair
   has total 1 (the
   structurally related unshifted recurrence family), both selectors coincide
   at q_0=(1/(2^L+1))(1,1,1). A recurrence alone does not separate the selectors.

The proof is an internal mathematical certificate. Any novelty statement still
requires a dated primary-source audit and specialist review.
