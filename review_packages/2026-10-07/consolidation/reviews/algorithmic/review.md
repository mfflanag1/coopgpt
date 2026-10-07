**Provisional verdict: no correctness findings in reviewed scope** (minor presentation/dependency notes only). Most important observation: every quantitative step I could recompute from the packet (posterior law, denominator, Hoeffding threshold, H₀, face count, 21m²K² bound, r<2L+2log₂r contradiction, union-bound sample size, violation-recovery t, expected-trial bound) checks out and matches the source notes without quantifier drift.

## Findings

**1. Low — undefined dependency notation (algorithmic.tex:65–71).**
The proof writes `q p_i^q+(1-q)m_i^q=r_i^q` and “taking expectations over q gives M_i”, but `p_i^q, m_i^q, r_i^q` and the identity `M_i=j∫_0^{1/j}r_i^q dq` are never introduced in this section. The exact-mean claim is correct only if the exact hybrid’s `p_i^q` is defined with (a) the *independent* q-mask on others, (b) first minimizer of the raw score, (c) cap at T after selection. The notes state this; the LaTeX relies on it silently. Verification: confirm the exact-mechanism section defines `p_i^q` exactly as (a)–(c), otherwise `E[X_i|q]=r_i^q` is an unverified step.

**2. Low — source constants unverifiable in packet (algorithmic.tex:219–228).**
Factor 4, radius ε/16, exponent 128 (Haussler Cor. 1) and covering bound `2[A₀ ln A₀]^D` (Thms 6, 12) are transcribed consistently from UNIFORM_SAMPLING_THEOREM.txt §4, and the algebra 4·2=8 and the sample-size inversion are correct. I cannot confirm the primary-source numbering/constants (journal vs. January manuscript). Note the covering bound needs the [0,1] range and ε≤1; both hold given η≤1 (line 149), so the hypothesis is present.

**3. Low — statement scope mismatch (algorithmic.tex:250–258).**
The preamble fixes *arbitrary* rational θ_k∈[0,1], η≥0, but the theorem refers to “(alg:sample-payment)”, whose θ’s are the specific posterior values from (alg:integrals) and η>0. The proof is valid for the general rule; the statement should say “the rule with the supplied θ,η”. No correctness impact (exact θ_k are rational per Prop. alg:cost).

**4. Informational — lexicographic oracle assumes lex-ordered complete vertex list (algorithmic.tex:88–90, 113–121).**
The oracle equals “first minimizer in V” only when V is the full vertex set of a nonempty pointed Q ordered coordinate-lexicographically. The section fixes an arbitrary ordered V; line 122–123 acknowledges this. The vertex/uniqueness argument itself is correct.

**5. Informational — T=0 compression in certification (algorithmic.tex:335–336).**
The note’s argument that frozen forms vanish at T=0 closure points was dropped. Not a gap: the linearity/closure argument plus rational witness recovery already makes any negative closure minimum a genuine strict-region violation.

Items I checked and found correct: π_k, θ_k∈(0,1/j), Σ C(n,k)π_k=1; denominators divide (n+2)!j^{n+2} (max a+h+1 = n+2, max j-power n+1); 1+N(n+1) queries and 1+N(n+1)(d+1) LP calls; H₀≤3mK² (m≥1); recurrence and (1+2H)^p; 2(21m²K²)^p; 1/p+log₂21−6<0; frozen-formula closure equivalence; t-choice gives G(b_t)<0 and b_t∈C_σ; 3H(1+2H)^p margin LPs; corollary’s 1/(1−δ) expectation; no polynomial-preprocessing overclaim.

## Scope limitations
- Exact hybrid section not in packet; coverage/budget (alg:exact-budget) assumed per instructions.
- Cannot verify Haussler constants, cited audit files, or any code/tests.
- Did not audit historical priority.

## Verdict
**No correctness findings in reviewed scope.** Transcription from the three source notes is faithful; no hypothesis dropped or quantifier weakened. Recommend addressing items 1 and 3 editorially.
