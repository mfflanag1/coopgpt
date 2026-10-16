**Provisional verdict: no findings in reviewed scope.** The most delicate step — the untruncated floor (H7) — is correctly gated by (H3), and the overlap extension correctly replaces (H7) with the two-sided majorant k(t) ≤ ½·exp(1−t) plus the explicit Γ₋ᵢ charge rather than dropping the cap.

## Findings

No errors or missing hypotheses identified. Verified steps:

**(H3)** (HEADROOM §2): U_k>0 with Γ=0 forces u_k ≤ 1−U_k < 1, so p_k=u_k and p_k+z'_k ≤ 1; U_k=0 forces z'_k=0. Holds for deviator too (own monotonicity gives z'_i ≤ z_i ≤ U_i). Correct.

**(H4)–(H6)**: C_i = Z−z_i−M₋ᵢ ≤ ½ (complement surplus, M=1) and ≤ z_i+ε (half-marginal lemma; checked x·e^{−x} monotone on [0,1], q ≥ ½e^{m−x}). G = r+v is the identity Σ(d_i−a_i) = S−1. The v ≤ ½−ε bound uses qρ ≤ ½ for ρ≥1 and d_i ≥ z_i ≥ hardware-role_i. Z_neg ≥ v from (1−q)a_i ≥ a_i/2. All correct.

**(H7)**: d_i + π₋ᵢ + M₋ᵢ = S − C_i ≥ 1 for S ≥ 3/2; payment a_i + q g_i with q = ½e^{1−total}. Correct given (H3).

**Reduction (§5)**: exp(ε)+Ab = e^{1/2} exactly, so L1 = A0r+(A0−B)v; L2 slope e^ε−A−B<0 by convexity; v* and (α,β) algebra verified; min of increasing/decreasing lines ≤ intersection height globally; e^{−r}(sr+c) decreasing for r≥1 when s,c>0. All-r reduction sound.

**Interval coefficients** (certify_headroom_high_total.py lines 33–39): α decreasing in b (∂α/∂b = (B−A0)/(1+b)² < 0) justifies b_lo; β uses (1+h)/(1+b_lo) and A0−B_lo; L1(b) uses b_hi. B_lo/B_hi directions (ε−c bounded via CU/CL) correct. Taylor bounds: even-degree partial sum at negative x is upper, odd-degree lower; positive-x geometric tail valid for x<18. Crossing logic (steeper line is the min to the left) correct. Note the target margin is thin (1.40166 vs 1.4017 vs C² ≈ 1.401714) but structurally sound.

**(3) in OVERLAP**: g(t)=t−1/t−2log t has g'=(1−t)²/t² ≥ 0, g(1)=0, so f' ≤ 0 and f(1)=0 ⇒ f ≥ 0. Correct on both sides of the switch. Addendum: ∫(Σ_{w_k<t}U_k)dt = Σ(1−w_k)U_k = Γ₋ᵢ by algebra. N ≤ 1/8 and the 7/8+0.5267e^γ assembly correct (also when P_chord−N<0).

**THREE_CAP**: d_k > ½ for k∈J follows from p_k > 1−U_k ≥ (1−z_k)/2; |J|<2S correct. Off-J members never cap (π_k+U_k ≤ 1 with p_k<1).

**FINITE_CAP**: distributive identity (1) correct for both p_k<1 and p_k≥1 (q_k=0); exactness for O justified. LP feasibility, (4)≥(2), and dominance over layer-cake (min(v_k,q_k) ≥ w_k v_k, swap of minima, nested O∪A_t constraints present in (6)) all check. v₀ is purely an accounting aggregate; no report or incentive constraint is attached.

## Scope limitations

- Cannot execute scripts; the "27/14 intervals, worst 1.40166" figures are unverified, only the arithmetic structure.
- Half-gap incoming response (form (1−z_k)/2), negative-gap savings coefficient 4/5, k-as-valid-envelope below the outer switch (FIXED_OPPONENT_COALITION_FLOOR), and own/cross monotonicity are accepted as previously audited; not in packet.
- Thin margin: a factor error of ~3×10⁻⁵ anywhere in the certificate would break (H2); none found.

## Verdict

No findings in reviewed scope.
