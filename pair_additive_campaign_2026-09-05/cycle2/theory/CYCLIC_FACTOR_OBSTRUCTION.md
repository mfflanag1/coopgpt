# Cyclic pair gains: exact obstruction to bilateral factorization

5 September 2026. Bounded theory cycle, scratch only. This identifies a precise obstruction; it does not prove a universal fairness constant or an amplification family. The difference-constraint duality is standard and is not a novelty claim.

## 1. What factorization would mean

Let p=(u,v,z) be a full strict-triple core vector for w_ijk=A_ij+B_ik+C_jk. Ask whether p can be split among its incident bilateral interactions so that each pair component separately covers its pair values. Components are allowed to be real, rather than imposing nonnegativity and silently strengthening the task.

Write the A components as alpha_i,beta_j, and the B component at sector3 as gamma_k. The other components are forced by actual player payoff preservation:

sector1: A component alpha_i; B component u_i-alpha_i;
sector2: A component beta_j; C component v_j-beta_j;
sector3: B component gamma_k; C component z_k-gamma_k.

The desired pair covers are

alpha_i+beta_j >= A_ij,
u_i-alpha_i+gamma_k >= B_ik,
v_j-beta_j+z_k-gamma_k >= C_jk.

These conditions preserve the original labeled payoff vector exactly. They are stronger than the strict-triple core inequalities; the following lemma characterizes the difference.

## 2. Exact directed-cycle lemma

Set a_i=alpha_i, b_j=-beta_j, c_k=gamma_k. Form a directed graph with three layers I,J,K and arcs/costs

I_i -> J_j:  -A_ij,
J_j -> K_k:  v_j+z_k-C_jk,
K_k -> I_i:  u_i-B_ik.

Bilateral factorization of p exists if and only if this graph has no negative directed cycle.

Proof. Each pair-cover inequality is exactly a difference constraint potential(head)-potential(tail)<=cost on its displayed arc. Finite difference constraints are feasible exactly when every directed cycle has nonnegative cost: necessity follows by telescoping; sufficiency follows from shortest-path potentials after adjoining a source with zero-cost arcs to all nodes. The graph and its variables are finite, and disconnected components present no difficulty.

For a three-arc cycle I_i->J_j->K_k->I_i, its cost is

u_i+v_j+z_k-(A_ij+B_ik+C_jk),

precisely the original triple slack. Thus strict-core feasibility certifies all three-arc cycles but does not certify longer cycles.

A simple cycle has length 3r and takes the form

I_i1 -> J_j1 -> K_k1 -> I_i2 -> ... -> J_jr -> K_kr -> I_i1.

Its cost is

sum_l (u_il+v_jl+z_kl)
 - sum_l [A_il,jl + C_jl,kl + B_i(l+1),kl],

where i(r+1)=i1. The player terms count each player on the cycle exactly once. The pair terms need not combine into r feasible triples with those same pair values. This is the exact failure of importing the chain proof: the third pair interaction closes a directed cycle of factor constraints, and strict-core inequalities control triangles, rather than every cycle of this factor graph.

## 3. Frustration supplies a certified negative cycle

Let T_A,T_B,T_C be the optimal perfect-matching values of the three pair matrices, and let Delta=T_A+T_B+T_C-T. Projection of any triple matching gives Delta>=0.

Choose three optimal pair matchings and orient them I->J->K->I as above. Their union is a disjoint union of directed cycles. Every player occurs exactly once, so the sum of their cycle costs equals

sum_i p_i - (T_A+T_B+T_C) = -Delta.

Consequently, if Delta>0, every strict-core vector has a negative factor cycle and admits no such bilateral factorization, even allowing negative component payoffs. This is stronger than merely saying that a convenient composition proof has not been found.

If Delta=0, this particular uniform cover of cycles has total cost zero. It does not by itself inspect all cycles on smaller subsets. Therefore a proof for the Delta=0 class still needs the nonnegativity of every cycle, or an additional argument showing that core constraints and efficiency imply it. No such implication is asserted here.

The reduced 5/18 witness has (T_A,T_B,T_C,T)=(3,2,4,8), so Delta=1. Thus every one of its core vectors is outside the factorized class. This explains why the successful strict-chain difference-constraint proof cannot extend by simply adding a third bilateral subsystem.

## 4. Negative cycles alone do not imply unfairness

Take two players in each sector and let A,B,C have entries 1 when their two indices differ and 0 when they agree. Every nonconstant binary triple has value 2, while the two constant triples have value 0. A complementary pair of nonconstant triples gives T=4; p_i=2/3 for every player covers all triples and has total4, and therefore is full leximin.

The pair optimal values are all2, giving Delta=2. The three opposite-index pair matchings form a six-arc cycle of cost -2. Nevertheless leximin is exactly uniform. Accordingly neither a negative factor cycle nor positive Delta is itself a fairness counterexample mechanism.

A small direct verification is sufficient: the eight triple values are 0 or2, and every nonnegative allocation of total4 has minimum at most2/3. Uniform payoffs attain that floor uniquely.

## 5. Precise remaining amplification question

The reduced example's crossed low-payoff budget is a genuine fairness bottleneck. The present factor graph identifies an independent structural source of incompatibility. To turn these into an amplification family, one must make a negative-cycle interaction participate in successive tight leximin budgets while preserving an explicit large coordinate-ideal witness. Adding a block creates whole slices of incidental triples; their inequalities can reduce the target ideal and negate the putative gain.

A viable next proof must show either:

(a) a bound on the total loss obtainable from all such critical budgets, using more than simple existence of negative cycles; or
(b) a two-block composition that keeps every new triangle slack nonnegative for the entire claimed core and ideal witness, and whose full lexicographic stages produce a genuine multiplicative loss.

The current cycle supplies no proof of (a) or (b). It rules out an incorrect factorization route exactly, provides an explicit cycle certificate of that obstruction, and keeps incompatibility distinct from fairness failure. No broad parameter search was run in this theory lane.
