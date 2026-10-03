**Provisional verdict: findings.** One medium scope/interpretation error and two low ones. Both inequalities and all displayed arithmetic check out by hand from the supplied matrices; nothing was executed.

## Findings

**1. Medium — PATH_COMPLEMENT.md:98 vs 102–106: the "concrete limit of the elementary route" is contradicted by the note's own old bound.**
- The Q-deletion bound at line 106 caps each of the eight unmatched coordinates (A2, A3, A10, B2, B4, B10, C1, C3) at 2/51.
- Their diagonal caps are 4/51 each, so the unmatched cap sum falls from 73/51 to 57/51, or 55/51 with the C7 cut.
- That gives J(M,P) ≤ 47/51 + (55/51)/3 − 1 = 43/153 < 1/3 (45/153 without the C7 cut).
- So elementary tools already put CW-01's named-P obstruction below one third; line 98 is true only for the path cuts "alone" and misleads as a summary.
- Verification: recompute with Fraction and compare to the paired full record's 5/18 = 42.5/153, which is consistent.

**2. Low — RESIDUAL_PROPAGATION.md:13: "exactly coincides" is overstated.**
- The packing does reproduce (RP) (player loads ≤ 1, target uncovered), but only after bounding each completed team's worth below by the opposite diagonal pair.
- With actual team worths the packing is weakly stronger; (RP) is a relaxation of it.
- Suggested wording: "is implied by".

**3. Low — RESIDUAL_PROPAGATION.md:15 and PATH_COMPLEMENT.md:76: one unevidenced claim and one unstated dependency.**
- "CW-04 also violates (RP)" has no witness. It is true: for A4, k=5, R=211/2361, u=132/2361, so 5H ≤ 739/2361, while h=211/2361 gives 1055/2361.
- "Proves the true fixed-P bound" presupposes the record's matrices have an optimal diagonal and nonempty core. The `core` vectors pass diagonal tightness, all P-team covers and my spot checks, but I did not check all 1728 triples.

## Checked with no finding
- **(RP) proof:** the comparison x_(s,b) ≥ x_i − u_i is valid, since team worth ≥ opposite diagonal pair by nonnegative pair entries, plus diagonal tightness. Sector s has exactly k players in U, and x(U) ≤ R. The k=1 case and repeated labels (e.g. P-team (3,3,6)) are fine.
- **Path statement (1)–(3):** quantifiers are correct. It uses pointwise floors, not other sectors' ideals, and the cycle-removal argument holds.
- **Matrix layout:** inferred as AB, AC, BC from the P supports; all off-diagonal support lies in P pairs, as the frozen formulation requires.
- **CW-01 arithmetic:**
  - d = (6,4,4,4,4,4,4,5,4,4,4,4)/51, W=47/51, R=4/51, k=6.
  - u_A6=1/51, giving the 1/34 cap and 5/102 violation.
  - Teams (7,6,6) and (9,7,9) are worth 5, giving H_C7 ≤ 3/51.
  - Caps sum to 73/51 and the bound is 59/153.
  - Q-labels, 26/51, 24/51 and the eight coordinates are correct.
- **CW-04 arithmetic:**
  - W=2150, T=2361, caps sum to 3100, relaxed J=2467/7083.
  - The four team worths are 171, 186, 182, 217, giving floors 83, 89, 60, 6.
  - All five reduced players are unmatched; the reduction is 215, giving 2252/7083 with gap 109/7083.
- **Old-tool status:** both notes correctly disclaim novelty and global bounds.

## Scope limitations
- The values 211/714 and 5167/19782 have no artifact in the packet. As feasible values of a maximisation relaxation they are not upper bounds on anything without an exact dual.
- Hashes, the full records (5/18, 4/17), SECTOR_MINIMUM_CORE.md and the solver/checker code were not provided.

## Next lemma
A subset-Q residual bound: for Q ⊆ P with label set L, bound every unused coordinate on L by d(L) − w(Q), combined with the path floors. (RP) is the Q=P analogue. The load-bearing test is whether this family, with an exact dual, bounds J below 1/3 on a support where the full LP is not already certified.
