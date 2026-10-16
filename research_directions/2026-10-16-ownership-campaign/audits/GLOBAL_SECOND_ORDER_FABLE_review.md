**Provisional verdict: no findings in reviewed scope that break the argument; two dependency-scope items need confirmation.** Most important: inequality (6) in §3 applies the accepted outgoing bound K·z_i to underreports that *include hardware reductions*; the packet never exhibits that theorem, and §2's own per-unit hardware-withholding constant (1+2/e ≈ 1.736) exceeds K ≈ 1.718, so the claim cannot be rederived from this file.

## Findings

**F1 (Medium – unverified dependency scope).** GLOBAL §1 line 33–35 states (i)–(ii) for an "arbitrary mixed local underreport"; §3 line 100–101 uses "the sharp outgoing Kz_i theorem" for underreports H'<1 that cut hardware. SHARP_INCOMING_ENTROPY_v2 §4 and INCOMING_ENTROPY §5 (line 128–129) use the same bound for whole-bundle underreports, so this is consistent with accepted usage, but SHARP_OUTGOING_LOSS / SHARP_NONLINEAR_OUTGOING_LOSS are not in the packet. Verification: confirm the adjudication-10/13 statement covers hardware coordinates explicitly.

**F2 (Low – label ambiguity, no mathematical effect).** §4 line 143: "At ties, choose hardware short." For a tie branch, q_j=1/2, so (1-q_j)T_j = T_j/2 and (13) still holds; the long-stage bound (iii) at ρ=1 gives K·V ≥ post-switch gain d/2=V. Fine, but the text should say the tie choice does not affect (13).

**F3 (Low – regularity addendum).** The a.e. argument needs that where an opposing account coincides with H on a positive-measure set, d_k' = 1 = H'; the formula (7) with m counting "strictly above" and W counting uncapped z_k'=1 gives the same contribution either way. Consistent, but worth one sentence.

## Verified steps (by direct recomputation)
- §2 (2)–(4): q' = q(ρ−m)/T, bounds 1/2, 1+2/e (max at ρ=2), 2q≤1 — correct.
- §3 (6): min(b,H')/H' ≥ min(b,1) for 0<H'≤1 — correct; 1-Lipschitz step correct.
- (7)–(9): Q' = Q(ρ−m−W)/H; N_i' = 1−Q+Qd'+Q'(d−a); bounds 3/(2√e)<1 and Q(2+2/e)<1 for ρ≥3/2 — correct, both gap signs, capped own account covered.
- §4 (10)–(13): log-sum, monotonicity of v[1+log(X/v)], G_- ≤ 1−X/2 via U_i ≤ a_i, Σa_i=1, hardware-role aggregate (1−q_j)T_j ≥ T_j/2 — correct; no owner/role reassignment.
- §5 (14): ΣN_i = 1+q_0 r; negative-gap gain ≤ q_0 g I_i with S' ≤ S+I_i and hardware kept short via (6) at H'=1; positive gaps use the independent accepted comparison — correct.
- §6 (15): substitution Y=X/2, stationary equation x+log x = L+log 2+β+1, value x−2+1/x → K(L−log L)+1+K log 2+o(1) — correct. (16): maximizer r=1−t/A, value cA·exp(t/A) — correct; expansion (17) with ε²L² = o(ε) — correct. Uniformity is genuine: (14) is pointwise in (r,X) and the sup is taken of an explicit scalar function; no sup/limit exchange.
- Excluded region: e^{−1/2}/4 ≈ 0.152 < c ≈ 0.184 — correct, uniform by continuity on a compact range.
- No invalid actual/restored substitution: every restored coordinate is the same fixed owner's; intermediate profiles are underreports of the full profile, so (6) applies throughout.

## Scope limitations
- Cannot inspect SHARP_OUTGOING_LOSS, SHARP_NONLINEAR_OUTGOING_LOSS, NEGATIVE_GAP_SAVINGS, or the class-specific lower bound's full derivation beyond the packet; the lower O(ε) is taken from accepted v2 (B).
- Did not re-audit INCOMING_ENTROPY §5's positive-gap comparison through outer pool switches; accepted as stated.
- No tools executed; all checks are hand recomputation.

## Verdict
**No findings in reviewed scope** that invalidate (SO-global), conditional on F1 (outgoing K·z_i bound covering hardware-inclusive underreports) being confirmed from the accepted adjudication. Root/pivot agreement was not used as evidence.
