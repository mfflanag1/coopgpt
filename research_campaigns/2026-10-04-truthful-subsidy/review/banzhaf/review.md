**Provisional verdict: no error in the identification itself; two low-severity wording findings in the priority paragraph.** The source definition is unauthenticated, so the result is conditional on the paraphrase being accurate.

## Checks that pass (hand re-derivation, nothing executed)

- **Game validity (lines 15–16):** min_j(A_j z_j) ≤ A_{j*} z_{j*} ≤ T, so f_A maps into [0,1], with f_A(0)=0 and f_A(1)=1. It is monotone and continuous.
- **Endpoints (lines 18–19):** z_j=0 forces the min to 0. z_j=1 gives min(A_j, min_{l≠j} A_l z_l)/T.
- **Tail integral (lines 21–24):** P(X>t) = 1{t<A_j}·∏_{l≠j} max(1−t/A_l, 0), which vanishes for t ≥ T in both cases named at lines 27–28. So E[X] = ∫_0^T ∏_{l≠j}(1−t/A_l) dt = A_j p_j(A), matching Theorem 1 line 16.
- **k=1:** BZI_1 = f(1)−f(0) = 1 and A_1 p_1 = T, consistent with proof (b) line 44.
- **T=0:** f_A is undefined, and the file correctly defers to the zero-payment rule. T>0 implies every A_l>0, so there are no hidden divisions by zero.
- **Normalization (lines 32–33):** Σ_j BZI_j = Σ_j A_j p_j / T lies in [1,(k+1)/2] by Theorem 1(d), so the index is indeed not efficient. The "may destroy coverage" claim is true: take pools (2,1) with the left pool split into owners 1+1. Then p=(1/4, 3/4), and rescaling pool totals to sum to T gives prices (0.2, 0.6). The coalition {one left unit, right owner} has v=1 but receives 0.8.
- **Pool vs owner (lines 17, 30–32):** correctly stated. The within-pool proportional split is not itself a Banzhaf index of any owner-level game, and the file does not claim it is.

## Findings

1. **Low — BANZHAF_COMPARISON.txt lines 36–41 — overattribution of the "sharp two-pool bound".**
   - The paragraph says the Banzhaf functional plus proportional division obtains the sharp two-pool bound.
   - In Theorem 2 the Banzhaf rule attains the bound only for α ≤ 1/2. For α > 1/2 the upper bound needs the auxiliary rule z (POOLING_THEOREM lines 84–91), and the lower bound is a separate argument.
   - Fix: reword to "attains the class optimum for α ≤ 1/2; with an auxiliary rule for larger α".

2. **Low — line 38–39 — loose terms.**
   - "Exact coalition coverage": Theorem 1(a) is the inequality y(S) ≥ v(S), and the rule overpays whenever subsidy is positive. Drop "exact".
   - "Own-capacity monotonicity" should carry the underreport-only qualifier from POOLING_THEOREM lines 10 and 46–47.

## Scope limitations

- **Kurz Def. 6.11 is not authenticated.** I cannot confirm its integrand, domain or codomain requirements, the name "absolute", or whether the numbering is specific to v1. Line 4 links an unversioned URL; pin it to v1.
- **f_A depends on the reported profile A.** The identification is therefore profile-by-profile with a family of games, not one fixed game. That is harmless for the identity but relevant to any prior-art framing.
- **Prior art is wider than Banzhaf.** Theorem 1 line 34 already notes that p_j is the probability that pool j has the minimum among independent uniforms. Matching it to Banzhaf does not exhaust earlier appearances of this functional.
- **Not reviewed:** novelty, and Theorems 1–2 beyond the lines used above.

## Verdict

**No findings on the mathematical identification in the reviewed scope**, conditional on the paraphrased definition. Minor wording findings only, as listed.
