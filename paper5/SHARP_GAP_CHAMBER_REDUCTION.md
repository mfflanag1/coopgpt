# Fixed-dimension selector-chamber reduction

Status: candidate conventional lemma for hostile audit, 2026-08-30.  This is
part of the sharp asymptotic gap campaign.  It does not modify or strengthen
PXC151 and does not supply an asymptotic bound.

## Statement

Fix `n`.  Let `E_n` be the set of singleton-normalized exact `n`-player
games with `v(N)=1`.  There is a finite rational polyhedral refinement of
`E_n` such that on every cell both `Lmin(v)` and `Lmax(v)` are rational affine
functions of `v`.  After a further finite refinement by the signs of
`Lmin(v)_i-Lmax(v)_i`, the function

```
rho(v) = ||Lmin(v)-Lmax(v)||_1
```

is rational affine on each cell.  Therefore `s_n` is a maximum, is rational,
and can in principle be obtained by finitely many rational linear programs.

The cells are selector chambers, not merely faces of the exact-game cone.
The statement therefore does **not** reduce the maximum to exact-cone facets
or extreme rays, and it does not bound the number of lower-envelope
generators or player roles as `n` grows.

## Proof

The cone of exact games is rational polyhedral (equivalently, it is described
by the finite family of semi-balanced inequalities at fixed `n`).  If
`v in E_n`, exactness and singleton normalization imply

```
0 <= v(S) = min_{y in core(v)} y(S) <= 1
```

for every coalition `S`: every core point is nonnegative and has total one.
Thus `E_n` is a closed subset of the cube `[0,1]^(2^n)` cut out by rational
linear equalities and inequalities, hence a compact rational polytope.

Now fix an ordered partition `B_1,...,B_k` of the players that is proposed as
the complete sequence of Lmin strata.  At stage `j`, the previously exposed
blocks are fixed at levels `lambda_1,...,lambda_{j-1}` and the LP maximizes a
new common floor `lambda_j` subject to

```
y(N)=1,  y(S)>=v(S) for every S,
y_i=lambda_h for i in B_h, h<j,
y_i>=lambda_j for every player not yet fixed.
```

Choose a primal basis and a dual basis for each stage.  Primal feasibility,
dual feasibility, and equality of their objectives are rational linear
conditions in `v`, the stage levels, and the primal and dual variables.
They certify optimality without a genericity assumption.  Requiring exactly
the coordinates in `B_j` to be forced at that level can likewise be written
as a finite disjunction of rational LP optimality certificates.  There are
only finitely many ordered partitions, bases, and certificate supports.
After projecting the auxiliary certificates, the graph of the full Lmin map
is therefore a finite union of rational polyhedra.  The completed staged
program has a unique allocation, so on a refinement by bases that allocation
is the rational affine basic solution.

The Lmax argument is identical with the inequalities and stage objective
reversed.  Intersect the two finite refinements.  Finally choose, for each
player, one of the two weak signs of `x_i-z_i`; on such a sign cell,

```
rho(v)=sum_i sigma_i (x_i-z_i)
```

is rational affine.  Maximizing it on each nonempty compact rational cell is
a rational LP.  The global maximum is the largest of finitely many rational
optima, proving attainment, rationality, and finite exact computability.

Degenerate boundaries cause no gap: they are included by weak inequalities
and by at least one primal-dual optimal basis.  Different basis descriptions
may overlap, but the fully staged selector itself is unique.

## What this isolates

This lemma answers the algorithmic part only at fixed dimension.  An
asymptotic theorem needs an additional compression result—such as a bound on
the selector-chamber complexity, semi-balanced support, or role count of a
maximizer—that is uniform in `n`.  Fixed-`n` polyhedrality alone supplies none
of those bounds.

The next falsification task is precise: search for a normalized exact game
whose strict selector-separation maximum on a chosen exact-cone face occurs
at a selector-wall intersection rather than at an extreme ray of that face.
Such a witness would decisively kill the naive facet/extreme-ray reduction
while leaving the chamber theorem intact.

## Review obligations

1. Check the use of the published semi-balanced facet description of the
   exact-game cone, including its lineality/normalization conventions.
2. Expand the `forced at this stage` condition into explicit primal-dual
   certificates rather than relying on prose.
3. Check closedness at degenerate ordered partitions and continuity of the
   single-valued selector map.
4. Compare the statement with generic multiparametric lexicographic LP
   results (for example Jones--Kerrigan--Maciejowski, 2007) before making any
   novelty claim.
