**Provisional verdict: no findings in reviewed scope** (two low-severity presentation gaps). The most important concrete check: the post-switch inequality (d−u)/2 ≤ V in §3 holds because d−u ≤ d·e^{−u} on 0≤u≤d≤1 (RHS−LHS is 0 at u=0 with derivative 1−d·e^{−u} ≥ 0), and the proposed m-branch lower family does realize Σ raw = C with ε=1/(2m)→0, so C is the sharp ε→0 constant of (D).

## Findings

**1. Low — §4 lines 95–99: monotonicity of f applied in an order not stated.**
f(v,t)=v[1+log(t/v)] is monotone on 0<v≤t, but after the short stage T may be smaller than V_full (e.g. the deviator held most of the short pool), so f(V,T)≤f(V_full,T) is not directly available. The valid route is f(V,T)≤f(V,T_full) (V≤qT≤T/2≤T_full) then f(V,T_full)≤f(V_full,T_full). Conclusion unaffected; the text should state the order. Verification: check ∂_v f=log(t/v)≥0, ∂_t f=v/t>0 and the domain conditions in that order.

**2. Low — §7 line 182: substitution of A≤11/10 into A²/[2(A+B)] needs stated monotonicity.**
A appears in the denominator. It works because d/dA[A²/(A+B)]=A(A+2B)/(A+B)²>0 and the expression decreases in B, but neither is written, and `check_incoming_diffuse_constants.py` only checks rational comparisons (it does not verify exp(x)≤1/(1−x), the alternating Taylor bound, or this monotonicity). Add one line.

**3. Low — line 190 dependency citation mismatch.** The file imports "SHARP_OUTGOING_LOSS.txt" while the audited-dependency list names "SHARP_NONLINEAR_OUTGOING_LOSS.txt". Confirm these are the same result and that its statement is a bound on Σ_{k≠i}(z_k−z_k^i)_+ aggregated over all branches in terms of the full z_i, which is what (4) needs.

**Verified steps (no issue found):** §2 derivatives q′=q(ρ−m)/T≥0 (ρ≥m), z_k′=q′(d_k−s_k)+q·1_{cap}; capped recipients cannot gain (d_k=T≥s_k); uncapped gains sum ≤q′Σs_k≤qρ≤1/2; V_i nonincreasing in the short stage since q increases with T. §3: ρ drops by exactly u pre-switch; exp(u)−1≤Ku on [0,1]; switch case requires v<1 ⇒ no other caps, u=ρ−1∈[0,d], uv≤d; combined ≤eVρ and ρ≤1+log(T/(2V)). §4 log-sum direction correct; zero cases closed (q>0, 1−q≥1/2 forces both coordinates 0). §5: S≥1 from Z≥M and bottleneck; (5) via 1-Lipschitz min with own term unchanged; (7) via g(t)=t−1/t−2log t, g′=(1−1/t)²≥0, g(1)=0; positive-gap opposing-short case correctly uses D_h≤1 and a_i<d_i≤S_i; negative-gap opposing-short case uses q_h≤1/2 and b_i=d_i<1; zero-gap a_i=d_i=1 handled by ceiling. §6: G_−≤Σa_i=1, maximizer r=B/A gives (A/2)e^{−B/A}; ε=0 yields exactly C. §7 rational chain reproduces 6931/4995<7/5<(161/136)².

**Lower family check:** branch tie gives z=1/(2m) each; outer opposing total 2, no caps for m≥2 (max b=3/(2m)≤3/4), hardware short, ρ=2, raw sum =1+q0=C; H=1≤P+M=2. E_i≥N_i via truthful reports in the box. Hence sup Σ E_i/H ≥ C for every ε=1/(2m), matching (D)'s ε→0 limit. The claim is correctly scoped: sharpness of the limiting constant only, not of (D) at fixed ε.

## Scope limitations
I did not verify the imported primitive own-monotonicity, coverage, or the outgoing (e−1)z_i theorem beyond the context statement; I did not execute the checker. No attempt to evaluate the exact envelope E_i.

## Verdict
No findings of substance; three low-severity clarifications. (I), (D), (F) and the asymptotic sharpness of C hold on the evidence in the packet.
