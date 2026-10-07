**Provisional verdict: no findings in reviewed scope.** The direct general-f mechanism (OWNER_COUNT §2–4) is sound as written; I found no gap or counterexample. Most consequential check: the boundary extension of the relative supporting inequality (lines 98–107) is correct and genuinely needs only concavity along the segment from a boundary point of F_J to x, not continuity, so the "boundary-discontinuous" claim holds.

## Findings

No correctness defects. Verified step-by-step:

- **Relative supergradient (lines 86–96).** Existence on the open orthant of F_J is standard; u_e≥0 from x+te_e; Euler (4) from λ>1 and λ<1 scalings. Correct.
- **Compact canonical choice (109–113).** Set is an intersection of closed half-spaces, boxed by 0≤u_e≤f(x)/x_e via (4); min-norm element unique. Only property needed downstream is "deterministic function of (f,x)"; satisfied.
- **∞·0 convention (115–122).** ell_x(y)=+∞ iff supp(y)⊄J; additive (supp(y+z)=supp y∪supp z) and monotone in the extended sense. ell(0)=0 in every case, so b_i=0 pays zero.
- **Global majorization (6).** On F_J by the extension lemma; off F_J trivially. x=0 case consistent.
- **Incentives (153–159).** Given B_i=0, x_B and hence ell_{x_B} are b_i-independent; min{ell(b_i),T(b)} is nondecreasing, including finite→∞ transitions since min≤T≤T'. m_i^q off term fixed. Correct.
- **No ∞ subtraction (169–178).** At the ON aggregate x, b_i and x−b_i have support ⊆ supp(x), so all three values finite; (9) follows and ell(b_i)≤f(x)≤T makes it exactly the capped ON contribution. Correct.
- **ON mass identity (10).** Same finiteness argument; each ON summand ≤f(x_B)≤T so capping is inert.
- **Identities (11).** qΣp=Z−g; g'=−Σm (multiaffine derivative); integration by parts reproduces (11) with the −(1−b0)g(b0) and −2∫g terms; g≥0 gives the inequality.
- **Finite-range Chernoff.** |V_b|≤2^n; convexity of a↦log(q+(1−q)e^{−λa}) checked (h''≥0); tail integral gives (logH+λ+1)/α; q+(1−q)j^{−2} increasing in q so α≥α_j on (0,1/j]; α_j>0 since j³−j²−j+1=(j−1)²(j+1). C_j(2^n) and (3) follow; M_i≤T gives the min with n.
- **T=0.** a_i=min{ell,0}=0, masked values 0 by monotonicity+f≥0. Correct.
- **§6 floors.** Core nonempty via ell_c (all supports ⊆supp c); H_i≤U_i; group algebra |G|T−(|G|−1)A≤T uses A≥T; dimension bound c−b_i≥(1−ρ_i)c correct, incl. ρ_i=1 via f(0)=0.
- **§5 fallback.** Correctly uses §1's 2^n budget (not K=m), boundary continuity for w^q·x≤f(q)→f(x), and subnet (not subsequence) compactness. No regularity claimed.
- **RESOURCE_DIMENSION.** Rule (1): monotonicity incl. c_{−i,e}=0; coverage via b_ie≤ρ_ic_e (also c_e=0) and homogeneity with r_S possibly >1; budget d_+(c). §2 max_e example is convex, correctly not a concave lower. §3(a),(b) checked; θ_i≤ρ_i by weighted-average with w_ec_e>0 terms. Bound (4) simplification E T≤m[1+h e^{−D/Z}] follows from p_0=1/Z.

## Scope limitations

- The inequality B≥A/((1+α)E T) and formula (4) are imported from SHARP_THEOREM/manuscript; not re-derived here. The "all-D" step to (5) relies on E T being nonincreasing in D, plausible from (4) but not spelled out.
- Main min-linear theorem taken as audited prerequisite; only its Chernoff/budget identities re-checked.
- No tests run, no files outside the packet inspected, no novelty/historical assessment.

## Verdict

**No findings in reviewed scope.** The general concave-homogeneous extension with extended-value relative supporting forms, the 2^n range counting, the ON/OFF finiteness arguments, the optional floors, and the dimension fallback are all correct as stated; residual uncertainty is confined to the imported hierarchy lower bound.
