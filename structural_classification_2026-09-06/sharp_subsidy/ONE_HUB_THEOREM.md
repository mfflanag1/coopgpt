# A constructive one-third theorem for incidence trees with at most one degree-three label

Date: 2026-09-07. Conventional all-size proof, exact constant-dimensional construction, and independent rational certificates. Global sharp bounds remain **1/3 <= S_3 <= 2/5**; novelty and external review remain unconfirmed.

## 1. Statement and scope

Let mu be an optimal perfect diagonal matching, and P an integral partial matching. Suppose their label/P incidence graph is a nontrivial tree, and at most one diagonal label contains three players used by P. For every nonnegative three-sector pair-additive market with nonempty original entire core, define the frozen ideals H_i as in SHARP_SUBSIDY.md. Then

    3 w(P) + sum_{i unmatched by P} H_i <= 4T,
    J(M,P) <= T/3.

The construction below supplies explicit fractional deletion matchings proving the coefficient inequality for all pair values at once. This bounds the specified obstruction P, not every other packing in the same market.

Combined with the existing connected-component and replication reductions, an obstruction above one-third must have a cyclic reduced incidence component or an acyclic component with at least two degree-three labels. A degree-three label is a diagonal team whose three players are used by P; P-nodes themselves always have degree three and are not counted by this restriction.

## 2. Counts

Write r=|P|>=1, m=2r+1, h=m-r=r+1, and u=3h. Let g in {0,1} be the number of degree-three labels. Each P-team has three distinct labels, because otherwise the multigraph incidence would not be a tree.

Let L_s be the number of degree-one labels whose unique P-used player is in sector s, and put ell=L_0+L_1+L_2. Tree degree counting gives

    ell=r+g+2.

The number of unmatched sector-s players at degree-two labels is L_s-g-1, so each L_s>=g+1. Put R=ell-3=r+g-1. Except for r=1,g=0, we have ell>=4 and 0<R<=r. In the exceptional case L=(1,1,1) and R=0.

## 3. A constant-dimensional scaling lemma

For any positive integers L_0,L_1,L_2 with ell>=4, there are nonnegative rational numbers a_(s,t) for s!=t, and deficits delta_t, satisfying

    sum_{t!=s} L_t a_(s,t)=1                     for each s,
    delta_t=1-sum_{s!=t} a_(s,t) >=0,
    (R-L_s)a_(s,t) <= delta_t <= R a_(s,t),      R=ell-3.   (1)

Here t denotes the used sector of a leaf and s denotes an unmatched player at that leaf.

### Existence

For w in R^3, define

    Phi(w)=sum_t L_t log(1+sum_{s!=t} exp(w_s))-sum_s w_s.

This continuous differentiable function is coercive. One explicit argument uses log(1+sum exp)>=max(0,w_s,w_v). For a nonempty subset A of positive coordinates, the total weight of leaf types incident to A is at least |A|+1: for a singleton it is the sum of the other two positive L counts, at least two; for two or three coordinates it is ell>=4. Integrating these finite level-set inequalities over the positive coordinate heights gives

    Phi(w) >= max_s max(w_s,0) + sum_s max(-w_s,0)
           >= ||w||_infinity.

Thus Phi attains a finite minimum. At a minimizer set z_s=exp(w_s), and, for the two sectors s,v other than t, set

    delta_t=1/(1+z_s+z_v),
    a_(s,t)=z_s delta_t.

The three first-order equations are exactly the sector normalizations in (1). Summing them shows

    sum_t L_t delta_t = ell-3 = R.

Also, writing x_s=1/z_s, the sector normalization gives

    x_s=sum_{t!=s} L_t delta_t=R-L_s delta_s.

Hence R-L_s < x_s < R, and delta_t=x_s a_(s,t). This proves all inequalities in (1), initially over the reals. Strict convexity can give uniqueness of this particular nonlinear scaling, but uniqueness is not needed for the proof.

### Exact rational construction

Conditions (1) describe a nonempty bounded rational polytope in six a variables. Eliminate one a variable per sector using its normalization, leaving three variables. Nonnegativity of the six a values, the three deficits, and the twelve inequalities in (1) gives 21 affine inequalities.

A nonempty bounded polytope has a vertex, and in three dimensions a vertex can be found by choosing three independent active constraint planes. The existence argument provides a relative interior point with strict inequalities here, so the reduced polytope is full dimensional. Enumerating at most C(21,3)=1330 triples of planes, solving each 3-by-3 system over the rationals, and checking all inequalities therefore terminates with an exact feasible scaling. one_hub.py implements precisely this finite algorithm, without a numerical optimizer. The problem dimension does not grow with the number of market labels; rational bit sizes can grow with the counts.

