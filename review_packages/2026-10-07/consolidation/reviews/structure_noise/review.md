**Provisional verdict: findings (one unjustified step in the antichain reduction; remaining transcriptions check out numerically and logically within the packet).**

## Findings

**1. Medium — `structure_and_noise.tex` lines 121–123 (Prop. `noise:antichain`, reduction part).**
The step "No original minimum cut can contain $e$, since such a cut would give $c_e=\delta_e$" is asserted without argument, and the implication "$C^*\ni e \Rightarrow \delta_e=c_e$" is false in general. Counterexample: edges $m:s\to u$ (cap 1), $e:u\to t$ (cap 1), $uv$ (cap 1), $f,g:v\to t$ (cap 1 each). Then $T=1$, $C^*=\{e,f,g\}$ is a minimum cut, $A=\{e,f,g\}$ is an antichain, $R(A)=1=R(\{f,g\})$, so $\delta_e=0<c_e=1$. The conclusion "there is a common unchanged minimum cut disjoint from $A$" therefore rests on an unproven step. Impact is bounded because the proposition explicitly asserts nothing about existence of a violating $A$, but the stated reduction should not be cited as established. *Verification:* supply an argument that uses the violation hypothesis ($y(A)>R(A)$, minimality), or weaken the conclusion to "no minimum cut of $G_A$ contains $e$".

**2. Low — lines 17–19 (tail bound $\Prob(\sum a_eU_e\le1)\le(e/\rho)^\rho$) and the $U(K)$ formula.**
Cited as "usual" and not proved in the packet; the derivation of $U(K)=a_K+1/\log a_K$ from a union bound and the integral tail is consistent (I checked the tail integral $\le 1/\log a_K$), but the base inequality for unequal $a_e\in[0,1]$ is external.

**3. Low — line 184 vs. 186 (Prop. `noise:series`).**
The first claim is only proved when all block members share $d(q)$ at every underreport; this holds for "no internal attachments" as stated. Fine, but note the collapsed noise remark (Beta$(1,k)$) implies the series block is *not* an instance of the uniform-law classification; scope consistent.

Items I verified and found correct (not findings): hinge formula and $\delta_{eh}\le f_e$; $z\le r\le 2z$ via concave $g$; bound (A) and the two-edge/bundle cases including $\delta_iW\le BD_i$ (requires $W\ge B$, which follows from $\delta_i>0$); cut-height bound $K\ge\ell+r(r-1)/2$, $\ell\ge2r-1$, and the Fibonacci counts ($\sum(2r-2h+1)=r^2$, $\sum h(2r-2h+1)=r(r+1)(2r+1)/6$); the $5/12$ event in the series example (simplex volume $4^{-m}/m!$, Chebyshev $4/(3M)$); Bernoulli upper (log-sum-exp convexity, Chernoff/union, integration), monotonicity/invariance argument, (B), the two-owner identity and both lower-bound regimes (including the $m\ge\lfloor\cdot\rfloor$ loss absorbed by $e^h/h\ge e$); the $O_X(K)$ upper with $A_\mu$; the nonconstant-law constants ($a\nu+b\mu=\mu-d/4$; $a\mu s>\mu+d/2\iff(\mu s-\nu)^2>0$), Hoeffding ranges, union bound $\le 3/16$, and both $K$ formulas/exponents; $\sqrt K/64$; arrival-order $2KT$ and $K(1-1/(B-1))$; both deletion examples ($\beta/3$, $\beta(1-\beta)/6$, $K/72$ normalization); $\E W_T=187/(8000T)$, $3929/3024000$, the scale-envelope gaps $g_j-g_i$, variance/Chebyshev $\le1/6$, balanced variant; the ceilings ratio $\to4/q$ and $\log K/\log\log K\sim 3q^2/2$; formula (C) via Dirichlet integrals, $7627/134400000$, $1161/44800000$, $23/100800$; $q_h=5/6+h/[12(1+h)^2]$, $q_1-q_{.1}=27/1936$.

## Scope limitations
- Theorem `prod:upper` and the coalition-coverage/monotonicity-of-$z$-on-TTSP facts are referenced but not in the packet; I did not assess them.
- No tools run; all arithmetic is hand-checked to stated precision.
- I did not attempt to decide whether a violating antichain exists.

## Verdict
**Findings.** One unjustified (and generally false) implication in the `noise:antichain` reduction; otherwise the structural, fixed-noise, and method-boundary transcriptions are internally consistent, with scope correctly limited to specific rules rather than all mechanisms.
