# One weakened pair opens the core of a cyclic market

Date: 2026-09-07. Evidence: conventional proof below, with independent integer checks of retained instances. External review and novelty confirmation remain outstanding. Global bounds remain 1/3 <= S_3 <= 2/5.

## Statement

For every integer b >= 2 there is a strict full-team three-sector pair-additive market with m=4b players per sector, nonnegative pair values, original grand worth T=12b, and a nonempty entire original core, such that every original individual core maximum is 3 and

    s_3 = 4b-2,       s_3/T = 1/3 - 1/(6b).

It is obtained from the zero-subsidy market in RING_ZERO_SUBSIDY.md by lowering exactly one AB pair entry from 2 to 0. The grand worth is unchanged. Thus required frozen-ideal subsidy need not decrease when pair values decrease across original markets. Each market's ideals are computed from its own entire original core and then frozen; no ideal is recomputed during a subsidy intervention.

## Market and tree behind the cycle

Number labels 0,...,4b-1. All diagonal entries in the AB, AC, and BC matrices equal 1. Define the partial matching P by

    e_j = (j,(j+1) mod b,b+j),           0 <= j < b,
    f_j = (2b+2j,2b+2j+1,j),            0 <= j < b.

Set the three off-diagonal pairs of each P-team to (AB,AC,BC)=(2,1,2), except AB(0,1)=0. Other off-diagonal entries are zero. All displayed teams have three distinct labels. Players of each sector are distinct across P, so this is an actual partial matching, not a fractional packing.

Write z=b and e_0=(0,1,z). Call e_0 the soft team and the other 2b-1 P-teams hard teams. The soft team has worth 3; each hard team has worth 5. Deleting e_0 from the label-team incidence graph leaves z isolated and a connected tree on the other 4b-1 labels. Indeed the remaining ring teams connect labels 1,2,...,b-1,0 in a path, each with its own C leaf; each f_j attaches two new leaves to label j. Call this the main tree.

Root the main tree at any label v, assign v an arbitrary sector color k in {A,B,C}, and traverse its teams away from the root. In each team assign its two newly visited labels their own sector positions in that team. The tree property makes this well-defined. Every hard team has at least two endpoints colored in their own sector positions. Consequently every pair in a hard team has at least one such endpoint.

Let c^A be the coloring rooted at 0 with color A, and c^B that rooted at 1 with color B. Along the open ring path the first coloring assigns every hub label A, and the second assigns every hub label B: traversing from 0 toward 1 introduces the A endpoint of each ring team; traversing from 1 toward 0 introduces its B endpoint. In particular

    c^A(0)=c^A(1)=A,       c^B(0)=c^B(1)=B.

## Explicit core witnesses for every individual ideal

Use x_{s,v} for the payoff in sector s at label v. For each target coordinate (k,v) with v != z, use the main-tree coloring c rooted at v with color k, extend it by c(z)=C, and set

    x_{s,j} = 1_{s=k} + 2 * 1_{c(j)=s}.

Every label sums to 3, every coordinate is nonnegative, and x_{k,v}=3.

For targets at z, give the target sector 3 at z and the other two sectors zero. On the main labels set:

    target A:  x_{s,j} = 1_{s=A} + 1_{c^A(j)=s} + 1_{c^B(j)=s};
    target B:  x_{s,j} = 1_{s=B} + 2 * 1_{c^B(j)=s};
    target C:  x_{s,j} = 1_{s=C} + 2 * 1_{c^A(j)=s}.

These also sum to 3 at every label and attain 3 at their target. In every witness all coordinates of its target sector are at least 1.

We verify coverage of every full team; summing over disjoint teams and using nonnegativity then verifies every original coalition.

### Hard pairs and teams

A hard team receives at least four units from the coloring terms and one unit from the base sector, so receives at least 5. Its pair endpoints receive at least two coloring units: either twice one correctly colored endpoint, or at least one endpoint from each of c^A and c^B. Thus any full team containing just one hard off-diagonal pair covers that pair's value, at most 2. If it also contains a diagonal pair, its third label equals one of those endpoints. All its labels then lie in the main tree, its three sector coordinates include one base unit, and its total payoff is at least 3. This covers its total worth, at most 2+1.

### Soft pairs and team

The only soft off-diagonal pairs are AC(0,z)=1 and BC(1,z)=2. For a target on the main tree, C_z has two coloring units, and every full team includes a base unit. Hence any team with a soft pair receives at least 3, sufficient even with a diagonal pair or the second soft pair. For target C at z, C_z=3 gives the same conclusion.

For target B at z, both main endpoint labels 0 and 1, and z itself, have payoff vector (A,B,C)=(0,3,0). The soft BC pair receives 3, enough even with a diagonal pair. The soft AC pair receives zero, but every B coordinate is at least 1, covering its value 1. If a diagonal pair also occurs, its B label must be 0 or z, where its payoff is 3, covering total worth 2. The soft team receives 3.

