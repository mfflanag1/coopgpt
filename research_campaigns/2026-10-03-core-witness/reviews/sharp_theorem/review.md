**Provisional verdict: no findings in reviewed scope.** I found no invalid step and could not construct a counterexample. Every display (1)–(11) re-derives by hand as a nonnegative combination of core constraints, and the lower family holds for all q≥1.

## Findings

No correctness findings. Checked in `SHARP_ONE_THIRD_CANDIDATE.md` unless noted:

- **L17–33, (1)→(2).** (1) needs only nonnegativity and diagonal tightness. The transfer to maxima runs in the valid direction: the witness maximises the *subtracted* coordinate (t,j_s), and the other coordinate is bounded by its own maximum. No simultaneous attainment is used, and coinciding labels give true inequalities.
- **L47–49, (3).** The sum runs over sector positions, so repeated labels are counted with multiplicity and Σ_e λ_e·#{s: j_s=j} = n_j exactly.
- **L51–63, (4)–(5).** D_p cancels and the deficit coefficient is 3p+2q−n_j = Σ_{t≠r} q_(t,j) ≥ 0 for any n_j≤3. (3) needs only λ≥0; p≤1 enters only here.
- **L67–84, (6)–(9).** (7) holds for every i, including q_i=0. The bound x_j ≥ H_i−u_i may be negative but is weighted by q_j≥0, and real k>0 is only divided by. The strictness cases (C_2>0; C_2=0⇒B=0; k=0) are exhaustive and use T>0.
- **L88–94, duality.** The dual is correct. The LP is finite, feasible and bounded, so the maximum is attained, which strictness requires.
- **L100–117, (10)–(11).** The weights give (8k−5)/(2k−1). (11) follows from (E+L)/2 = 5T−B−V and F = 3kT+(k−1)B−kV, with F≥0 by (7).
- **Edge cases.** For m=1, V=3T for every λ. Empty P and perfect P both give V≤3T.
- **Tightness cross-check.** On the retained family, V = 24q+9 = 5T−B = 3T+B−C_2/k with B=6q+6, and all slacks in (2) and F vanish. Neither bound over-claims there.
- **Lower family (`SHARP_SUBSIDY.md` L17–40).** The special edges use A-labels {0..q−1}, B-labels {q..2q−1} and C-labels {2q,0..q−2}, so players are disjoint. Only consecutive edges share a label, so the incidence graph is a tree. The witness case analysis is exhaustive, giving T=3m, H≡3, s=2q.

Low severity, non-blocking:

1. **`SHARP_SUBSIDY.md` L22.** It is implicit that the special pair positions are pairwise distinct and off-diagonal. This is true (disjoint players, distinct labels within an edge) but should be stated.
2. **`SHARP_SUBSIDY.md` L5–7, L60–64; `FORMULATION.md` L13.** These still record "unresolved" and 39999/100000. That matches the candidate's hold at L3 but must be reconciled at release.
3. **Candidate L25–33.** Pair-additivity enters only through (1) and Σu=2T. Saying so would help readers locate where the earlier 2/3 argument is beaten.

Suggested verification:
- Machine-check the coefficient identities (4), (8) and (11) symbolically.
- Run an exact-rational harness on small markets that computes H by LP and tests (1), (2) and V<4T. This is falsification only, not proof.
- Have a second reader re-derive the direction of (2) independently.

## Scope limitations

- This is hand algebra on the three supplied files; nothing was executed.
- `tree_certificate.py`, `CORE_COMPATIBILITY_UPPER.md`, `REDUCTIONS.md` and the audit files were not in the packet.
- The lower family was checked only from the prose in `SHARP_SUBSIDY.md`.
- Novelty, priority and external validation were not assessed.
- This is one reviewer's reading, not a formal verification. Given how short the certificate is relative to the earlier 39999/100000 frontier, a formal or symbolic check is still warranted before the frontier is replaced.

## Verdict

No findings in reviewed scope. The upper bound s<T/3 for arbitrary fractional packings, the sharp integral bound (10), the slack identity (11), and the all-q lower family each check out within the frozen model.
