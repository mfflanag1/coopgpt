**Provisional verdict: no substantive findings in reviewed scope; two low-severity gaps (undefined constant `c`, unstated numerical lemma) in the conditional 1789/1280 chain.**

## Findings

**1. (Low) Undefined `c` and unstated inputs in the negative-saving step — COALITION_SHIFTED_POSITIVE_DUAL.txt:114–115.**
The text asserts "Since delta<=c<3/16, the uniform negative saving exceeds (2/5)(1-c)v" without defining `c` or justifying the 2/5. Reconstructing: delta=CM−Z ∈ [0,(C−1)M] and M≤H=1 give delta≤1/(2e)≈0.1839<3/16, so `c=1/(2e)` works but is nowhere stated. The 2/5 requires q0·L(K²Z₋G₋) ≥ 2/5 at S=1, i.e. L(K²/4) ≥ 4/5 (using Z₋G₋≤1/4 from Z₋+G₋≤1). I compute L(K²/4)≈0.8119, so the step holds with ~1.5% margin, but neither the lemma nor the margin appears. Suggested verification: add one line "delta≤(C−1)M≤1/(2e); L(K²/4)≥4/5 since √(1−K²/4)≈0.5117". The downstream arithmetic (1+7/40+(3/16)(19/16)=1789/1280<7/5<C²) is correct.

**2. (Low) External dependency for b≥1 direct bound — :86–87.**
E_i≤a_i+k(d_i+R_i)g_i is cited via GRID_WEIGHTED_COALITION_FLOOR.txt:33, which in turn cites FIXED_OPPONENT_COALITION_FLOOR.txt (not in packet). I checked that s↦k(a+R+s)s is nondecreasing on the relevant range (derivative k(t)−s·q_h/t² ≥ 1−q_h(1+1/t) >0 for t<1; exp(1−t)(1−s)/2≥0 for t≥1, s≤1), so the bound is sound, but the packet does not contain the proof. The k(d+R)≤1/2 step needs d+R>b≥1, which holds.

## Independently verified (no issue)
- CS1: r≤1−a from d'≤1; r≤t−b from t≥d'+R. b<S from R≤S−d, g>0.
- F'(t) sign = (1−λ_b)(S−b)−q_h(t)D(t) with D as stated; (q_hD)' has the sign of Q(t)=−(2b+1)t²+(S+b+2bS)t−bS; Q(b)=2b²(S−b), Q(1)=(1+b)(S−1). All coefficients recomputed exactly.
- λ_b, η_b=F(u), A_b=1−q[1+(u−b)/u²] algebraically consistent; A_b>0 for u<1; A_b=b/2 at u=1. b=0 recovers PD3 constants.
- Region [1,min(S,1+R)]: J'(t)=k(S−t)(t−b−2)/(S−b)≤0; J(1)=λ_b(1)=(1−2b+bS)/(2(S−b)); λ_b decreasing in u ⇒ λ_b(u)≥λ_b(1).
- λ_b(1)−1/(2S)=b(S−1)²/(2S(S−b)) ✓; constant-cap region via q0exp(v)(1−v)≤q0 ✓.
- Endpoint S=u=1: F(t)→(1−b)/2=η_b, λ_b=1/2 ✓.
- Fixed-λ=1/2 comparison: λ_b strictly decreasing on (b,1] with λ_b(b)=k(b)>1/2>λ_b(1) (S>1) ⇒ unique u; old quotient has unique maximizer u₀<1 (strict decrease on (u₀,1] and on [1,S)); pointwise ≤ plus strict inequality at u₀ gives strict max comparison. η²/(λ−η) increasing in η ✓.
- CS4 square completion identical to PD1; min{·} bounds hold simultaneously.
- Automatic w_i=0 at S=1 with ≥2 positive recipients ✓.

## Scope limitations
Not re-derived: sharp outgoing theorem, negative-gap saving lemma, own-monotonicity/restoration, and the floor construction (treated as previously audited per root context). No tools executed; numerics are hand computations. Non-vacuity of the S=1, b_i≥1/2 class is not assessed.

## Verdict
**No substantive findings.** CS2–CS4 and the strict fixed-λ improvement are correct as stated; the conditional 1789/1280 theorem is correct but relies on an undefined `c` and an unstated bound L(K²/4)≥4/5 that should be made explicit.
