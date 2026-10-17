**Provisional verdict: no mathematical defects found in reviewed scope; sharpness and the two "optimal" claims rest on uninspected dependencies.** Most important point: the singleton-corner bound c+c(t0−V)+cV=1 is exactly tight, and every step feeding it checks out (details below), so the proof has no slack to absorb an error — I re-derived each step rather than trusting it.

## Findings

**1. (Verified, no defect) Core singleton corner — energy/GENERAL_LOGARITHMIC_FACE_OUTSIDE.txt L157–174.**
Re-derived: density c/(1−u) has mass −c·log(1−t0)=1; EU=1−c·t0=c (using c·t0=1−c). A_l, B_j are degree-0 in C for fixed d, so the common scaling of x is legitimate. v_l(u)≥u·x coordinatewise ⇒ ΣA_l≥cV. Euler at (t,u·x_{−j}) gives ∂_jG=[H−uH']/t; (1−u)·c/(1−u)=c makes the second B_j term (c/t)·I. Lemma B with H(t)≥t, H(1)=V, t≤V<t0 gives ≥c(t0−V). Case split is exhaustive since V≥t.

**2. (Verified) Lemma A, Lemma B, funding, TCWM.**
q(t) formula and continuity at t0 (both equal c²/(1−c)) confirmed; q+ct−1=c(1−t)[−1−log(1−t)/t]≥0 correct; 2c≈1.086>1. Lemma B hinge residuals s(t−s), (s−t)(t0−s), t(s−t0) recomputed and match; piecewise-linear concave nondecreasing decomposition with nonnegative weights is valid; the only endpoint pathology is at 0 (nondecreasing+concave forces H(1)=H(1−)), handled. Jensen chain Σ_jF(cC+(1−c)C_je_j)≤kF(((1+c(k−1))/k)C) correct. Derivative dominance: U·∂_lF·d_l≤F(C)d_l/C_l and ∂_jF·d_j≤F(C)d_j/C_j are uniform in u, so differentiation under E is justified.

**3. (Low — clarification) L180–183, δ-passage.** "d+δ·1" must mean the all-ones on the *active face*; a full-R^d ones vector leaves the face where smoothness/derivative formulas hold. Also finiteness of DY_S[1] is needed for the limit; it follows from the L186–188 bounds but is not stated.

**4. (Low — scope statement) L11.** Proof works at aggregate coalition level; per-owner withheld_i≤b_i is never used beyond feasibility. Fine, but the theorem's "arbitrary fixed mixed owners" is thus trivially inherited, not an extra result.

**5. (Verified independently) root/GENERAL_FACE_AVERAGE_TCWM.txt upper.** Jensen ≤(k+1)F(c)/2 correct; coverage via ∫_0^1∂_jF du_j≤F(·)/c_j and supergradient averaging correct; specialization to the multi-glove integral ∫_0^TΠ(1−t/c_l)dt confirmed; min(A,B) prices t/2, 1−t/2 confirmed. Optimality of (d+1)/2 is **not** verifiable here (depends on uninspected min_d TCWM lower).

**6. (Verified) root/OWNER_FULL_OUT_SIMPLE_UPPER.txt.** Superadditivity argument, coverage, (n+1)/2 Jensen bound, and n=2 Shapley nonnegativity/OUT all check. Caveat correctly flagged by the file: pays zero reporters, so it is a different eligibility regime than the face rule; "smaller of" selection must be ex ante.

## Scope limitations
- Sharpness (L25–28, L229–232) and "lower-bound mechanisms need not be anonymous/continuous" depend on SHARP_MULTIPOOL_OUTSIDE_CANDIDATE.txt, which itself depends on COALITION_PRICE_REDUCTION_CANDIDATE.txt, OUTSIDE_LOGARITHMIC_PRICE_THEOREM.txt, MULTIPOOL_OUTSIDE_LOGARITHMIC.txt — none supplied. I only spot-checked the [tq/(1−t)]′ identity in §5 there (correct). The lower is stated for coalition OUT, not individual IC, so no silent substitution occurred in the supplied text.
- No tests run, no numerics executed; constant c≈0.5431 checked by hand to ~1e-4.

## Verdict
No findings of mathematical error in the reviewed scope (main theorem upper, both lemmas, nonsmooth/zero-face passages, TCWM upper, owner corollary). Two low-severity clarifications (Finding 3). Sharpness claims: insufficient evidence in packet.
