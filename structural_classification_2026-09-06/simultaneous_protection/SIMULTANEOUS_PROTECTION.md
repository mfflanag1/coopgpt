# Acyclicity and simultaneous protection of individual core maxima

7 September 2026. Conventional proof and reproducible certificates; historical priority and external specialist acceptance are not established.

## 1. Statement and quantifiers

Fix a connected simple allowed sector graph G on K≥2 vertices. Each sector has m≥1 agents, and every edge carries a nonnegative m×m pair matrix (zero matrices allowed). Only full K-sector teams are productive. Their values add the pair values; coalition worth is the maximum weight integral matching of contained full teams. Consider only positive grand worth and nonempty entire core C. Write H_i=max_{x∈C}x_i and

    rho(M)=max_{x∈C} min_{i:H_i>0} x_i/H_i,
    R(G)=inf_{m, admissible matrices} rho(M).

**Theorem.** R(G)=1/K for trees, and R(G)=0 for cyclic G. Thus cycles can preclude any positive size-independent simultaneous protection guarantee, regardless of which core selection rule is used.

For the explicit triangular family below, with m=3q+1 and q≥1,

    rho(M_q)=1/(2q+3).

The family uses only pair entries {0,1,2}, has grand worth 6q+1, and contains a strictly positive core point. Its entire core is affinely isomorphic to a simplex of dimension 4q+2. The statement does not assert that one fixed player is poorly paid in every core allocation: the poorly protected player may depend on the selected allocation. Randomizing among core allocations cannot improve the guarantee in expected payoffs, because their mean is again in the convex core.

## 2. Elementary benchmarks and an upper certificate

For any nonnegative compact core with n_+ positive ideals, average one maximizer of each positive coordinate. This produces a core allocation with x_i≥H_i/n_+, proving rho≥1/n_+>0 for each finite market. The theorem concerns the infimum over growing sector sizes; it does not claim rho=0 in a finite market.

If P is any disjoint partial matching, U its unmatched players, and delta=T-w(P), core inequalities and efficiency give

    sum_{i∈U} x_i ≤ delta.

Consequently, if sum_{i∈U}H_i>0,

    rho(M) ≤ delta / sum_{i∈U}H_i.                 (B)

This is a dual certificate: weight each matching-team inequality and efficiency by 1/sum_U H, and sum the normalized-floor inequalities over U. No optimization output is needed to verify it. Lower bounds on individual H_i also suffice for a possibly weaker upper certificate.

## 3. The triangle matrices

Labels are L_0 and O_s,L_s,R_s (1≤s≤q). There are sectors a,b,c. The nonzero entries of A (a,b), B (a,c), C (b,c) are:

- A(O_s,O_s)=A(O_s,R_s)=2;
- B(O_s,O_s)=B(O_s,L_s)=2;
- C(L_s,L_s)=1 for 0≤s≤q;
- C(R_s,R_s)=C(R_s,L_s)=C(L_{s-1},O_s)=1 for 1≤s≤q.

All other entries are zero. The diagonal triples have values 1 on L/R labels and 4 on O labels, summing to T=6q+1. A baseline cover pays a_O=4, b_L=b_R=1 and all other coordinates zero. For a weak (L/R) a-player only a C edge can produce value. For a_O with at most one positive A/B edge, its payoff 4 covers value at most 3. With both positive edges the four (b,c) choices (O,O),(O,L),(R,O),(R,L) have values 4,4,4,5 and baseline payoff sums 4,4,5,5. Thus the baseline covers every triple. The matching/cover sandwich proves the integral worth is exactly T, and every diagonal triple is tight throughout C.

## 4. An exact representation of the entire core

Every weak a-player has identical productivity. For weak labels t,u, replacing a_u by a_t in u's diagonal triple preserves its value. Comparing the resulting core inequality with diagonal tightness gives p_{a_t}≥p_{a_u}; reverse t,u. All weak a-payoffs therefore equal a common alpha≥0.

Define

    l_s=p_{c_Ls} (0≤s≤q),
    r_s=p_{c_Rs}, d_s=p_{b_Os}, o_s=p_{c_Os} (1≤s≤q).

Diagonal equalities imply

    p_{b_Ls}=1-alpha-l_s,
    p_{b_Rs}=1-alpha-r_s,
    p_{a_Os}=4-d_s-o_s.

The triples E_s=(a_L(s-1),b_L(s-1),c_Os), of value 1, and N_s=(a_Os,b_Rs,c_Ls), of value 5, imply

    o_s≥l_{s-1},
    l_s≥alpha+r_s+d_s+o_s.

Set e_s=o_s-l_{s-1}, f_s=l_s-alpha-r_s-d_s-o_s, and h=p_{b_Lq}. Necessarily all alpha,l_0,d_s,r_s,e_s,f_s,h are nonnegative and

    (q+1)alpha + l_0 + sum_s(d_s+r_s+e_s+f_s) + h = 1.    (S)

Conversely, take any nonnegative parameters satisfying (S), and reconstruct recursively

    o_s=l_{s-1}+e_s,
    l_s=l_{s-1}+alpha+d_s+r_s+e_s+f_s,

then use the displayed diagonal formulas. We prove that every reconstructed vector is in the entire core.

The sequence l_s is nondecreasing and l_q=1-alpha-h≤1-alpha. Hence all b_L are nonnegative. Also r_s≤l_s-alpha≤1-2alpha, so b_R is nonnegative. Since d_s+o_s≤l_s-alpha-r_s≤1, a_O≥3. Every remaining coordinate is visibly nonnegative. Diagonal sums give efficiency.

