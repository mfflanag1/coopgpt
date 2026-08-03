# Six-player (3,2,1) circuit frontier

For
\[
n=6,qquad A=\{1,2,3\},\quad B=\{4,5\},\quad R=\{6\},
\]
the first dynamic-cut batch examined 27 numerical supports before the final
MILP time limit. It extracted seven distinct exact unit-circuit orbits: six at
support 10 and one at support 11. Their \(S_3\times S_2\) orbits comprise 78
transported supports (six orbits of size 12 and one of size 6). This is a
nonexhaustive discovery frontier.

Six circuits have exactly certified recoloring capacity one. The sole
recoloring obstruction has capacity \(2/3\), equal to the universal two-color
mixture lower bound \(\rho_0\). Its endpoint-exactness LP has exact optimum
zero Farkas margin and a coefficientwise rational dual. The dual compresses
into seven two-level blocks: two balanced and five genuinely two-level.
Therefore every orbit currently exposed in this geometry is harmless on exact
endpoints.

Evidence:

- `results/disjoint_n6_321_milp_probe30.json`;
- `results/disjoint_n6_321_probe30_recoloring_capacity.json`;
- `results/disjoint_n6_321_circuit5_exact_endpoint.json`;
- `results/disjoint_n6_321_circuit5_two_level_dual.json`.
