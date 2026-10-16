Closing fixed-public-value and Pareto addendum,16 October2026.

Proof: WEIGHTED_VALUES.txt; base proof: CONTINUOUS_ATTACK.txt.
Corrected Pareto scope: PARETO_NOTE_v2.txt supersedes frozen old PARETO_NOTE.txt.
The correction excludes m1 and distinguishes a single-rule tradeoff from
separately optimized infima. Do not present the old note without this correction.

Reproduce weighted exact checks, Python standard library only:
  python3 -B -O verify_public_values.py
Expected ten PASS lines matching PUBLIC_VALUE_CHECKS.jsonl. Full ternary
capacity grids: m2 values(3,1),(0,2),(0,0); m3 values(3,1,2),(2,2,0);
theta1/2,1 each. The exact independent max-profit-flow oracle checks all
coalitions. Adjacent own increases imply whole-coordinate/bundle monotonicity
on this grid. Grids corroborate the proof, not a substitute for all-real proof.

Independent Codex audit of weighted proof by pivot_grounding passed. Root
handles focused cross-model review of weighted and corrected Pareto notes;
no cross-model completion claimed here. Established ingredients credited;
historical novelty unconfirmed. The original floor-free mixed-owner frontier
is not solved by this explicitly restricted institution and added floor.