For a weak a-player, the positive C-edge cases (L_s,L_s), (R_s,R_s), (R_s,L_s), (L_{s-1},O_s) have total payoffs respectively

    1, 1, 1+l_s-r_s, 1+o_s-l_{s-1},

all at least 1. Zero-C cases follow from nonnegativity. For a_Os with at most one positive A/B edge, the full value is at most 3 and a_Os≥3 covers it. With both positive edges:

| (b,c) | value | payoff sum |
|---|---:|---|
| (O_s,O_s) | 4 | 4 |
| (O_s,L_s) | 4 | 4+l_s-o_s ≥4 |
| (R_s,O_s) | 4 | 5-alpha-r_s-d_s ≥4 |
| (R_s,L_s) | 5 | 5+l_s-alpha-r_s-d_s-o_s ≥5 |

For the third row alpha+r_s+d_s≤l_s≤1. This exhausts every full triple. Summing these covers over any coalition matching and retaining nonnegative unmatched payoffs proves every coalition inequality. Thus (S) characterizes the entire core, not a selected face. Reconstruction is injective because all parameters are recovered from the displayed payoff differences. There are 4q+3 nonnegative barycentric coordinates after scaling alpha by q+1, hence the claimed simplex dimension.

## 5. All individual ideals and the exact optimum

The representation proves

    H_{a_Ls}=H_{a_Rs}=1/(q+1),
    H_{a_Os}=4,
    H_{b_t}=H_{c_t}=1 for every label t.           (H)

For attainment of weak a-maxima choose alpha=1/(q+1) and all other independent parameters zero. The baseline h=1 attains all a_O maxima and all b_L,b_R maxima. Choosing d_s=1 attains b_Os=1; choosing r_s=1 attains c_Rs=1. Choosing l_0=1 attains every c_L,c_O maximum. The upper bounds follow from (S), the reconstructed formulas, and diagonal tightness. These are separate core witnesses; simultaneous attainment is not assumed.

The disjoint partial matching formed by all E_s and N_s has value 6q. Its unmatched set is

    U={a_Lq,b_Lq,c_L0} ∪ {a_Rs,b_Os,c_Rs:1≤s≤q}.

It has q+1 weak a-players, each with ideal 1/(q+1), and 2q+2 b/c players, each with ideal 1. Thus sum_U H=2q+3. Certificate (B) gives rho≤1/(2q+3).

For the matching lower bound set t=1/(2q+3), alpha=t/(q+1), l_0=h=t, d_s=r_s=t, e_s=f_s=0. Equation (S) holds exactly. All b/c coordinates are ≥t: l_s≥t, o_s≥t, d_s=r_s=t, b_Ls≥h=t, and b_Rs=1-alpha-t≥t. Weak a-coordinates are tH_i. Strong a-coordinates are ≥3≥4t=tH_i. This is a strictly positive core point with all coordinates ≥tH_i. Therefore rho=t exactly.

For q=1 this is a 12-player, three-sector counterexample to the proposed 1/K bound: rho=1/5<1/3. For q→∞ even the best stable allocation has vanishing simultaneous protection.

## 6. Every fixed cyclic graph

Use the already proved selective-subdivision construction in dependencies/GRAPH_DICHOTOMY.md, Sections 1–3. Its hypotheses apply to the same E/N partial matching: the subdivision bonuses are 2 on O_s,L_s labels, zero elsewhere, and the partial matching consumes every positive bonus label. Thus each subdivision preserves the unit shortfall. Every old core point lifts with its original coordinates unchanged and bonus coordinates appended. In particular, every original b/c player in U still has individual ideal at least 1 in the enlarged entire core. The enlarged partial matching still leaves those original players unmatched.

For any chosen simple cycle of length ell, repeated subdivision yields the ell-cycle with the same unit unmatched budget. Appending zero-interaction sectors preserves the same properties. Assigning zero matrices to the other allowed edges embeds this construction in any connected cyclic G with K sectors. The 2q+2 original b/c players in U alone imply

    rho(M_{G,q})≤1/(2q+2)→0.

The earlier positive floor witness remains valid, so the enlarged core is nonempty and contains a strictly positive point. All pair entries remain in {0,1,2}. We do not claim that all old ideals are unchanged or that this upper bound is the exact optimum for longer cycles. Their lower bound of 1, and the matching budget, suffice.

## 7. Trees and sharpness

The existing entire-core tree clipping theorem in dependencies/ALL_TREES.md gives a nominal-leximin point with x_i≥H_i/K, so rho≥1/K for every tree market. To show sharpness, take m=1 and nonnegative edge values summing to 1 on any tree. Every proper player coalition omits a sector and has worth zero. The core is the K-player unit simplex, each H_i=1, and rho=1/K. Hence R(G)=1/K. For K=1 the pure edge-sum model has no positive-worth instance and is excluded.

## 8. What is and is not new in this campaign

The matrices, tree protection proof, and subdivision gadget were established in the preceding project campaign. The new deductions here are the entire-core simplex representation for this family, its complete ideals and exact best simultaneous protection, and the resulting impossibility for every core selection on cyclic graphs. This is a strengthening of the same construction, not a second independently discovered counterexample family.

The old nominal target has a point achieving its ideal; here every chosen core point has some poorly protected player. These quantifiers must not be interchanged. The result is specific to strict productive full teams, arbitrary nonnegative pair matrices, equal sector sizes, and the entire core. It is not an impossibility of all meanings of fairness, and it does not claim a finite-size sharp bound over all markets.

The source audit in SOURCE_STATUS.md credits the bilateral half-optimal core and retains original-source access gaps. Free-only work excludes a separately paid model consultation. The proof is not presented as externally reviewed or as an established field-level breakthrough.
