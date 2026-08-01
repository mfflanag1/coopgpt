# Six-player partition-shape frontier

Shape:
\[
n=6,qquad A=\{1,2,3\},quad B=\{4,5,6\},quad R=\varnothing.
\]

This is a nonexhaustive discovery frontier. Two resumable dynamic-cut batches
produced 20 distinct exact positive-circuit orbits, comprising 441 transported
supports. Every prototype has exact nullity one and unit kernel weights. One
orbit has support 9 and the other 19 have support 10. Their orbit-size
histogram under \(S_3\times S_3\) is: three orbits of size 9, eleven of size
18, and six of size 36.

## Recoloring capacities

`src/analyze_balanced_recoloring_capacity.py` verifies exact primal and dual
capacity certificates for every orbit:

| capacity | orbits |
|---:|---:|
| \(1\) | 11 |
| \(3/4\) | 3 |
| \(2/3\) | 1 |
| \(1/2\) | 5 |

Thus nine orbits fail balanced recoloring. All nine were passed to the full
endpoint-exactness LP.

## Exactness outcome

Every one of the nine recoloring obstructions has exact optimum zero Farkas
margin and an exact rational coefficientwise dual. No exact three-game
counterexample was found. Compressing the duals into the manuscript's
two-level blocks gives the following `(total blocks, genuinely two-level
blocks)` pairs:

\[
(3,2),(8,7),(7,3),(19,18),(6,3),(9,8),(3,1),(4,2),(10,8).
\]

Two exceptions therefore admit especially short hand-proof templates with
only three blocks. The support-9 circuit uses:

- a \(t_A\) collection with coverage \(1+\mathbf1_{\{2\}}\);
- a \(t_B\) collection with coverage
  \(1+\mathbf1_{\{2,5\}}\);
- one ordinary balanced \(t_B\) collection of total two.

Their two-level exactness inequalities sum, after common-base cancellations,
to the circuit bound. A second exception uses two balanced blocks and one
genuine two-level block.

## Interpretation

Together with the \((2,2,2)\) probe, the observed subunit capacities are
\[
\frac12,\quad\frac23,\quad\frac34.
\]
Every associated recoloring failure is repaired by a two-level exactness
decomposition. The capacity ladder is not determined by the aggregate bump
multiplicities: every circuit in this \((3,3,0)\) sample has the same universal
mixture bound \(\rho_0=1/2\), while internal recoloring raises some optima to
\(2/3\) or \(3/4\). Thus the useful structural datum is the geometry of the
capacity-dual player potentials, not merely the denominator of \(\rho\). The
block count is likewise not determined by capacity—degenerate LP duals can be
much less sparse—but sparse three- and four-block representatives occur among
the exceptions.

Machine-readable evidence:

- `results/disjoint_n6_330_milp_probe30.json`;
- `results/disjoint_n6_330_milp_seeded_probe30.json`;
- `results/disjoint_n6_330_probe30_recoloring_capacity.json`;
- `results/disjoint_n6_330_seeded_probe30_recoloring_capacity.json`;
- `results/disjoint_n6_330_circuit*_exact_endpoint.json`;
- `results/disjoint_n6_330_seeded_circuit*_exact_endpoint.json`.
