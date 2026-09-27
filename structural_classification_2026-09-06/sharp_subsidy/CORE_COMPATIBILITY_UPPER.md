# Uniform improvement using actual original-core compatibility

2026-09-08 UTC. Conventional proof with exact scalar and local-module
certificates. Focused cross-model audits completed on 2026-09-20; independent specialist
review and novelty assessment remain pending. See audit_20260920/AUDIT.md.
This is the main target of the active exploratory goal, not a replacement goal.

**Theorem (internally checked; external review pending).** In the original strict three-sector nonnegative
pair-additive model, with equal finite sector sizes, nonempty original entire
core and positive ordinary matching worth T,

    1/3 <= S_3 <= 39999/100000 = 2/5 - 1/100000.           (A)

The lower bound is the existing certified family. H_i always means the maximum
in the ORIGINAL entire core. This proof changes no floor, coalition worth, or
subsidy convention. The numerical improvement is small; field-level significance
and novelty are not asserted. The substantive mechanism couples different
original-core allocations through cloning and value-weighted incidence counting.

## 1. Established reductions and notation

Use the exact replication, sparsification and component reductions of
REDUCTIONS.md. It suffices to bound

    J = w(P)+sum_{i unmatched by P} H_i/3-T

for every connected diagonal/P reduction with positive T, where P is an ordinary
partial matching and the diagonal matching is optimal. The elementary cases
P empty and h=m-|P|<=1 have nonpositive obstruction. Consider h>=2. All original and restricted core payoffs are nonnegative,
since singleton coalitions have worth zero. Every label in a nontrivial
connected component has at least one P-incidence.

Let d_j be a diagonal label's worth and k_j its number of players used by P.
Nontrivial connectedness gives k_j in {1,2,3}. Call labels with k_j=1 leaves and
those with k_j=2 or 3 internal. Put

    D=sum_{j internal}d_j, D_2=sum_{k_j=2}d_j, D_L=T-D.

Incidences, including repeated labels within a P-team, are counted with
multiplicity. Let I be the internal labels. Whenever I is nonempty, every
P-team has an internal player: otherwise its three leaf incidences form a
separate connected component. Let tau=min_{j in I}d_j/T.

If I is empty, connectedness forces one P-team on three distinct leaf labels.
Apply (4.1) with a minimum-worth label designated 0. Since d_0<=T/3,
J/T<=1/18+17/54=10/27<39999/100000. This discharges the all-leaf case.
Sections 2, 3 and 5 below assume I is nonempty.

Choose ANY three original core allocations y^s, indexed by sectors s, and put

    Q_j=sum_s(d_j-y^s_{s,j}), Q=sum_{j in I}Q_j.

Each Q_j is nonnegative by diagonal tightness. Also
sum_s H_{s,j}>=3d_j-Q_j. This is not simultaneous attainment of the ideals.

## 2. Three-core compatibility inequalities

For a P-team t, let b(t) be the minimum d_j among its internal players. Define

    B_all=sum_{t in P}b(t),
    B_3=sum_{t in P with all players internal}b(t),
    B_n=B_all-B_3,
    M_3=sum_{t in P with all players internal}sum_{j in t}d_j,
    W_3=sum_{t in P with all players internal}w(t).

The inner sum in M_3 counts incidences, including repeated labels. We have

    w(P)<=D_L+B_3+Q,             W_3<=B_3+Q.              (2.1)

For a team with a leaf, choose a sector absent among its internal players and
apply the corresponding y^s. Bound leaf payoffs by their diagonal worths. All
remaining internal payoffs have sectors other than s. For an all-internal team,
choose the sector of its minimum-worth internal player, bound that player's
payoff by b(t), and retain the other two payoffs. Summing these inequalities
counts each leaf once. For each fixed s the retained internal player payoffs
are bounded by sum_j sum_{r!=s}y^s_{r,j}=sum_j(d_j-y^s_{s,j}), because P is
player-disjoint. This proves the first inequality and, by restricting the sum
to all-internal teams, the second.

