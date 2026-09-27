# A whole-core obstruction to shrinking the small-team weight

5 September 2026. Independent theory check of the proposed repeated cross-block coupling. This proves a failure of the proposed internal-player amplification route, not of every possible coupled construction.

## Family and exact total

Use blocks s=0,...,L, each with player names (a_s,b_s,c_s; d_s,e_s,f_s; g_s,h_s,i_s). Within each block use

A=[[0,0,0],[2,0,1],[0,1,0]],
B=[[0,0,delta],[1,0,0],[0,0,0]],
C=[[0,1,0],[3,0,0],[2,0,0]],

and otherwise zero pair entries, except A_{c_s,d_{s+1}}=2 for s=0,...,L-1. Thus this is the computational two-block coupler repeated as a directed chain, with the original B_{a_s,i_s}=1 replaced by delta.

Each block supplies matching triples (a_s,f_s,i_s), (b_s,d_s,h_s), (c_s,e_s,g_s), of values delta,3,4. The displayed integral matching has total (L+1)(7+delta).

For every 0<=delta<=3, the following allocation, repeated in every block, is an entire-core cover:

(a,b,c;d,e,f;g,h,i)
 = (delta/3,1,1; 1,delta/3,delta/3; 3-delta/3,1,delta/3).

It has the displayed matching total, proving optimality and nonempty entire core.

Here is a complete all-size coverage argument. Every local triple slack is affine in delta. At delta=0 and delta=3 respectively the three 3-by-3 slack matrices, indexed by first-sector player, are

at delta=0:
[[4,1,1],[0,1,0],[1,1,0]],
[[2,0,0],[0,2,1],[0,1,0]],
[[5,2,2],[0,1,0],[2,2,1]];

at delta=3:
[[4,2,0],[1,3,0],[2,3,0]],
[[1,0,1],[0,3,3],[0,2,2]],
[[4,2,3],[0,2,2],[2,3,3]].

All entries are nonnegative, so all local triples are covered throughout the interval. A nonlocal triple not using a coupler can contain at most one positive pair entry. Every such pair's two payoffs already cover its value, except (a_s,i_s), whose shortfall is delta/3 and is covered by the third player's payoff (every payoff is at least delta/3). A triple using the coupler (c_s,d_{s+1}) has two-player payoff 2, exactly its pair value. The row B_{c_s,*} is zero, and the only possible additional positive entry is C_{d_{s+1},h_{s+1}}=1, covered exactly by h_{s+1}=1. This exhausts every local, mixed, and coupler triple for arbitrary L.

## The incidental inequalities that stop the naive recurrence

Matching efficiency makes, in every core vector,

a_s+f_s+i_s=delta,
b_s+d_s+h_s=3,
c_s+e_s+g_s=4.

The following are actual triple constraints and require no assumption about a leximin stage:

(a_s,e_s,g_s) has value3, so c_s<=1+a_s;
(b_s,f_s,i_s) has value1, so b_s>=1-delta+a_s;
(b_s,f_s,g_s) has value4, so e_s<=b_s-c_s+f_s.

The new mixed triple (c_s,d_{s+1},h_{s+1}) has value3. Combining with b_{s+1}+d_{s+1}+h_{s+1}=3 gives the proposed coupler c_s>=b_{s+1}.

A stronger bound uses the complete array rather than just the local first-sector player. Let mu be the minimum payoff of ALL first-sector players. For every block r and every first-sector player j, the triple (j,e_r,g_r) has worth at least C_{e_r,g_r}=3 because all other pair entries are nonnegative. Thus mu+e_r+g_r>=3. Combining with the matched total c_r+e_r+g_r=4 gives c_r<=1+mu.

For an internal block 1<=s<=L-1, there are both incoming and outgoing couplers. Consequently

b_s <= c_{s-1} <= 1+mu,
c_s >= b_{s+1} >= 1-delta+a_{s+1} >= 1-delta+mu.

Subtracting cancels the same global minimum and yields b_s-c_s<=delta. The local cross budget therefore gives

e_s <= b_s-c_s+f_s <= delta+f_s <= 2*delta.

The final bound uses f_s<=delta from its small matched team and nonnegativity. It holds for every entire-core vector, so H_{e_s}<=2*delta. Both couplers are essential to this conclusion: no identical claim is made here for the first or last block.

At delta=0 this proves H_{e_s}=0. More explicitly, a=f=i=0, c_s<=1, and b_s>=1. Each coupler forces c_s=b_{s+1}=1. Every internal block therefore has b_s=c_s=1, and its cross budget forces e_s=0. These are fixed-zero players, which full leximin must skip. A recurrence that continues treating them as positive active-floor players is invalid.

## Quantitative obstruction for positive delta

For 0<delta<=3, the explicit cover above attains a common floor delta/3. No larger first floor is possible because every small matching team totals delta. Thus full leximin x satisfies x_j>=delta/3 for every player, including internal e_s. Combining with the whole-core ideal bound yields

x_{e_s}/H_{e_s} >= (delta/3)/(2*delta) = 1/6.

Consequently shrinking delta cannot lower the internal e_s ideal fraction below 1/6 in this family, regardless of the number of blocks. The intended ideal is shrinking along with the payoff. The delta=0 version makes those players fixed zero altogether. At delta=1 the independently proved long-path family attains ratios approaching 1/6, so this lower bound is sharp across these parameter choices for internal target players.

This bound does not exclude a different target coordinate, endpoint behavior, another coupler, or a redesigned local block. It does rule out the stated internal-budget extrapolation and identifies the exact incidental triples responsible. No claim about full-selector distance follows from this argument.
