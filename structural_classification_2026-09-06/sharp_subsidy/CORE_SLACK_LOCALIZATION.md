# Core compatibility and weighted localization: first exploratory result

2026-09-07 America/New_York / 2026-09-08 UTC. The bounded two-hour phase started
at 03:05:49 UTC and has its checkpoint at 05:05:49 UTC. This note records progress
inside that phase, not completion of the global goal. The target remains a
size-independent improvement below 2/5 for the full original market class, or
an exactly certified sequence approaching 2/5. Global bounds remain 1/3 to 2/5.

## 1. Exact slack identity for the existing upper-bound proof

Use REDUCTIONS.md and MIXED_DONOR_UPPER.md. Fix mu, P and unmatched set U, u=|U|.
For each i in U choose a separate ORIGINAL core allocation x^i attaining H_i.
No simultaneous attainment assumption is made. Let lambda^i be the existing
fractional deletion packing avoiding i, load l_iv<=1, team worth w(t), pair
weights a_e, and aggregate pair coverage A_e. Define

    C = sum_i sum_{v != i} (1-l_iv) x^i_v,
    F = sum_i sum_t lambda^i_t [x^i(t)-w(t)],
    E = sum_e [A_e-(u-21/5)a_mu(e)-3a_P(e)] a_e.

Here a_mu(e),a_P(e) are pair incidence counts, not monetary weights. All three
quantities are nonnegative, by player capacity, original-core coverage, and
pair domination respectively. Direct expansion gives the exact identity

    3[(2/5)T-J] = C+F+E.                                  (1)

Indeed sum_i[T-H_i-w(lambda^i)]=C+F, while
sum_i w(lambda^i)=(u-21/5)T+3w(P)+E. This is ordinary LP slack bookkeeping,
not a new general duality principle. It identifies the actual original-core
constraints that any near-extremizing sequence would have to make nearly tight.

## 2. Compatibility of three core allocations with hub value

Assume every diagonal label has P-degree one (a leaf) or three (a hub).
This section does not require acyclicity. Write d_j for its diagonal worth,
D_H for total hub worth and D_L=T-D_H for leaf worth. Let y^0,y^1,y^2 be ANY
three original core allocations and define

    Q = sum_{s=0}^2 [D_H - sum_{j hub} y^s_{s,j}] >= 0,
    B_3 = sum_{t in P, all three labels hubs} min_{j in t} d_j.

Then the following weighted compatibility inequality holds:

    w(P) <= D_L+B_3+Q.                                    (2)

Proof. For each P-team with a leaf, choose a sector s absent among its hub
players. In y^s, cap each leaf player's payoff by its diagonal worth and retain
the hub payoffs; all retained hub payoffs have sector different from s. For an
all-hub P-team, choose the sector s whose player's diagonal worth is smallest.
Cap that player's payoff by d_j and retain the other two hub payoffs. These
choices bound w(t) by leaf diagonal worths, or its contribution to B_3, plus
hub payoffs in sectors different from the selected core allocation's index.
Sum over P. Every leaf label contributes once because its P-degree is one.
For any fixed s, player-disjointness of P bounds retained hub payoffs by
sum_{j hub} sum_{r != s} y^s_{r,j}=D_H-sum_j y^s_{s,j}.
Summing over s proves (2). The y^s need not be common maximizers.

If the whole incidence multigraph is a tree, also

    B_3 <= D_H/2.                                        (3)

Proof by threshold integration. For each t>=0 keep hub labels with d_j>t and
all-hub P-teams whose three labels survive. This incidence subgraph is a forest.
If it has v surviving labels and k team nodes, 3k<=v+k, so k<=v/2. Integrating
k(t)<=v(t)/2 gives sum_team min_j d_j <= sum_hub d_j/2. This argument controls
arbitrary nonnegative weights, including concentration. It does not extend (3)
to cyclic supports merely because their unweighted cycle density is small.

## 3. Connect compatibility to the deleted-player packing

Now assume a connected incidence TREE with only leaves and b degree-three hubs,
b>=5. Counting gives h=m-|P|=2b+2 and L_s=h/2 in all three sectors. Define

    y^s = (1/h) sum_{i in U, sector(i)=s} x^i,
    e = 1/5-2/h > 0,
    k_b = eh/b = 2(b-4)/(5b).

The y^s are original core points, so (2) applies. In the original t=4/5
construction every unmatched row has extra donor transfer e, allocated equally
across the b hubs. In a sector-s deletion row, each hub's sector-s player has
load one; its other two players have load 1-e/b. Therefore the hub contribution
to C is EXACTLY

    C_H = (e/b) sum_s sum_{i in U_s}
                    [D_H-sum_{j hub}x^i_{s,j}]
        = k_b Q.                                        (4)

