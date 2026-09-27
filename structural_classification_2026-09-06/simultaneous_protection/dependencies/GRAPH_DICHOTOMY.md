# Acyclicity characterizes uniform leximin-to-ideal protection

Conventional classification, independently reviewed by Claude with no load-bearing defect; exact certificates and raw-core checks pass. The required four-sector milestone was completed first in ../selective_c4/MILESTONE.md. No unconditional priority or field-level significance claim.

## Exact statement

Let G be a fixed finite connected simple graph on K>=2 sectors. Every sector has the same finite size m>=1. Each allowed edge carries an arbitrary nonnegative real m-by-m pair matrix; a zero matrix is permitted. Only complete K-sector teams are productive, their values are the sums of their edge pair values, and arbitrary coalition worth is maximum weight integral matching of contained complete teams. Restrict to positive grand worth and nonempty ENTIRE core. Keep all labeled coordinates in full ascending sorted (nominal-payoff) leximin x, and define H_i as the maximum of coordinate i on that same entire core.

For K=1 the edge-sum model has no positive-worth instance; the substantive classification is K>=2.

The greatest uniform constant satisfies
    c(G)=1/K if G is a tree;
    c(G)=0 if G contains a cycle.
For H_i=0 the inequality x_i>=c(G)H_i is automatic, and such coordinates are not removed from the optimization. In the cyclic witnesses every ideal is positive. This theorem is about an allowed interaction graph with nonnegative matrices, not a requirement that every allowed pair entry be positive.

The tree half, including all lexicographic stages and zero ideals, is the existing [strict-core clipping theorem](ALL_TREES.md), with its [full-core cut representation](TREE_CORE_AND_PATH.md). Its sharpness uses m=1 and a unit full-team simplex. We prove the cyclic half below rather than assuming graph subdivision preserves the core.

## 1. Selective edge subdivision: cover and matching transfer

Take ANY strict k-sector market of the stated kind, with an optimal perfect matching relabeled to the diagonal, worth T, and an edge joining sectors u,v with nonnegative pair matrix B(i,j). Choose D_j>=max_i B(i,j). Insert a new sector d, replace uv by ud with matrix B, and by dv with diagonal matrix D_j*1_(i=j). All other pair matrices stay unchanged. Write w0(t) for an old full team's value, with u-label i and v-label j, and let h be the new label. Then
    w1(t,h)=w0(t)-B(i,j)+B(i,h)+D_h*1_(h=j).
For any old entire-core point z, the lift (z,D) covers every new full team:
* h=j: z(t)+D_h>=w0(t)+D_h=w1(t,h).
* h!=j: z(t)+D_h>=w0(t)+D_h>=w0(t)-B(i,j)+B(i,h), using B(i,j)>=0 and D_h>=B(i,h).
The lift is nonnegative with sum T+sum D; the extended diagonal integral matching has exactly that value. Thus the new integral worth equals T+sum D, the lifted point is in the new ENTIRE core, and every extended diagonal team is tight throughout it.

If z has floor tau, set t=k*tau/(k+1) and define the shifted lift
    z'_i=z_i-t/k for each old coordinate,
    z'_d(j)=D_j+t.
Every full-team sum stays unchanged; equal sector sizes make the total change -km*(t/k)+mt=0. Old coordinates are >=tau-t/k=t, and new coordinates >=t. Thus this is a core point with floor at least t.

Now suppose an old partial matching P contains 0<=r<m teams, has value T-delta with delta>0, and its unmatched set U includes a target. Extend each team by choosing the new label equal to its v-label. The new labels are distinct, so this remains a partial matching. Assume every label j with D_j>0 occurs as a v-label in P. Then its added bonus is sum D, and its shortfall from the new grand worth stays exactly delta. Its unmatched set has (k+1)(m-r) players.

If the old floor was tau=delta/[k(m-r)], the displayed new cover attains floor t=delta/[(k+1)(m-r)]. The unmatched budget is <=delta throughout the new entire core, hence forces every unmatched coordinate to t on the ENTIRE first optimal face. The old target, which remains unmatched, consequently has full-leximin payoff t.

Suppose additionally that the target belongs to an old sector, that its diagonal team has common label j0 (in particular its v-label is j0) and value H, that an old core witness attains target H, and that D_j0=0. The new diagonal target-team value stays H and gives the same ideal upper bound. The unshifted old ideal witness lifts with target H. Thus the target's whole-core ideal stays exactly H. No equality of the entire two cores, or preservation of other ideals, is claimed or needed.

## 2. Start with the proved triangular family