For target A at z, labels 0 and 1 have vector (2,1,0), while z has vector (3,0,0). The soft AC pair receives 2, sufficient even with a diagonal pair. The soft BC pair receives 1 and every A coordinate is at least 1, covering its value 2. If a diagonal pair also occurs, the A label is 1 or z, giving total payoff at least 3, as required. The soft team again receives 3.

### Exhaustion of full teams

Because P is a partial matching, any two positive off-diagonal pairs sharing a player belong to the same P-team. A full team with two such pairs is therefore a P-team, already covered. Every other non-diagonal team has at most one such pair and at most one diagonal pair. Those with one off-diagonal pair were covered above. Those with no off-diagonal pair have worth at most 1 and receive at least one unit from the global target-sector lower bound. Fully diagonal teams receive exactly 3. This exhausts the possibilities.

The diagonal matching has worth 3m=12b. Every constructed witness covers all teams and has that total, upper-bounding the worth of every integral matching. Thus T=12b and all witnesses belong to the entire original core. In any core allocation, the m diagonal inequalities, each at least 3, must all be equalities because they sum to T. Nonnegativity bounds each coordinate by 3. The witnesses attain 3 separately at every coordinate; hence H_i=3 for every player.

## Exact protected allocation and matching lower bound

Give every player payoff 1, and add 2 to the A player of each hard P-team. These A players are distinct. Every hard team then receives at least 5; the soft team receives at least 3. Any other full team has worth at most 3 by the same pair classification, so the baseline suffices. This allocation covers every coalition and all frozen floors H_i/3=1. Its total is

    3m + 2(2b-1) = T + 4b-2.

Conversely, sum the original coalition constraints of the disjoint P-teams and the floor constraints of all players outside P. There are 6b such players, and

    w(P) = 5(2b-1)+3 = 10b-2.

Every protected allocation therefore totals at least (10b-2)+6b = T+4b-2. Primal and lower bound coincide, proving the formula for s_3.

## Why this matters for the next proof

The unmodified ring has s_3=0 and the same grand worth, as proved in RING_ZERO_SUBSIDY.md. Lowering one coefficient weakly decreases every original coalition worth but expands the core enough to permit all coordinate maxima to reach 3. Opening a payoff-comparison cycle can therefore have a macroscopic effect on protected claims. A cycle-opening reduction must account for this ideal expansion explicitly. It cannot rely on subsidy monotonicity under decreasing values.

This supplies a second all-size family approaching the already established one-third lower bound. It neither raises that bound nor proves a universal bound for unicyclic supports.

## Corollary: no size-independent modulus for the subsidy

Scale both the unmodified ring and the broken ring by 1/(12b), so each original grand worth is 1. Positive scaling scales the entire core, its coordinate maxima, and the subsidy by the same factor. Write v_b and v'_b for their characteristic functions, and let delta_b=1/(6b). Their pair matrices differ in exactly one entry by delta_b, so the entrywise l1 distance is delta_b.

Every integral matching uses the altered pair at most once. The difference in its worth is therefore between zero and delta_b, which gives 0 <= v_b(S)-v'_b(S) <= delta_b for every coalition S by comparing maximizing matchings. The three-player coalition e_0 has worth difference exactly delta_b. Consequently

    max_S |v_b(S)-v'_b(S)| = delta_b,
    |s_3(v_b)-s_3(v'_b)| = 1/3-delta_b,
    |s_3(v_b)-s_3(v'_b)| / delta_b = 2b-1.

Both cores remain nonempty and both grand worths equal 1. Thus no function omega(delta) tending to zero as delta tends to zero can uniformly bound subsidy differences over all finite market sizes in terms of either pair-matrix l1 distance or characteristic-function sup distance. This is a lack of a size-independent modulus, not a claim of discontinuity at any fixed market size. It rules out cycle-opening arguments that charge ideal expansion solely to the removed pair value with a universal constant.

## Free original-source comparison

Soh Kumabe and Yuichi Yoshida, [Lipschitz Continuous Allocations for Optimization Games](https://drops.dagstuhl.de/storage/00lipics/lipics-vol297-icalp2024/LIPIcs.ICALP.2024.102/LIPIcs.ICALP.2024.102.pdf), ICALP 2024, Example 3, pp. 102:3-102:4, already give bipartite assignment games whose unique core allocations move by order n under a bounded edge-weight perturbation. Their measured output is a selected allocation vector. Our corollary measures the scalar cost of protecting original coordinate maxima, keeps grand worth fixed, and uses the strict three-sector pair-additive class. That distinction requires a wider priority audit; it does not establish novelty. The general instability of assignment-core allocations is established prior work. The free original was inspected on 2026-09-07; no purchase was made.

## Reproduction and evidence scope

Run `python3 broken_ring.py` to regenerate the five retained integer certificates, then `python3 -O verify_broken_ring.py`. The latter reconstructs the matrices and matching independently of the coloring algorithm, checks every original full-team inequality for every individual core witness and protected allocation, derives the diagonal ideal upper bound, and matches the disjoint-team lower bound. Cases b=2,3,4,6,8 entail 4,465,088 full-team checks. A damaged witness is rejected. The finite checks corroborate the conventional all-size proof, rather than establishing its quantifier. No external review or novelty claim is implied.
