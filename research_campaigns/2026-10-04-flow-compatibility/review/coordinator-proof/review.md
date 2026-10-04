**Provisional verdict: no findings that break the claims in the reviewed scope.** I rechecked every step by hand from the packet; nothing was executed. The one-sided quota theorem, the transfer lemma, the embedding and the 32-coalition certificate all hold up. What remains are scope and framing issues.

## Findings

**1. Low–Medium (framing overclaim) — BUNDLE_OBSTRUCTION.txt l.1, l.49–53.**
The certificate itself is correct. I recomputed all 16 table bounds for U and Z, the count of 32 coalitions (21 positive), the no-lift argument for J=(3,3,1), H_source=(3,3,2) attained at Z, the sink ideals (5,5), and the window identity.

The overclaim is in the "flow-specific" and "mechanism isolated" language. Failure of max-closure for the firm/source projection is not special to bundles: in the many-to-one class of the theorem, Step 4's lattice lives on worker salaries only. Firm payoffs are a constant minus a sum of salaries, so two firm vectors are generally dominated by, not equal to, a core point. Salaries (1,0) and (0,1) for a quota-2 firm already show this.

The obstruction therefore refutes nothing the theorem used and gives no evidence against directedness. Suggested check: state explicitly that source-projection max-closure fails even inside the proved class, and that the open property is directedness.

**2. Low (evidence scope) — INSTANCES.json, EXACT_CHECKS.json, verify.py.**
All eight fixtures report subsidy 0. None of G04–G08 has unit sink capacities, so none lies in the theorem's class with a positive bound. The finite checks give no support to parts (2) or (3).

Sharpness rests only on the analytic chain argument in FLOW_CHAIN_CANDIDATE.txt, which I rechecked: the cut S_i, the lower bound n−1+(n+2)/3, and the upper allocation are all correct. UNIT_FLOW_BOUND.txt and DISCOVERY.json are not in the packet, so the certificates and the PASS status are unaudited. Suggested check: register an in-class instance with a source quota above 1 and m≥2, and confirm H and the subsidy exactly.

**3. Low (model dependence) — TRANSPORTATION_EMBEDDING.txt l.16–20.**
The proof is correct, but it needs parallel twin arcs (a multigraph). A single middle arc of capacity M can have positive deletion marginal, so the twin is load-bearing. CONTRACT l.8 does not explicitly admit parallel arcs. No hidden ownership or path assumption was found beyond this. Suggested check: confirm the frozen class admits multigraphs.

**4. Low (proof gaps, all repairable) — ONE_SIDED_QUOTA_THEOREM.txt.**
- **l.75–76:** existence of an optimal μ that fills every quota is not argued. It needs one line: complete an optimal matching arbitrarily; added pairs have nonnegative value, so optimality forces them to be zero.
- **l.122–124:** "e must cross" should say forward; a backward crossing also leaves a cut of capacity T−1, so the contradiction still holds.
- **l.20:** the reversed version is asserted, not proved; it follows by arc reversal.
- **l.65–67:** the citation is unverifiable here, but it is not load-bearing because the proof is self-contained.

**Steps with no finding:**
- **Step 1:** capacity capping preserves v.
- **Lemma 1 and Step 2:** all four coalition cases hold, the face identity holds in both directions, and the source and sink transfer maps are kept separate.
- **Step 3:** integral b-matching identification is correct.
- **Step 4:** dummy players are null with zero core payoff; necessity and sufficiency of (i)–(iii) hold, with the pairing count relying on filled quotas; min/max closure of Y holds.
- **Step 5:** middle ideals are binary and m ≤ T.
- **Step 6:** the three-point average and raises of at most (m−1)/3 are valid.
- **Scaling:** correct.

## Scope limitations
- This is a manual read only; I ran no code and did not verify hashes or sources.
- Novelty was not assessed.
- The frozen target remains UNKNOWN; nothing here bears on the two-sided-quota case or on parallel endpoint ports.

## Verdict
No correctness findings in the reviewed scope; minor framing and evidence-scope findings only (items 1–4).
