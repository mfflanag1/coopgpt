**Provisional verdict: no findings in reviewed scope (conditional).** The dual structure is sound: every row is a necessary constraint on any all-report mechanism restricted to binary profiles, signs are correct, and the cancellation logic yields `B ≥ constant/alpha`. The most important caveat is that the implication "B > 21/10" rests on two modelling axioms (own-monotonicity, payment nonnegativity) that the packet asserts but does not source, and on an exact Fraction computation I could not execute.

## Findings

**1. (Info) Symmetrization argument is valid — ENCODING.txt:15–22.**
Group G = S_k ⋉ (S_m)^k acts on binary profiles; worth (min over pools of report sums) is G-invariant. Defining x'_i(p) = avg_g x_{g(i)}(g·p) preserves budget, coverage (gS at gp has the same worth as S at p), nonnegativity, and own-monotonicity (gp' is gp with g(i) raised). G is transitive on (profile, owner) pairs with equal (s, h, low/high), so invariant payments a_(s,h), b_(s,h) exist. Restricting to binary profiles only drops constraints, so the result is a valid lower bound on the unrestricted constant.

**2. (Info) Row semantics and signs — verify.py:27–50.**
- Budget: `+μT·B`, `−μ s_h(m−h)` on low, `−μ s_h h` on high. Correct for `T_s B − Σ payments ≥ 0`; `T = min over present types` is right since `m−h+Hh` is increasing in h for H ≥ 2.
- Cover: payments `+μ s_h u_h / v_h`, `constant += μ·min(caps)`. Correct for `payment − worth ≥ 0`; one selection per present pool type is enforced (lines 33, 43), so worth = min over all pools.
- Mono: `−μ` on `(s,h,low)`, `+μ` on `(s−e_h+e_{h+1}, h+1, high)`. Correct for `b_(s',h+1) − a_(s,h) ≥ 0`; `h<m`, `s[h]>0` checked.
- Aggregation (52–54): `αB + Σ d_v y_v ≥ constant` with all `d_v ≤ 0` and `y_v ≥ 0` gives `αB ≥ constant`. Correct.

**3. (Info) Spot-check of cancellation.** At (0,50,974), coordinate (h=1, high): budget contributes `−50·3/4748577650 = −3/94971553`, exactly offset by the mono row from (1,49,974) h=0 with weight `3/94971553` — consistent with the described repair recipe. Coordinate (h=2, high): budget `−5844/4748577650 ≈ −1.23e-6` vs mono-in `79/77030315 ≈ 1.03e-6`, net negative. At (0,56,968) all four coordinates are within ~1e-7 of zero by hand; exactness must come from the Fraction run.

**4. (Low) Unverified conditions the bound depends on.**
- Own-monotonicity (raising one's own report never lowers one's payment) and payment nonnegativity are treated as axioms. If the target class lacks either, the mono rows (used heavily, e.g. weight 137797333/19769246 at (1,55,968)) are not necessary constraints and the bound fails. Verification: cite the problem definition.
- The worth function is assumed to be min-over-pools of report sums; the packet does not define the underlying game independently.

## Scope limitations
- I did not run `verify.py`; `strip-1024-4-4.exact.json` is self-reported, and hashes are unverifiable here. 97 rows × exact rationals cannot be re-summed by hand; I confirmed signs/structure and two coordinates.
- "Previous universal lower constant 2" is not in the packet.
- The `--strip` driver and cut separation are irrelevant to soundness and were not assessed beyond noting that dropped constraints cannot invalidate a dual.

## Verdict
**No findings in reviewed scope.** Given (i) own-monotonicity and nonnegativity are axioms of the target mechanism class, (ii) worth = min over pools of report sums, and (iii) `verify.py` genuinely passes on this certificate with Fraction arithmetic, the finite dual implies every such mechanism on this 4096-owner instance has `B ≥ 2.1095… > 21/10`, hence the unrestricted uniform constant exceeds 21/10. This is a lower witness only; no upper, optimality, or asymptotic claim follows.
