# Review: C4 twelve-player witness, ratio 5/44

## Summary of what I did

All statements below are **hand verification** from the packet contents (matrices, `x`, `y`, `dual`, `ideal_dual`). I did **not** execute `check_synthesis.py`; I traced its logic by reading it. I did not verify the `H` or `levels` fields beyond `H[0]`, consistent with the packet's own disclaimer.

## Findings

### No mathematical errors found (hand-verified)

**Team values / matching (C4_INTEGER.md:5, JSON `T`).** With w(t) = A01[t0][t1] + A12[t1][t2] + A23[t2][t3] + A03[t0][t3]:
- w(0,0,0,0) = 4+0+20+8 = 32, w(1,1,1,1) = 2+4+4+0 = 10, w(2,2,2,2) = 3+2+0+4 = 9. Sum 51 = T. ✓

**Cover `x` (all 81 teams).** Since sector 0 is uniform (5/4), I reduced to max over t0 of A01[t0][t1]+A03[t0][t3] for each (t1,t3) and checked all 27 (t1,t2,t3) triples. All satisfied; x sums to 204/4 = 51. Tight teams found include exactly the ten dual teams. ✓

**Floor certificate (md:7–16, JSON `dual`).**
- Each dual team is tight at x (e.g. (0,2,1,0): w = 6+2+25+8 = 41 = 5/4+21/4+25/4+113/4; (2,1,1,0): w = 1+4+25+7 = 37 = x(t)). ✓
- Loads: sector0 = (19/20, 11/20, 19/20); sector1 = (13/20, 16/20, 1); sector2 = (13/20, 1, 16/20); sector3 = (1, 12/20, 17/20). All ≤ 1; d_target = 1/20 as stated. ✓
- Every d_i > 0 player has x_i = 5/4 (players 0,1,2,3,4,6,8,10,11). ✓
- Σλ_t w_t = 965/20 = 193/4; T − 193/4 = 11/4; τ·Σd = (5/4)(44/20) = 11/4. Identity holds exactly. ✓
- The deduction (md:11–16) is sound: for core p, Σd_i p_i ≤ τΣd_i with d ≥ 0, Σd > 0, so max-min over the core is τ and every core p ≥ τ has p_target = τ. The leximin conclusion follows since the leximin point satisfies p ≥ τ. ✓

**Ideal bound (md:18–22, JSON `ideal_dual`, `y`).**
- w(1,2,2,2) = 0+2+0+1 = 3, w(2,1,1,0) = 37, total 40; teams disjoint (players {1,5,8,11}, {2,4,7,9}); target 0 unmatched. Core + efficiency ⇒ p_0+p_3+p_6+p_10 ≤ 11. ✓
- `y` sums to 19+4+7+21 = 51. I checked all 81 teams by the same reduction; all covered (many tight, e.g. (0,0,0,0), (1,1,1,1), (1,2,2,2), (0,2,·,0)). y_0 = 11. ✓
- Hence H_target = 11 and τ/H = (5/4)/11 = 5/44 < 1/8 < 9/40. ✓

### Checker review (check_synthesis.py) — no material omissions found

Traced against the JSON: every `require` passes on the recorded values. The ideal-dual check (lines 33–40) correctly encodes Σ coeff_i p_i = μT − Σ weight_t p(t) ≤ μT − Σ weight_t w(t), with coeff_target ≥ 1 and coeff_i ≥ 0 elsewhere (core nonnegativity from zero-valued singletons makes this valid). The floor check (lines 22–30) verifies exactly the hypotheses used in the md argument (d ≥ 0, d_target > 0, pinning, exact identity).

### Minor / non-blocking observations

| Severity | Location | Note |
|---|---|---|
| Low | check_synthesis.py:43 | Default input path is `cycle_m3_sector0_above8.json`, not `C4_INTEGER_CERTIFICATE.json`. The md (line 24) does not state the invocation; a reader running the checker without an argument will check a different (possibly absent) file. Suggest documenting `python check_synthesis.py C4_INTEGER_CERTIFICATE.json`. |
| Low | JSON `H`, `levels` | Not verified by the checker (documented as auxiliary in md:24). Values like H[9]=32 are plausible but uncertified; fine as long as no downstream claim relies on them. |
| Low | check_synthesis.py:31 | `threshold` check (11 > 8·5/4 = 10) is coarser than the exact ratio; the exact ratio is reported separately as `ratio_upper_bound`. Cosmetic. |
| Info | check_synthesis.py:21 | Requires `x[target] == min(x)`; the argument only needs x_target = τ on the pinned set. Stricter than necessary; harmless here. |

## Scope limitations

- I could not execute the checker; "PASS" is inferred from tracing, not observed.
- The claim that 9/40 was the previously certified C4 bound is outside this packet.
- Novelty, cyclic vanishing, optimal size, and the all-tree theorem are explicitly not claimed here and were not reviewed.
- Discovery narrative (md:26) is not verifiable from the packet and is not load-bearing.

## Verdict

**No findings in reviewed scope** (mathematical content). The integer witness, floor-pin certificate (dual, loads, identity, pinning), partial-matching ideal bound 11, attaining point `y`, and checker logic all hand-verify exactly. Only minor documentation/reproducibility notes above.
