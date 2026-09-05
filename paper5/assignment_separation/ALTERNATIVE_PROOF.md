# A sharp finite divergence bound in assignment-game cores

Status: conventional proof independently derived from fixed-optimal-matching potentials and reviewed during the internal campaign. The main manuscript uses the shorter minimax-witness proof, which also covers every minimax point. No novelty claim is made here; see SOURCE_AUDIT.md.

Let a standard weighted bipartite assignment game have nonempty core and positive total matching value T. Write x for its full leximin allocation (ascending sorted payoffs maximized lexicographically), and z for its full leximax-min allocation (descending sorted payoffs minimized lexicographically). Define rho = ||x-z||_1/T. Fix any optimal matching with k positive-weight edges, dropping zero-weight edges. Then

- if k=1, x=z;
- if k>=2, rho <= k/(k+1), and this bound is attained for every k.

Consequently, among assignment games on n players, the exact supremum is floor(n/2)/(floor(n/2)+1) for n>=4. For n=2 or 3 it is zero, restricting throughout to positive total value.

## 1. Fixed matching representation, including degeneracies

Number the positive matching edges (L_i,R_i), i=1,...,k, of weights s_i>0. Summing their edge core constraints and using efficiency shows that every core allocation satisfies

    u_i + v_i = s_i,

and gives every unmatched player payoff zero. This also covers agents matched only through zero-weight edges, since these may be dropped. Set v_i=s_i-u_i. A cross edge (L_i,R_j) imposes

    u_i-u_j >= w_ij-s_j.

Edges touching an unmatched player impose individual upper or lower bounds on a matched u_i. Edges between two unmatched players have nonpositive weight, since otherwise the matching could be improved. Nonnegativity adds 0<=u_i<=s_i. Hence the core is a compact difference-constraint polytope in u, with individual bounds. No exactness assumption and no unique-matching assumption is needed.

## 2. Feasible superlevel shifts

Take any two core potential vectors u and q and put d_i=u_i-q_i. For any threshold t>0, set G_t={i:d_i>=t}. At u, decreasing each coordinate indexed by G_t by the same sufficiently small epsilon>0 is feasible.

Indeed, at a tight lower difference constraint u_i-u_j=c_ij, feasibility of q gives d_i<=d_j. Thus a tight constraint can never have i in G_t and j outside G_t, the only configuration harmed by this shift. A lower bound tight at u_i also gives d_i<=0, so no tight lower bound is harmed. Upper bounds improve. All remaining constraints have positive slack, and there are finitely many of them, so a common positive epsilon exists.

If G={i:d_i=D} for D=max_i d_i>0, then increasing q on G is also feasible for sufficiently small positive epsilon. At a constraint tight at q, feasibility of u gives d_i>=d_j. Consequently a tight constraint cannot have j in G and i outside G. Tight upper bounds at q imply d_i<=0 and likewise cannot occur in G. The same argument also works for every positive superlevel set, but only the maximal set is needed below.

In full payoff coordinates, either shift transfers epsilon between the two agents of each selected matched pair. Unmatched coordinates remain fixed at zero. Interchanging the two market sides gives the corresponding statements for negative d.

## 3. Lexicographic direction tests

Suppose a feasible local direction increases every coordinate in a set P by epsilon, decreases every coordinate in a disjoint set Q by epsilon, and leaves all other coordinates fixed.

At a full leximin point a,

    min_{p in P} a_p >= min_{q in Q} a_q.

Otherwise a sufficiently small shift raises the lowest affected payoffs and decreases only strictly larger payoffs, strictly improving the full ascending sorted vector.

At a full leximax-min point b,

    max_{p in P} b_p >= max_{q in Q} b_q.

Otherwise it decreases the highest affected payoffs and increases only strictly smaller payoffs, strictly improving the full descending sorted vector. Both tests remain valid with arbitrary fixed coordinates elsewhere, including fixed zeros. This is exactly why the full lexicographic selections, rather than just the first maximin/minimax stage, are used.

