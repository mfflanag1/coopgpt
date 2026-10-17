**Provisional verdict: no substantive findings in reviewed scope.** Most important check: the general hinge transfer (Section 3) does not rely on a hidden beta=1 step — the singleton-corner inequality (5) closes using only (4) at t=s, 2mu≥beta, and H(t)/t≥1; the pair-cap lower (Section 4) integrates on [a,b]⊂(0,1) with a>0 for every beta∈(beta0,1), so the delicate t→0 endpoint is used only at the already-audited beta=1 case.

## Findings

**Independently re-derived (all consistent):**
- Mass: mu[2a+1+b−a−a²]=1 by (1). Mean: mu a²+mu[log((1−a)/(1−b))−(b−a)]=mu(a²+1−b+... )=mu. ✓
- Endpoints: a=0 gives −log(1−b)=1+b ⇒ b=t0, mu=c. a=a0, b=1−a0+a0² gives −log a0=2−2a0, mu=1/2. a0≈0.203188 ⇒ beta0≈0.9190485. ✓
- Derivatives: Φ_a=a(1−2a)/(1−a), Φ_b=b/(1−b) ⇒ b′ and (1+b+a−a²)′=(1−2a)(b−a)/[b(1−a)] as stated; beta numerator b′a(1−a)−(1+b)(1−2a)<0. ✓
- (4): on [0,a], g=mu(2−t+t²)−mu(1−a)²+mu(b−a)=1−mu t(1−t) using mass identity; g′=0 on [a,b]; g=mu(1+t) on [b,1]. Min=beta. ✓
- (3): D″=mu[2−1/(1−t)], D(a)=D′(a)=0, D(b)=mu(1+b²)−b=(mu−½)(1+b²)+(1−b)²/2≥0. ✓ Note (3) holds with equality on (0,a]; coverage is tight there (not an error).
- Hinge values: h(u)=s·1_{u>s}/t, so E[(1−U)h]=(s/t)R(s); constant gives A[mu+(1−beta)/t]; linear gives B(2mu−beta). Both hinge cases reduce to (4). ✓
- z-rewrite: q+t(1−t)q′=z+(1−t)z′ exactly; for the constructed law z+(1−t)z′=g(t)−mu t, so equality in (7) on [a,b]; z_C(a)=a−Ca², z_C(b)=mu=C. ✓ Integrating-factor contradiction z(b)>C vs z′≥0, z(1)≤C is valid; beta is increasing in mu, so beta≤beta_C ⇔ mu(beta)≤C. ✓
- Reduction: D=beta F is degree-one homogeneous and nonnegative, so T_k-invariance, Lipschitz (via implied TCWM), and cross-face step (3) of the reduction carry over; the r→2 limit's outside term is beta·min(u,v) with vanishing extra-resource payments. ✓

**Minor (low severity), Section 4 line 200–203:** the inequality p+q+t(1−t)q′≥beta is stated for a coalition holding "none of the long resources", which cannot withhold a long coordinate. It is correct only via the limit-of-interior-corners argument (OUTSIDE_LOGARITHMIC_PRICE_THEOREM lines 129–131: the expression is affine in alpha and the ε-term εp′(1−t)→0). The main file should cite this explicitly. Verification: write g_A+g_B at alpha=ε and let ε→0 a.e.

**Minor, Section 6 line 269–271:** relies on GENERAL_OUTSIDE_FLOOR_FRONTIER.txt (not supplied) for full OUT of the proportional rule p_j=F(C)/C_j on general F. I checked the corner condition: corner J gives Σ_{j∉J}d_jF(C)/C_j+|J|∇F(C)·d ≥ F(d) in all cases, so the claim is plausible, but the smoothing/face passage is unverified here. The floor bound y_i≥mu M_i follows from F(C−b)≥F(C)(1−max_j b_j/C_j). ✓

## Scope limitations
- Not supplied: GENERAL_OUTSIDE_FLOOR_FRONTIER.txt, MULTIPOOL_OUTSIDE_LOGARITHMIC.txt, UNRESTRICTED_OUTSIDE_SHARP_CANDIDATE.txt, and the sharp TCWM lower (d+1)/2 used for beta≤beta0. Their correctness is assumed from the packet's audit labels.
- Smoothing/endpoint/integration steps (Section 3, lines 182–187) are inherited from GENERAL_LOGARITHMIC_FACE_OUTSIDE; I verified only that no step there depends on beta=1 or the specific logarithmic density (they use mean mu, bounded density, no atom at 0, support <1).
- No tests run; numerics are hand estimates.

## Verdict
No findings of substantive error in the reviewed scope. Two minor citation/completeness notes above.
