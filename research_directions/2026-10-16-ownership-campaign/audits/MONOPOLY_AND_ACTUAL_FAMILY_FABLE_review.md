**Provisional verdict: no findings in reviewed scope (both exact results recompute correctly).** Most important observation: both proofs depend on the root-audited outer own-coordinate monotonicity (including across the pool tie) and branch coalition coverage; those are cited, not reproved, and I accepted them as stated.

## Findings

**1. MONOPOLY_HARDWARE §1–2 (Low, confirmatory).** Recomputed: with hardware short, `rho' = (m - rho)/h`, so `q' = q(rho-m)/h ≥ 0`; `Phi_a' = 1 - q - q(rho-m)(1 - l_a/h) ≥ 1 - q(1+rho)`, and `(1+rho)e^{1-rho}/2` has derivative `-rho e^{1-rho}/2 < 0`, equal to 1 at `rho=1`. Pool tie `h=L` gives `rho=1, q=1/2`, matching (2). Outer derivatives (7)–(8) check: `∂W/∂b_a = q(H-b_a)/H + q`. Valid.

**2. §3 composition (Low, implicit step).** Lines 77–84 combine monotonicity in `H` (with `b` fixed) and in each `b_k` (with `H` fixed) to a simultaneous increase. This needs product-order monotonicity (chain the single-coordinate comparisons); valid since each single-coordinate result is global, but the step is unstated. No correction needed.

**3. §4 counterfamily (Low, confirmatory).** Recomputed `H=2, M=3/2`; regular branch `rho=3+s`, branch outputs sum to `(1+q(2+s))/r`; anchor `(1/2+1/2)/2 = 1/2`; `Z(s)<2` since `u e^{-u}/2` decreases for `u>1`; (10)–(11) correct, and `2√e>3 ⇔ e>9/4`. Correctly scoped as a diagonal, not a solved envelope.

**4. §6 dominance class (Low, hypothesis correctly stated).** `z_a ≥ m({a})` via `{a}`-coalition coverage holds at every profile where a's resources are fixed; `b_a ≥ H` forces hardware short and `d_a=H`, so `N_j = d_j e^{-r}/2` with `r = Σ_{k≠a} d_k/H`. Sign pattern (§5) plus `x e^{-x/H}` increasing on `[0,H]` gives `E_j=N_j`. `E_a=H` uses payment ≤ min(H',B') ≤ H. `F=H` follows from `P+M ≥ p_a+m({a}) ≥ H`. Attainment example: `r=1`, total `=C`. This is the primitive's generic bound applied to the outer rule once `E=N`; correctly labeled class-specific, not a C² resolution.

**5. AGGREGATE_OBSTRUCTION §1–3 (Low, confirmatory).** Full profile: branch tie gives `z_A=1/2, z_B=(1-ε)/2, z_Ck=ε/(2m)`, `S=19/10`, `N_A=1-e^{-9/10}/4`. Under a local owner's withholding, the branch is local-short with sole long owner A, so `rho=1, q=1/2`, and A's branch payment is `L'_j/2` — the equal-loss `D` claim holds for arbitrary branch distribution. `f_B(D)=½e^{-9/10+2D}(9/10-D)` has stationary point `D=2/5 < 9/20`; `f_B(2/5)=e^{-1/10}/4`; ε≥1/5 formula and its nonpositive derivative check. For A: `q_j ≤ 1/2` bounds opponents' locals; `(1-q)t ≤ T0/2` via `e^x ≥ 1+x`; restored opposing total in `[7/5, 19/10]` keeps hardware short, so payment ≤ `1-q0/2`, attained at truth. (AO1)/(AO2) correct; `F=1` (implicit, `P+M=19/10 ≥ H=1`).

## Scope limitations
- AGGREGATE_DUAL_OBSTRUCTION.txt and the "57/40 compressed certificate" are not in the packet; I cannot verify the obstruction being resolved or that the family matches.
- Outer own monotonicity across the pool tie and branch coalition coverage are accepted as audited dependencies (root file), not re-derived here.
- No execution or numeric checks performed; all arithmetic done by hand.

## Verdict
**No findings in reviewed scope.** Both results are correct rule-specific class theorems with hypotheses stated (sole hardware owner / fixed family); neither asserts an unrestricted mechanism or optimal-subsidy claim, and both say so.
