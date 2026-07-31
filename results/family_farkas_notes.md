# Three-game Farkas frontier

Fix a base-plus-two-arm family with edges \(b\to t_A\) and \(b\to t_B\).
For fixed \(n,A,B\), the family LP matrix is fixed; only its right-hand side
depends on the three games. Its Farkas cone is therefore the correct finite
object for the three-game theorem.

## Sensitivity reduction

Only two inequality rows contain changed worths:

- the core row for coalition \(A\) in game \(t_A\);
- the core row for coalition \(B\) in game \(t_B\).

A Farkas ray using neither row reduces to balancedness of the base after
substitution. A ray using only one changed row is already present in the
corresponding two-game family, which is feasible by assigning one endpoint
core point to both games. Therefore an infeasible three-game family requires
an extreme Farkas ray with positive weight on both changed rows.

This gives a precise finite target:

> Classify the extreme rays simultaneously sensitive to \(t_A(A)\) and
> \(t_B(B)\), and prove their right-hand-side inequalities from exactness when
> \(A\cap B=\varnothing\).

## Positive control

The known balanced, non-exact overlapping-arm obstruction at \(n=4\),
\(A=\{1,2,3\}\), \(B=\{2,3,4\}\), has exactly such a ray. Its active
inequalities, all with weight one, are

- base core: \(\{2,3\}\);
- \(t_A\) core: \(A,\{1,4\},\{2,4\}\);
- \(t_B\) core: \(\{1,3\},\{1,4\},B\);
- monotonicity: player 3 on the \(A\)-edge and player 2 on the \(B\)-edge;
- efficiency weights \((0,2,2)\).

Its stationarity matrix has nullity one, so this is an extreme ray, and its
exact Farkas right-hand side is \(-1\). This validates the sensitivity test.

## Disjoint-arm evidence

For the canonical open shape
\[
n=5,\quad A=\{1,2\},\quad B=\{3,4\},\quad R=\{5\},
\]
the new miner src/mine_family_farkas_rays.py sampled normalized cone vertices
under random and bump-focused objectives. This is discovery evidence only, not
a complete enumeration.

An independent family screen generated balanced, generally non-exact bases by
lowering arbitrary worths beneath the lower envelope of two to four common-sum
points. Both disjoint bumps were taken to the largest values certified balanced
by those points. Across 28,361 such families:

- infeasible families: 0;
- exactly boundary-slack families (within float tolerance): 4,292;
- minimum family slack: numerical \(-0.0\).

This evidence suggests a stronger statement than exact-game feasibility:
disjoint two-arm stars may be feasible for all balanced endpoints. The next
proof step is not more game sampling; it is a complete decomposition theorem
for both-sensitive Farkas rays, or a targeted extreme ray violating that
decomposition.
