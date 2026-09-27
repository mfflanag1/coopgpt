# An all-size cyclic pair-additive family with ideal fraction tending to 1/6

5 September 2026. Conventional proof of the construction identified by the bounded coupling search. Priority remains unassessed. This is progress on the extremal question, not a proof that every positive dimension-independent guarantee fails.

## Family and statement

For any integer q>=3, take q blocks indexed s=0,...,q-1, each with players

(a_s,b_s,c_s; d_s,e_s,f_s; g_s,h_s,i_s).

The three sectors thus each contain 3q players. Within each block place the pair matrices

A=[[0,0,0],[2,0,1],[0,1,0]],
B=[[0,0,1],[1,0,0],[0,0,0]],
C=[[0,1,0],[3,0,0],[2,0,0]].

All pair entries between blocks are zero, except A_{c_s,d_{s+1}}=2 for s=0,...,q-2. Each complete strict triple has worth A_ij+B_ik+C_jk, and a coalition receives the maximum worth of disjoint triples within it.

The integral value is T=8q and the entire core is nonempty. If x is its full leximin payoff, then for every s=1,...,q-1,

x_{e_s}=1/3+1/q,
H_{e_s}=max_{y in core} y_{e_s}=2.

Consequently

x_{e_s}/H_{e_s}=1/6+1/(2q) -> 1/6.

Every player counts: there are 9q players. The construction has 9q-1 positive pair entries, with pair values in {1,2,3}; its induced triple values are at most4. This theorem makes no assertion about full-selector distance tending to two.

## 1. Matching and a cover attaining the relevant floor

In every block the matching triples (a,f,i), (b,d,h), (c,e,g) have values1,3,4. Together they give an integral matching of value8q.

Let t=1/3+1/q. Define a payoff vector p as follows. Set a_s=f_s=i_s=1/3 in every block. In block0 set

(b_0,c_0,d_0,e_0,g_0,h_0)=(5/3,4/3,2/3,2/3,2,2/3).

For s>=1 set

c_s=4/3-s/q,
e_s=t,
b_s=4/3-(s-1)/q=c_{s-1},
d_s=h_s=(3-b_s)/2,
g_s=4-c_s-t.

All nonanchor payoffs are at least t when q>=3. The three matching totals in every block are1,3,4, so p totals8q.

We check every type of triple, rather than only the intended matching and coupling constraints.

### Local triples

For one block with a=f=i=1/3 and matching equalities b+d+h=3, c+e+g=4, the following sufficient conditions cover all27 local triples:

b,c,d,e,g,h >=1/3,
c<=4/3, h<=4/3, g>=4/3, e<=7/3,
b>=c+e-1/3.

To verify sufficiency directly, most nonzero team values are already bounded by summing the coordinate lower bounds. The potentially restrictive slacks reduce to

4/3-c, 4/3-h, g-4/3, 7/3-e,
b-c-e+1/3, b-c, g-h,
d-1/3, e-1/3, b-1/3, c+e-2/3,
d+h-2/3, b+h-2/3, c+e+h-1, c+d+h-1,

or nonnegative payoff sums. All are nonnegative under the displayed conditions: b-c>=e-1/3 and g-h>=0. The supplied p satisfies these inequalities. In particular b=c+e-1/3 in every block, c_0=4/3, e<=2/3, and for s>=1 we have g_s>=7/3 and h_s<4/3.

### Nonlocal triples without a coupler

Such a triple contains at most one positive pair entry. Every within-block pair's two payoffs under p are at least its value minus1/3, and its third player has payoff at least1/3. Explicitly, the only inequalities needed for positive pairs are

b+d>=5/3 for A_bd=2,
b+f>=2/3 and c+e>=2/3 for A_bf=A_ce=1,
a+i=2/3 for B_ai=1,
b+g>=2/3 for B_bg=1,
d+h>=2/3 for C_dh=1,
e+g>=8/3 for C_eg=3,
f+g>=5/3 for C_fg=2.

They all follow from the supplied formulas; b+d=3-h and e+g=4-c are useful identities. Hence every such mixed triple is covered.

### Triples containing a coupler

The coupler uses (c_s,d_{s+1}) and has pair value2. The row B_{c_s,*} is identically zero. The only possible additional positive pair entry is C_{d_{s+1},h_{s+1}}=1. For that third player,

