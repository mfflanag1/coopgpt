**Provisional verdict: no findings of invalid steps in reviewed scope**, conditional on the concurrently audited SHARP_NONLINEAR_OUTGOING_LOSS (SN) and two stated model hypotheses. Most important point: the entire square-root correction in (3) rests on SN applied to a deviation that reduces *both* local short (hardware) and long (resource) coordinates; this is covered only by SN §4's stage composition, which I did not re-prove.

## Findings

**1. (Low) NEGATIVE_GAP_SAVINGS, lines 36–40 — SN applied to mixed-coordinate local underreports.**
The whole-owner deviation reduces i's hardware (short) on some branches and resource (long) on others. The step `W−W' ≤ Σ_{k≠i}(z_k−z'_k)_+ ≤ K√(z_i D)` is valid only if SN's (SN) holds for simultaneous short+long reductions across branches. SN §4 asserts this via sequential stages, subadditivity of positive parts and Cauchy–Schwarz. Since that proof is under separate audit, (1)–(2) inherit its status. The Lipschitz step `(b_k−1)_+ − (b'_k−1)_+ ≤ (z_k−z'_k)_+` and `Z'−Z ≤ δ` are correct independently.

**2. (Low) Lines 8–12 — unproved model hypotheses.**
`M ≤ 1` and `P+M ≥ 1` are assumed, not derived. `M ≤ 1` follows if every branch's shorter total is bounded by that branch's hardware; `S ≥ 1` then follows as stated (total local payout ≥ T since ρ ≥ 1). Verification: confirm the model guarantees these on every productive network, otherwise (1) is vacuous where S < 1 (q0 > 1/2 would break line 56).

**3. (Informational) Lines 43–44, 60 — boundary case g_i=0, d_i=a_i=1.**
The restored-account formula `d_i−D` assumes own overflow zero, which fails when b_i ≥ 1. The claimed ceiling E_i ≤ a_i = 1 is nonetheless trivial (any outer payment ≤ max own pool share ≤ 1), so no gap; the text's "shown below" is slightly misattributed.

**Verified algebra (no issues):** pool switch cases (S' ≥ 1: payment a_i−q'(g_i+D), q' ≥ q0 e^{−δ−K√(z_iD)}; S' < 1: all accounts uncapped, q_h ≤ 1/2 because Σ min(h_k,S') ≥ S', bound a_i−(g_i+D)/2); z+g ≤ 1 ⇒ K²zg < 1; roots x_± and the comparisons K(z+g) ≤ 2 / < 2; x_−²/g = (1−r)/(1+r), Ax_− = 1−r, minimum gL(K²zg); L decreasing via d/dr log = r/(1+r); L(K²/4) ≈ 0.812.

**ACTUAL_NEGATIVE_GAP_OBSTRUCTION — verified:** branch ratios (first: hardware short T=1/r, long 2/r; second: resource short T=1/(2r), hardware long 1/r), q=c both; H=2, M=3/2, Z=(3/2)C, δ=0; z_A=3c/2, z_B=1−c/2; outer S_0=5/4+c, a=1/4, d_0=3c/4, G_0=(1−3c)/4>1/10; q_ε=c e^ε, z'_A, S_ε, d_ε as displayed; B's cap persists (c e^ε < 1); W'(ε)=Q_ε(c/2)e^ε[(1−ε)G_ε−ε] with bracket ≥ 9/200 on (0,1/20]. The deviation is an actual single-level resource underreport with hardware/grid untouched, so W(ε) is the actual nested payment — the ACTUAL profitability claim holds. Expansions D_A=(c/2)ε²+O(ε³), S_ε−S_0=(c/2)ε+O(ε³) confirmed; β>1/2 obstruction follows. Family is r,m-independent in payoffs, so unboundedness is genuine. Sanity: realized gain ≈ 0.005·q0g, within the 1−L ≈ 0.012·q0g slack of (1) at z_A=3c/4 — consistent, no contradiction.

## Scope limitations
- SN (including SHORT_STAGE_NONLINEAR_THREE_HALVES, not supplied) accepted as dependency; not re-derived.
- Outer primitive's joint own-coordinate monotonicity (hardware + account simultaneously) accepted as stated dependency.
- No tests executed; no files beyond the packet inspected.

## Verdict
**No findings** of incorrect steps in either document within reviewed scope; validity of the √ correction is contingent on SN §4 (Finding 1) and hypotheses M ≤ 1, P+M ≥ 1 (Finding 2).
