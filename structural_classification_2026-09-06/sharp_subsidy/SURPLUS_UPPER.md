# Universal upper bound from fully used label surplus

**Historical bound:** the newer [mixed donor construction](MIXED_DONOR_UPPER.md) improves the global upper bound to 2/5. This earlier theorem and its certificates remain valid.

Date: 2026-09-07. Conventional all-size theorem, with independent rational coefficient checks. The sharp constant and novelty remain unresolved.

**Theorem.** In the original strict three-sector nonnegative pair-additive model with equal finite sector sizes, positive original integral grand worth T and nonempty original entire core,

    1/3 <= S_3 <= 5/12 = 0.4166666666... .

This improves the previous upper bound (7-4 sqrt(2))/3. The lower construction is unchanged. Original ideals H_i are frozen throughout; no subsidized-core maxima are introduced.

## 1. The same dual target, with an additional source of capacity

Use the replication, pair-deletion and connected-component reduction in REDUCTIONS.md. It suffices to fix an optimal diagonal matching mu and a partial matching P in a connected label component and bound

    J = w(P) + sum_{i in U} H_i/3 - T,

where U consists of the players unmatched by P. Write h=m-|P| and u=3h. Empty P, h=0, h=1 and trivial components have J<=0, as already proved. Below h>=2 and each diagonal label has used degree d_j in {1,2,3}.

We construct deletion fractional matchings whose aggregate pair incidence covers

    (u-17/4) a_mu(e) + 3 a_P(e)                         (1)

for every pair e. For every original core point attaining H_i, the value of a matching avoiding i is at most T-H_i. Thus (1) implies

    sum_U H_i <= (17/4)T - 3w(P),
    J <= (5/12)T.

All comparisons use nonnegative pair weights; shared mu/P pairs are counted additively. It remains to give a universal construction of (1).

## 2. Connectedness supplies donors

Let ell, n_2, n_3 count labels of degrees 1,2,3. Then

    2ell+n_2=3h.

Put k=ell-h. The connected bipartite incidence multigraph of labels and P-teams has m+|P| vertices and 3|P| edges, including repeated incidences if labels coincide within a team. Connectedness gives 3|P|>=m+|P|-1, hence m>=2h-1. Therefore

    n_3=m-ell-n_2=m+ell-3h >= k-1.                      (2)

Degree-three labels will supply additional transfers. Their sector players are all used by P, so none is ever the excluded player.

For each sector s, let L_s count degree-one labels whose unique used player is in s. Their other two players form residual pairs. Let N_s count sector-s unmatched players at degree-two labels. The remaining h-N_s unmatched players are at degree-one labels. As before,

    ell=h-N_s+L_s,   0<=L_s,N_s<=h.

Set alpha=1/h, beta=1-alpha, t=3/4 and delta=max(0,t-2alpha). For fixed s write L=L_s,N=N_s. If L=0 or delta=0, no residual-pair transfers are needed.

Otherwise give each unmatched row i the initial transfer capacity

    c_i=min(L alpha,beta)        if d_label(i)=2,
    c_i=min(L alpha,beta-delta)  if d_label(i)=1.

The demand is L delta. Its shortfall is

    D_s=max(0,L delta-sum_i c_i).                        (3)

## 3. All sector shortfalls fit the donor budget

We prove

    sum_s D_s <= (5/4)n_3,                              (4)

and that D_s>0 implies n_3>=4.

If L=h, the count identity forces N=h. Then sum c_i=h beta=h-1 and L delta<=h-1, so D_s=0. If L<=h-1, strong-row capacity equals L alpha. If the weak-row minimum also equals L alpha, total capacity is L>=L delta, again D_s=0.

In the remaining branch delta>0, weak-row capacity is beta-delta=1/4+1/h. Set x=L/h and B=ell/h=1+k/h. Then N/h=x-(B-1). Direct substitution into (3) gives

    D_s = [h(-x^2+B x-B/4) - (x+B)]_+.

Here [z]_+=max(0,z). Completing the square gives

    -x^2+B x-B/4 <= B(B-1)/4,
    D_s <= [B(k-4)/4-x]_+ <= (B/4)[k-4]_+.

Because 2ell<=3h, B<=3/2. Consequently

    sum_s D_s <= (9/8)[k-4]_+.

For k<=4 there is no shortfall. Otherwise k is an integer at least 5, so (2) yields n_3>=k-1>=4, and

    (9/8)(k-4) <= (5/4)(k-1) <= (5/4)n_3.

This proves (4). It is an all-size counting proof, not extrapolation from the certificates.

## 4. Explicit row transfers

If sum c_i>=L delta, scale every c_i by theta=L delta/sum c_i, set b_i=theta c_i and e_i=0. Then sum b_i=L delta.

