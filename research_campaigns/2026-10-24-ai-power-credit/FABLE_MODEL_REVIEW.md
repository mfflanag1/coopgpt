**Provisional verdict: no findings of mathematical error in L1–L4 within the reviewed scope; three low-severity interpretive/assumption gaps.** Most important: L2's "feasible financing exists iff V ≥ τ(b)" (line 35) conflates allocation feasibility (q ≥ 0) with financing feasibility (q ≥ I(1+r)) as defined in the common block (line 8).

## Findings

**F1 — Low — MODEL_CALIBRATION.txt:35.** "Feasible financing exists iff V>=tau(b)" only establishes existence of some q ≥ 0. Under the stated benchmark (line 8), the financing condition is V − τ(b) ≥ I(1+r) (single state). The max-receipt statements (lines 35–36) are correct; only the word "financing" overreaches. Verification: substitute I(1+r) > 0 and check the "iff" fails.

**F2 — Low — L1, lines 13–24.** The lemma is correct as stated: nested finite sets ⇒ P_K ≤ P_H pointwise; min(D,·) is nondecreasing; expectation preserves order; 1+r > 0. Two hypotheses are implicit rather than listed: (i) D fixed across K and H (a larger rights package priced into a different face value is outside the lemma); (ii) R is one lender's receipt, so the lemma says nothing about other creditors or counterparties — it cannot by itself address the campaign's "spread distress" question (CAMPAIGN_CONTRACT.txt:7). The consequence list (lines 21–24) should be read as "for this creditor". R ≥ 0 is unnecessary for the proof.

**F3 — Low — L4, lines 63–69.** Arithmetic correct: min(8,10)=8, min(8,2)=2, E = 2(1−p)+8p = 2+6p. The nonidentification claim holds for the stated skeleton. Implicit assumptions: step-in/consent is costless, D=8 is treated as given (if D were chosen ex ante, capacity would be (2+8p)/(1+r) for D ≥ 10), and p is a property of the completion family, not a disclosure. Correctly labeled hypothetical.

**Verified correct (no action):**
- **L2 LP/dual (lines 33–39):** dual of min 1ᵀx s.t. Ax ≥ b, x ≥ 0 is max bᵀλ, Aᵀλ ≤ 1, λ ≥ 0 with A the coalition–owner incidence; strong duality holds (primal feasible, bounded by 0). Additive case τ = Σb_i (primal x_i=b_i, dual λ on singletons). Core case: x(N) ≥ b(N) is a primal constraint so τ ≥ b(N); a core allocation attains it; x_i ≥ b({i}) ≥ 0 by nonnegativity.
- **Witness (lines 47–52):** x=(½,½,½) feasible, total 3/2; λ=½ on three pairs, each owner load 1, objective 3/2; so τ=3/2 by weak duality. Core empty: summing pair constraints gives 2x(N) ≥ 3 > 2·b(N). V=5/2 ⇒ q=1. All correct.
- **L3 (lines 54–61):** creditor maximizes min(10,R): a→10, b→8; U-maximizer picks b, pays 8; surplus 13 vs 16. Orderings differ as claimed. Also robust if controller receives residual (a: 2+1=3; b: 0+8=8). "Veto restores L1" is correct only if the veto reduces the feasible set to {a}, making the creditor the effective selector — consistent with L1's "selection authority" hypothesis.

## Scope limitations
No tools; file text only. CONTRACT_MAP.txt treated as context, not verified. No CoreWeave recovery inferred. L2's additive/core claims are classical, as the file states; no novelty assessed. Full equilibrium, renegotiation, or cross-creditor incentives are explicitly outside L1–L4 and were not evaluated.

## Verdict
**Findings (low severity only).** L1–L4 are mathematically valid as bounded statements; fix the "financing" wording in L2, state D-fixed and single-lender scope in L1, and note costless step-in in L4. No incentive or bundling-harm theorem follows from L1–L4, consistent with lines 74–78.
