**Provisional verdict: no findings in reviewed scope.** I rederived every algebraic cell, the feasible-use intervals, the funding collapse, and all holding-cube minima independently and found no error. The most significant item is a dependency/status issue, not a mathematical gap: the proof invokes the differential certificate as "accepted" (P4 file line 67), while the certificate file itself is labeled "Candidate structural lemma; independent review pending" (certificate line 2).

## Findings

**1. Status mismatch on the key dependency (Low, documentary).**
`upper/P4_PROTECTED_LEAF_OUT.txt:67` says "the accepted full OUT differential certificate"; `inputs/OUTSIDE_DIFFERENTIAL_CERTIFICATE.txt:2` says "independent review pending." The P4 theorem's OUT conclusion is only as strong as that lemma (sufficiency via mollification, §2 of the lemma). Verification: reconcile labels in INPUT_MANIFEST.json; either cite the lemma's acceptance record or downgrade the P4 claim to "conditional on lemma."

**2. No mathematical defects found.** Independently checked:
- Max-flow values: vertex covers of the double-cover components are {A,D},{A,C},{B,D} in each orientation, giving V, V' exactly as stated (lines 16–17).
- Feasible-use interval (lines 22–27): lower bound from w_A≤A, upper from C_L's single neighbor D_R; nonemptiness from V≤A+C, V≤A+αD. Realizability of every interior w_C follows from V≤α(B+D).
- Equivalent formulas (35–38): verified w_A and w_C by exhaustive case split including the degenerate branches (V<βC forces A=C=0; min(C,αD,V)=min(C,αD) since V≥min(C,αD)).
- Funding (48–55): per-vertex collapsed load ≤(1+α)c_v, so (V+V')/(1+α)≤F. Correct, no integrality used.
- 4A: w-values under u≤0 confirmed from the formulas; g_A=1+αθ_B, g_B=(αA/B)(1−θ_B). Single-edge: t≥α minimum at θ_X=0,θ_Y=1 gives α(1+t)≥α+β≈1.207.
- 4B: (αu−v)_+≤αu uses v>0; at most one positive part since α<1.
- 4C: p_A≥β ⇔ αv≥βu ✓; all four g's rederived; A–B minimum β+min(p_A,α), A–D minimum min(p_A,α)+min(p_D,α), both ≥1 given p_A,p_D≥β.
- 4D: w_D≤D via αu≤βv≤v; p_D≥β derivation (lines 120–124) correct using 2β=1; w_C=C subcase g's correct (no a_C term since p_C≡1). A–B minimum α+β at θ_C=1,θ_D=0.
- §5: a_v p_v∈[0,a_v] gives boundary continuity; piecewise-linear w gives local Lipschitz p on positive orthant. Hypotheses of the lemma are met.
- §6: complete bipartite inter-group connections make the distribution step a feasible transportation problem; additivity of F over disjoint components is immediate.

## Scope limitations
- I did not verify the differential-certificate lemma itself (mollification/sufficiency), only that its stated hypotheses are satisfied here.
- No numerical tests run; none would constitute proof anyway.
- The result is correctly scoped as P4 + complete blow-ups + disjoint unions; it is not a universal gate-1 result (contract line 33), and the file says so (lines 177–182).
- Optimality of 1+1/√2 on this class is not claimed and not assessed.

## Verdict
No findings in reviewed scope. The explicit mechanism and all cell computations are correct as written; the OUT conclusion is conditional on the pending differential-certificate lemma, whose status label should be reconciled.
