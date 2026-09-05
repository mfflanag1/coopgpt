# Independent structural audit: shifted roots and replicated top pairs

2026-09-04. Audited by structural route independently of construction route after receiving its symbolic proposal. All statements below concern the entire core of a standard three-sided assignment game. No external correctness or novelty review is implied.

## Parameters and raw construction

Take integers L>=1 and R>=0. Use recurrence pairs U[l,i],V[l,i], for l=0,...,L and i in Z/3Z. At even levels U has color i and V color i+1; at odd levels these colors interchange. Each pair has its own local dummy D of the third color. Introduce global dummies G[0],G[1],G[2] of their respective colors. Add R copies of each top-level pair, with the same colors as that pair and their own local dummy.

Every root pair has total s=2; every other pair and copy has total s=1. For every pair, list both the local-dummy triple {U,V,D} and global-dummy triple {U,V,G[missing color]} at weight s. List root lower-bound triples {U[0,i],G[i+1],G[i+2]} at weight1.

For l>=1 and {j,k}=Z3\{i}, list {U[l,i],V[l-1,j],V[l-1,k]} at weight2. List the complementary triple {V[l,i],U[l-1,j],U[l-1,k]} at weight3 when l=1 and weight1 otherwise.

For every copy (Uc,Vc) of (U[L,i],V[L,i]), list {Uc,V[L,i],G[missing]} and {Vc,U[L,i],G[missing]}, each at weight1. Unlisted triples have weight0. Each listed triple contains exactly one player of each side, and listed triples are distinct. The values belong to {0,1,2,3}.

## Nonemptiness, integral matching total, and full core

Local-dummy pair triples form a disjoint matching of weight

  T=3(L+R+2).

The allocation z giving root U=V=1, other U=0,V=1, and every dummy0 covers every listed triple at equality and has total T. Therefore no integral matching exceeds T; the displayed matching attains it. This proves both the correct integer total and nonempty entire core without assuming balancedness.

For every core allocation, summing the local-dummy matching inequalities and using efficiency pins all global dummies to0 and each local pair triple to its designated total. Global-dummy alternatives force local dummies0 and U+V=s. Root lower-bound triples give U[0,i]>=1. Set q[0,i]=U[0,i]-1 and q[l,i]=U[l,i] for l>=1. Each recurrence and its complementary triple imply opposite inequalities, hence

  q[l,i]=q[l-1,j]+q[l-1,k].

The copy cross-constraints likewise give Ucopy=U[L,i], Vcopy=V[L,i]. Thus the entire core is exactly the recurrence system with 0<=q[0,i]<=1, 0<=q[l,i]<=1, pair complements as specified, and every dummy0. Conversely these equations imply all listed inequalities and efficiency; all other triple inequalities follow from nonnegativity. Triple inequalities characterize the whole cooperative core because summing them over each coalition's matching bounds its worth.

## Both full selectors

The largest payoff is always at least1 because each root U>=1. The allocation z above has largest payoff1. Any core point with maximum<=1 must have all three root U=1 and hence q[0]=0; recurrence, pair, and copy identities then force it to equal z. Therefore z is the unique minimax point and the full descending leximax-min point, including asymmetric feasible allocations.

The core is invariant under simultaneously rotating every color and index. The full ascending leximin payoff vector is unique on this compact convex set, so it is fixed by this rotation. Consequently all its root q-coordinates equal a common t, and q[l,i]=2^l t. Every symmetric vector with 0<=t<=2^-L is feasible.

After ignoring the fixed-zero dummies in the sorted order, the smallest coordinate of such a vector is

  min(2t, 1-2^L t).

Root U=1+t and V=1-t cannot be smaller; the lowest positive-slope active coordinates occur at level1. The unique maximizer is t=1/(2^L+2). This identifies full leximin: if it had any other t, the displayed feasible symmetric vector would improve its first nonfixed sorted coordinate. The symmetry argument avoids any unsupported assumption that an arbitrary first-stage maximin optimizer is unique.

## Quantitative distance and conclusion

Each root pair contributes 2t to the l1 distance from z; each level-l pair contributes 2^(l+1)t; each top copy contributes 2^(L+1)t. There are three indices at every level and R copies per index. Therefore

  ||x-z||_1 = 6t [2^(L+1)-1+R*2^L],
  rho(L,R) = 2 [ (R+2)2^L-1 ] / [ (2^L+2)(L+R+2) ].

The number of players, counting every local and global fixed zero, is

  n=9(L+R)+12.

Taking R=L^2 and L→infinity gives rho→2. Since nonnegative vectors with equal positive total always satisfy rho<=2, the supremum across all such three-sided markets is exactly2. Every finite nonempty core has strict rho<2 for these full selections by the generic overlap lemma; the family makes the sharp supremum nonattained.

An all-large-n padding conclusion also follows. Choose L=floor(log2 n), R=floor((n-12)/9)-L for sufficiently large n, build this market, and add at most8 isolated zero-value players. Then rho→2 and 2-rho=O(log n/n). The extra isolated players may be placed on any side and count toward n; side cardinalities need not be equal. A simpler statement using R=L² suffices for the primary structural target.

The root-shift changes are essential: the uniform-pair-total unshifted recurrence family instead has coincident selections despite an exponentially vanishing individual guarantee. Omitting a complementary recurrence constraint is another falsifying control for the advertised entire-core characterization.
