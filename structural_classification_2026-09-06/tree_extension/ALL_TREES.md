# Sharp leximin protection for every strict tree market

Conventional proof, September 6, 2026. Claude independently rederived the argument and found no correctness defect; 120 exact clipping checks against raw full-team constraints pass. No priority claim. Standing model and exact tree-cut representation are in TREE_CORE_AND_PATH.md from the structural classification checkpoint: k>=2 sectors, equal finite size m>=1, nonnegative pair matrices on a connected tree, only full k-tuples productive, integral coalition worth, T>0. Core coordinates include every player, and full ascending sorted leximin is used. Ideals are maxima over that same entire core.

## Theorem

For every tree G on k vertices, c(G)=1/k. In particular c(K1,3)=1/4. Branching does not destroy size-independent protection in this model.

## A closure fact

If two vectors a,b obey all inequalities u(i)-u(j)>=c_ij, then their coordinatewise minimum obeys them too. Indeed a(i)>=a(j)+c and b(i)>=b(j)+c imply min(a(i),b(i))>=min(a(j),b(j))+c. Adding a uniform constant to every coordinate of a vector also preserves all such inequalities.

## Tree coordinates, rooted at the target sector

Root G at an arbitrary sector r. Choose edgewise optimal perfect matchings and consistently relabel so they are diagonal. This is possible on a tree and gives T=sum of the edge matching optima. For each nonroot vertex v let S_v be its descendant subtree, s_v=|S_v|, and d_vb(j) the diagonal pair value on edge v->b. For a core point p put

    U_v^p(j)=sum_(a in S_v) p_a(j)-sum_(edges internal to S_v) d_edge(j),
    U_r^p(j)=0.

The exact full-core representation is:

    U_b(i)-U_b(j)>=A_vb(j,i)-d_vb(j)         for each edge v->b,
    p_v(j)=U_v(j)-sum_(b child of v)U_b(j)+sum_(b child of v)d_vb(j)>=0.

Every feasible cut vector reconstructs an efficient nonnegative cover of all full teams; conversely every core point gives such a vector. Thus the representation preserves the entire core and ideals. Its proof is reproduced in the preceding checkpoint and is not a hypothesis about a smaller partial-coalition core.

## Clipping lemma

Let x,y be any two core points (in particular x,y>=0) and beta>=0. Define, independently on each nonroot cut layer,

    Z_v(j)=min(U_v^x(j), U_v^y(j)+s_v*beta),
    Z_r(j)=0.

Let z be the payoff reconstructed from Z. Closure under uniform translation and minimum proves every structural difference constraint for Z.

For a nonroot v and label j, if Z_v(j)=U_v^x(j), then Z_b(j)<=U_b^x(j) for each child, so z_v(j)>=x_v(j). If instead Z_v(j)=U_v^y(j)+s_v*beta, then Z_b(j)<=U_b^y(j)+s_b*beta and s_v=1+sum_b s_b, so z_v(j)>=y_v(j)+beta. These cover ties as well. Therefore

    z_v(j)>=min(x_v(j),y_v(j)+beta)>=min(x_v(j),beta)       (v != r).

At the root, each child cut is at most its x cut, hence

    z_r(j)>=x_r(j).

Each child cut is also at most its shifted y cut, and the child subtrees partition k-1 nonroot vertices. Hence

    z_r(j)>=y_r(j)-(k-1)*beta.

These bounds prove every reconstructed payoff nonnegative. The exact representation then proves z is in the full core, with no fractional/integral substitution and no loss of efficiency. This lemma does not require x to be leximin or have positive minimum payoff.

## Protection proof, including all lexicographic stages

Let x be the full leximin point and let the target player belong to sector r, at label j. Write alpha=x_r(j). If H_r(j)>k*alpha, choose an ideal-attaining core point y and a number beta with

    alpha<beta<H_r(j)/k.

Apply the clipping lemma. The target payoff satisfies

    z_r(j)>=H_r(j)-(k-1)*beta>beta>alpha.

Every other root payoff weakly increases. At a nonroot coordinate with x_i<=alpha, we have y_i+beta>=beta>alpha>=x_i; the lemma therefore gives z_i>=x_i. At a coordinate with x_i>alpha, both x_i and y_i+beta exceed alpha, so z_i>alpha. Thus no old payoff at or below alpha decreases, all old payoffs above alpha stay above alpha, and the target strictly increases.

This strictly improves the sorted payoff vector: if any entry below alpha increases, use the smallest old value at which an increase occurs; no lower entry changes and no old higher entry falls to that value. Otherwise all entries below alpha are unchanged and the number of entries equal to alpha strictly decreases. Both cases contradict full leximin. Consequently H_i<=k*x_i for every player. The argument also covers alpha=0 and shows x_i=0 implies H_i=0; zero-ideal players are not deleted.

For sharpness, take m=1 and nonnegative edge weights totaling1 (for example one edge has value1 and the others zero). The only full team has worth1 and every proper coalition has worth0. The full core is the k-player unit simplex, x_i=1/k and H_i=1. This works on every connected tree, hence c(G)=1/k.

## Scope

The theorem supplies the acyclic sufficient side for connected sector graphs. It does not prove that every cyclic G has c(G)=0. C4 still has only a finite upper bound (now5/44 in the companion certificate), so the four-sector milestone and general classification remain incomplete. Cut-variable decomposition, difference-constraint lattice closure and matching duality are established types of tools; novelty of this precise application is not yet established.
