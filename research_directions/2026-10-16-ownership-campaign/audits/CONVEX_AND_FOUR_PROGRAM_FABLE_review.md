**Provisional verdict: no findings in reviewed scope (conditional on the assumed (ER) hypothesis, whose supporting theorem is not in the packet).** The most important point: every formula in both certificates rederives correctly from the two-pool primitive in `root/campaign_review_context.txt`; the only gaps are scope/dependency, not mathematical error.

## Findings

**F1 (Info / dependency, not an error) — `JOINT_RESPONSE_CONVEX_LOCAL_FRONTIER.txt` lines 25–28; `OWNER_SPECIFIC_HARDWARE_RESTORATION.txt` lines 2–3.**
(ER) is assumed, and its named source (`GLOBAL_DIFFUSE_SECOND_ORDER.txt §3`) is explicitly "audit in progress" and absent from the packet. The convex theorem is therefore proved only for owners where (ER) is established by other means (no hardware; monopoly owner). Both sharpness/four-region families use no-hardware owners, so they do not depend on the unaudited theorem. The counting in the restoration file (|J| < eZ/(S−3/2) ≤ (e+½)/(S−3/2); 2e+1 < 7 ⇒ ≤6 at S≥2; ≤3, ≤2, ≤1 at S≥5/2, 3, 7/2) is arithmetically correct, but its premise is unverified here.
*Verification:* audit `GLOBAL_DIFFUSE_SECOND_ORDER.txt §3` separately.

**F2 (Minor / presentation) — `JOINT_RESPONSE…` line 112.**
The feasible set uses the strict constraint `a_i < x`, so it is not closed; "convex program in the standard sense" usually presumes a closed feasible set. The attainment argument (objective → −∞ as x↓a_i, other terms bounded on compact Q) is valid, so this is cosmetic. A closed reformulation (x ≥ a_i+ε for some ε below the full-profile candidate value) would remove the caveat.

**F3 (Minor / notation) — `CONVEX_LOCAL_FOUR_PROGRAM_BOUND.txt` line 24.**
`d_k` is redefined as min(l_kj,T) while the parent uses `d_k = min(b_k,H)`. No proof step is affected, but the clash invites misreading in (1)–(6).

## Independently verified steps (no discrepancy)

- Local branch: hardware short (T=H_j) under (LB); q = q0·exp(−u/T); ψ_j(q) = h_ij − h_ij q − Tq log(q/q0); ψ'' = −T/q; ψ' = u−h_ij−T ≤ 0 ⇒ β_i ≤ b_i. Opponent affine (5). Map (3) is a bijection onto [0,u_max]; reports above T collapse to u=T.
- M unchanged; Z(t) ≥ M via coverage; (2) holds; (8) matches the outer primitive incl. tie case.
- Exactness of the auxiliary x: raising x to x_*(q) preserves (10); ∂L/∂x = 1/(x−a_i) − 1/H ≥ 0 for x ≤ H; on region (9), C_A = C, so program value is realized by an actual joint report. Both directions of (12) hold.
- Section 5 permanent-assignment argument is sound (dropped patterns only duplicate boundary values).
- (2): Σ_{k≠i}h_k ≤ T and R·exp(1−R) ≤ 1 for R≥1 ⇒ 3T/2; fixed branches ≤ C·T_j; (3) uses M=Σ physical outputs ≤ H.
- (4): p_k < H from nonnegative local payments; 51/40 + 3/2 = 111/40 < 3 ⇒ c_i ≤ 2.
- (6): A−B = RT−(T−h_i), B ≤ T−h_i, q_low ≥ q_high/e; f(R)=e^{1−R}(R−1/e)/2 maximal at R=1+1/e giving e^{−1/e}/2; C < D since e^{−1/e} > 1/e.
- Sharpness family: R=1+1/e, totals T(1−q_low) + RTq_high = T(1+q_high) = DT; H=M=1; (LB), (A), (D) hold.
- Four-region family: R=1, q∈[1/(2e),1/2]; A_g account range [7/8, 9/8−1/(4e)] straddles 1 (needs e>2); half-report price e^{−1/2}/2 > 1/4 (needs e<4) gives account < 1; B accounts ≤ T/2; π=5/4; positive own gap in all four patterns.

## Scope limitations

No numerical execution; no files outside the packet (in particular the global diffuse theorem, the padded-lattice construction, and the restoration theorem's proof). Claims are correctly scoped as exact real-arithmetic representations, not polynomial-bit or finite-precision-truthful results; I did not evaluate those excluded claims.

## Verdict

**No findings in reviewed scope** (F2–F3 are presentational; F1 is an explicit, correctly disclosed dependency).