If there is a shortfall, set b_i=c_i. The available headroom is q_i=L alpha-c_i. Its sum equals L-sum c_i, at least D_s because delta<=1. Distribute the shortfall explicitly:

    e_i = D_s q_i / sum_j q_j.

Thus sum_i(b_i+e_i)=L delta, b_i+e_i<=L alpha, and 0<=e_i<=1. Give every residual-pair column the same row amount (b_i+e_i)/L. Its column sum is delta and each entry is at most alpha. For degree-one rows, b_i<=beta-delta; for all rows b_i<=beta.

If L=0 or delta=0, set b_i=e_i=0. Combining sectors, sum_i e_i=sum_s D_s. If any e_i>0, there are n_3>=4 donors. Give each donor label the row reduction

    z_i=e_i/n_3.

Then z_i<=1/4<=beta. Also each donor's total reduction across all deletion rows is at most 5/4 by (4). If all e_i vanish no reductions are used, including when n_3=0.

## 5. The deletion matching and its capacities

Fix i in sector s at label j. Add the following coefficients:

1. beta on every diagonal team other than j, reduced to beta-z_i on each degree-three donor label;
2. alpha on every P-team;
3. mass beta-b_i on the opposite-sector pair at label j, and mass b_i/L on each residual-pair column. Complete each pair uniformly with the h-1 sector-s players in U other than i;
4. for every donor label d and every residual-pair column l, add mass z_i/L to the triple consisting of sector-s player d and the two residual players at l.

Steps involving L in the denominator are omitted when L=0; step 4 is omitted when e_i=0. The masses in step 3 total beta.

All coefficients are nonnegative and i is excluded. Each other unmatched sector-s player receives beta from its diagonal and alpha=beta/(h-1) from step 3. An ordinary used sector-s player receives beta+alpha=1; a donor receives beta-z_i+alpha+z_i=1. At the other sectors of donor labels the load is reduced, not increased.

The two partners at j have no diagonal load and receive at most beta from step 3 and, if used, alpha from P. A residual-column player is unmatched and outside j; its load is beta+(b_i+e_i)/L<=beta+alpha=1. Distinct columns have disjoint residual pairs. All other players receive at most their old diagonal and P loads. This proves every deletion matching feasible.

## 6. Aggregate coverage

Step 2 supplies u alpha=3 copies of each P pair.

At a degree-three label, the initial diagonal coverage is u beta=u-3. Its total donor reduction is at most 5/4, leaving u-17/4 as required. At a degree-two label there is no donor reduction; coverage is (u-1)beta=u-4+alpha, also sufficient.

At a degree-one label, initial coverage is (u-2)beta=u-5+2alpha. Its deficit is at most delta. Each of the two diagonal pairs incident to the unique used player receives at least beta-b_i>=delta from the deletion row of its opposite unmatched player. The residual pair receives its column sum delta from steps 3 and 4 combined. Thus every diagonal pair reaches (1).

This proves the theorem. A protected allocation can be recovered using the original finite primal LP; strong duality and this bound ensure its required subsidy is at most 5T/12. The formula above supplies rational deletion certificates without an optimizer. It does not replace the separate original-core ideal LPs or claim a new allocation-LP formulation.

## 7. Verification and the limit of this particular repair

`surplus_template.py` generates exact rational coefficients. `verify_surplus.py` independently checks each deletion exclusion, each individual player capacity, and every required aggregate pair coefficient. Thirteen cases include shared pairs, cycles, old families, and large junction patterns that actually use the new donor transfers. It checks 75,306 retained rational entries and three negative controls. This verifies the finite certificates; Sections 2–6 provide the universal proof.

There is a precise reason not to merely raise t in the same construction. For even h form a cyclic P on m=2h labels with

    P_j=(h+j,j,j+1 mod h)  for even j,
    P_j=(j,h+j,j+1 mod h)  for odd j.

These are disjoint actual triples. The h original cycle labels have degree two, the h added labels have degree one, and n_3=0. In sectors A and B, L=N=h/2. For a fixed t>3/4 and sufficiently large h, the initial transfer shortfall is

    D_s=h(t-3/4)-3/2 > 0,

while there are no degree-three donors. At h=32,t=4/5 the exact shortfall is 1/10; the verifier checks this. This refutes extending the same row-capacity construction solely with degree-three donors beyond t=3/4. It does not refute a stronger universal bound or the one-third conjecture.

The next live mechanism is to exploit degree-two diagonal surplus, or a different coupling of the deletion matchings. The sharp gap remains 1/3 to 5/12. No matching lower family for 5/12, global sharpness, worldwide novelty, or external specialist review is claimed. No paid consultation or outreach was used.
