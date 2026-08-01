# Six-player \((4,2,0)\) circuit frontier

For
\[
n=6,\qquad A=\{1,2,3,4\},\quad B=\{5,6\},\quad R=\varnothing,
\]
the first dynamic-cut batch examined 19 numerical supports before reaching
the requested ten-circuit limit. Exact subcircuit extraction produced ten
distinct unit-circuit orbits, all at support 10. Their
\(S_4\times S_2\) orbits comprise 408 transported supports: six orbits of
size 48 and four of size 24. This is a nonexhaustive discovery frontier.

Exact primal and dual recoloring calculations give:

| capacity | orbits |
|---:|---:|
| \(1\) | 6 |
| \(3/4\) | 1 |
| \(1/2\) | 3 |

All three half-capacity circuits attain the universal mixture lower bound.
The \(3/4\) circuit improves strictly on its mixture bound \(1/2\), again
showing that aggregate bump multiplicities do not determine capacity.

Each of the four subunit-capacity circuits has exact endpoint optimum zero
Farkas margin. Both primal feasibility and the coefficientwise rational dual
identity were checked exactly. The duals compress into the following
`(total blocks, genuinely two-level blocks)` pairs:
\[
(10,7),\qquad(13,12),\qquad(6,3),\qquad(6,4).
\]
Therefore every orbit exposed in the last disjoint six-player geometry is
harmless on exact endpoints.

Across the four disjoint six-player shapes, the representative frontier now
contains 62 distinct exact circuit orbits and 1,127 transported supports. All
are neutralized by balanced recoloring or a rational two-level exactness
certificate. This is strong discovery evidence for the dimension-free
two-level decomposition conjecture, but none of the four searches is an
exhaustive six-player classification.

Evidence:

- `results/disjoint_n6_420_milp_probe25.json`;
- `results/disjoint_n6_420_milp_probe25_recoloring_capacity.json`;
- `results/disjoint_n6_420_circuit{1,2,6,8}_exact_endpoint.json`;
- `results/disjoint_n6_420_circuit{1,2,6,8}_two_level_dual.json`.
