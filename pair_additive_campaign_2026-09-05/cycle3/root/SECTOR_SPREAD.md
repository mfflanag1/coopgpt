# A normalized within-sector spread gate

September 5, 2026. The elementary lemmas below are proved here as working tools, without novelty claims. The stronger proposed bound in Section3 was DISPROVED by the new finite example. Sections1–2 remain valid; this proof route is closed in its stated form.

## 1. Sector translation and the first floor

Let P be the nonempty full core of any complete strict three-sided assignment market with three nonempty equal-sized sectors I,J,K and T>0. Pair-additivity is not needed in this section. For p in P write mu_r(p)=min_{i in r}p_i and S(p)=mu_I(p)+mu_J(p)+mu_K(p). Let tau=max_{p in P}min_i p_i, the first leximin floor.

Adding constants a_I,a_J,a_K with sum zero to their respective sectors preserves every triple sum and total efficiency, and stays in P whenever all resulting coordinates are nonnegative. Subtract each sector minimum and add S(p)/3 to every coordinate. This is a core point with global minimum S(p)/3. Conversely a point attaining tau has S>=3tau. Therefore

    max_{p in P} S(p)=3tau.

At the full leximin point x, the three sector minima equal tau. Indeed, if one sector minimum were larger than another, shifting a sufficiently small positive amount from the former sector to the latter would raise some lowest affected coordinates and lower only strictly larger coordinates, improving the ascending sorted payoff vector. Compactness ensures all maxima used here exist. This argument includes tau=0.

For every sector r, max_P mu_r=3tau: the upper bound follows from S<=3tau and nonnegativity, and equality follows by moving the other two minima into sector r at a maximizer of S.

## 2. Exact ideal decomposition and elementary bounds

For player i in sector r define

    R_i=max_{p in P}(p_i-mu_r(p))
       =max_{j in r} max_{p in P}(p_i-p_j).

Thus R_i is a finite family of ordinary linear-programming optima; no maximum of a concave objective is being substituted. R_i is invariant under sector translations.

Move the other two sector minima into sector r. The resulting core payoff to i is p_i-mu_r(p)+S(p). Since S(p)>=mu_r(p), it is at least p_i. Applying this construction to all p proves the exact formula

    H_i=max_{p in P} [p_i-mu_r(p)+S(p)].

The bracket is at most R_i+3tau. Consequently

    R_i <= H_i <= R_i+3tau.

The lower bound uses mu_r>=0. The two maxima R_i and3tau need not be achieved at the same point; H_i=R_i+3tau is not asserted universally.

If pair weights are nonnegative and (i,j,k) belongs to any optimal perfect matching, its matching equality and all mixed triples also give

    p_i-mu_I(p) <= A_ij+B_ik,
    H_i <= A_ij+B_ik+3tau.

For the first inequality, minimize the first-sector coordinate in p_a+p_j+p_k>=C_jk, then subtract from p_i+p_j+p_k=A_ij+B_ik+C_jk. This crude bound is insufficient on the known family and is not the proposed proof.

## 3. The rejected sufficient lemma

The pilot challenged the statement

    R_i <=3x_i for every i in every nonnegative pair-additive market.

Together with Section2 and tau<=x_i it would imply H_i<=6x_i. However, the independently verified27-player example in FINITE_ATTAINMENT.md has x_(b_1)=1/3 and R_(b_1)=H_(b_1)=2. It violates this stronger bound by a factor2 while attaining the conjectured original ratio1/6. The implication was sufficient, not equivalent, so this is not a counterexample to one-sixth. A supporting LP inequality need not be tight at x.

This gate isolates within-sector disparity, removing the explicitly controlled common-sector shifts. The exact counterexample closes the proposed factor3 route. Replacing it by factor6 would yield only H_i<=9x_i through Section2, and that replacement has not been proved either. Do not promote another unsupported constant or revive this route without a different relation between spread and sector minima.

## 4. The old family makes the factor3 necessary

Use the canonical cycle2 all-q family and an incoming-link player e_s, s>=1. At every core payoff p and for any second-sector player j,

    a_s+p_j+i_s >= B_(a_s,i_s)=1
    a_s+f_s+i_s=1.

Hence p_j>=f_s. Since f_s is itself in that sector, f_s=mu_J(p); this holds for every block s. The existing mixed-triple ideal proof gives e_s<=1+f_s. Therefore R_(e_s)<=1. The ideal witness E from the reviewed family has e_s=2 and minimum second-sector payoff1, attaining this bound. Thus

    R_(e_s)=1, tau=1/3, H_(e_s)=2,
    R_(e_s)/x_(e_s)=1/(1/3+1/q) ->3.

The old family alone requires K>=3 for a universal R_i<=K*x_i. The new finite example strengthens that necessary condition to K>=6. This shows why calibration solely against the path family was insufficient.

## 5. Diagnostic evidence and limits

The floating-point diagnostic checked the first64 eligible archived records (all sector-size2), then explicitly amended the protocol to inspect all78 eligible archived sector-size3 records. No new games were generated. The maximum observed R_i/x_i was3 up to floating tolerance; all142 records are observations, not an exhaustive theorem or exact certification.

The known family was checked separately at q=3,4,8 for one designated coordinate; each numerical R was1. Section4 supplies the all-q exact proof independently of these calculations. Scripts and retained outputs document the finite work. All general priority claims remain unassessed.

The subsequent finite construction supplies an exact counterexample despite all142 clean archived diagnostics. `verify_finite_attainment.py` checks its whole-core witnesses and the ideal certificate independently; the conventional first-face argument identifies its full leximin target.