Use the [symbolic source family](SOURCE_FAMILY_PROOF.md), for each q>=1:
- k=3, m=3q+1, labels L0 and O_s,L_s,R_s (1<=s<=q);
- pair entries in {0,1,2}, diagonal worth6q+1, positive core floor1/[3(q+1)];
- r=2q disjoint critical triples N_s=(O_s,R_s,L_s), E_s=(L_(s-1),L_(s-1),O_s), of total value6q;
- unmatched target c_L0, diagonal target-team value1, and a core witness giving that target1.

Use the edge B from sector a to sector c. Its only nonzero columns are Hset={O_s,L_s:1<=s<=q}; their column maxima are2. The critical partial matching uses every Hset label exactly once in sector c. Define D=2 on Hset and0 on L0 and every R_s. Then sum D=4q, all transfer hypotheses hold, delta=1, and m-r=q+1.

Subdivide this B-edge once to obtain the already reviewed C4 family. For each further subdivision, subdivide the edge still carrying the original B matrix, oriented from a to its current neighboring sector. That neighbor's labels in the extended partial matching are still exactly Hset, and the target diagonal label remains L0 with D_L0=0. Thus the hypotheses propagate at every step; this is an induction on proved cover/matching properties, not an assumed subdivision invariance.

After ell-3 subdivisions, for ANY fixed ell>=3, the support is a simple ell-cycle. It has
    T_ell(q)=6q+1+4q(ell-3),
    partial matching value T_ell(q)-1,
    unmatched cardinality ell(q+1),
    full-leximin target 1/[ell(q+1)], target ideal1.
All matrices still have entries in {0,1,2}; each cycle-edge matrix is nonzero. Every added diagonal matrix has value2 only on Hset.

For a direct floor formula, start with the old triangular floor witness z of floor tau3=1/[3(q+1)]. Let t_ell=1/[ell(q+1)]. Pay every original coordinate z_i-(ell-3)t_ell/3 and pay each inserted-sector label j the amount D_j+t_ell. This is the result of the inductive shifts, or follows by summing them; its total and every full-team sum match an unshifted iterated lift. Old coordinates are at least t_ell and the new ones at least t_ell. The target ideal witness is the original triangular ideal witness with D appended in each inserted sector.

## 3. Zero-valued added sectors and a general cyclic allowed graph

Adding a new sector with only zero interactions leaves full-team weights unchanged. An old nonnegative cover z lifts to (z,0), with unchanged total and a diagonal integral matching of that value. If z has floor tau, use z'_old=z-t/k and z'_new=t with t=k*tau/(k+1); the same team-sum, total and positivity calculation gives a core point at floor t.

Extend the critical partial matching by any r distinct labels in the new sector. Its worth and its unit shortfall are unchanged; its unmatched set gains m-r=q+1 players. Hence the whole-first-face pinning proof applies again, and the target ideal stays1 because its diagonal team retains value1 and the ideal witness extends by zero. Multiple zero sectors can be added sequentially. These are constructed witnesses and entire-core upper certificates, not an assertion that arbitrary selector coordinates are preserved.

Every connected cyclic G on K sectors contains a simple cycle of some length ell between3 and K. Relabel the ell-cycle construction onto those vertices, add the remaining K-ell sectors as above, and assign zero matrices to all other allowed edges, including any cycle chords and edges incident to the additional sectors. The full-team values therefore remain exactly those already covered. This produces, for every q>=1,
    T(q)=6q+1+4q(ell-3)>0,
    x_target/H_target = 1/[K(q+1)],   H_target=1.
There is a strictly positive core point; all sectors have3q+1 players and all pair values lie in {0,1,2}. Given any proposed c>0 choose q with K(q+1)>1/c. Its target violates c-protection. Nonnegativity trivially gives c(G)>=0, so c(G)=0. Combined with the tree theorem, this proves the classification.

## 4. The structural mechanism and its boundaries

The preserved quantity is a UNIT residual budget from an actual partial matching. Selective bonuses are fully collected by that matching, while each added sector supplies q+1 additional unmatched players. The full ascending leximin floor therefore falls, but a value-one optimal diagonal team and an explicit ideal witness keep the target ideal at1.

Pairwise incompatibility is not required. The source diagonal matching attains the row-maximum upper bound separately on A,B,C; every inserted diagonal matrix and every zero matrix has the same property. Thus the counterexamples admit simultaneously optimal pairwise diagonal matchings on every allowed edge. They do not exploit a fractional/integral worth gap.

This is not a theorem about games with productive partial-sector coalitions, normalized leximin of ratios, a selected proper core face, strictly positive entries on every allowed edge, or unequal sector sizes. No assertion of historical priority follows. Original-source limitations remain material and must be retained beside this classification.
