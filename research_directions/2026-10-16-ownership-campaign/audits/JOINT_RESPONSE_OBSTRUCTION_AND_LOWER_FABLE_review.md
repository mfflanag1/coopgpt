**Provisional verdict: no substantive findings in reviewed scope.** The three-owner arithmetic, the exact ratio (11e^{2/5}−8)/7, both certified rational inequalities, and the lift's module identities all check by hand. Most important observation: the lift silently drops the pair lower's "all changed accounts stay ≤ ε" property (A's account rises to ≈1.197ε after G's deviation); this is harmless under the stated definition of W but should be flagged explicitly.

## Findings

**F1 (Low) — Obstruction identities verified; script does not check them.**
`JOINT_SIGNED_RESPONSE_OBSTRUCTION.txt:27–40`. Hand check: hardware-short, ρ=7/5, q=e^{−2/5}/2 → z=(1−q, q, 2q/5). G-deletion: local short at 2/5, cap 2/5, q=1/2 → (1/5,1/5,0), L_G=3/5−3q/5 ✓. A-deletion: tie → (1/2,1/2,0), L_A=1/2−q ✓. (L_G+L_A)/(7q/5)=11/(14q)−8/7=(11e^{2/5}−8)/7 ✓. `certify_joint_signed_obstruction.py:17–23` only certifies the four terminal scalar inequalities (Taylor tail bound at lines 11–13 is valid: ratio x/(n+2)); the primitive identities (1)–(3) rest on the prose. Suggested verification: add exact-Fraction replay of the three-owner primitive to the script.

**F2 (Low) — Deviation profile exceeds ε bound; definition-dependent.**
`JOINT_RESPONSE_DIFFUSE_LOWER.txt:79–80`. After G deletes, A's local payment is (w e^w + 1−w)ε ≈ 1.197ε > ε. `SHARP_SIGNED_RESPONSE_DIFFUSE_PAIR_LOWER.txt:11` constrains only the full profile, so the envelope lower is unaffected, and `check_joint_response_diffuse_lower.py:62` correctly checks diffuseness only at full. But the pair lower (lines 41–44) explicitly preserved sub-ε changed accounts; the lift should state the relaxation rather than "may increase by O(ε)".

**F3 (Informational) — Margins are thin but exact.**
J−2Λ ≈ 0.0093; residual-coefficient gain ≈ c·0.0093 ≈ 0.0017. The certified bounds: e^{2/5} ≥ Taylor₄ = 1.491733 > 82/55 = 1.490909; Λ < 6889/5760 = 1.19601 < 6/5 < ratio lower 1.2013. All strict with positive rational slack; `(1−v)²/v` decreasing is correct (derivative −(1−v²)/v²). Script line 21's chained comparison does evaluate both relations.

**F4 (Informational) — Lift identities confirmed.** D_G = (3/5)(2e^w−1)·ε by scaling the obstruction (3 branches, t_J=ε/(3q_J)); A-deletion joint loss 3(1/2−q_J)t_J = (e^w−1)ε; residual module is the sharp module scaled by (1−w), loss (1−w)Λε; z_A=wε+(1−w)ε=ε ✓. G's gain e^wε hidden by cap (b_G=1+e^wε); G's own cap stays exactly 1 after its deletion (script line 76 `>=1` is correct for exact Decimal). S changes and gains (8),(9) follow from outer q=c·exp(2−S). Z−M=O(εL) so P+M>1 ✓. The growing family's z_Bj<ε needs 2e^{2/5}−1<2, i.e. e^{2/5}<3/2 (certified; m≥2 would already suffice). Script 2's primitive (lines 10–15) matches the stated rule incl. tie orientation-independence; branch index sets at line 72 are correct.

**F5 (Scope statement — correctly handled).** Both notes correctly label (J) as a hypothesized inequality, not a theorem, and the lift as a lower for the specified envelope, not a mechanism impossibility. The refutation is consistent with the sharp signed theorem (signed sum for A's deletion is exactly 0 because G's gain 1/2−q cancels B's loss).

## Scope limitations
- No execution; "passes under python -I -O" unverified (no `assert` used, so `-O` is irrelevant).
- The sharp constant Λ proof and the core expansion g_core (pair lower §5) were not re-derived; the lift inherits them.
- The claim that the ε-sufficiently-small conditions (ρ≥3, a>0, p_A>0) hold is inherited from the pair lower, not independently bounded here.

## Verdict
No findings requiring correction; two low-severity documentation/verification gaps (F1, F2).
