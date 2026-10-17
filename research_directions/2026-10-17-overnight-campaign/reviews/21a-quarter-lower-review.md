**Provisional verdict: no findings in reviewed scope (proof checks out); minor documentation/quantifier notes only.**

Most important point: the transition inequality (6) is correct and genuinely uses nothing beyond nonnegativity, stabilizer symmetry at C_m, and weak-increase TCWM. I could not construct a counterexample to any step.

## Re-derivation (independent)

- **Symmetrization (§1).** ȳ(x)=|G|⁻¹Σ_g g⁻¹y(gx). All four constraint families are linear and the box/technology/eligibility are G-invariant, so ȳ inherits them with the same κ. At a profile x fixed by a stabilizer element h, re-indexing g→gh⁻¹ shows hȳ(x)=ȳ(x). The stabilizer of C_m contains active-branch permutations and A_m↔B_m swaps for active m, so all 2m active owners get q_m=T_m/(2m). Stabilizer of D contains power-owner permutations, so each gets Y_P/R. Sound.
- **Bootstrap (§2).** F(D)=min(1,ε)=ε; coalition {A₁,B₁,power i} standalone worth min(1/R,ε,ε)=ε; coverage minus Y_P/R≤κε/R gives (4). D→C₁ changes only A₁,B₁ (both strictly up), giving (5). Sound.
- **Transition (§3).** C_{m-1}→C_m changes only A_m (0→1); B_m, inactive owners, power owners unchanged. S_m low payment ≥T_{m-1} by nonnegativity; high payment (2m−1)q_m. Hence (1−1/(2m))T_m≥T_{m-1}. No inactive-payment assumption anywhere. Sound.
- **Algebra.** T_M≥P_M·ε(1−κε), T_M≤κ ⇒ κ≥P_M R/(R²+P_M). Π_{m=2}^M 2m/(2m−1)=4^M(M!)²/((2M)!·2)=4^M/(2·C(2M,M)) ✓. P_M∼√(πM)/2, so P_M/4∼√(πM)/8 ✓. R=2B: bound>B ⇔ P_M>4B² ✓. R≈√P_M gives ≈√P_M/2∼π^{1/4}M^{1/4}/(2√2), n=2M+O(M^{1/4}) ✓.
- **Pure vs mixed owners.** A mechanism for mixed owners restricted to this pure-owner instance is a valid pure-owner mechanism, so the lower applies to the cube-root upper's class; Ω(M^{1/4}) vs O(M^{1/3}) gap is coherent (M=2 sanity: upper 4, lower ≤0.58).

## Findings

1. **Low — definitional dependency (UNRESTRICTED…txt lines 13–14, 65–71).** S_m contains 2m−2 members whose reports do not change. The result requires TCWM in the *weak* sense (coalition restoration of a subset). This is standard and consistent with the upper note's "coordinate restoration" proof, but the theorem statement should say "weakly increase" explicitly. Verification: state the definition formally.

2. **Low — bounded-collusion quantification (not stated).** Coalition sizes used are 3, 2, and 2m−1 for m≤M. Under a collusion cap k, the product truncates at m≤(k+1)/2, giving κ≥P_{⌊(k+1)/2⌋}R/(R²+P_{⌊(k+1)/2⌋}) ≈ Ω(k^{1/4}), independent of M. No smaller coalition relates T_m to T_{m−1} ({A_m} alone yields q_m≥0 only). Worth recording so the "unrestricted" claim is not read as collusion-size-free.

3. **Low — stale cross-document text (COMMON_CAP_CUBE_ROOT_UPPER.txt lines 11, 135).** Still describes the lower as "square-root-logarithmic" and the gap as "sqrt(log M) versus M^(1/3)"; superseded by this note.

4. **Info — checker scope (verify_common_cap_quarter_lower.py).** Verifies only the fixed-point identity, product closed form, and the B-threshold equivalence; it does not test the symmetry/TCWM logic (correctly disclosed in `limits`). The `isqrt(P.numerator//P.denominator)` floor is fine for picking a near-optimal R.

## Scope limitations

Predecessor notes (INACTIVE_BRANCH_RESERVE_BARRIER, RANK_THREE_UNBOUNDED_TCWM), the "factor 3 grand marginals" and "3/2 two-sparse" claims, and the mechanism code are not in the packet; not verified. Checker not executed by me.

## Verdict

**No findings in reviewed scope.** The quarter-power lower bound κ≥P_M R/(R²+P_M) is correctly derived from nonnegativity, coalition coverage, funding, weak TCWM, and valid group averaging; the S_m coalition removes any inactive-payment assumption as claimed. Items 1–3 are presentation/consistency notes, not correctness defects.
