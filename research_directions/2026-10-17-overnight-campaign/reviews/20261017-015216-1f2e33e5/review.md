**Provisional verdict: no findings of substantive error in reviewed scope.** All four documents check out line-by-line; the only items worth recording are low-severity presentation gaps and definitional dependencies outside the packet. Most important concrete observation: the (B)-necessity argument (REALIZATION line 50–54) is a one-liner that relies on an unstated step — that a coalition's aggregate bundle lies in the *relative interior* of its own support face, so a finite supergradient of the face-restricted concave F exists. The step is true, but the file should say it.

## Findings

**1. Low — REALIZATION_LEMMA.txt:50–54, (B) necessity for general concave F.**
Evidence: "use a nonnegative supporting price on its active coordinate face." Missing justification: (i) b(A) has all support coordinates positive, so it is relative-interior of its face; (ii) F restricted to that face is concave and finite there, so a supergradient p exists; (iii) monotonicity within the face gives p ≥ 0; (iv) homogeneity gives p·b(A)=F(b(A)); (v) sub-bundles b(T), T⊆A, stay on the face, so z_i = p·b_i is an efficient nonnegative core. For finite min-linear F the argument is immediate (pick the minimizing form at b(A)). Verification: add these five lines; no new assumption is needed beyond monotone/concave/homogeneous F.

**2. Low — REALIZATION_LEMMA.txt:12, "nonnegative" in (B) is redundant.**
For a normalized monotone game every core element of any subgame satisfies z_i ≥ v({i}) ≥ 0, so nonnegativity is automatic. Harmless, but the SCOPE line 95–96 could state the condition simply as total balancedness.

**3. Low — BALANCED_CLOSURE.txt:46–56, definitional dependence.**
The "exact characterization" claim assumes (a) the envelope is a supremum over single-owner own underreports at the full profile, and (b) the projection depends only on P_N(w^i). Under those definitions both directions are valid: any actual underreport yields an a^i ≤ v agreeing with v off i (locality + monotone F), and closure leaves P_N unchanged (item 2 of the lemma, verified). The definitions are not in the packet, so I cannot confirm (a).

**Verified correct (no action):**
- Realization proof: at (V,S) with z=1_{V∩S}, form (U,A) gives p^{(U,A)}(S)+H|V∩S∖U|; the two cases and equality at (V,S) are right; H ≥ v^U(S) follows from coalition-monotonicity. Form count 2^n(2^n−1) correct; rational cores correct.
- Star corollary: at all-high, w^i forms with i∈S are ≥H, with i∉S are ≥w^i(S)=v(S); at single-drop i, v forms ≥v(S)≥w^i(S), w^j forms (j≠i) ≥H or =v(S)≥w^i(S). No cross-star compatibility is used.
- Closure lemma items 1–5 and sparse-row locality: for S∌i all U⊆S omit i, so P_S(a^i)=P_S(v) and C(a^i)(S)=v(S); P_N(C(a))=P_N(a) via restriction argument. Correct.
- Three-owner example: recomputed all coalition values at t=0,1 (v12=v13=1; v123=1 then 3/2); KKT at (2/3,1/3,1/3) with λ=(1/3,1/3) under x=A^Tλ normalization; Cauchy–Schwarz at (1/2,1/2,1/2). Two-owner formula x1=max{a,min{T/2,T−b}} verified in all three cases; monotone under a,T↑.
- Veto lemma: cover, efficiency, V_new⊆V_old with i∈V_new, and T/|V| ratio monotone all verified; simple-game veto argument needs only balancedness (support of core ⊆ every winning coalition).

## Scope limitations
- Original production model, envelope, and sqrt(n) conjecture definitions not supplied; per instructions I did not evaluate the conjecture or any general lower bound.
- Kalai–Zemel representation taken as established background per task.
- Priority/novelty of the control-coordinate embedding not assessed.
- No tests run; no files outside the packet inspected.

## Verdict
No findings in reviewed scope (three low-severity presentation/definitional notes).