## 4. Half of every feasible payoff

**Lemma.** For full leximin x and any core allocation y, x_a >= y_a/2 for every player a.

Proof. First take a matched right agent R_i with y_Ri>x_Ri. Let t=y_Ri-x_Ri=x_Li-y_Li>0 and set d_j=x_Lj-y_Lj. On G_t={j:d_j>=t}, the feasible shift at x decreases the left payoffs and increases the right payoffs. Every decreasing left payoff satisfies x_Lj=y_Lj+d_j>=t. The leximin direction test therefore gives x_Rj>=t for every j in G_t, in particular x_Ri>=t. Thus y_Ri=x_Ri+t<=2x_Ri. If y_Ri<=x_Ri the claim is immediate. Swap market sides for left agents. Unmatched agents have zero in every core allocation. QED.

Now compare x and z. Put d_i=x_Li-z_Li, D_i=|d_i|, and D_sum=sum_i D_i. Since matched pair sums are fixed,

    ||x-z||_1 = 2 D_sum.

The lemma ensures s_i>=2D_i for every matched pair: if d_i>0, x_Ri>=d_i and z_Ri=x_Ri+d_i>=2d_i; for d_i<0 use the left coordinate; the zero case is trivial.

## 5. A strict total-mass surplus from the minimax selection

Suppose D=max_i D_i>0. Swap market sides if necessary so that D=max_i d_i, and define G={i:d_i=D}. The local shift at x decreases left and increases right payoffs on G. The leximin test gives

    min_G x_L <= min_G x_R.

Because x_L=z_L+D and x_R=z_R-D on this particular set,

    min_G z_R >= min_G z_L + 2D >= 2D.

The reverse shift at z increases left and decreases right payoffs on G. The leximax-min test gives

    max_G z_L >= max_G z_R >= 2D.

Choose j in G attaining max_G z_L. Both z_Lj and z_Rj are at least 2D, so s_j>=4D. Its contribution exceeds its generic lower bound 2D_j=2D by at least 2D. Consequently

    T = sum_i s_i >= 2 D_sum + 2D
      >= 2 D_sum (1+1/k).

This proves rho=2D_sum/T<=k/(k+1).

If k=1 and D>0, the two inequalities on the singleton set would instead give z_R>=z_L+2D and z_L>=z_R, a contradiction. Hence x=z for k=1. The case D=0 is immediate for all k.

## 6. Equality construction

For k>=2 take a complete k-by-k assignment market. Give one distinguished left agent edge weight 2 to every right agent, and give each of the other k-1 left agents edge weight 1 to every right agent. Let a_i=1 for the distinguished agent and 0 otherwise, so w_ij=a_i+1.

Every perfect matching has value T=k+1. Every edge belongs to a perfect matching, so its core inequality is equality (sum that perfect matching's inequalities and use efficiency). It follows that the core is exactly

    u_i=a_i+t,   v_j=1-t,   0<=t<=1.

The smallest payoff is min(t,1-t), uniquely maximized at t=1/2. The largest is 1+t, uniquely minimized at t=0. Thus these are also the full lexicographic selections, and

    ||x-z||_1 = k,    rho = k/(k+1).

Adding isolated zero-value agents leaves both selections and the divergence unchanged. Since every matching on n players has at most floor(n/2) positive edges, this proves the stated exact n-player bound. Negative or missing edges are harmless; the equality family uses only positive integer weights in {1,2}.

## Additional structural interpretation

The half-payoff lemma is stronger than the divergence conclusion: full leximin delivers at least half of each player's maximum possible core payoff, simultaneously. The finite divergence improvement uses a maximal-displacement block and the opposite tail selection, which forces an additional matched pair mass of at least twice that displacement. The extremal family already has a one-dimensional core and constant-size integer weights.
