**Provisional verdict: no substantive findings in reviewed scope.** The most important observation is that the exact-rational verifier certifies only the final arithmetic of (7); every probabilistic step (3)–(6) rests on the hand proof, which I re-derived and found correct.

## Findings

**1. (Low) Verifier does not exercise the probability model — PERSONAL_CEILING_OBSTRUCTION.txt lines 77–78, personal_ceiling.py lines 17–24.**
The script never constructs N, the graph, or any distribution; it checks three algebraic cancellations (lines 19–21) and evaluates `bound(q)`. The claim "exact rational verifier gives R_16<1/2…" is true only as a statement about (7). The validity of (3)–(6) is independent of the script. I re-derived them: the first-component minimum cut under ceiling m is δU_e+min((1−δ)U_a, mY)=X_m; under ceiling 1 it is X_1; exactly one bundle wins a.s.; (4) follows from the simplex CDF and Nx=2^m; (5)/(6) from the stated union bounds with t=(q−2)/(2q²)>0. All check. Suggested verification: state in the text that the certificate covers (7) only.

**2. (Low) Bernoulli inequality checked only for n<30 — personal_ceiling.py lines 30–35.**
The proof applies (1−x)^N≤1/(1+Nx) at N=m!q^m. The analytic proof at line 61–62 is correct ((1−x)^{−N}=(1+x/(1−x))^N≥1+Nx), so this is cosmetic, but the comment "independent check" overstates it.

**3. (Low) Budget bound inherits the prior U(K)T theorem under T‑clipping — lines 21–22.**
DAG_BASELINE.txt proves U(K)T with D_e‑clipping, not min(c_e,T). The argument transfers (a_e=min(c_e,T)/T≤1, the deterministic minimum cut keeps ρ=1 since clipping cannot lower a cut below T), but the text should cite the T‑clipped variant explicitly. Nothing else in (1) is in doubt: for B_e>T every minimum cut contains e, so c_e≤T and Σ_exc p_e≤Σ_{e∈C*}c_e=T.

**4. (Nit) `len(str(r.numerator))` — personal_ceiling.py line 28.**
`set_int_max_str_digits(0)` is applied only under `__main__`; importing `run()` on Python ≥3.11 raises at q=128 (denominators far exceed 4300 digits).

## Checks performed (no issues)
- Truthfulness: with others' capacities fixed by B_e (independent of c_e), the conditional payment is E[min(a_e,(B−A)^+)], nondecreasing in a_e=min(c_e,B_e). Correct.
- Infinite B_e (bridge): a^(e)=c, e in every cut, p_e=c_e; since every minimum cut contains e, c_e≤T. Covered by the "B_e>T" branch; no gap.
- T=0: B_e=0 gives a^(e)=0; B_e>0 forces c_e=0. All payments vanish. Correct.
- Counts: K=N+m+1, vertices m+N+2, owners m+2+Nm, L=m+1+N, T=1 (unique min cut {e,a}); ceilings (2) correct (B_a=min(m+δ,m)=m).
- v_c(S)=δ; (3) uses that bundle owners share one clipped profile, so Σ_j Pr(C_j wins)=Pr(Z<X_1).
- Asymptotics: (1−t)^m≤e^{1−q/2}; R_q=(4+o(1))/q; log K~3q²log q gives multiplier Ω(√(log K/log log K)). Numerically R_16≈0.46, R_32≈0.125, R_64≈0.0625, R_128≈0.031, consistent with the targets.
- Scope statements (lines 3–4, 86–91) correctly avoid inferring a general lower bound.

## Scope limitations
- U(K) and the "original effective-capacity rule is optimal on TTSP" claim (line 87–88) are external to the packet; not verified.
- No code executed; verifier reviewed by reading only.
- Did not audit the definition of "truthful" beyond own-report monotonicity, as used in DAG_BASELINE.txt.

## Verdict
No findings affecting correctness. Minor presentation/robustness items (1–4) only.
