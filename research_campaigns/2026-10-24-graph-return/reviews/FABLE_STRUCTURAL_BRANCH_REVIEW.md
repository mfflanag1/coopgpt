**Provisional verdict: no findings in reviewed scope.** All four finite rational certificate chains, the sign convention, the two P4 gap identities, the homogeneous-gradient impossibility, and the balanced double-cover failure recompute correctly. The most consequential thing to state is a scope limit, not an error: the localization lemma is bipartite-only, so it says nothing about non-bipartite instances of the gate's universal target.

## Findings

**F1 (Info, lower_chain/BUDGET_SUPPORT_LOCALIZATION.txt L33–47).** Sign convention verified: +μ on the high profile, −μ on the low profile; balance g≤ν with η=ν−g≥0 is exactly Farkas for the y≥0 rows. Checked on the exported 4/3 dual: s_C has g=−2/3, ν_P=0 (η=2/3, dropped not zeroed); l_A,l_B,l_C,l_D all have g=1/2=ν_L (tight). L_dual=4/3, D_dual=1.

**F2 (Info, same file L57–82).** Quoted scalar formulas checked against direct calculus: c(2−e^{−1/c})=1 gives c≈0.54306, t0≈0.84141; q continuous at t0 (both branches ≈0.64542); q(0)=1, q(1)=p(1)=c; q′=−c(−log(1−t)−t)/t²≤0; q+tq′=1+c·log(1−t)≥0 iff t≤t0; p+q+t(1−t)q′ **equals 1 identically** on (0,t0] and equals c(1+t)≥1 on [t0,1] with equality exactly at t0. g_A,g_B match ∂Y/∂A,∂Y/∂B for fixed holdings (αA,βB). Budget total H(c+q(t)) peaks at 1+c as t→0. Formulas (3)–(6) follow.

**F3 (Info, same file L145–171).** Δ=min((x0−x1)_+,(x3−x2)_+) and C−F=max(0,x1−x0,x2−x3) both verified; supports disjoint. Two-regime necessity is correct as a necessary condition only, as stated.

**F4 (Info, lower/THREE_PROFILE_PASSIVE_CERTIFICATE.txt).** Outputs at P,L,H all 1 for R≥1; F(d)=0 for both transitions (d∝e3; d=e0+Re2); the six terminal pair covers each equal 1; K≥4/3 and the replicated (3m+2)/(2m+2) ratio (m=2 recovers 4/3) rederived. Unchanged-member coalitions (A∈ACD, B∈BCD) are licensed by GATE_CONTRACT L12.

**F5 (Info, root/HOMOGENEOUS_GRADIENT_PRICE_OBSTRUCTION.txt).** Proof valid: m(A)=A·Φ_A nondecreasing + Φ∈[0,KB] + ∫_{A0}^T Φ_A du ≥ η log(T/A0) → contradiction. Consistency check: the inherited rule is non-integrable (−t²q′≠ct), so it escapes the proposition, as the note says.

**F6 (Low, upper/DOUBLE_COVER_ROUTE.txt L29).** "Full-OUT on a single edge *exactly* when α(1+α)≥1" proves necessity (corner (0,1) at t=α) but sufficiency needs the full segment/boundary integration; not written. Inconsequential since 1+α≥1.618>1+c and no improvement is claimed. Verify by writing the segment integral across t=α and t=1.

**F7 (Info, same file L35–65).** Counterexample verified: all max flows saturate the right side and take the (s,t) form; ∂/∂s|₀=2α(t1−t2)>0, ∂/∂t|₀=2α(1/t2−1/t1)>0 ⇒ s=t=0; S's payment α(B1+A2) is independent of A1,B2 while F(d)=ε. The condition t1<1 is unused but harmless.

## Scope limitations
- The inherited OUT theorem (passive members, side-switches, zero boundaries) is credited; I verified only the quoted pointwise identities, not Sections 1–4 of the cited file.
- Localization is proved for bipartite G only; the gate's universal target includes non-bipartite graphs, where no two-sided H exists.
- No files outside the packet inspected; no code run.

## Verdict
No findings in reviewed scope. Conclusions are correctly bounded: no new unrestricted bound; frontier remains 1+c≤K≤2.
