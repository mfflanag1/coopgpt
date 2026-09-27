# The entire diagonal-subdivision family has uniform protection

Conventional proof reviewed by Claude with no correctness defect; specific family only, no general C4 claim and no priority claim.

Use q>=1, m=3q+1, labels L_0=0 and O_s=3s-2,L_s=3s-1,R_s=3s. Nonzero source matrices are
A(O_s,O_s)=A(O_s,R_s)=2; B(O_s,O_s)=B(O_s,L_s)=2;
C(L_s,L_s)=1 (0<=s<=q), C(R_s,R_s)=C(R_s,L_s)=C(L_(s-1),O_s)=1 (1<=s<=q).
The strict four-sector market has full-team value
w(a,b,c,d)=A(a,b)+C(b,c)+B(a,d)+M*1_(c=d), M>0.
Only full teams are productive; each coalition's worth is its maximum integral matching value. All sectors have m players, and the entire core consists of nonnegative covers with sum T=6q+1+mM. The diagonal matching attains the sum of all four edge row maxima, proving this value. Every diagonal team is tight in every core point. Ideals H_i use the entire core; x is the full ascending sorted leximin allocation, retaining all labeled coordinates.

## Theorem

For every q>=1 and every M>0, every player satisfies x_i/H_i >= 1/676.
In particular no target choice and no positive sequence M(q), including M(q)->0, yields vanishing protection in this exact family. This closes this construction; it does not settle c(C4).

## 1. Uniform floor, recalled with proof

The three-sector source has a core point z at floor tau=1/[3(q+1)]: at L_s its a,b,c entries are tau,1-(3s+2)tau,(3s+1)tau; at R_s they are tau,1-2tau,tau; at O_s they are 4-(3s-1)tau,tau,(3s-2)tau. Its all-q full-team cover proof is in [Two complete core covers](../zero_sector_extension/SOURCE_FAMILY_PROOF.md), which explicitly checks the four positive-C cases and the four double-positive A/B cases symbolically.
At M=2, p^2=(z+1/2 on a,b,c; 1/2 on d) covers every team: B(a,d)-B(a,c)<=2, with equality of the B terms when c=d. Its sum is T(2).
At M=0, p^0 assigns rowmax A+rowmax B to a, rowmax C to b, and zero to c,d, hence is a core point. For 0<M<2 interpolate (1-M/2)p^0+(M/2)p^2. Coverage and efficiency are preserved since both w(M) and T(M) are affine. Every coordinate is at least M/4. For M>=2 the direct point (z+M/4 on a,b,c; M/4 on d) covers by the same comparison. Thus all H_i are positive and x_i>=M/4 for all M>0. Diagonal tightness also gives H_i<=4+M.

## 2. A uniform ideal bound for all weak players

Call these players weak:
* a_j for j not an O-label;
* b_(O_s), all s;
* c_(O_s), all s, c_(L_s) for 0<=s<q, c_(R_s) for 1<=s<q;
* every d-player.
All remaining players are strong. We prove H_i<=3M for each weak player using explicit partial matchings worth T-3M.

A partial matching missing a player i with value T-3M implies p_i<=3M for every core point: sum its cover inequalities, subtract from efficiency, and use nonnegativity of every other unmatched payoff.

For each s, gadget U_s starts from all diagonal teams, deletes those at L_(s-1),O_s,L_s,R_s, and inserts
(O_s,R_s,R_s,L_s), (L_(s-1),L_(s-1),O_s,O_s), (L_s,L_s,L_s,R_s).
The deleted value is 7+4M; inserted values are 5,1+M,1. The unmatched players are a_(R_s),b_(O_s),c_(L_(s-1)),d_(L_(s-1)).

Gadget V_s deletes just diagonal teams O_s,L_s,R_s and inserts
(O_s,R_s,R_s,L_s), (L_s,L_s,L_s,R_s).
The deleted value is 6+3M and the inserted value 6. Unmatched players are a_(R_s),b_(O_s),c_(O_s),d_(O_s).
Changing the second inserted team's d-label from R_s to O_s preserves its value 1 and makes d_(R_s) unmatched. Alternatively changing the first team's d-label from L_s to O_s preserves its value 5 and makes d_(L_s) unmatched. These are separate variants, not simultaneous edits.

