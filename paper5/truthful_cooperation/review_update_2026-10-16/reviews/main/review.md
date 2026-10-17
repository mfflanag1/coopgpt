**Provisional verdict: no substantive findings in reviewed scope.** The new Section 3 proofs check out line by line against the frozen notes; the only items are low-severity presentation/verification gaps. Most important: the $n$- and $d$-lower bounds invoked in §3.4 and the conclusion ("earlier logarithmic-over-logarithmic lower bounds") are never stated or located in the main text.

## Findings

**1. Low — §3.4 (l.494–495), Conclusion (l.672–674): unlocated lower bounds in $n,d$.**
The text asserts unrestricted lower bounds of order $\log n/\log\log n$ and $\log d/\log\log d$ but gives no theorem number or derivation. They are derivable from Theorem 4.2's construction (one owner and one resource per edge, $n=d=k(2R+3m)$, $\log n=(1+o(1))d_0\log d_0$), but a reader cannot verify this from the manuscript. Verification: add a one-line corollary after Theorem 4.2 or cite the supplement theorem by name.

**2. Low — §3.4 (l.500–505): Bachrach et al. (2009) "Theorem 3.5".**
The theorem number and the phrase "the corresponding superadditive-game bound" cannot be checked from the packet (arXiv:0907.4385v1 not supplied). The distinction drawn (static CoS vs. cross-report linking) is correctly argued: the uncapped support $\ell_c$ is an efficient core allocation at each profile, so static CoS is trivially zero. Verification: confirm theorem number/statement in v1; consider "cost of stability is zero" → "no supplemental payment is needed" to match their definition.

**3. Informational — §3.1 (l.364–371): redundant segment argument.**
The supergradient at a relative-interior point of $F_x$ already majorizes $f$ on all of $F_x$ (standard finite-dimensional result); the segment/concavity step is correct but unnecessary. No error.

## Items verified (no finding)

- Relative support: $u\ge0$ on active coordinates (monotonicity vs. support inequality), $u\cdot x=f(x)$ (homogeneity above/below), $u\cdot z\ge f(z)$ on $F_x$ without continuity; min-norm selection well-defined (nonempty closed convex set).
- Fixed-mask eligibility: coverage via cap-or-face argument (needs only $v(S)\le T$); open marginal $\ge\ell_{x_B}(b_i)$ since $x_B-b_i\in F_{x_B}$; own-monotonicity of closed (own-excluded $x_B$, $+\infty$ off-face, cap $T$ nondecreasing) and open owners.
- Endpoint identity: $-g'=\sum_i m_i$ (diagonal derivative of multilinear polynomial), sign of integration by parts, $g(0)=T$, $g\ge0$.
- $B_n(a)$: using $g(q)\ge(1-q)^nT$ in both $(1-a)g(a)$ and $\int_0^a g$ gives exactly $n[1-(1-a)^{n+1}]/(n+1)$; $a=\sqrt{2/(n+1)}$ equalizes; $B_1(a)=1$; $a=1$ at $n=1$ handled.
- Reciprocal lemma: $\min\{u/S,1\}\le 2u/(u+S)$ in all cases including $u>0=S$ and $0/0=0$; conditioning identity and $\Pr(S_B>0)$ correct; two equal weights give exactly $2q$.
- Coordinate domination: off-face case, $u_e(x_B)_e\le T$, subadditivity of $\min\{\cdot,1\}$, $x_B=b_i=0$; also valid for the fixed-priority global form.
- $D_d(a)$: $\int_0^a q/(1-q)=-a-\log(1-a)\le a^2/[2(1-a)]$; $a=1/(1+\sqrt d)$ gives $1+2\sqrt d$ exactly.
- $dT$ baseline: $c-b_i\ge(1-\alpha_i)c$, $\sum_i\alpha_i\le d$, coverage via uncapped support at $c$.
- Whole-rule selection from public $(n,d)$ before reports; abstract/intro/conclusion wording consistent ("remain open", "no polynomial preprocessing", "restricted barriers are not lower bounds").

## Scope limitations

Supplement (ESM 1), verification code, and Bachrach 2009 not supplied. Section 2 and Section 4 proofs not re-audited beyond references. No tests executed.

## Verdict

No findings of mathematical error or claim inflation in the reviewed section; two low-severity verifiability gaps (unlocated $n,d$ lower bounds; unchecked external theorem number).
