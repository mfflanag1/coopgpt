# A uniform deletion construction and the branching frontier

Current global bounds and the new all-size construction are in [current universal proof](MIXED_DONOR_UPPER.md). The one-third statements below retain their stated scope.

Date: 2026-09-07. Status: **ACTIVE; S_3 is between 1/3 and 2/5.**

The construction below proves the proposed one-third obstruction bound for an infinite class of reference matchings, including every chain length. This concerns arbitrary nonnegative pair coefficients with that reference configuration, rather than just the earlier numerical family. It is not a universal upper-bound proof.

## Statement and count condition

Let mu be an optimal diagonal matching and P an ordinary partial matching. Assume each diagonal label contains at least one player used by P, as holds in a nontrivial connected reduced component. Let h=m-|P|>=2, so each sector has h unmatched players and u=|U|=3h. Write d_j in {1,2,3} for the number of used players at label j.

For sector s define:

- L_s: the number of labels with d_j=1 whose unique used player lies in sector s. Their other two players form residual diagonal pairs.
- N_s: the number of unmatched sector-s players at labels with d_j=2.

The remaining h-N_s unmatched players of sector s lie at labels with d_j=1. Assume, whenever L_s>0,

    L_s(h-2) <= N_s min(L_s,h-1)+(h-N_s).                 (C_s)

**Theorem.** Under these conditions there are explicit rational fractional deletion matchings satisfying the pair domination condition (4) of LEAF_AND_DELETION.md. Therefore

    3w(P)+sum_{i in U}H_i <= 4T,
    J(M,P) <= T/3

for every nonnegative pair-additive market with this optimal mu and nonempty original core. The ideals are always those of the original entire core. The h<2 cases are handled by the elementary zero-obstruction bounds already proved.

## 1. Construct the transfer amounts

Set alpha=1/h, beta=1-alpha, and delta=1-2alpha. For each sector s, form a matrix x_{i,l}: rows are its unmatched players i and columns are its L_s residual-pair labels l. We require

    sum_i x_{i,l}=delta;
    0<=x_{i,l}<=alpha;
    b_i:=sum_l x_{i,l}<=alpha if d_label(i)=1;
    b_i<=beta if d_label(i)=2.                             (5)

When L_s=0 there are no columns and b_i=0. Otherwise set

    c_strong=min(1,(h-1)/L_s),  c_weak=1/L_s,
    C=N_s*c_strong+(h-N_s)*c_weak,
    theta=(h-2)/C.

All these numbers are rational and C>0. Condition (C_s) is precisely C>=h-2, so 0<=theta<=1. Use x_{i,l}=alpha*theta*c_strong for rows with d_label(i)=2 and alpha*theta*c_weak for the other rows. Every column sums to delta. The entry bound and both row bounds in (5) follow directly. This is a closed formula, not an invocation of an unproved flow-existence claim.

## 2. Construct each deletion matching

Fix i in sector s, at label j. Define lambda^(i) by the following nonnegative team coefficients; add coefficients when a team appears more than once.

1. Put beta on every diagonal team except j.
2. Put alpha on every team of P.
3. Assign mass beta-b_i to the pair formed by the two other players at label j, and mass x_{i,l} to each residual pair at a column label l. Complete each such pair with every player a in U_s other than i, distributing its assigned mass equally over these h-1 choices.

The pair masses in step 3 sum to beta. Each a in U_s other than i consequently receives additional load beta/(h-1)=alpha. Player i is never used. The columns l cannot equal j: i is unmatched in sector s, while a column label has its sector-s player used by P.

## 3. Verify capacities

In sector s, every other unmatched player has load beta from its diagonal team plus alpha from step 3. Every used player has load beta from its diagonal team plus alpha from P. Thus these loads are one and the deleted player's load is zero.

In either other sector, a player at label j has no diagonal load. If used, its load is alpha+(beta-b_i)<=1; if unmatched its load is beta-b_i<=1. A player in a column's residual pair is unmatched and outside j, so has load beta+x_{i,l}<=1. Other used players have load beta+alpha=1 and other unmatched players have load beta. Distinct column labels give disjoint residual pairs. These cases exhaust all players, proving that each lambda^(i) is a feasible fractional matching without i.

## 4. Verify aggregate pair coverage

