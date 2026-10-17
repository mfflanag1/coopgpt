**Provisional verdict: no correctness findings in reviewed scope.** Most important point: the lower-bound chain (Sections 1–5 of the candidate) is internally consistent given dependency (A); every explicit inequality, derivative, and the final transcendental step re-derives correctly. The only issues are stale/inconsistent cross-file statements and unverifiable dependencies.

## Findings

**F1 (Low, documentation inconsistency).** `MULTIPOOL_OUTSIDE_LOGARITHMIC.txt:11-13` states "no sharpness claim is made for r>=3", and `OUTSIDE_LOGARITHMIC_PRICE_THEOREM.txt:169` states "The unrestricted full-OUT optimum is NOT established." Both contradict the candidate's headline claim. Not a math error, but the upper file should be updated or the candidate should cite the superseded wording explicitly. Verification: reconcile the three headers.

**F2 (Low, missing referenced artifacts).** `SHARP_MULTIPOOL_OUTSIDE_CANDIDATE.txt:119` and `FINITE_OUTSIDE_OBSTRUCTION.txt:116,118` reference `SHARP_MULTIPOOL_OUTSIDE_v1_INTERVAL_FROZEN.txt`, `UNRESTRICTED_OUTSIDE_SHARP_CANDIDATE.txt`, and two checker scripts not in the packet. The proof does not depend on them, but the "asymptotic constant proved separately" pointer at line 115-116 points to the wrong file name relative to this packet (the sharp two-input lower is in the candidate via (B)).

## Verified steps (independent re-derivation)

- **Upper (MULTIPOOL):** q' = c[t+log(1−t)]/t² <0; q+tq' = 1+c·log(1−t) ≥0 iff t≤t0; ct+q+t(1−t)q' ≡1 on log branch, = c(1+t)≥c(1+t0)=1 on c/t branch; value/derivative match at t0 reduces to c(1+t0)=1; q≤1 ⇔ u·log u ≥ u−1. Derivatives g_j, g_l, g_s and the sum identity (lines 85-88) check; the shortest-tie and second-shortest-tie restricted derivatives agree with the generic formulas (I verified both hyperplane cases explicitly). Coverage q+ct≥1 holds on both branches.
- **Lower §1:** (1) follows from budget minus A×coverage; (2) is a valid TCWM comparison (withheld bundle has zero outside value).
- **§2–3:** extra-price sum ≤ k·min(A,B)/M; (RC) re-derived exactly; both lines of (7) correct (forward λ=1, reverse λ=(M−w)/M); the OUT inequality limit (4) has the right retained/withheld accounting; zero-production low pair handled.
- **§4:** T_h preserves budget, coverage, (4), (3); averaging error ≤ k·min(A,B)/(C_j L) ≤ k/L; rational dilation invariance follows from integer invariance.
- **§5:** [tq/(1−t)]' identity correct; ∫(1−Cs)/(1−s)² gives exactly Q_C(t); max of tQ_C at t_C=1−e^{−1/C} equals 1−C+Ce^{−1/C}; f(C)=C(2−e^{−1/C}) has f'>1; C0=0 contradiction holds; c≈0.5430634 and t0≈0.8414057 numerically satisfy c(2−e^{−1/c})=1.
- **Finite certificate:** all of (1)–(6) re-derived; A=2641667/111000, B=20045/333; final ratio 1588934000/1058001797 and gap 3862609/2116003594 confirmed exactly; Ω(333)=3, Ω(4)=2 justify shift constants 2796 and 8/5; N bound is loose (max count ≈ 4000·1110^{L−1}).

## Scope limitations

- Dependency (A) (`COALITION_PRICE_REDUCTION_CANDIDATE.txt`) was read, not independently proven; I checked the symmetrization-to-counts step, T_k invariance, and the Proof C Lipschitz comparison and found no defect, but the cross-face Proof D was only skimmed.
- Measure-theoretic justification that a.e. derivative constraints follow from finite OUT inequalities for locally Lipschitz p,q is accepted from the earlier note, not reproved.
- No execution or numeric checker results were examined.

**Verdict: no findings in reviewed scope (two low-severity documentation issues).**
