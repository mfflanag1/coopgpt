**Provisional verdict: no substantive errors found in reviewed scope; two dependencies are unverifiable from the packet.** Most important point: the NHC hidden-loss bound on remaining branches (K × deviator's payment, line 114–116) rests on an unsupplied "accepted sharp outgoing theorem"; everything else recomputes.

## Findings

**1. (Medium – missing evidence) NHC §3, lines 114–116.** The capped owner k's loss on *remaining* branches (incl. local-short branches and post-switch hardware-short branches) is bounded by K(z_i−V) via the "accepted sharp outgoing theorem", not in the packet. Single-branch check: post-switch, retention (4) gives B=1−q−q_new ≤ KV, so short-side loss ≤ K·V_j is consistent (e.g. v=d=0.9: B ≤ 0.328 ≤ KV=0.347). Local-short branches unverified. *Verify:* supply the outgoing theorem and confirm it covers hardware-role losses on local-short branches.

**2. (Low – status inconsistency) NHC lines 3–5, 58, 168–170.** EFFECTIVE_HARDWARE_ENTROPY_MASS and TWO_CAPPED_ACCOUNTS_DIFFUSE_GAP are called "accepted"; their own headers say "Candidate" / "review pending". NHC's proof is conditional on both.

**3. (Low – stale interval claim) NHC lines 16–17, 187–188.** "Remaining interval width cK" uses only the one-capped lower −c[e+1+K log2]. TWO_RESPONSE_BRANCH_DIFFUSE_LOWER (16 Oct) gives c[2B−2e−K log2] ≈ −4.355c. With B=(4/5)[2e^{1/5}−e^{−19/5}−1] ≈ 1.136 < K, the NHC upper −c[2+K log2] ≈ −3.191c still exceeds it, so no contradiction; width would be 2c(K−B) ≈ 1.16c. Neither note claims equality of constants (NHC line 188; TWO_RESPONSE lines 25–26) — confirmed.

**4. (Low – notation) NHC line 51.** Symbol m in q_new′=q_new(ρ_new−m)/t is undefined (should be the count of hardware coordinates ≥ t). With that reading, dropping −m only weakens q_new′ and the bound 1−q_new(1+ρ_new) ≥ 0 holds (ρ≥1 ⇒ e^{1−ρ}(1+ρ)/2 ≤ 1).

## Recomputed items (all consistent)
- Pre-switch: B=q(e^u−1), R=q(d−u)e^u; ΔZ=Bv+(R−V)−B gives (1) with equality; (B+R)′=q(d−u)e^u ≥ 0; q(e^d−1) ≤ Kqd by convexity.
- Post-switch B+R ≤ KV ⇔ (1−q_new)(1+t−v) ≤ q(1+Kd), i.e. retention (4).
- Low split: η=L⁻², ρ_j ≥ 1+2logL−log2 > 2 ⇒ no switch; (5) via B_j/T_j ≤ Kq_j ≤ Kη(1−q_j)/(1−η).
- (4): capped change ≤ raw change for uncapped accounts; capped k change ≤ 0 ≤ raw+(z_k−z_k′)_+.
- (8): ∂_B = g{log[…]−2} > 0; ∂_R <0 ⇒ R=0; ∂_V ≥ Kg(L/2−log2−2)−(g+β)−g(C_η+K) > 0 ⇒ V=ε. (9),(10): x+log x = L+1−log2−(K+1)/K, Q = K(L−logL)−2K−2−K log2; outer expansion 2K+Q yields −c[2+K log2]. Q is exactly EHM's Q minus K, as expected from the added −B term.
- TWO_RESPONSE: t=2e^{1/5}ε<2.5ε; ratio 1+v→5 after deletion; (4) old−new = (1−v)(1−q_new)t+vε=(1+B)ε; S=2 exactly (sole overflow G's ε); P+M=2−ε(ρ+2v−2); Δ=ε[K(L−logL−log2)−e]; TΔ=Kε+o(ε); g_1,g_G,g_A as stated; 2B>46/25>7/4>K. Counts k=⌊L⌋ and ⌊ρ⌋ diverge; max z_i=ε at full profile; exactly one capped account (G), so not excluded by TWO_CAPPED.

## Scope limitations
Not in packet: the primitive payment convention (gain = q0g − q0′(g+D), which makes G's capped own loss costless), hardware-restoration theorem, short-local incoming estimate, sharp outgoing theorem, SHARP_LOCAL_ONLY_ENTROPY, one-capped lower. No execution performed.

## Verdict
No findings of error in reviewed scope; proof of (NHC) is conditional on Finding 1's unsupplied theorem and on acceptance of two candidate dependencies (Finding 2).