Step 2 across the u deletion matchings contributes u*alpha=3 copies of every P pair. Count this contribution separately, including when a P pair is also a diagonal pair.

At label j with k_j=3-d_j unmatched players, step 1 contributes (u-k_j)beta copies of every diagonal pair.

- If d_j=3 this equals u-3, exceeding the required u-4.
- If d_j=2 this equals u-4+alpha, again sufficient for all three pairs without any additional contribution.
- If d_j=1 this equals u-5+2alpha, leaving deficit delta for each pair. For either pair incident to the unique used player, its opposite unmatched player i supplies beta-b_i>=beta-alpha=delta in step 3. For the residual pair between the two unmatched players, the column sum in (5) supplies exactly delta.

Thus every diagonal pair receives at least u-4 copies, in addition to the three copies of P pairs. Other pair incidences are nonnegative. This proves the required coefficient domination. Applying it to nonnegative pair values and using H_i<=T-value(lambda^(i)) proves the stated theorem.

## 5. Infinite family and exact corroboration

For the chain P={(s,q+s,s-1):1<=s<q} union {(0,q,2q)}, m=2q+1 and h=q+1. The sector counts are

    (L_A,N_A)=(1,0),
    (L_B,N_B)=(h-1,h-2),
    (L_C,N_C)=(1,0).

All three conditions (C_s) hold for every q>=1. Consequently the theorem proves the one-third obstruction bound uniformly along chains for **all pair coefficients**, including heterogeneous diagonal values. It does not rely on the previously refuted discount by an arbitrary root's full diagonal worth.

The three-branch star on seven labels has h=4 and (L_s,N_s)=(2,0) in every sector, also satisfying the condition. uniform_template.py implements the closed formula without an optimizer. verify_uniform.py uses the independent coefficient checker and does not use the construction formula. For chain lengths q=1,...,12 and the star it checks 17,136 rational packing entries across 13 configurations and rejects a damaged certificate. These finite checks corroborate the all-parameter proof above.

## 6. First configuration outside the criterion

Consider m=11 and

    P={(0,1,2),(3,0,4),(5,6,0),(1,7,8),(9,10,1)}.

Labels 0 and 1 each have d_j=3; the other nine labels are leaves. Here h=6 and (L_s,N_s)=(3,0) for every sector. Condition (C_s) fails: its two sides are 12 and 6. Therefore the uniform formula does not handle this configuration. Failure of the sufficient count condition is not a counterexample to the subsidy bound or even to the deletion template itself.

An exact separate certificate does satisfy the deletion template for this configuration. DOUBLE_JUNCTION_DELETION.json contains 328 rational packing entries. The first floating solution could not be safely certified by bounded-denominator rounding. discovery/refit_deletion.py selected a 328-variable active basis numerically, solved that basis over exact rational arithmetic using SymPy's DomainMatrix, and then checked **all** inequalities, not just the basis. Its common denominator has ten digits. verify_double_junction.py independently verifies the resulting fixed configuration without SciPy, SymPy or the basis-selection code.

Floating market synthesis for this configuration attained 10/33, with equal diagonal worths. This remains discovery evidence; the exact deletion certificate proves only its one-third obstruction upper bound for all coefficients. No exact claim of optimality at 10/33 is made here.

## 7. Next mathematical step

The remaining target includes components failing (C_s), not just paths or single branching points. A useful explicit stress family has b labels of degree three arranged in a chain of junctions, m=4b+3, |P|=2b+1, h=2b+2, and (L_s,N_s)=(b+1,0). Condition (C_s) holds for b=1 and fails for every b>=2. The first b=2 case now has an exact separate certificate.

To extend the current construction, it must use the available coverage on degree-three labels to support additional residual-pair coverage, while preserving every deletion matching's capacities. Merely asserting that a capacity count is sufficient would leave the main lemma unproved. A uniform certificate for this family, followed by general connected configurations, or a certified market above one-third remains the substantive objective.

discovery/junction_probe.py explicitly constructs this stress family. For b=3, a fixed-obstruction floating LP returned approximately 14/45 on 15 labels. This is additional discovery evidence only; it is neither an exact optimum certificate nor a proof for all b.

The worldwide novelty audit and external review remain incomplete. Equal-treatment, LP-duality and subsidy concepts are established ingredients as documented in the existing source notes. No field-level breakthrough is claimed, and no paid consultation, purchase or outreach occurred.