c_s+d_{s+1}+h_{s+1}=b_{s+1}+d_{s+1}+h_{s+1}=3.

For every other third player, its payoff is at least1/3 and

c_s+d_{s+1}=(3+c_s)/2 >=5/3.

Thus all coupler triples are covered. The inequality uses c_s>=1/3.

This exhausts all triples. Summing a cover over any matching bounds its value by8q, so the displayed matching is optimal and p belongs to the entire core. Coalition inequalities follow by summing over any coalition's matching; no smaller direct-production coalitions have been introduced.

## 2. The full leximin coordinates are forced

Every core allocation has the matching equalities

a_s+f_s+i_s=1,
b_s+d_s+h_s=3,
c_s+e_s+g_s=4.

The first common floor is at most1/3; the cover above attains it. Thus the first leximin stage fixes a_s=f_s=i_s=1/3 for every block. For q>=3 the same cover makes every other payoff strictly greater than1/3, so no other coordinate is forced at that initial level.

On this remaining face, local triple (a_0,e_0,g_0), of value3, implies c_0<=4/3. The local triple (b_s,f_s,g_s), of value4, gives

b_s>=c_s+e_s-1/3.

The mixed triple (c_{s-1},d_s,h_s), of value3, and matching equality b_s+d_s+h_s=3 give c_{s-1}>=b_s. Hence for s=1,...,q-1,

c_{s-1}>=c_s+e_s-1/3.

If all remaining payoffs are at least eta, summing yields

4/3 >= c_0 >= c_{q-1}+sum_{s=1}^{q-1}(e_s-1/3)
                 >= q*eta-(q-1)/3.

Therefore eta<=1/3+1/q=t. The cover in Section1 attains this value, so it is the exact second leximin floor. Equality in the displayed sum forces every e_s for s>=1, and c_{q-1}, to equal t throughout the second optimal face. Subsequent lexicographic stages cannot change them. This proves x_{e_s}=t for the full selector without asserting that every coordinate of the displayed cover is already the final leximin payoff.

## 3. A whole-core upper bound on the ideal

Let y be any core vector and let mu be the minimum payoff of all first-sector players. For any block r, every triple consisting of an arbitrary first-sector player, e_r, and g_r has worth at least C_{e_r,g_r}=3 because the other pair terms are nonnegative. Thus

mu+e_r+g_r>=3,

and matching equality c_r+e_r+g_r=4 implies c_r<=1+mu.

For s>=1 the incoming coupling gives b_s<=c_{s-1}<=1+mu. The local cross triple gives e_s<=b_s-c_s+f_s. Since c_s>=mu and f_s<=1 by the small matching equality and nonnegativity,

e_s<=1+f_s<=2.

This holds on the entire core, proving H_{e_s}<=2.

## 4. An entire-core witness attaining two

Fix any target s>=1. Use the following full block vectors before, at, and after that target:

P=(0,1,1;1,1,1;2,1,0) for each r<s,
E=(0,1,0;1,2,1;2,1,0) for r=s,
D=(0,0,0;2,1,1;3,1,0) for each r>s.

Every block has matching totals1,3,4 and the target has e_s=2. Each of P,E,D covers all27 local triples by direct substitution.

For mixed triples not involving a coupler, every positive pair is already covered by its two payoffs except B_{a_r,i_r}=1. Those two payoffs are zero, but every second-sector player in every block has payoff at least1. Thus those mixed triples are covered as well.

For couplers, prefix-to-prefix or prefix-to-target has c_prev+d_next=1+1=2. Target-to-suffix and suffix-to-suffix have c_prev+d_next=0+2=2. In every case h_next=1, covering the one possible additional C entry in the triple with h_next. Since B_{c_prev,*}=0, there are no other extra positive pair terms.

This is a cover of total8q and therefore an entire-core point, with e_s=2. Combining with Section3 proves H_{e_s}=2.

## Interpretation and remaining task

The all-size family improves the proved upper bound on the best possible individual guarantee in the general pair-additive class to1/6. It remains consistent with a positive dimension-independent guarantee. Its mechanism is a sequence of saturated budgets, and its exact ideal witnesses account for all incidental mixed triples. The earlier proposed ideal3 witnesses failed those mixed inequalities and are not used here. No maximal-distance or field-breakthrough claim follows from this result.
