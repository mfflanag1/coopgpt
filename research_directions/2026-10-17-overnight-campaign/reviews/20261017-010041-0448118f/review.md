**Provisional verdict: no findings (no genuine errors) in reviewed scope.** Most important observation: the checker comment at `verify_linear_tcwm_obstruction.py:34–36` claims to verify an "exact dual identity … every TCWM row" but line 37 only asserts the arithmetic (n−1)/2+1/n = (n²−n+2)/(2n); the dual combination itself is verified analytically in the text, not by code.

## Findings

**1. (Low — documentation) `verify_linear_tcwm_obstruction.py:34–37`.** Comment overstates what is checked. The code never forms the certificate Σ_k(TCWM row k) + (n−1)/2·(3) + (1/n)·(4) against raw c_{i,S}; it checks only the final constant. The text's claim ("checks … coefficient identities") is accurate; the inline comment is not. Suggested fix: reword comment or add an assertion building K from random rational α_k, β_k satisfying (2)–(4) and checking K ≥ (n−1)/2+1/n.

**2. (Low — precision) `TCWM_OWNER_FRONTIER.txt:19–22`.** "To obtain all n" with t=floor(√((n−1)/2)) yields t≤1 for n<9, where the sharp theorem (s≥2) is not stated and β=0. The transfer argument is correct, but the resulting bound is trivial for n<9; state "n≥9" or note triviality.

**3. (Informational) Analytic steps not covered by code:** direct-sum technology (block independence), owner-label symmetrization preserving TCWM/coverage/factor, and the TCWM payment-change identity ε[α_k+(n−k)β_k]. I verified these by hand (below); the text correctly states they are analytic.

## Hand-traced verification (linear obstruction)

- Gadget: for x=1_T, L_T=|T|(|T|+1)/2; T⊊U gives excess |T|(|U|−|T|)/2≥1/2; T⊄U gives ≥M>n(n+1)/2. z=1/4<1/2 margin, so only v(S) changes. Checker lines 16–23 confirm for n≤8 (includes T∌h, T∋h≠S, T=S cases).
- (2): a_k+k·b_k = C(n−1,k−1)[α_k+(n−k)β_k] via k·C(n−1,k)=(n−k)·C(n−1,k−1); checker line 31–32 confirms.
- (3): C(n−2,k−2)/C(n−1,k−1)=(k−1)/(n−1) (line 28, incl. k=1 → 0); gives Σ(k−1)a_k≥(n−1)/2.
- (4): nα_n≥1, a_n=α_n.
- K: Σ_{S∋1,|S|=k} Σ_i c_{i,S} = C(n−1,k−1)[kα_k+(n−k)β_k] = k(a_k+b_k); then k(a_k+b_k)=(k−1)a_k+(a_k+kb_k)≥(k−1)a_k. Chain closes exactly; n=2 case gives bound 1.
- Symmetrization is valid since v_{b∘π}(S)=v_b(πS) keeps the rule in the linear class with the same F; averaging preserves all linear inequalities and the factor.
- Routine upper (n+1)/2 and its coverage/TCWM/superadditivity argument check out.

## Hand-traced verification (√n/(2√2) lower)

- Sharp finite lower (2): (3),(4),(5) and the rearrangement to (s−1)((r−1)s−1)/[2s²+(r−3)s−1] verified; P1/P2 use chained single-coordinate increases for the same coalition C — valid.
- r=2t+1, s=t → n=2t²+1, β=(t−1)(2t²−1)/(4t²−2t−1) ~ t/2 ~ √n/(2√2). Denominator identity 2u²+2u+L, derivative numerator L(L−2u²), envelope L/(2+2√(2L)) all correct; checker lines 9–18 confirm rationally.
- Zero-owner padding argument preserves coverage/TCWM/nonnegativity/total for active owners — correct.
- Outside-production extension: |S|≥2 and |S|=1 cases correct.

## Scope limitations

Reviewed only the supplied five files; no code executed. Did not assess historical priority, the unrestricted (nonlinear) TCWM lower, or the original individual-IC gap, per instructions. Gadget checker covers n≤8 only; all-n is analytic.

## Verdict

**No findings of mathematical error in reviewed scope.** Verified scope: fixed-linear coalition-value TCWM rules with all owners fully eligible, lower (n−1)/2+1/n and upper (n+1)/2; K_TCWM(n) ≥ (1/(2√2)+o(1))√n via the sharp multi-glove family, with optimality only within that parameter family. Two low-severity documentation/precision issues noted above.
