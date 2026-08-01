# Seven-player \((3,2,2)\) threshold frontier

For
\[
n=7,\qquad A=\{1,2,3\},\quad B=\{4,5\},\quad |R|=2,
\]
a deliberately bounded dynamic-cut probe examined 13 numerical supports and
extracted four distinct exact support-10 unit-circuit orbits. This is a
falsification probe, not an exhaustive enumeration.

Their exact recoloring capacities are
\[
2/3,\qquad1/2,\qquad1/2,\qquad1.
\]
For each of the three deficient circuits, the weak/strict superlevel sets of
the two bumped-game capacity-dual potentials alone yield an exact rational
endpoint certificate. Exact inclusion minimization leaves one common tight
coalition and two two-level blocks in every case. Thus the first dimension
beyond the six-player frontier exhibits no new repair mechanism and matches
the stronger single-threshold conjecture.

Evidence:

- `results/disjoint_n7_322_milp_probe15.json`;
- `results/disjoint_n7_322_milp_probe15_recoloring_capacity.json`;
- `results/disjoint_n7_322_circuit{1,2,3}_arm_threshold_exactness.json`;
- `results/potential_guided_minimal_tights.json`.
