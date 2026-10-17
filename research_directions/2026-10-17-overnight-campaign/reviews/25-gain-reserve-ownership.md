**Provisional verdict: findings (minor); no defect found in the core mathematics.** Most important: the sharpness transfer in doc 1 (lines 119–131) rests on an unverified hypothesis that the accepted general-r upper mechanisms are defined on the fully eligible (mixed-owner) domain.

## Findings

**1. Medium — Sharpness transfer needs mixed-owner upper (ZERO_COOPERATION_GAIN_RESERVE_OBSTRUCTION.txt:119–131, 138–146).** The lower-bound half of the transfer is sound: pure-role lower constructions embed by zeroing coordinates, and the completion lemma lifts any G=0-slice bound to a global bound. The upper half ("the all-profile upper mechanisms achieve the same reserve with K=0") requires the accepted (r+1)/2 TCWM rule and 1+c(r−1) OUT rule to be defined and valid on the fully eligible orthant/cube where the completion is feasible. Root 23 supports this for two pools ("same actual owners", "without individual capacity caps"); nothing in the packet (root 22 absent) confirms it for general r. Verification: cite the mixed-owner domain statement of the accepted general-r upper theorems, and confirm the lower's report domain is contained in the domain used for sharpness ([0,1]^r vs orthant).

**2. Low — Floor lower constant inconsistent with root record (OWNERSHIP_SENSITIVE_COMMON_CAP_FRONTIER.txt:65–66).** Doc states "K>=2theta Q"; ROOT_ADJUDICATION_23 line 9 records kappa>=1+(1−1/M)k·theta·Q for k=2, i.e. 1+(1−1/M)·2theta·Q. The Theta order survives (factor ≥1/2 for M≥2; M=1 covered by K≥1), but the displayed inequality should match the cited source or be derived explicitly.

**3. Low — Full-OUT status of the R-rule (OWNERSHIP_SENSITIVE…:17–19, 24, 33–34).** The convex mixture inherits full OUT only if both ingredients have it. Root 23 confirms the owner-cover rule's coverage/activation but does not explicitly record full OUT. If the R-rule is TCWM-only, line 19's "displayed upper uses full OUT" is inaccurate for the min(R,·) branch (the order claim under TCWM is unaffected). Verification: check AI_OWNERSHIP_BOUNDARY for an explicit OUT proof.

**4. Low — t=0 upper citation (OWNERSHIP_SENSITIVE…:94–96).** For theta>0 the relevant constant upper is the floor rule at M=1 (K1=3), not the floor-free "sharp two-pool bound". Conclusion Theta(1) is correct; citation is imprecise.

**Verified in packet (no defects):** completion lemma chain Y(b)≤Y(h)≤ρF(h)=ρF(b); min-r completion (owner minima = b_{i,j*}, aggregate j* unchanged, others ≥C_{j*}); feasibility on cube; restoration lemma; (2)⇒efficiency at G=0 and (3)⇒global 1+δ; certificate arithmetic 2b≥1, sx≥1/2, q+x≥1, Y(P1)≥1+(s−1)/(2s), G(H1)=0, giving ρ≥3/2−1/(2s) (5/4 at n=3); symmetrization preserves all linear constraints; OUT⇒TCWM via F≥0; Q=4^M/(2C(2M,M)) equals root 21's P_M; bounds √(3M+1)/2≤Q≤√M and monotone ratio; r-choice yields Ω(min(R,M^{1/4})); appended-owner argument; both floor witnesses (static and W=ε(a+b)+min, including coalition OUT via superadditivity of min); W=ℓ·c+F_net identity and (3)–(4); fallback formula; Nash derivation (5) and 1.5>1 overlap example.

## Scope limitations
Root check counts, root 22, AI_OWNERSHIP_BOUNDARY, COMMON_CAP_FULL_OUTSIDE_RATE, floor-frontier, and concentrated-power documents were not supplied; dependencies taken as stated. External citations (Equinix, PJM June 2026, Karaca et al., Nash 1950) not verifiable here. No tests run.

## Verdict
Findings — four minor items; core theorems check out within the supplied evidence. No novelty or deployment claim endorsed.
