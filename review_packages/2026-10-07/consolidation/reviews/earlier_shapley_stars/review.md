**Provisional verdict: no blocking errors found in the self-contained derivations; two claims depend on material outside the packet.** Most important: the headline "$3/14$ exceeds the two-pool upper bound $1/(2e)$" (earlier_incentives.tex L306–307) is *not* established by anything in the packet.

## Findings

**1. (Medium) hist:small-stage-lower — binding bound is imported, not proved.** L311–312: the first bound $(k-1)/(2(k+3))$ is cited from `Theorem~\ref{thm:unrestricted}` (not in packet). The bound actually proved here, $(k-2)/(2k+3)$, gives $2/11\approx0.1818$ at $k=4$, which is *below* $1/(2e)\approx0.1839$. So the comparison at L307 and L327–328 rests entirely on the external theorem. Verification: supply thm:unrestricted (with its $r,t$ parametrization) or reword to state only $2/11$ in-packet.

**2. (Low) Undefined $H_i$ and unverified $H_i\le M_i$.** L19, L90, L195: all floor guarantees assume $H_i\le M_i=T-v_c(N\setminus\{i\})$ (used explicitly at L40, L90, L195). The cross-partition lower bound in hist:aggregate (L55–57) further needs $H_i=1$ exactly at $(1\mid1)$ to get $p,q\ge\alpha$. Neither $H_i$'s definition nor Lemma lem:cap (L201) is in the packet.

**3. (Info) Checked and consistent.** I recomputed the following and found no errors:
- hist:aggregate: $\sum_jp_j=1$, $(c_i-C_j+T)_+\le c_iT/C_j$, $p_j\ge T/(kC_j)$, budget $(k+1)T/2$, convex combination giving $\beta=\alpha$, cross-partition lower bound.
- hist:shapley-half: $f_a(z)+f_a(D-z)\ge f_a(D)$; Chebyshev/Cauchy–Schwarz error terms yield exactly $\tfrac12+\tfrac{\sqrt2q^2}{q^3-1}+\tfrac1{2q}+\tfrac1{\sqrt2q^2}$.
- hist:four-shapley: predecessor grouping of $\phi_1$ (weights $1/4,1/12,1/12,1/4$), $6\phi(\{2,3\})$ identity, all three $K$-cases, $\phi=(7/12,1/4\mid7/12,7/12)$, and $(41/60,41/60\mid11/60,11/60,4/15)$ with $49/25<2$.
- hist:exponential: budget $T[1+ue^{-u}/2]$, floor via $te^{-t/T}$, short-region derivative $1-p(1+\rho)\ge0$, seam continuity ($x/2$ both sides), and the $1/8$ lower bound ($y_3(a),y_0(b)\le4\beta$).
- hist:softmax: short-region bracket reduces to $1-\sum_{\ell\ne j}u_\ell e^{-u_\ell}$; $F\le b_k$ via $(u-b)e^{-u}\le e^{-1-b}$; $k=4$ derivative $(1-3/e)/(1+3/e)^2<0$; $1683/5000>1/3$.
- hist:capped-totals: $[x+(1-x)/(kx)]^{-1}=q^2/(2q-1)$ at $x=1/q,k=q^2$.
- noise:shapley-paths: veto/outsider shares, $25/52$; balanced-pool argument: $md<n\le(m+1)d$, $j/n-(m-1)/m\ge1/(mn)\ge1/M^2$, band placement in the type-$m$ all-outsider gap, $Q=rq_m-q_n\ge M+1$, lower-band exponents $1/[M(M+1)]$ and $1/(2M)$, unanimity-band bound $(M-1)L^{-2M}$; $M=4,L=10^{40}$ gives $0.43001<0.431$. Three-pool calibration integrals: $7/20$, $101/140$, $9/28$, $139/140$.
- noise:star-domain: $T_e(t)=\min(T,b_e+t)$ via parametric cuts; $\max_{x<1/B}x(1-Bx)/(1-x)=(\sqrt B-\sqrt{B-1})^2\le1/(4(B-1))$; mixture cost $\le BT_e(t)$; $B=2+\sqrt L/2$ satisfies $4(B-1)^3\ge LB$. Path-star bound $1/(4(B-1))$ at $u=2(B-1)$; complete-DAG $2^r$ cuts and $3T$ bound.

## Scope limitations
Not verifiable from packet: Section sec:model definitions ($H_i$, admissibility, "payment-only"), Lemma lem:cap, Theorem thm:unrestricted, Section sec:banzhaf, Huang Prop. 1, Kurz Def. 6.11, and the meaning of $L$ (assumed max path length) in the star-domain section. No tests were run.

## Verdict
**Findings (non-blocking in reviewed scope).** Formulas and the balanced-pool asymptotic argument check out. The only substantive issue is that the $3/14>1/(2e)$ comparison is unsupported within the packet (Finding 1); Finding 2 is a definitional dependency.
