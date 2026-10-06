**Provisional verdict: no load-bearing gap found in the reviewed proof; the algebra, coalitions, edges, and asymptotics check out. The claim remains conditional on model definitions not in the packet (see Scope).**

## Findings

**F1 (Low — unverifiable premise, not an error).** `HIERARCHY_LOWER_CANDIDATE.txt:12,21-23`. The proof relies on four model facts: (i) worth = min over pools of selected capacity, (ii) T = min pool total, (iii) budget ≤ B·T, (iv) own-report increase weakly increases *that owner's* payment. These match `ENCODING.txt:24-31` and `STAR_BARRIER.txt:14-18`, but the manuscript definitions are not in the packet. If (iv) is derived rather than assumed in the manuscript, or if (iii) is normalized differently, (1) and (4) change. Verification: quote the manuscript's monotonicity and budget axioms verbatim.

**F2 (Low — parametrization of the Θ claim).** `:4-6,51-53,64-66`. Pool size m grows with d (m=2d, later m=d·q_d), so the family is not fixed-m. The bound is in k (pools), and "matching the known upper order" requires the manuscript upper to be O(log k/log log k) uniformly in m. Since m = polylog(k), a bound in total owners N=mk has the same order, but if the upper is stated for bounded pool size, "Θ" is not established. Verification: state B_k's quantifier over m explicitly and cite the upper's hypothesis.

**Checked and confirmed (no issue):**
- Symmetrization (`:12-15`): all pools equal size m, group acts on inputs and outputs jointly; constraints linear and invariant; invariance yields payments depending only on (histogram, type, low/high). Correct.
- Edge/destination (`:18-23`): S_h keeps ≥1 type-0 pool (n_0≥2 covers h=0), so T=m; raised owner is one of (h+1)(n_{h+1}+1) indistinguishable highs; (1) follows from nonnegativity + budget. Correct.
- Coalitions: C0 needs m−d≥1 lows in type-d pools ✓; C1 needs m−h ≥ m−d+1 for h<d ✓, worth min(m−d+1, m)=m−d+1 ✓.
- Coefficient algebra: (m−d)+d(m−d+1)=(d+1)m−d² ✓; type-d coefficients (m−d)x_d+d z_d exactly match the base budget row ✓. Explicit dual: covers (m−d, d), base budget 1, edge h weight A n_h, destination budget h weight A n_h/((h+1)(n_{h+1}+1)); every residual payment coefficient is ≤0, so nonnegativity cancels. ✓
- Elementary family: A=d(d+2) ✓, n_h/(n_{h+1}+1)<1/L ✓, A·H_d/L ≤ 1/2 ✓, B>(d+2)/3 ✓. Padding only decreases the last Σ term ✓.
- Asymptotics: A/m = d+1−d/q_d ✓; bracket ≤1+1/(1+log d) ✓; log L=(2+o(1))log d since A≈d²log d ✓; log k_d=(2+o(1))d log d; with d=⌊(1/2−ε)log k/log log k⌋, log k_d=(1−2ε)(1+o(1))log k ≤ log k ✓. Natural log required for q_d≥2 when d≥2 ✓.

**d=5 specialization (exact):** m=10, A=35, L=350, n_h=2·350^h, k_5 = 2(1+350+350²+350³+350⁴+350⁵) = 10,534,473,495,702. C0: one low per pool (type-5 pools have 5 lows). C1: 6 lows per type-h<5 pool (10−h≥6), one high per type-5 pool; worth 6. Weights 5 and 5; RHS 35; type-5 coefficients 5x_5+5z_5 = budget row ✓. Σ < H_5/350 = 137/21000, so bracket < 737/600 and **B > 2100/737 ≈ 2.849 > 2** (stronger than the stated 7/3). Note k_5 ≈ 10¹³ makes a full-state LP infeasible; verify instead by checking the (d+2)-profile explicit dual above with Fractions.

## Scope limitations
Manuscript axioms, the definition of B_k, the upper-bound statement, and prior literature were not supplied; novelty unassessed. No tools executed.

## Verdict
**No findings of error in reviewed scope.** Proof is sound conditional on F1/F2 being confirmed against the manuscript.
