**Provisional verdict: no invalidating findings in reviewed scope.** The staged inequalities (1)–(11), both Cauchy–Schwarz steps, the linear-impossibility family, and the cap inequality D_i ≤ Dcap_i + w_i all check out on independent rederivation. The one concrete issue is a loose linkage in the Cap Consequence to the obstruction file (low severity).

## Findings

**1. Low — NONLINEAR_OUTGOING_LOSS.txt:161–164, justification mismatched to the obstruction family.**
The sentence "a recipient exactly at its cap with w_i=0 cannot keep that cap unchanged while causing any positive loss" is correct (w=0, Dcap=0 ⇒ D_i=0 ⇒ L_i=0), but it does not describe owner G in CAPPED_SUMMATION_OBSTRUCTION.txt: there w_G = 3/5+q−1 = q−2/5 ≈ 0.0094 > 0. What actually eliminates relaxation (2) is the preceding min-bound: with Dcap_G=0, removable other cap mass ≤ B√(z_G w_G) ≈ 2.7·√(0.409·0.0094) ≈ 0.17 < R ≈ 0.67. Also, re-running FULLY_CAPPED_RECIPIENT_BOUND's optimization with (12) is no longer the kappa-linear argument (u ≤ D + B√(z(D+w)) is nonlinear in D, so the "derivative ≤ 0 for u ≥ κ" step does not transfer verbatim). The file's stated consequence (only the D=0 relaxation is removed; no C² claim) is defensible, but the text should cite w_G>0 and the min-bound explicitly. Verification: compute B√(z_G w_G) vs R from the obstruction's exact rational bounds.

**2. Informational — items checked and found correct (no action).**
- §1: q′=q(r−m)/t, r≥m, r≥1 (long total ≥1≥t), cross-derivative bound q[r²−m(r−1)] ≤ 2/e; (2); (3) both cases including exp(1−1/t) ≤ t and v/t ≥ v; (4)–(5) including x(2v+ε)−ε = v(2x−ε) ≥ 0.
- §2: (7) exact algebra; D_l ≥ q0ψ(u) ≥ 0; concave quadratic in d on [u,1]; endpoint values u² and ψ(u); sign of R′ is (e^u−1)e^u[2+u−(2−u)e^u], whose derivative is ψ(u) ≥ 0.
- §3: a ≤ d ≤ 1, q0 = e^{−u_c}/2 (other long accounts uncapped since v<1), U_cross = a/2 ≤ q0 d via u_c ≥ d(1−e^{−u_c}); tie-agreement (q=1/2 both orientations); no second switch since new long total 1 ≥ t; post-crossing lemma hypotheses (T=1, long total exactly 1 unchanged) satisfied.
- §4: both CS steps, A ≤ B, degree-1 homogeneity of the primitive, branch independence, D_ij ≥ 0.
- Necessity family: D/(cε²)→1/2, L/(cε)→1, L²/(zD) = R(ε) ≤ (e−1)², equality at ε=1; consistent with K.
- B < 11/4 from e∈(8/3, 11/4); D_i ≤ Dcap_i+w_i by case split on b, b′ vs H.

## Scope limitations
- Primitive definition, own-monotonicity, and branch independence taken as stated; not verified against source files outside the packet.
- Numerical comparisons in Finding 1 are hand approximations, not exact certificates.
- Did not re-audit SHARP_OUTGOING_LOSS.txt's switch-stage integral J(v); NL only reuses its derivative bound (1), which I verified.
- No check of optimality of B (none claimed).

## Verdict
**No invalidating findings in reviewed scope.** (NL), (NL_role), the linear-in-D impossibility, and (12) hold as written. One low-severity presentational gap: the claimed elimination of the obstruction's relaxation should be argued from w_G>0 and the B√(z_i w_i) term, not from the w_i=0 remark.
