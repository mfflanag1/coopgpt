# Three-sided cores have no uniform individual leximin guarantee

Internal theorem and conventional proof, 2026-09-04. This addresses the individual guarantee, not the distance target. In fact the family below has coincident full selectors.

**Theorem.** For every integer L>=0, there is a standard three-sided assignment game with 3(L+1)+1 players on each side, weights in {0,1,2}, integral matching value T=3(L+1), and nonempty entire core, such that a player i has max_core p_i=1 but Lmin_i=1/(2^L+1). Both full sorted selectors coincide. Thus no positive dimension-independent individual fraction survives, and the proposed one-third guarantee fails already at L=2 (30 players, including twelve fixed zeros).

## Explicit market

Indices i are modulo 3, and colors denote the three market sides. At every level l=0,...,L and index i, introduce players U[l,i], V[l,i], D[l,i]. D[l,i] has color i+2. When l is even, U[l,i] has color i and V[l,i] color i+1; when l is odd, their colors are interchanged. Each level contributes three players to each market side. Also introduce a global dummy G[c] on each side c.

Specify the following positive triples; all unlisted triples have weight zero:

1. {U[l,i],V[l,i],D[l,i]} and {U[l,i],V[l,i],G[i+2]} each have weight 1, for every l,i.
2. For l>=1 and {j,k}={0,1,2}\{i}, {U[l,i],V[l-1,j],V[l-1,k]} has weight 2.
3. For the same indices, {V[l,i],U[l-1,j],U[l-1,k]} has weight 1.

Every listed set contains exactly one player of each color. All triples are distinct. The local-dummy triples in the first list form a disjoint matching of weight T=3(L+1), leaving just the three global dummies unmatched. The allocation U=0,V=1,D=G=0 has this total and covers every listed triple at its value. Thus weak duality implies that the integral maximum matching value is exactly T, and this allocation proves entire-core nonemptiness. No balancedness assumption or fractional substitute is used.

## Entire-core characterization

The entire core consists exactly of the allocations

  D=G=0, U[l,i]+V[l,i]=1,
  U[l,i]=U[l-1,j]+U[l-1,k]  (l>=1),
  0<=U[l,i]<=1.

Indeed, summing the disjoint matching inequalities and applying efficiency first forces every global dummy payoff to zero and U+V+D=1 in each matched triple. The global-dummy alternatives then give U+V>=1, so every local dummy is zero and U+V=1. For a recurrence, substituting V=1-U into the weight-2 triple gives U[l,i]>=U[l-1,j]+U[l-1,k], whereas the complementary weight-1 triple gives the reverse inequality. This proves all stated identities. Conversely these identities imply every positive triple inequality, efficiency and nonnegativity; zero triple inequalities are automatic. Summing matching edges inside any coalition shows that triple covering inequalities are the entire cooperative core, not a restricted core-like set.

## Full selectors

Full ascending leximin and descending leximax-min have unique payoff vectors on any compact convex set. A brief standard proof of uniqueness is that if distinct vectors have the same lex-optimal sorted vector, their midpoint strictly improves the relevant sorted vector at the first payoff level where their coordinate classes differ. Each selector is consequently invariant under every coordinate-permutation automorphism of its feasible set.

Simultaneously rotating i and every market color cyclically preserves this market. Therefore both full selections have U[l,0]=U[l,1]=U[l,2]=2^l t and V[l,i]=1-2^l t for some t in [0,2^-L]. Every such symmetric vector is feasible.

All dummies are fixed at zero. After these irrelevant fixed coordinates, the minimum among active players is min(t,1-2^L t), uniquely maximized at t=1/(2^L+1). The maximum among active players is max(2^L t,1-t), uniquely minimized at the same t. Thus both full selectors equal this vector. This argument needs uniqueness and symmetry: the first unconstrained maximin stage is identically zero because fixed-zero players are counted.

For each level-L player V[L,i], its selected payoff is 1/(2^L+1). Its core maximum is exactly 1, attained at U=0,V=1. The ratio tends to zero exponentially while the number of players grows linearly. Explicitly the ratio is 1/(2^((n-12)/9)+1) on n=9L+12 players. The selectors' normalized distance is exactly zero, so this family also demonstrates that failure of individual fairness guarantees does not decide selector disagreement.

## Generalized recurrence gadget

The same proof works with arbitrary positive pair totals s[l,i], replacing pair weights1 by s[l,i], weight2 by s[l-1,j]+s[l-1,k], and the complementary weight1 by s[l,i], provided the affine recurrence has a nonnegative feasible allocation. The core is then exactly U+V=s, D=G=0, U_l=(J-I)U_(l-1), 0<=U<=s. The integer matching total is sum s. This gadget may be reusable independently of the uniform-total coordinate example.
