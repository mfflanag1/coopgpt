# Strict chain markets: a proved dimension-independent protection theorem

5 September 2026. One bounded theory follow-up. This is a mathematical derivation, not a priority finding. The network optimization framework is classical: Held, Korte, Maßberg, Ringe and Vygen, [Clock Scheduling and Clocktree Construction for High Performance ASICs](https://www.cs.york.ac.uk/rts/docs/SIGDA-Compendium-1994-2004/papers/2003/iccad03/pdffiles/03d_4.pdf), ICCAD2003, §3.2 and Theorem3.1, explicitly maximize ascending-sorted slacks on selected arcs while retaining the other potential constraints, crediting earlier minimum-balancing work. The proof below is a self-contained chain-game consequence of that framework, not a claim to a new general slack-balancing method. Chain-specific priority remains unestablished; see the [targeted comparison](../literature/NOVELTY_CHAIN.md). No existing manuscript was changed.

## Statement

There are m players in each of three sectors. Only triples produce value, with

w_ijk = P_ij + Q_jk,   P,Q >= 0.

Let K be the entire core, T>0 the integral matching value, x the full ascending-sorted leximin payoff, and H_a=max_{y in K} y_a. Then

x_a >= H_a/3 for every player a,
||x-y||_1/T <= 4/3 for every y in K.

In particular the distance bound applies to the full descending-sorted lexicographic minimum. Both constants are sharp across this class: complete player-additive arrays are a subclass and supply the already established 1/3 ideal-share example and opposing-selector distance supremum 4/3. For distance to an arbitrary core point, 4/3 is already attained in a finite constant-weight market, including the one-team simplex. The displayed opposing-selector family approaches 4/3; this argument does not decide finite attainment for that distinct comparison.

No smaller coalition receives direct bilateral worth in this statement. Every player remains in the payoff vector, including fixed-zero coordinates. The core is a nonempty compact convex polytope: all payoffs are nonnegative with fixed finite total T, and only finitely many linear constraints occur. Full leximin therefore exists and has a unique labeled payoff vector, as can be obtained by successively fixing every coordinate forced at each optimal floor. The potential representation below is injective because the outer-sector player payoffs recover all nonanchor potentials.

## 1. Exact core representation

Choose optimal perfect matchings in P and Q. They can be joined through their middle-sector agents into a triple matching. Each triple matching projects to bilateral matchings, so this joined matching has optimal total T equal to the sum of the two bilateral optimal values. Relabel the first and third sectors to make both chosen bilateral matchings diagonal. Set s_j=P_jj+Q_jj.

Write payoffs (u,v,z) in sector order. Matching efficiency forces u_j+v_j+z_j=s_j. The entire core is exactly

u_j>=0, z_j>=0, v_j=s_j-u_j-z_j>=0,
u_i-u_j >= P_ij-P_jj for all i,j,
z_k-z_j >= Q_jk-Q_jj for all j,k.

Necessity of the last two inequalities follows from triples (i,j,j) and (j,j,k). Conversely their sum is the inequality for arbitrary triple (i,j,k). This proves equality with the full core, not merely inclusion of a convenient face. Nonemptiness also follows by adding nonnegative optimal bilateral dual payoffs at each middle player; nonnegative matrices admit such bilateral optimal duals.

## 2. A general directed-cycle certificate lemma

Consider a finite directed graph with node potentials q, one anchor potential fixed at zero. Every arc e=(tail,head) has a nonnegative slack

s_e(q)=c_e+q_tail-q_head >=0.

Some arcs are designated as player payoffs; the remaining arcs impose structural constraints. Suppose the feasible payoff set has a full leximin vector x. Fix a player arc e and let alpha=x_e. Form D from:

- every structural arc that is tight at x;
- every player arc f whose payoff x_f<=alpha.

Then D contains a directed path from head(e) to tail(e).

Proof. If there is no such path, let S be the nodes that can reach tail(e) in D, including tail(e) itself. The head of e is not in S. Set h=1 on S and h=0 outside S. Every arc a->b of D satisfies h_a>=h_b: otherwise a reaches a node that reaches tail(e), contrary to a outside S. Subtract the anchor's h value from all h values to keep the anchor fixed; potential differences do not change.

Moving q a sufficiently small positive amount in direction h increases player e, decreases no player with payoff <=alpha, and harms no tight structural constraint. All other structural constraints have positive slack, and all other player payoffs exceed alpha, so finiteness permits a common positive step that preserves feasibility and leaves any decreasing payoff above alpha. The sorted payoff vector strictly improves lexicographically. This contradicts full leximin. Therefore the path exists.

This cut argument does not require the graph to be connected: all nodes outside the backward-reachable set receive the same initial zero perturbation, and the common anchor shift preserves every difference. Choose a simple such path. Together with e it forms a simple directed cycle Z. Its structural arcs are tight at x, and all its player arcs have payoffs <=x_e. Potential differences telescope around Z. Consequently, for every feasible y,

sum_{player arcs f in Z} y_f <= sum_{f in Z} c_f
                              = sum_{player arcs f in Z} x_f.

The first inequality uses nonnegativity of the structural slacks at y; the equality uses their tightness at x. In particular, if Z contains at most r player arcs then

y_e <= r*x_e.

Zero payoffs require no separate exception: the same argument shows that a leximin-zero player belonging to such a certificate is fixed at zero throughout the feasible set.

## 3. Apply the certificate to strict chains

Introduce nodes 0, U_j, Z_j and potentials

q_0=0, q_{U_j}=u_j, q_{Z_j}=-z_j.

The three types of player arcs and their slacks are

U_j -> 0:       u_j,
0 -> Z_j:       z_j,
Z_j -> U_j:     s_j-u_j-z_j = v_j.

All structural arcs stay within one layer:

U_i -> U_j, constant P_jj-P_ij,
Z_j -> Z_k, constant Q_jj-Q_jk.

Their slacks are precisely the two difference-constraint systems in Section 1.

Every simple directed cycle containing a player arc has exactly three player arcs, one from each sector. Indeed, the only transition from the Z layer to the U layer is a middle-player arc; the only way back passes through 0, using one first-sector and one third-sector arc. A simple cycle visits 0 at most once. Structural arcs cannot change layers. This also covers a cycle initially specified through an outer-sector player arc.

The certificate lemma with r=3 now gives y_a<=3*x_a for every player and every y in K. Maximizing over y proves H_a<=3*x_a.

Finally, min(x_a,y_a)>=y_a/3. Both payoff vectors are nonnegative with total T, so

||x-y||_1 = 2*(T-sum_a min(x_a,y_a)) <= 4*T/3.

This establishes the statement for the entire core and full leximin, without deleting dummy players or replacing leximin by an arbitrary first-stage maximin optimizer.

## 4. Sharpness and research consequence

The complete player-additive family w_ijk=1+1_{i=1}+1_{j=1} lies in the chain class by taking P_ij=1+1_{i=1}+1_{j=1} and Q_jk=0. With m>=2 its entire-core calculations already in the consolidated paper give the sharp ideal fraction 1/3 and full-selector distance 4m/[3(m+2)], which tends to 4/3.

Together with the independently checked triangle-of-pair-gains example having fraction 5/18, the theorem distinguishes chain interaction from cyclic pair interaction at the 1/3 guarantee. It does not establish that cyclic interaction destroys every positive dimension-independent guarantee. It also does not show that cyclic pair-additive distance exceeds 4/3.

A concrete useful artifact is the per-player certificate: a directed cycle with one player per sector, all three leximin payoffs at most the target's, whose structural arcs are tight. This certificate certifies the target's ideal bound by an ordinary sum of inequalities. Priority review should compare this argument with classical max-min fairness for potential/slack networks and locally additive assignment markets before calling it new.
