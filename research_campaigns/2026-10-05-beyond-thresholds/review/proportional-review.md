**Provisional verdict: no proof-breaking findings in reviewed scope.** Theorem 1 and its certificate check out by hand; the only issues are scope and wording ones in Corollary 2 and the Implication section. Nothing was executed; all checks are by reading.

## Checks that passed (PROPORTIONAL_THEOREM.txt)

- **H (L28-29):** T=r and d=1, so total payment is r·Σp_j ≤ Br, which gives Σp_j(H) ≤ B.
- **L_j (L31-38):** T=1 and the named coalition has value 1. Coverage is p_j+Σ_{l≠j}p_l ≥ 1 and budget is p_j+rΣ_{l≠j}p_l ≤ B. Their combination gives (2) with no sign assumption on r−B.
- **Links (L41-47):** P_{j,h} has T=h+(r−h)/r, which lies in [1,r], and every capacity is ≤1≤T. So d=c, both for capped and raw rules. Exactly one owner changes per step, ownership is fixed, and all reports are positive. The changing owner's own payment gives p_j(P_{h+1}) ≥ p_j(P_h)/r, hence (3).
- **Certificate (L55-63):** the weights (r−1)r^{h+1} telescope to (r−1)r^r·p_j(H) − (r−1)·p_j(L_j). Other-pool prices cancel as r−r. One H row, weighted (r−1)r^r, cancels all k terms. The residual is [k+(r−1)r^r]B ≥ kr.
- **Numeric (L24-25):** 648/(216+54)=12/5.
- **Corollary lower bound (L71-75):** r·log r ≤ (1−ε)L and log(r−1)=o(L), so (r−1)r^r/k→0. The order "sup over ownerships, then inf over rules" is correct.
- **Upper bound:** the SCALING base rule is in the capped class, and its base factor E[ρ_W] ≤ R_k+1/log R_k (Theorem C, L50-64) is a budget factor, not a subsidy. I found no gap in the Theorem A/C steps as written.

## Findings

1. **Low-Medium — L11-12 vs L66-70: the sharp corollary holds only for the capped class.**
   - Theorem 1 extends to raw y_i=c_i·p_j, but the upper mechanism pays d_i·p_j, which is not raw-proportional when c_i>T.
   - Verify by stating in Corollary 2 that A_k is over capped-proportional rules, with the raw upper bound open.

2. **Low-Medium — L90-91: "strictly removes the earlier restriction" is not verifiable from the packet.**
   - The "fixed-statistic independent threshold" class is never defined here, so whether all its members pay proportionally is unshown.
   - The new bound also does not quantitatively subsume SCALING Theorem E, which gives Ω(√k) with about √k owners; (1) is always below r and needs k ≫ r^r.
   - Verify by defining the earlier class and proving containment, or weaken to "extends to arbitrary profile-dependent pool prices."

3. **Low — L87-88: the Implication could be stated more precisely.**
   - The proof uses proportionality only on H, L_j and P_{j,h}.
   - On H and L_j it needs only equal payment for equal-capacity owners within a pool; the unequal-capacity identity matters only on the intermediate profiles.
   - Rules such as y_i=f(c_i)·p_j are not addressed.

4. **Low — L56-62: certificate wording.** Say explicitly that the H row is added once in total, not once per j, and that monotonicity rows are payment rows 1·p_j(P_{h+1}) − (1/r)·p_j(P_h).

5. **Informational — L24:** divergence needs both k and r to grow. For fixed r the bound is below r, and for fixed k it tends to 0. This is consistent with CONTRACT L23.

Suggested verification for the theorem itself: an exact-rational LP on a small instance such as k=8, r=2, confirming the dual weights reproduce (1).

## Novelty (separate from proof)

Not established. L98 correctly disclaims priority, and I found no evidence either way in the packet.

## Scope limitations

- SCALING_THEOREM's claimed finite checks and review artifacts are not in the packet.
- The floor-satisfying proportional class and unrestricted mechanisms remain open, as L83-84 and L91-92 correctly state. The contract's primary target is not met.

## Verdict

Findings (minor, scope and wording only); Theorem 1, certificate, and Corollary 2 for the capped floor-free class are sound in reviewed scope.
