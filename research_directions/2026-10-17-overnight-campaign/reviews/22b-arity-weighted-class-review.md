**Provisional verdict: no mathematical findings in reviewed scope.** All displayed derivations (recurrence, gamma identity, upper funding, coalition derivatives, layer identity, scalar necessity) check out by hand. The most notable item is definitional, not an error: the lower bounds (file 1 §1, file 3 §1) use *single-coordinate* coalition increases, so the Θ claim depends on TCWM meaning arbitrary coordinatewise increases — which is the notion the upper proves (file 1 §4), so the three files are internally consistent.

## Findings

No correctness, regression, or research-validity defects identified. Verified steps:

**COMMON_CAP_GENERAL_ARITY_RATE.txt**
- L39–43: coverage of {k first-branch owners + 1 power owner} gives private payment ≥ ε − Y_P/R ≥ ε(1−κε) with ε=1/R. Correct.
- L48–52: coalition {k(m−1) old actives + X_m1}: old ≥ T_{m−1}, new = [k(m−1)+1]T_m/(km); [k(m−1)+1]/(km) = 1−(k−1)/(km). (4) correct; stabilizer of C_m is transitive on the km active owners, so q_m is well-defined.
- L53–54: iterating and T_M ≤ κ yields κ ≥ QR/(R²+Q). Correct.
- L58–63: Q = M!·Γ(1+1/k)/Γ(M+1/k) (telescoping ∏(j+1/k)); asymptotic sqrt(Q)/2 at R≈√Q. Correct.
- L87–89: max of (1−1/z)z^{−1/k} at z=k+1 equals k/(k+1)^{1+1/k}=A_k. Correct.
- L101–105: Z′ = 1+Σ_{t≠l}s_jt/x_jt ≥ 1 when g_j′=1; (f−krf′)G′ ≥ 0 with f−krf′ ∈ {0,1}. Correct.
- L106–108: G ≥ Pt/C ⇒ r′ ≥ 0 and Pr′ ≤ r; s_P h′r′ ≥ Ph′r′ ≥ rh′; h+rh′ ∈ {0,1}. Correct.
- L123–129: 1+kA_k M^{α}/C = 1+C at the chosen C; C=1 branch gives 2 ≤ k+1. (17) correct; k=1 gives 2.
- L140–142: integer-C condition and f^k formula are algebraically consistent with (7)–(8).

**HETEROGENEOUS_COMMON_CAP_COROLLARY.txt**
- L27–30: rescaling z=αx, b=(α/β)c is correct and owner-linear.
- L44–49: summation by parts with v_{(M+1)}=0 and greedy prefix equality prove (4) for every capacity vector, hence for every coalition aggregate. Correct.
- L60–63: K_{k,l} nondecreasing in l, or common C with per-layer branch count ≤ M. Correct.

**TUNABLE_CAP_SCALAR_OPTIMAL_LEADING_CONSTANT.txt**
- L33–41: G = ε+(M−1)u = 1/r; u<1/L iff r>r0; Z = kG−(k−1)ε; Z′=1, G′=1 ⇒ f−rf′[k−(k−1)ε/G] ≥ 0. ε→0 at fixed r is legitimate since f, f′ are evaluated at the same r. Correct.
- L42–44: (f r^{−1/k})′ ≤ 0 a.e. + local AC ⇒ nonincreasing; right-continuity at r0 extends. Correct.
- L47–58: h(L)≥1 (H→∞ at fixed r=L), Rh(R)+kf(R)≤κ, right-continuity ⇒ L≤κ; h+f≥1 ⇒ f(R)≥1−κ/R. Correct.
- L61–66: κ ≥ k(M−1)f(r0)/L, R=(k+1)κ>L, f(R)≥k/(k+1); exponent sum 1+1/k+(k−1)/k = 2 ⇒ (1). k=2 check: (16/27)^{1/4}. Correct.

Minor clarifications (not defects):
1. File 1 L15–17: the Θ statement is a sup over owner models; the witness needs n = kM+O(M^{α/2}) owners. The text says this (L64). Fine.
2. File 3 regularity is assumed only on (r0,∞) with r0 = L/(M−1), yet r can reach L/M on full profiles; the proof deliberately uses an absent branch so all test points lie in [r0,∞). Self-consistent, costs only M vs M−1.
3. File 3 L50: the H→∞ limit needs f(L) finite, which holds for any real-valued f.

## Scope limitations
- Only the three supplied text files were reviewed; the referenced CAPPED_UTILIZATION_CUBE_ROOT_BARRIER.txt, the "unit-graph 3/2 theorem" (file 1 L23), and the exact-arithmetic checker (file 1 L145) were not available and are not verified.
- No tests or code were run. Novelty claims are not assessable here.
- Symmetrization (file 1 L32–36) was checked at the level of the stated argument; the averaging construction is standard but not written out.

## Verdict
**No findings in reviewed scope.** The fixed-k, fixed-owner, coordinatewise-TCWM scope is stated explicitly and respected in all three files; no counterexamples or unverified steps were found.
