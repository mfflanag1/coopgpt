**Provisional verdict: no findings in reviewed scope (hand-rederived every inequality; nothing broke). Most important observation: the max-short/k=0 case is zero-slack — (RT_balance) holds with equality at L=λ=1 for every s∈(2/3,1), so the tilt f is exactly critical, not merely sufficient.**

## Findings

No correctness errors found. Verified items (all by independent hand derivation, no tools):

1. **Tilt function** (§1–2): f'(u)=9/10−2/(5u²), f'(2/3)=0 (C¹), f'(1)=1/2, f(1)=1/10; the three (RT_bounds) and (RT_hprime) bounds h'≥−1/6, h'₊≤11/18, h'₊≤1/9 (e=1) all check.
2. **Key identity** (§6 l.192–193): f(1)−f(s)=(9s−4)(1−s)/(10s), so (1+s)[f(1)−f(s)]/(1−s)−sf'(s)=(9s²+5s−4−9s²+4)/(10s)=1/2 exactly. Also (f(L)−f(s))/(L−s)=9/10−2/(5Ls) (numerator factors as (L−s)(9Ls−4)), so Q(L) is as stated and increasing. Both auxiliary-active and inactive endpoint expressions (l.174, l.194) rederive correctly from (RT_short) with P=λ/L resp. λ²/(sL), β=1/λ resp. 2/λ−1/s; the λ-slopes −9/20, −9/10 check.
3. **Water identities / dominant-cap lemma** (§2): β formulas from (m+1)λ+U=1+s and mλ+U=1 match; β≥1−s/λ uses k≤m≤(1+s−λ)/λ. Lemma R<L/2 vs R>1/2 is valid.
4. **Long derivatives** (§3): ηd≤5/18, η≤5/12<1/λ; nonmax case 1−2R≥3D(t−2/3)>(3/2)(t−2/3)≥λd|η| and (1−t)/t+5/18<1 check.
5. **Short easy cases** (§4) and **nonmax owner** (§5): P(1+βx)≤1/s (x≤1−s), 7/540 margin; inactive margin (λ−x)/(2λ)≥3V/4 verified via φ(t)=1/2−t/(4(2t−1))−(3/4)(t−2/3) concave, φ(2/3)=φ(1)=0; active margin (2s−1)/(2s)≥3V iff s≤2/3; (RT_cost) ratio 39/20−9t/20−9/(10t) increasing, =3/5 at t=1. Note the inactive margin needs P=λ/L≥λ, but the inequality survives since L>λ (l.144 bound is still valid; this step is implicit).
6. **Persistent D=A** (§7): exactly one positive cap =A follows from Σz>A; derivatives 1−h, ≥7/20, 1+h'(1−x) correct.
7. **Funding** (§8–10): K bound (actual (5+2R)R/(1+R)²≤4/3 gives 4/15, looser 3/5 suffices); 32(1+s)³−27(2s+1)²=(2s−1)²(8s+5) ✓; g'(s) numerator J=−27s³+34s²−21s+8 recomputed term by term ✓; J'(s) discriminant −2180 ✓; F(2/3)=125/972<g(s_*). Newton from J(0.749)≈−8.9e−5 gives s_*≈0.748994, g≈0.130125, consistent with the stated decimal. Attainment profile gives E=[1−2f(s)]λ³/s=g(s) exactly.

## Scope limitations
- Frozen water-product and concentration theorems taken as audited; not re-proved.
- No numerical/symbolic tools run; all algebra by hand, so arithmetic slips are possible though each step was cross-checked.
- "Balance ODE" (§6) is a design identity, not an ODE; terminology only.
- Derivative is discontinuous (payment continuous) entering the D=A face; monotonicity unaffected, but any later Lipschitz claim would need separate work.
- Sharpness is of this rule only, as the file states; no optimality or novelty assessed.

## Verdict
**No findings in reviewed scope.** The proof chain is complete and the claimed factor γ≈1.130125 is correctly derived and attained.