For 1<=s<q, start with U_(s+1) and replace its still-present diagonal team (R_s,R_s,R_s,R_s) by (R_s,R_s,L_s,L_s). Its value remains 1+M. This makes c_(R_s) and d_(R_s) unmatched, instead of c_(L_s),d_(L_s).

Finally all non-O a-rows are identically zero on both incident matrices. To omit any such a-player j, start with V_1, whose unmatched a-player is R_1. If j is already unmatched do nothing; otherwise replace j in its unique matched team by R_1. This preserves weight and disjointness, and leaves a_j unmatched. These gadgets cover every weak player and prove the bound, uniformly in q and M.

## 3. Strong players away from the terminal block

At any core point p, diagonal tightness and the weak bounds give
p_(a,O_s)>=4+M-9M=4-8M.
For s<q, p_(b,L_s)>=1-8M; for 1<=s<q, p_(b,R_s)>=1-8M.
The only remaining strong players are b_(L_q),b_(R_q),c_(L_q),c_(R_q).
Write L=L_q,R=R_q and S_L=p_(b,L)+p_(c,L), S_R=p_(b,R)+p_(c,R).
Both S_j=1+M-p_(a,j)-p_(d,j) lie in [1-5M,1+M].

## 4. A terminal replacement that preserves every other payoff

Assume 0<M<=1/42. Starting from ANY core point p, replace only four coordinates by
    y_(c,L)=1/2+7M,  y_(c,R)=1/2-7M,
    y_(b,L)=S_L-y_(c,L),  y_(b,R)=S_R-y_(c,R).
All four are at least 1/2-12M>=3/14; all other coordinates remain exactly p's. Sum and nonnegativity are preserved. We verify every full-team inequality.

For every a,b,d, the unchanged a-payoff obeys
    p_a >= A(a,b)+B(a,d)-8M:
for O-rows this follows from p_a>=4-8M and A+B<=4; other rows have A+B=0 and p_a>=0.

A team whose b,c labels are both nonterminal is unchanged. A team with b=c=L or b=c=R has unchanged b+c sum, hence is covered. For the cross pair b=R,c=L, C=1 and
    y_(b,R)+y_(c,L)=S_R+14M>=1+9M.
Together with the displayed a bound and d>=0 this covers A+B+C+M*1_(c=d).
For every other changed team, C(b,c)=0: no nonterminal row has a positive C-entry in a terminal column; terminal rows only have positive entries in terminal columns; and C(L,R)=0. Such a team includes at least one changed coordinate, so y_b+y_c>=1/2-12M>=9M. Again the a bound and d>=0 cover A+B+M*1_(c=d). These cases exhaust all teams. Therefore y is a core point.

Apply this replacement to the full leximin point x. If any terminal coordinate were below 3/14, the replacement would leave every nonterminal coordinate unchanged and place all four terminal coordinates at or above3/14. In ascending sorted order this is a strict lexicographic improvement (the smallest changed value below 3/14 is removed, and no value below that threshold is introduced). Contradiction. Thus every terminal coordinate of x is at least3/14.

## 5. Combine the regimes

For 0<M<=1/42, weak players have x_i/H_i>=1/12. Nonterminal strong players have x_i>=1-8/42=17/21; terminal strong players have x_i>=3/14. All strong ideals are <=4+1/42=169/42, so all strong ratios are at least 9/169.
For M>=1/42, the floor and diagonal ideal bound give
    x_i/H_i >= M/[4(4+M)] >= 1/676.
Since both 1/12 and9/169 exceed1/676, this proves the theorem. The constant is deliberately conservative; no sharpness is claimed. The M=0 endpoint separately has the [established tree 1/4 guarantee](../tree_extension/ALL_TREES.md) on positive ideals.

## Scope and evidence

This is a route-specific elementary proof, not a new classification or a novelty claim. Its source-family floor is an existing proved ingredient. New steps here are the all-weak-player partial matchings and terminal replacement. Exact arithmetic tests complement, but do not replace, the all-q proof. C4 remains unresolved in general.
