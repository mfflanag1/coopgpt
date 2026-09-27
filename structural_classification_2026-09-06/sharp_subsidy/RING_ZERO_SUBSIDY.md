# A cyclic junction family with zero frozen-ideal subsidy

Date: 2026-09-07. **All-size theorem for this explicit family.** The global sharp-constant bounds remain 1/3 <= S_3 <= 2/5.

This family was tested as a possible stronger lower construction. Its cycle instead forces additional restrictions on the original core maxima. The result concerns actual markets and their entire cores, not only a failed deletion-certificate template.

## 1. Market

For any integer b>=2 let m=4b. There are m players in each sector A,B,C. Start all three pair matrices with the identity, and use the following disjoint actual triples:

    ring teams:       (j,j+1 mod b,b+j),                 0<=j<b,
    attached teams:   (2b+2j,2b+2j+1,j),                 0<=j<b.

For each displayed (a,b',c), set the off-diagonal pair entries AB[a,b']=2, AC[a,c]=1 and BC[b',c]=2. All other off-diagonal entries remain zero. Each displayed team has worth 5; every diagonal team has worth 3. Write P for this set of 2b teams.

The label incidence graph has one cycle, b degree-three hub labels, and 3b degree-one labels. Equal sizes, strict full-team production and nonnegative pair matrices are preserved.

## 2. An explicit original-core allocation

Give A and B players at hub labels j<b the payoff 4/3. Give C players at hub labels 1/3. At every other label, give its unique P-used player 7/3 and its other two players 1/3. Call this allocation y.

Each diagonal team sums to 3, so y(N)=3m=12b. Every displayed P-team sums to 5. All coordinates are nonnegative.

To check all other triples, note that P consists of disjoint actual teams. Any triple containing two off-diagonal positive pairs is therefore one of the displayed P-teams. A different triple has at most one positive off-diagonal pair and at most one diagonal pair. If its off-diagonal pair has value 2, its endpoints' payoffs plus the minimum possible third payoff are at least 3: the smallest cases are the ring AB pair (4/3,4/3) and attached BC pair (7/3,1/3), with a third payoff at least 1/3. If its off-diagonal pair has value 1, its endpoints are either (4/3,7/3) or (7/3,1/3), again sufficient for the maximum possible total worth 2. A triple without off-diagonal pairs is either diagonal, already checked, or has worth at most 1, covered by three payoffs of at least 1/3.

Thus y covers every triple and consequently every original coalition. The diagonal matching attains 3m and y upper-bounds all integral matching values, proving T=3m and nonempty original core.

## 3. The cycle identifies a sector minimum

Consider any original core allocation x. Every diagonal team is tight. The original triple inequalities for

    (j,j+1 mod b,j),   (j,j+1 mod b,j+1 mod b)

both have right side 3. Comparing with diagonal tightness gives

    x_B(j+1)>=x_B(j),      x_A(j)>=x_A(j+1).

Going around the cycle forces all hub A payoffs to equal a common A, and all hub B payoffs to equal a common B. Hence all hub C payoffs equal C=3-A-B.

Let c=min_k x_C(k). The ring team's inequality gives x_C(b+j)>=2+C. Meanwhile the diagonal AB pair at bridge label b+j, completed with any C player, has worth at least 1. Completing with a player attaining c yields

    1-c <= x_A(b+j)+x_B(b+j)
        =3-x_C(b+j) <=1-C.

Thus c>=C. The opposite inequality holds because hub C players attain C, so **c=C**. The same inequalities give x_C(b+j)=2+c and x_A(b+j)+x_B(b+j)=1-c. In particular 0<=c<=1, and both unmatched payoffs at every bridge label are at most 1.

## 4. Attached leaves also have small core maxima

Put a=min_k x_A(k) and d=min_k x_B(k). For attached labels u=2b+2j and v=2b+2j+1, let p=x_A(u), q=x_B(v). The attached-team constraint is

    p+q+c>=5.

Diagonal tightness and sector minima give q<=3-a-c and p<=3-d-c. Therefore p>=2+a and q>=2+d. The other two coordinates at u sum to 3-p<=1-a<=1; those at v sum to 3-q<=1-d<=1. Every such coordinate is nonnegative and hence individually at most 1.

These inequalities hold for every point of the original entire core. Consequently H_i<=1 for all players outside P and for hub C players. All other players satisfy H_i<=3 by diagonal tightness.

The allocation y in Section 2 pays the former group 1/3 and every other player at least 1. Thus y_i>=H_i/3 everywhere, while y remains in the original core and sums to T. Therefore

    s_3(M_b)=0       for every b>=2.

No maxima were recomputed after subsidy, and no proper-coalition worth was changed.

## 5. Verification and research implication

ring_zero.py reconstructs the matrices and allocation from b. Its standard-library checks for b=2,...,12 verify 389,312 triple inequalities, diagonal totals, P-team worths, cycle comparison inequalities and protection using the proved ideal bounds. With --smt, it independently encodes the full original cores for b=2,3,4: six counterexample queries for the ideal upper bounds return UNSAT, and three allocation-witness controls return SAT. The finite checks corroborate the proof for all b; they do not replace it.

The uniform ring is therefore excluded as a route to a stronger lower bound. The mechanism is informative: cycling the comparison inequalities converts weak payoff orders into equalities, and a diagonal pair then pins the common hub payoff to a sector minimum. An incidence-count argument alone would miss this collapse in the original ideals.

Heterogeneous cyclic weights or patterns with several independent cycles remain live. The weight-selection proof route also remains open; the sector-centered cut and fixed harmonic maximal-diagonal constructions tested this turn were not universal. No global sharpness or novelty claim follows from this theorem.
