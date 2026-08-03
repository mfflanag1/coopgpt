# First six-player disjoint-circuit breakthrough

Shape:
\[
n=6,\qquad A=\{1,2\},\quad B=\{3,4\},\quad R=\{5,6\}.
\]

This is a discovery frontier, not an exhaustive classification. The eliminated
Farkas matrix has exact rank 15, so every circuit has support at most 16; the
determinant argument gives the rigorous normalized coefficient floor
\(1/(16\cdot15^8)=1/41{,}006{,}250{,}000\). The current exact support query
times out without stronger single-game subcircuit cuts, so no completeness
claim is made at six players.

## Dynamic exact subcircuit cuts

`src/minimize_both_sensitive_support.py` now treats a high-nullity numerical
support as a source of proof-relevant cuts. It searches the support for its
smallest exact positive subcircuit and blocks that subcircuit's full
\(S_2\times S_2\times S_2\) orbit. In the first 20-support probe this reduced
15 high-nullity candidates to exact subcircuits and exposed five distinct
both-sensitive 11-row unit-circuit orbits. Four admit exact balanced
recolorings.

Two resumable seeded batches then blocked those five orbits and exposed 20
further distinct support-11 unit-circuit orbits. All 20 have exactly certified
recoloring capacity one. The current nonexhaustive six-player frontier is
therefore 25 symmetry orbits (200 transported supports): 24 recolor and the
single orbit below has capacity \(2/3\). This is discovery evidence about the
exceptional templates, not a completeness claim.

## First failure of balanced recoloring

The remaining circuit has unit weights, efficiency weights \((0,2,2)\), and
orbit size eight. Its core rows are

- base: \(\{2,4\}\);
- \(t_A\): \(A, B, \{1,3,5,6\}, \{4,5,6\}\);
- \(t_B\): \(B, \{2,5\}, \{1,2,6\}, \{1,3,5,6\}\);

with the monotonicity rows for player 2 on the \(A\)-edge and player 4 on the
\(B\)-edge. Exact rank and kernel arithmetic verify that this is a positive
nullity-one circuit. The balanced-recoloring LP has no dual identity of the
kind in Lemma 7.8 of the manuscript. Thus balanced recoloring alone is not a
dimension-free theorem.

The exact recoloring-capacity LP in
`src/analyze_balanced_recoloring_capacity.py` gives this orbit capacity
\(\rho=2/3\): at most two thirds of both distinguished bump masses can be
retained simultaneously. Its primal and dual are both verified over
`Fraction`. Across the complete five-player censuses, the same invariant is
at least one on 608 orbits and equals \(1/2\) only on Type I. Thus the two
known recoloring obstructions form the sequence
\[
\rho_{\mathrm{Type\ I}}=\frac12,
\qquad
\rho_{(2,2,2)}=\frac23.
\]

## Endpoint exactness repairs the failure

`src/analyze_exact_circuit_endpoint.py` encodes one tight core witness for
every proper coalition of every game. Maximizing the circuit-supported worth
has exact optimum \(4b(N)\), hence zero minimum Farkas margin. A rational dual
with 12 core-witness inequalities, four efficiency/tightness equalities, and
one bump-nonnegativity multiplier verifies the coefficient identity exactly.
It uses only three tight endpoint witnesses:

- \(t_A\) tight at coalition 55, i.e. \(N\setminus\{4\}\);
- \(t_B\) tight at coalition 35, i.e. \(\{1,2,6\}\);
- \(t_B\) tight at coalition 54, i.e. \(\{2,3,5,6\}\).

The dual proves the strengthened inequality
\[
\text{circuit-supported worth}+\frac13d_B\ \leq\ 4b(N).
\]
Therefore all eight transported supports in this first recoloring-obstruction
orbit are harmless on exact endpoints.

This dual has a short hand proof. Let \(U=54=\{2,3,5,6\}\). The five
\(t_A\)-coalition weights
\[
A:1,\quad B:\tfrac23,\quad 53:\tfrac13,\quad
54:\tfrac13,\quad56:\tfrac23
\]
cover every player with total \(4/3\), and the two \(t_B\) coalitions 10 and
53 are complementary. Balancedness bounds these two collections by
\((4/3)b(N)\) and \(b(N)\). The remaining \(t_B\) collection
\[
B:\tfrac43,\quad18:1,\quad35:1,\quad53:\tfrac23,
\quad56:\tfrac13
\]
has coverage \(5/3\) on players outside \(U\) and \(2\) on players in
\(U\). Exactness at \(U\) therefore bounds it by
\((5/3)b(N)+(1/3)b(U)\). Summing and cancelling the common base-coalition
terms gives the displayed strengthened circuit inequality. This is an
instance of the manuscript's new two-level exactness lemma; it replaces the
12-row machine dual by a human derivation.

The recoloring-capacity dual has a particularly useful form: coalition prices
plus three player-potential vectors, one for each game color. Its feasibility
conditions compare the sum of player potentials on each coalition against the
coalition price, with extra charges on the two distinguished bump rows. This
is the same level-set geometry that appears in Bet 1's residual/carrier
analysis. The two Bets may therefore share a proof engine: choose exactness
witnesses at threshold coalitions of the dual potentials and sum their core
inequalities. In the new six-player circuit, that procedure collapses to the
three tight witnesses listed above.

## Updated theorem target

The five-player census suggested that balanced recoloring might be nearly
universal. The first six-player probe refines that conjecture:

> Every both-sensitive disjoint-arm circuit either admits a balanced
> recoloring or its recoloring obstruction generates a sparse
> coalition-tight endpoint-exactness dual.

The immediate mathematical task is to derive the exactness dual directly from
the player-potential dual obstruction to recoloring. That would replace both circuit
enumeration and case-by-case exactness LPs with a dimension-free alternative
theorem.

Machine-readable evidence:

- `results/disjoint_n6_222_milp_dynamic_cuts20.json`;
- `results/disjoint_n6_222_circuit1_exact_endpoint_optimum.json`.
- `results/disjoint_n6_222_recoloring_capacity.json`.
- `results/disjoint_n6_222_milp_seeded_probe30.json`;
- `results/disjoint_n6_222_milp_seeded_probe30_b.json`.