For L=(1,1,1), use a_(s,t)=1/2 and delta_t=0 directly. These satisfy (1) with R=0.

The logarithmic minimization and rational-polytope facts are established mathematical ingredients; the claim here is their use in this specific certificate construction, not novelty of those ingredients.

## 4. Deletion rows

For a deletion row i in sector s:

- If its label has degree two, put weight one on every diagonal team except that label, and no weight elsewhere.
- Otherwise its label is a leaf with unique used sector t!=s. Write a=a_(s,t). Put weight a on every P-team and 1-a on every diagonal team except the deleted label.

For a leaf row, add its own opposite-sector pair with mass delta_t. For each leaf label used in sector s, add its opposite-sector pair with mass

    f_(s,t)=(R a_(s,t)-delta_t)/L_s.

The scaling inequalities give 0<=f_(s,t)<=a. Complete every such pair uniformly with all r unmatched sector-s players other than i.

These source players cannot coincide with a destination label: the own-root source is excluded, and a sector-s-used leaf has no unmatched sector-s player. Thus the completion always changes exactly the deletion sector.

## 5. Capacity verification

The total added opposite-pair mass in a leaf row is

    delta_t + L_s f_(s,t)=R a <= r a.

Every source player therefore receives at most a extra load. Together with its diagonal load 1-a, this respects capacity one. Other P-used players outside the deleted label have load a+(1-a)=1.

At the deleted label the opposite pair includes the unique P-used player. Its extra mass is delta_t<=1-a, because delta_t=1-a_(s,t)-a_(v,t) and the partner weight is nonnegative. At every sector-s-used destination leaf, the other two players have no P load; their diagonal load 1-a plus f_(s,t)<=a is at most one. All remaining capacities are immediate, and the deleted player is never used.

Degree-two deletion rows are simply feasible diagonal matchings with their own label removed. These cases exhaust U.

## 6. Aggregate pair coverage

For every P-team the total weight from sector-s deletion rows is sum_{t!=s}L_t a_(s,t)=1. Thus there are exactly three aggregate copies of each P-team.

The sum of all row P weights is three. Consequently aggregate diagonal mass at a degree-three label is u-3, and at a degree-two label is u-4. At a leaf used in sector t, the two excluded rows have weights a_(s,t), a_(v,t); its aggregate diagonal mass is

    u-5+a_(s,t)+a_(v,t)=u-4-delta_t.

Each pair incident to the leaf's used player receives the missing delta_t from its opposite unmatched player's own-root addition. The residual pair missing sector t receives

    sum_{v!=t} L_v f_(t,v)
      = [R sum_{v!=t}L_v a_(t,v)-sum_{v!=t}L_v delta_v]/L_t
      = delta_t.

Thus every diagonal pair receives at least u-4 copies, in addition to the three copies of every P-pair. All other pair contributions are nonnegative.

For any original core point x, a fractional deletion matching without i has worth at most T-x_i. Its value therefore bounds the original entire-core ideal by H_i<=T-value(lambda^i). Summing these inequalities and using the pair domination proves

    sum_i H_i <= uT-[(u-4)T+3w(P)] = 4T-3w(P).

No ideal was recomputed, and no original coalition worth was altered.

## 7. Exact verification and remaining direction

ONE_HUB_CERTIFICATES.json contains ten rational examples, including strongly unbalanced leaf counts (10,2,2), (2,11,3), and (4,3,12). verify_one_hub.py reconstructs their topology and counts, checks every scaling inequality, and independently verifies every deletion capacity and aggregate pair coefficient. It checks 27,514 rational entries. Six examples fall outside the earlier UNIFORM_TEMPLATE.md count condition. A damaged empty certificate must fail.

Run `python3 -O one_hub.py` to regenerate the exact certificates and `python3 -O verify_one_hub.py` to verify them. Both are included in the package build. Finite certificates corroborate the proof; the convex existence argument and constant-dimensional exact recovery establish the all-size claim.

The exploratory row-specific inverse-cut kernel passed some earlier cases but failed three larger random trees numerically. Those observations are not promoted to exact impossibility theorems. The constructive result retained here is the low-degree-three-label theorem, not a claim that the inverse-cut kernel works universally.

Trees with at least two degree-three labels and cyclic incidence patterns remain the live structural region. The global sharp constant, the complete free-original novelty comparisons, and specialist review remain unresolved.