This follows directly from the packing coefficients and uses actual payoffs.
Combining (1), (2) and (4) gives

    3[(2/5)T-J] >= k_b [w(P)-D_L-B_3]_+.                 (5)

The retained packing is not improved here. The new information is the lower
bound on slack that its actual coordinate-attaining core allocations must leave.

## 4. A weighted restriction on possible near-extremizing trees

Normalize q=D_H/T, R=J/T, g=2/5-R. Since every unmatched player is at a leaf,
there are two such players per leaf, and H_i<=d_label. Thus

    R <= w(P)/T - 1 + (2/3)(1-q).                        (6)

Equations (3), (5) and (6) imply

    g >= [k_b/(3+k_b)] [(7/6)q-4/15]_+.                 (7)

To check the elimination, put a=(7/6)q-4/15. The bracket in (5), divided by T,
is at least a-g. Thus 3g>=k_b[a-g]_+. If a<=0, (7) is trivial; if g>=a it is
also immediate; otherwise solve (3+k_b)g>=k_b a.

Consequently, any sequence of these leaf/hub trees with J/T approaching 2/5
must have

    limsup D_H/T <= 8/35.

Here b tends to infinity by the existing finite-size correction, and k_b tends
to 2/5. If P has NO all-hub teams, B_3=0 instead gives the stronger version

    g >= [k_b/(3+k_b)] [(5/3)q-4/15]_+,
    limsup D_H/T <= 4/25.                                (8)

These are weight restrictions in a specific live class, not the desired uniform
global improvement. In particular, small hub-weight markets remain entirely
live. General near-extremizers may have degree-two labels and cycles; count
localization alone does not transfer (7) to them. No cycle-removal assertion is
made. Establishing a new bound in that remaining region is the next obligation.

## 5. Exact checks and unsuccessful computation

Four balanced branching chain supports have b=2,4,8,12 hubs and m=11,19,35,51
labels. The all-weight synthesis LP keeps a separate full-core witness for every
unmatched ideal and uses the exact sector-minimum projection from
SECTOR_MINIMUM_CORE.md. The numerical discovery optima were respectively
10/33, 6/19, 34/105 and 50/153. These are fixed-P optimization results, not an
exhaustive support classification or full-subsidy upper bound for every market
on those supports.

The stored primal examples were rounded to integer weights/payoffs at T=3m and
then verified EXACTLY against every full team. Every relevant ideal equals its
diagonal cap and has its own attaining witness. The numerical duals were rounded
to denominator 10^12, clipped to the required nonnegative sign, and checked by
reconstructing every coefficient. Residual deficits are paid explicitly using
the valid normalized variable bound [0,1] for weights, payoffs and sector minima.
The resulting rational upper bounds are slightly larger than the displayed
primal values; no exact optimality equality is claimed. All four certified
upper bounds are below 1/3.

The verifier also checks the exact slack identity, (2), (3), and the coefficient
identity (4) on these original-core witnesses. For b=2,4 the donor coefficient
is zero; these calibrate the inactive branch rather than (7). For b=8 and 12,
respectively, normalized slack decomposes as

    b=8:  C=272/4725,  F=32/945,   E=24/175;
    b=12: C=160/1989, F=448/9945,  E=8/85.

In both cases C+F+E=3(2/5-J/T) exactly. The independent checker covers 12,891,756
full-team inequalities and rejects an empty dual. These four optimization examples have no all-hub teams. Three additional
constructed markets (with one, two and three all-hub P-teams) check original
core feasibility and (2) with Q=0 and B_3>0. Uniform, varying, and concentrated
hub weights additionally calibrate (3). These finite checks supplement, and
do not replace, the conventional proofs of the general branches.

A b=16, m=67 synthesis hit its 45-second solver limit. That is inconclusive,
not a counterexample, feasible witness, or a bound. An initial attempt to
rationalize the smaller duals without residual correction failed exact residual
checks; the corrected certificates explicitly include that residual payment.

## 6. Research status and checkpoint

The substantive first-phase output is (2) coupled to (4), yielding (7)-(8).
It meets the proposed progress gate of a precisely stated compatibility
inequality with exact supporting checks. It does not complete the original
goal. The two-hour checkpoint remains in force; a continuation should now test
small hub-weight configurations and concentrated cyclic value, rather than
repeat these chain instances or optimize finite-size constants.

No novelty is asserted for these elementary consequences of original-core
constraints. Independent review and free-original source comparison remain
pending before promotion. No purchase or outreach occurred.
