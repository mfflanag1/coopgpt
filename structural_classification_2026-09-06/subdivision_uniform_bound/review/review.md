# Review: `UNIFORM_BOUND.md` (all‑q, all‑M>0 uniform protection for the diagonal‑subdivision C4 family)

## Findings

I traced every arithmetic and combinatorial step against the label/matrix conventions in `UNIFORM_BOUND.md` lines 5–10 and cross‑checked them against `source_family.py` (`construct`, lines 17–29; `w`, line 37, which confirms the 3‑sector value is `A(a,b)+B(a,c)+C(b,c)`, consistent with the 4‑sector extension on line 9). I found no error that breaks the argument. Details of what was verified, plus the only (low‑severity) remarks, follow.

### Verified correct (no action needed)

**Setup / T (line 10).** Row maxima: A → 2q, B → 2q, C → (q+1)+q = 2q+1; plus mM. Diagonal teams: O_s = 4+M, L_s = 1+M, R_s = 1+M; sum = q(4+M)+(q+1)(1+M)+q(1+M) = 6q+1+mM. The row‑max bound applies per team (a covers A and B rows, b covers C row, +M), so the diagonal matching is optimal and every diagonal team is tight in every core point. ✓

**§1 floor.** p² at M=2: needs B(a,c)+2 ≥ B(a,d)+2·1_{c=d}; holds (equality if c=d, B≤2 otherwise). Sum = 6q+1+2m = T(2). p⁰ at M=0 is a cover by row maxima and sums to 6q+1. Interpolation is valid because both w(·) and T(·) are affine in M. Coordinate floor M/4 comes from the d‑coordinates (M/2)(1/2); a,b,c are ≥ that. M≥2 direct point covers by the same comparison. Leximin maximizes the minimum, so x_i ≥ M/4. ✓

**§2 partial‑matching lemma (line 32).** Sum of matched covers ≥ T−3M, efficiency gives unmatched sum ≤ 3M, nonnegativity gives p_i ≤ 3M. ✓

**§2 gadgets.**
- U_s: deleted 1+M + 4+M + 1+M + 1+M = 7+4M; inserted (O_s,R_s,R_s,L_s)=2+1+2+0=5, (L_{s−1},L_{s−1},O_s,O_s)=0+1+0+M, (L_s,L_s,L_s,R_s)=1. Total 7+M ⇒ value T−3M. Sector‑wise disjointness checks; unmatched exactly a_{R_s}, b_{O_s}, c_{L_{s−1}}, d_{L_{s−1}}. ✓
- V_s: 6+3M deleted, 5+1 inserted; unmatched a_{R_s}, b_{O_s}, c_{O_s}, d_{O_s}. Both d‑label variants keep value (B(L_s,O_s)=0; B(O_s,O_s)=2) and free d_{R_s} / d_{L_s} respectively. ✓
- c_{R_s}, 1≤s<q: (R_s,R_s,L_s,L_s) = 0+C(R_s,L_s)+0+M = 1+M, same as the diagonal R_s team; (R_s,R_s,R_s,R_s) is indeed still present in U_{s+1}. ✓
- Non‑O a_j: A and B rows are zero for all non‑O labels, so swapping a_j ↔ a_{R_1} in V_1 preserves weight and disjointness (including j = L_1 inside (L_1,L_1,L_1,R_1), and j = 0). ✓

**Exhaustiveness of weak coverage.** a: all non‑O (via V_1 swap). b: O_s (U_s/V_s). c: O_s (V_s), L_0…L_{q−1} (U_1…U_q), R_1…R_{q−1} (modified U_{s+1}). d: L_0 (U_1), L_s/R_s/O_s for s≥1 (V_s variants). Together with strong = {a_{O_s}, b_{L_s} (s≤q), b_{R_s} (1≤s≤q), c_{L_q}, c_{R_q}}, this partitions all 4m players. ✓

