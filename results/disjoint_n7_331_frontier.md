# Seven-player \((3,3,1)\) threshold frontier

For
\[
n=7,\qquad A=\{1,2,3\},\quad B=\{4,5,6\},\quad |R|=1,
\]
a bounded dynamic-cut probe extracted four distinct exact circuit orbits from
six numerical supports. This is discovery evidence, not an exhaustive
enumeration.

Two circuits recolor fully. The other two have exact capacities \(1/2\) and
\(2/3\). Both pass the arm-potential threshold test with coefficientwise
rational certificates. Exact inclusion minimization leaves one common tight
coalition in each case; the half-capacity circuit uses two blocks, and the
two-thirds circuit uses three. This second seven-player geometry therefore
again satisfies the single-threshold recoloring criterion.

Evidence:

- `results/disjoint_n7_331_milp_probe15.json`;
- `results/disjoint_n7_331_milp_probe15_recoloring_capacity.json`;
- `results/disjoint_n7_331_circuit{1,4}_arm_threshold_exactness.json`;
- `results/potential_guided_minimal_tights.json`.
