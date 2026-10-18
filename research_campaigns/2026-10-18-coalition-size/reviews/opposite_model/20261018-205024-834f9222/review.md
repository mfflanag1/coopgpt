## Provisional verdict
**No fatal findings in reviewed scope.** Both statements survive re-derivation as *scoped* stop certificates; neither is phrased as an all-real upper. The one concrete gap is a definitional quantifier in Note 2: **"nontrivial" is never defined**, and the proof needs it to mean δ≠0, not F(δ)>0.

## Findings

**1. [Medium] ONE_RESTORATION_LAYER_BARRIER, lines 9–12 ("nontrivial legal protected comparisons").**
The partition hypothesis is only stated for "nontrivial" comparisons, but the payment split (y=u on L∪I, y=h on H) must satisfy *every* comparison the certificate includes. If "nontrivial" is read as F(δ)>0, a comparison with δ≠0 but F(δ)=0 could run H→L, requiring u_sink(C) ≥ h_source(C), i.e. u_h(C) − h_l(C) ≥ 0. Nothing in (1)–(2) gives that; the companion file's own fixtures (PRICE_CHARGE_FRONTIER §4, §5) exhibit optimal-price allocations dropping across a zero-value restoration. *Verification:* fix the text to "no profile with any outgoing δ≠0 comparison receives h," or add the explicit stipulation δ=0 ⇒ comparison is a self-loop. Under that reading the proof closes: u(C) ≥ F(b_C) by weak duality, Σu=V, u ≤ h, Σh ≤ rV, and u_l(C)+F(δ) ≤ F(B_h)−F(O) ≤ h_h(C) via (2) with B_h−b_{h,C}=O — all re-derived and sound, including V=0.

**2. [Low] UNIT_WORTH_PRICE_BASE_FRONTIER, line 100.** "the maximum is at m=s−1,s" is false as stated for s=2 (the rule's m=1 cost is 1, not 1+2q₁); line 101–102 patches it. A_s is unaffected because f(m)=m q_m satisfies f(s−1)=f(s), ratio 2(m+1)/(2m+1)>1 pre-tail and ((m+1)/m)α<1 for m>s−1.

**3. [Verified, no defect].** §2 cap forcing is correct: Σ over supported edges gives mc+(1−c) ≥ m ⇒ c=1 for m≥2, using only p≥0 and p·1_S=1 — hence it binds *every* witness, which is the right quantifier for the lower while §3's witnesses ("some p") suffice for the upper. §3 duals are feasible/efficient (every unsupported edge meets an absent row priced 1). §4's increment identity q_{m+1} − a_{m+1}(q_m−q_{m+1}) = 0 holds exactly with a_{m+1}=min(s−1,2m); §5's Q_h=4^h/[2C(2h,h)], A_s=1+2sq_s, A_s−B_s=2q_s, and A_s/√s → √(2π)/(3√e) all reproduce. §6's averaging is legitimate: feasibility, efficiency (equality) and (1) are linear at each profile, and C_m profiles have exactly s star triples, so all lie in L_H.

**4. [Scope caveat]** (1) is y_i ≥ p·b_i *with* the indicator; this is precisely what admits the upper (absent rows priced 1, paid 0). The note should not be cited as showing price domination at unreported rows is costless. §4's bound is exactly tight (zero slack), so the exclusion of two new edges / cap change rests entirely on ideal membership + linearity — which I re-derived as valid.

## Scope limitations
No execution; replay counts (13,584 profiles, 1,082,027 pairs, 22,046 OUT checks) unverified. Parent steps "terminal branch coverage and funding" and the GL-transitivity details are taken as accepted. PL-completeness, the 12-profile fixture, and the forest normal form were not audited.

## Verdict
Findings (one definitional gap, one wording error); both statements otherwise sound within stated restrictions — restricted binary ideal, and a single comparison layer — and neither is an unrestricted upper.