**§3.** a_{O_s} ≥ 4+M−3·3M; b_{L_s} (s<q), b_{R_s} (1≤s<q) ≥ 1+M−9M using weak a, c, d in the same diagonal team; S_L,S_R ≥ 1+M−6M. ✓

**§4 replacement.** y_{b,L} ≥ 1−5M−1/2−7M = 1/2−12M, y_{b,R} ≥ 1/2+2M, y_{c,R} = 1/2−7M; all ≥ 1/2−12M = 3/14 at M=1/42. Sum and diagonal tightness at L, R preserved. The a‑bound p_a ≥ A+B−8M holds (O rows: 4−8M with A+B≤4; others 0). Case split: C's nonzero pattern (rows L_s, R_s, L_{s−1}; columns L_q only from rows L_q,R_q; column R_q only from row R_q; C(L_q,R_q)=0) makes C(b,c)=0 in every changed team except b=R,c=L, which is handled with S_R+14M ≥ 1+9M. The residual requirement 1/2−12M ≥ 9M is exactly M ≤ 1/42. ✓

**§4 leximin contradiction.** Only four coordinates change; all four in y are ≥ 3/14 > v := min changed value in x. Counts of values < v agree; x has strictly more copies of v; so y's ascending sorted vector is lexicographically larger — contradicting leximin optimality. Handles ties with unchanged coordinates correctly. ✓

**§5 constants.** Weak: (M/4)/(3M) = 1/12. Nonterminal strong: 1−8/42 = 17/21. Terminal strong: (3/14)/(169/42) = 9/169. M ≥ 1/42: M/(4(4+M)) is increasing; at 1/42 equals (1/42)/(4·169/42) = 1/676. ✓

### Low‑severity remarks

1. **Low — `UNIFORM_BOUND.md` line 19 / dependency.** The all‑q validity of the 3‑sector floor point z (covering every (a,b,c) triple) is asserted by reference to a "prior frozen certificate." The snapshot's `source_family.py` only checks this for a given `q` by brute force (`verify`, lines 41–45), not for all q. Per the review instructions I treat it as established, but the snapshot itself does not contain an all‑q argument. Verification: confirm the referenced certificate contains a symbolic (not per‑q) proof, or run `verify(construct(q))` for the range of q you care about.

2. **Low — line 21.** The statement "H_i ≤ 4+M" is stated as uniform; for non‑O labels the tight diagonal team gives the sharper 1+M. Not a correctness issue (only loosens the constant), just noting the bound is deliberately coarse.

3. **Cosmetic — lines 41, 72, 76.** Run‑together numerals ("value1", "value5", "below3/14", "at least9/169") should be spaced; no mathematical impact.

4. **Low — line 79.** "The M=0 endpoint separately has the established tree 1/4 guarantee" is outside the theorem (M>0) and not proved or referenced in the snapshot; harmless to the theorem but unverifiable here.

## Scope limitations

- I did not execute `source_family.py` or any numerical leximin computation; all checks are by hand from the text.
- The 3‑sector core point z (line 19) and the M=0 remark are accepted as external dependencies; their all‑q proofs are not in the packet.
- The standard definitions are assumed: core = nonnegative covers of all full teams with sum T (line 10); ideal H_i = max of p_i over the core; leximin = lexicographic maximum of the ascending sorted vector (unique on a compact convex set). If the intended "protection" statistic uses a different leximin (e.g., of ratios x_i/H_i), the theorem as written does not address it — but that is outside the stated scope.
- No general C4 conclusion or novelty assessment was attempted, per instructions.

## Verdict

**No findings in reviewed scope** (only low‑severity/cosmetic remarks). Within the packet, the weak‑player coverage is exhaustive, every gadget's value and disjointness check out, the terminal replacement covers all team types including the diagonal bonus, the leximin lexicographic‑improvement step is sound, and the 1/676 constant follows from the two regimes at the M=1/42 boundary.