We also have

    M_3>=3B_3,                 B_n<=3D-D_2-M_3.          (2.2)

The first is immediate. For the second, bound each b(t) on a non-all-internal
team by the sum of its internal diagonal worths. Total internal incidence worth
is exactly 3D-D_2; removing all-internal teams removes M_3.

## 3. Weighted incidence counting, with cycles retained

The following bound holds for arbitrary cycles and repeated incidences:

    B_all <= 2D-D_2+min_{j in I}d_j.                     (3.1)

Remove the leaf vertices and their incidences from the connected bipartite
label/P graph. The remaining internal-label/P multigraph is connected, and each
P-node has at least one incidence. Internal-label degrees remain k_j.

For a nonempty proper subset S of internal labels, include the P-nodes all of
whose internal neighbors belong to S. Let K be their number, kappa the number
of components of this induced graph (including isolated labels in S), beta its
cycle rank, and bnd the number of incidences from S to omitted P-nodes. Counting
edges and vertices gives

    K=sum_{j in S}(k_j-1)+kappa-beta-bnd.

Connectedness of the whole internal/P graph implies bnd>=kappa: every induced
component must have an incidence to an omitted P-node on a path to a label
outside S. Therefore K<=sum_{j in S}(k_j-1). For S=I the same count instead gives
K=sum_j(k_j-1)+1-beta<=sum_j(k_j-1)+1.

Apply these bounds to S_t={j:d_j>t} and integrate over t>=0. The integral of K(t)
is B_all, and the integral of sum_{j in S_t}(k_j-1) is 2D-D_2. The extra full-set
term is integrated only for 0<=t<min_j d_j. This proves (3.1) even with arbitrary
concentration of value. It does not remove cycles or assume continuity of ideals.

## 4. A verified affine bound for a three-label component

For any nonnegative pair-additive three-label market supported on the diagonal
and P0=(1,2,0), with an optimal diagonal matching, nonempty original core,
and diagonal worths d_0,d_1,d_2 (so T=d_0+d_1+d_2),

    J(M,P0) <= T/18+(17/18)d_0.                          (4.1)

Here is an explicit weighted-team proof. For each unmatched player i, the
following row lists teams and integer multiplicities; divide every multiplicity
by 18. Sector letters identify the excluded player; teams give their three
label indices in sector order.

| Excluded player | Teams with multiplicities (all divided by 18) |
| --- | --- |
| A0 | 6(111), 6(222) |
| A2 | 1(022), 1(111), 5(120) |
| B0 | 6(111), 6(222) |
| B1 | 1(101), 3(120), 1(121), 1(122), 2(202), 1(222) |
| C1 | 2(110), 4(120), 2(222) |
| C2 | 2(011), 2(111), 4(120), 2(220) |

Each row avoids its excluded player and loads every other player by at most
1/3. Across the six rows, every pair of P0 is covered at least once, and each
pair in diagonal teams 111 and 222 at least 17/18 times. All other pair coverage
is nonnegative. For an original core point attaining H_i, that row's weighted
team worth is therefore at most (T-H_i)/3. Summing over the six excluded players
and using pair additivity gives

    2T-sum_{i not in P0}H_i/3 >= w(P0)+(17/18)(d_1+d_2).

Rearranging proves (4.1). This certificate in fact remains valid with additional
nonnegative pair entries; only its sparse case is needed here. Sector and
label permutations permit any one label to be designated 0. Zero-total
components contribute zero.

`FULL_AFFINE_MODULE.json` records these weights and their equivalent exact LP
dual; `verify_full_affine_module.py` reconstructs all 27 teams directly, without
using the compressed core formulation. It checks rational coefficient
domination with no rounding correction and rejects both an empty dual and a
removed affine term. The separate zero-boundary certificate independently
recovers the 17/18 affine coefficient from a different LP formulation.

## 5. Clone internal labels and bound the resulting components

Replace each internal label j by k_j full diagonal copies, with every copied
pair value inherited from its original players. Leave leaf labels single.
The new grand worth and entire core are

    T'=T+2D-D_2,
    C'={original core allocations with copied coordinates repeated}.

