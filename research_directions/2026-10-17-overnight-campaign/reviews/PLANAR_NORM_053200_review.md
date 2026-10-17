**Provisional verdict: no findings of substance in reviewed scope.** The planar ℓ_p L1 identity is correct, its endpoints and integrability are explicit, and the transfer through the signed-compensation theorem checks out step by step. The most important caveat is a dependency gap, not an error: the sharpness claims rest on min-game lower bounds (3/2 and 1+c) in files not in the packet.

## Findings

**1. (Low) Checker description overstates coverage — NORM_PRICE_FRESH_PLANAR_STOP.txt:122–124; NORM_PRICE_FRESH_PLANAR_CHECK.py:33–37.**
The note says the checker verifies "the constant endpoint transfers." The script contains no mechanism, funding, or incentive check at all; it checks only p=2 antiderivative identities, the max identity, H-equivariance, and a tautology (line 36: `2a²-(-2a²)==4a²` never evaluates the Jacobian). Suggested fix: reword line 124 to "p=2 identities, p=∞ identity, and the H symmetry/diagonal algebra." No proof weight is lost since the note correctly states the general proof is analytic.

**2. (Informational) Verified analytic steps.**
- f''(s)=(p−1)s^(p−2)(1+s^p)^(1/p−2) is correct; integrable near 0 (exponent p−2>−1) and at ∞ (decays as s^(−p−1)). Unbounded near 0 for 1<p<2 but still in L1, so the measure is finite.
- ∫w=f'(∞)−f'(0+)=1; ∫_0^R s w=Rf'(R)−f(R)+1 with f(R)−Rf'(R)=(1+R^p)^(1/p−1)→0 — correct.
- ∫max(a,s)w = af'(a)+[f(a)−af'(a)] = f(a); homogeneity and y=0 case correct; max(|a|,|b|)=(|a+b|+|a−b|)/2 correct. (1) is a genuine fixed linear isometry; basis images 1 and ±s have finite L1 norms.
- p=1 and p=∞ representations correct.
- Composition theorem: identity (3), inequality (6) via |z⁺−w⁺|+|z⁻−w⁻|=|z−w|, the TCWM compensation (7), the three sign cases of (8), and the scalar derivative formulas/bounds for both rules (α,β in §3; q, q', q+rq', cr−r²q', and the r=1 identity in §4, continuity of q at t0 via q(t0)=c²/(1−c)=c/t0) all recomputed and agree. Seam handling along the path is adequate given piecewise-affine scalars and continuous one-sided C¹ pieces.
- Section 7 restriction (a,b)↦(a+b,(a−b)e) maps coordinatewise underreports and retained bundles into K, gives F=2·min, and halving preserves coverage, funding factor, TCWM and full-OUT — valid.
- §4 H-example: equivariance, vanishing on |x1|=|x2|, and DH(a,a)(1,−1)=4a²(1,−1) verified.

## Scope limitations
- Not in packet: COALITION_THREE_HALVES_CANDIDATE, SHARP_MULTIPOOL_OUTSIDE_CANDIDATE, P_NORM_GROWTH_RADIAL_LINEAR_BARRIER, COALITION_PRICE_REDUCTION_v1. I cannot confirm (a) that the min-game lower bounds use the same incentive contract and all-profile coverage as the cone mechanisms, which the "sharp" claims require; (b) that the 1+(p+1)/8 radial lower is stated under a contract comparable to TCWM/full-OUT, which the "scope distinction" (line 12–19) presupposes. The distinction as written is logically sound conditional on these.
- The common-price non-extension argument (§3) is a correctly hedged negative statement; no theorem is claimed, so nothing to verify beyond consistency.
- I did not run the checker; a passing checker is not treated as proof.

## Verdict
No findings in reviewed scope beyond a minor documentation mismatch; sharpness and the radial-vs-unrestricted scope distinction are conditional on out-of-packet lower-bound files.
