**Provisional verdict: no findings in reviewed scope.** I independently rederived the gradient (4), both factorizations (5), the coefficients (6), the minimizing vertices, the endpoint values (7)–(8), and the boundary/seam extension; all check. Most important observation: the only step stated loosely is the Section 4 minimization, which silently relaxes the constraint |y−w| ≤ t−u to |w| ≤ u; this is sound because the relaxed minimizer (h,−h,±h) is itself feasible, but the text should say so.

## Findings

**1. (Info, Section 4, lines 86–91) Relaxed order-interval bound is exact but not labeled as such.**
The bound φ(u) = L_v·max(−u, x−t+u) − |L_w|u drops the outsider constraint on w. Since L_v ≥ 0, φ ≤ true min everywhere; φ is decreasing on [0,h] (slope −(L_v+|L_w|)) and nondecreasing on [h,t] (slope L_v−|L_w| ≥ 0), min at u=h. The attaining point (h,−h,−sign(L_w)h) satisfies C−A = ((t+x)/2, (t+x)/2, y∓h) ∈ K because y+h ≤ (t+x)/2 ⇔ y ≤ x. So no gap; suggest adding one sentence. Note for τ=−1 the flat case L_v=|L_w| (x=y) is still fine.

**2. (Info, Section 5, line 112) "One-sided path derivatives agree" is stronger than needed.** Only nonnegativity of the smooth extension's derivative is required; since the ray inequalities are proved on the closed canonical region t>x≥y≥0 (including x=y, y=0), both extensions give g·D ≥ 0. Harmless.

**3. (Info, lines 17–21) Full-OUT counterexample arithmetic verified** (P(3,1,1)=(1,−¼,−¼) → 3/2; P(4,1,1)=(1,−⅕,−⅕) → 12/5; gain 9/10 < 1). The definition of "full OUT" is not in the packet, so I can only confirm the numbers, not the interpretation.

## Independently verified (rederived, not from checker)
- b = 1−ta, c = ya, b+c = (x+y)/(t+y) ≤ 1, b,c ≥ 0; coverage P·B ≥ F(B).
- Funding identity (3): both sides equal (t³−2ty²−tx²+2xy²)/H; ratio < 2 in interior, → 2 on axis.
- Seams: x=y gives b=c=x/(t+x); y=0 gives c=0; x=t limit gives (1,−1,0) matching the boundary facet choice. Dominant-sign change forces x=y=0 where P=(1,0,0). Hence P continuous, piecewise-rational with H>0 on the interior ⇒ locally Lipschitz.
- Gradient: g_t=1+av+Za_t, g_x=−1+at−Z/H, g_y=−a(y+w)+2yaZ/H, a_t=(2tx−t²−y²)/H²; cross-checked by finite differences at (1,.5,.25;.25,−.25,.25) giving (0.889,−0.133,−0.356).
- (5): g_t+g_x = a[(t+v)−2tZ/H] using a_t−1/H=−2ta/H; both τ cases reduce exactly to the stated factorization; nonnegativity from t−v ≥ t−u ≥ |y−w|.
- (6): using a_t+1/H=2(tx−y²)/H² and (t−τy)(x+τy)=(tx−y²)+τy(t−x); L_v±L_w identities confirmed; L_w ≤ 0 for τ=+1.
- Endpoints: constant term 2−a(t+τy) gives 2(x−y)/(t−y), 2(x+y)/(t+y), and (8); (8) ≥ 3/4 by AM–GM on (t−x)+(x−y)=t−y.
- Boundary cases: facet slacks are affine in s, so interior high endpoint ⇒ interior for all s>0; F superadditive ⇒ high endpoint F=0 forces zero path; 0 ≤ W ≤ 2F(C) from coverage plus (3) gives continuity to 0.
- Signed-permutation equivariance makes W invariant, so canonical region suffices.

## Scope limitations
- Matching lower bound (separate file) not reviewed; sharpness claim depends on it.
- "TCWM"/"full OUT" definitions not in packet; verified the mathematical monotonicity statement as written.
- Checker not executed; its identities only probe a 20×20 grid and specific vertices, so it is not evidence for all-profile claims (consistent with the text's own disclaimer).

**Verdict: no findings in reviewed scope** (two expository tightenings suggested; no correctness gap identified).