Proof: repeated diagonal teams attain T', and repeating any original core point
covers all copied teams at total T'. Conversely, each copied diagonal is tight
at every copied core point. Swapping same-sector original/copy players between
their tight diagonal teams forces equal payoffs in both directions. Restriction
therefore has total T and satisfies the original full-team inequalities. This
is selective diagonal replication; it proves the ideal identity before any
subsequent sparsification.

Assign each P-incidence at j to a different copy. P remains player-disjoint,
its worth is unchanged, and now each diagonal copy has exactly one used player.
This splits repeated-label teams as well. Sparsify to the copied diagonal and
relocated P. The grand worth remains T', and ideals weakly increase. Each
original coordinate at j gains k_j-1 unmatched copies; hence the new obstruction
J' satisfies

    J' >= J+sum_{j internal}(k_j-1)
                    [sum_s H_{s,j}/3-d_j]
       >= J-(2/3)Q.                                    (5.1)

The sparse label components are now three-label, one-P-team components. Each
component's entire-core ideals dominate the corresponding global copied ideals,
by restriction and diagonal tightness, exactly as in REDUCTIONS.md. Thus J' is
at most the sum of their local obstructions; no product-core claim is needed.

For a component with at least one leaf, apply (4.1), designating a minimum-worth
internal copy. For an all-internal component, simply use H_i<=d_label for its
six unmatched players, giving J_component<=w(t)-T_component/3. Summing gives

    J <= T/18+D/9-D_2/18+(17/18)B_n
                    +W_3-(7/18)M_3+(2/3)Q.             (5.2)

Here the non-all-internal components have total worth T'-M_3. Insert (2.1)-(2.2)
and (3.1) into (5.2). Normalize

    R=J/T, q=D/T, p=D_2/T, v=B_3/T, z=Q/T.

Two valid bounds result:

    R<=1/18+2q-p-(10/9)v+(17/18)tau+(5/3)z,             (5.3)
    R<=1/18+(53/18)q-p-3v+(5/3)z.                      (5.4)

Indeed use B_n<=2D-D_2+T tau-B_3 for the first, or
B_n<=3D-D_2-M_3 for the second; in both cases M_3>=3B_3.

Since there are two unmatched players at each leaf and one at each degree-two
label, their diagonal caps together with (2.1) also give

    R<=2/3-(5/3)q+p/3+v+z.                              (5.5)

Multiply (5.5),(5.3),(5.4) respectively by 26/47, 333/799 and 24/799 and add.
The positive coefficients sum to one; q and v cancel exactly. We obtain the
MASTER INEQUALITY, for I nonempty and any three original core points:

    R <= 37/94-(37/141)p+(61/47)z+(37/94)tau
       <=37/94+(61/47)z+(37/94)tau.                      (5.6)

This step is independently checked by exact rational coefficient identities
and an exact real-arithmetic counterexample query.

## 6. Near the old ceiling, the actual attainment witnesses make Q small

Suppose, for contradiction, that

    0<g=2/5-R<=1/100000.                                 (6.1)

Strict positivity follows from the existing finite upper correction. The
localization theorem EXTREMAL_LOCALIZATION.md and FINITE_UPPER_CORRECTION.md give,
with a=1/h, B=ell/h, x_s=L_s/h, and c the incidence cycle rank,

    a<=60g,   3/2-B<=1125g,
    (x_s-B/3)^2<=300g,    0<=c/h<=300g.                 (6.2)

These conditions imply I is nonempty. Use the original t=4/5 mixed-donor packing,
and choose each deletion witness x^i in the ORIGINAL core attaining H_i. Its
exact slack identity from CORE_SLACK_LOCALIZATION.md is

    3gT=C_player+C_team+C_pair,                           (6.3)

with all three terms nonnegative. Denote total donor budget by Gamma and the
sector transfer shortfall by Delta_s. The exact construction gives

    Gamma/h=(4/5)B-3/5-(6/5)a+(6/5)c/h,
    Delta_s/h=x_s(B-x_s)-B/5-a(x_s+B).                   (6.4)

