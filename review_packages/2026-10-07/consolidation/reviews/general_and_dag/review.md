**Provisional verdict: no substantive correctness findings in reviewed scope.** I rederived the critical steps of both proofs and the two counterexamples; the transcription preserves every hypothesis and quantifier of the audited notes. Most important item is a low-severity statement wording issue (Theorem `prod:upper`, line 20), not a mathematical gap.

## Findings

**F1 (Low, line 19–20).** "an eligible deterministic rule has factor $C_j(K)$" is grammatically ambiguous between ∀ and ∃. The notes (GENERAL_PRODUCTION_THEOREM.txt:20) say "there is a … rule". Suggest "there exists an eligible deterministic rule with factor…". Only the existential is proved.

**F2 (Low, lines 310–312).** "This proves why the shared fans above, and their explicit auxiliary budgets, are necessary" overclaims. The proposition shows only that the naive two-owner subdivision admits an efficient rule (which I verified: payment is $0$, $Q_e/2$, $Q_e$ across the mate threshold with $d$ fixed in the last two cases; coalition value is exactly $v_d(S^*)$; $p(S)\ge Q(S^*)\ge v_d(S^*)$; total $=T$). It does not show shared fans are necessary. The notes say only "would be invalid" (SIMPLE_DAG_SHARP_LOWER.txt:445–446). Suggest "motivates" or "shows the naive reduction fails".

**Rederived steps (no defects found):**
- Raw selection vs capped payments (lines 34–40, 76–79): open contributions satisfy $W\cdot b_i\le f(\sum B_hb_h)\le T$, so $\sum_iB_ia_i(W)=f(\sum B_ib_i)$; hence $q\sum_ip_i=Z-g$. Monotonicity of $p_i^q$ uses only that $W$ is $b_i$-independent given $B_i=0$ (report-independent priority, line 4).
- Endpoint inequality (67–72): $f(\text{on})=w_1\cdot(\text{on})$, $f(\text{off})\le w_1\cdot(\text{off})$, difference $\ge w_1\cdot b_i\le T$; averaging gives $r_i^q\ge z_i^q$.
- Integration (84–86): $\int_0^\eta(1-q)g'=(1-\eta)g(\eta)-T+\int_0^\eta g$, giving the stated $T-(1-\eta)g(\eta)-2\int g$; sign and factor 2 are correct.
- Chernoff (93–104): $u\mapsto\log(q+(1-q)e^{-\lambda u})$ has second derivative $\lambda^2q(1-q)e^{-\lambda u}/(\cdot)^2\ge0$; chord bound valid; tail integration gives $(\log K+\lambda+1)/\alpha$. Monotonicity of $q+(1-q)/j^2$ in $q$ justifies line 107; $\alpha_j>0$ for $j\ge2$.
- Constant assembly: $j[\tfrac1j\cdot\tfrac{T(\log K+2\log j+1)}{\alpha_j}+T]$ matches (prod:constant).
- Uncapped counterexample (150–159): dual vertices and $T=2-1/M$ confirmed; $2\int_0^{1/2}q(1-q)dq=1/6$; efficient rule covers $\{1\}$ (value $c_1/M$), $\{2\}$ (value $0$).
- DAG (223–237): weights $(m-d_0)$ and $d_0$ yield coefficient $A=(d_0+1)m-d_0^2$ on both sides and $(m/R)Q$; multinomial identity $\mu(\nu)\nu_h=(p_h/p_{h+1})\mu(\nu')\nu'_{h+1}$ confirmed; $Ap_h/p_{h+1}=\alpha(h+1)$; budgets $Y,Q$ disjoint so $\max\{1+\alpha,m/R\}$ is correct with $R=m$. Tail bound $(1-1/Z)^k\le e^{-k/Z}$, $d_0e^{-2\ell}\le d_0/(d_0+1)^2\to0$. $\log Z=(1+o(1))d_0\log d_0$ since $\log\lambda=2\log d_0+O(\log\log d_0)$; $4m\log2=o(d_0\log d_0)$. All-$K$ inversion at line 291 gives $\log K_{d_0}\le(1-\varepsilon+o(1))\log K$.
- Lower transfer to $\mathcal B_{\rm prod}$: restricting a bundle-eligible rule to scalar reports $b_i=c_ie_i$ preserves eligibility, so the DAG lower applies.

## Scope limitations
No tools; only the three supplied files reviewed. Structural-cut counts $C_{m,R}$ and small-instance flow checks in the notes are unverified here. Symmetrization averaging over module permutations is accepted on the series-minimum argument (line 214); I did not enumerate automorphisms.

## Verdict
**No substantive findings in reviewed scope**; two low-severity wording items (F1, F2). No transcription weakening or lost hypothesis detected relative to the audited notes.