There is no positive-part ambiguity here: (6.1)-(6.2) force

    Gamma>0, Delta_s/Gamma>=1/4,
    1/5+a < x_s < 1-a,
    |I|/h=2-B-a+c/h >=1/3.                              (6.5)

For explicit elementary bounds: B>=37/25, 11/25<=x_s<=14/25 and a<=3/5000.
The quadratic x(B-x) is increasing on this interval at the minimum permitted B,
so Delta_s/h>= (11/25)(26/25)-3/10-(3/5000)(103/50)
=0.156364>31/200. Also Gamma/h<=0.6036<31/50. This proves the ratio bound.
The remaining inequalities follow from these same intervals. The full real
domains in (6.1)-(6.2), not only these rounded intervals, are checked by SMT.

The inequality x_s<1-a in (6.5) is essential here: it ensures that
degree-two unmatched rows have full initial column capacity and hence zero
extra transfer. The inequality x_s>1/5+a gives positive leaf-row headroom. All leaf rows within a
sector have the same positive headroom, so their extra transfer is Delta_s/n_s,
where n_s is that sector's number of unmatched leaf rows. Define y^s as the
average of x^i over those n_s rows. They are original core points.

For an internal donor label j, let gamma_j be 1/5 at degree two and 6/5 at degree
three. In a sector-s leaf row the donor reduction is

    z_ij=(Delta_s/n_s) gamma_j/Gamma.

At each of the donor's OTHER two sector players the packing load is at most
1-z_ij: those players receive only their diagonal mass and, when used, their
P mass. Residual-pair completions occur at leaf labels, and donor completions
add only the sector-s donor player. The excluded label is a leaf, so cannot be
the donor. Consequently the player-capacity slack obeys

    C_player >= sum_s (Delta_s/Gamma)
                      sum_{j internal}gamma_j(d_j-y^s_{s,j})
             >= Q/20.                                  (6.6)

Thus (6.3) yields z=Q/T<=60g. This controls actual coordinate-attaining witnesses,
including markets whose degree-two labels carry disproportionate value.

The final bound in (6.5) and (6.2) give

    tau<=1/|I|<=3/h<=180g.                               (6.7)

No weight-uniformity or cycle deletion is assumed.

## 7. Contradiction and return to the original class

Insert (6.6)-(6.7) into (5.6):

    2/5-g <=37/94+(6990/47)g.

Therefore g>=3/70370>1/100000, contradicting (6.1). Every connected reduction
has R<39999/100000 (or is an elementary nonpositive case). Taking the supremum
and applying the exact fractional-packing replication reduction proves (A).
An explicit lower extremal family remains the existing one-third sequence;
this result does not establish the sharp constant.

## Verification scope and remaining review

The conventional proof above is the all-size argument. The local affine module
is supported by an exact rational LP dual covering all its nonnegative weights.
`verify_core_compatibility_upper.py --smt` checks five full-domain scalar claims
and requires UNSAT; a widened-range control must be SAT. Unknown fails closed.
The original full project checks remain required. Computational checks do not
replace the cloning, component, coarea or donor-load arguments.

The earlier Claude review of the preliminary compatibility result timed out
at 60.01 seconds; it supplied no review or approval. The final combined proof has passed the internal audit recorded in
CORE_COMPATIBILITY_AUDIT.md and the full build with --smt (exit 0). The separate
free-source comparison is in CORE_COMPATIBILITY_SOURCE_AUDIT.md; it does not
confirm novelty. On 2026-09-20 two focused Claude audits completed: cloning/counting and
donor-slack, respectively. The former identified the omitted I=empty case and
implicit hypotheses, now made explicit above; no invalidating finding remained
in their reviewed scopes after coordinator checking. These scoped model reviews
are not specialist review or proof-assistant certification. A sharper local
affine lemma and an exact limitation of the aggregate route are recorded in
audit_20260920/AFFINE_REFINEMENT.md; they do not establish the global 1/3 bound.
