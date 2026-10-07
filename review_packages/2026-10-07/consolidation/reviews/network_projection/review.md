**Provisional verdict: no substantive findings in reviewed scope.** Every inequality, closed form, cut count, and effective-capacity formula I could check by hand is consistent; the mechanism-specific vs. unrestricted-lower distinction is drawn correctly throughout (lines 176–177, 345–349, 444–445, 595–613, 619–621).

## Findings

**1. (Low) Bundled-bridge proof cites `net:conditional` outside its stated hypothesis — lines 205–206.**
Eq. (net:conditional) is derived in the TTSP proof under co-cut independence ($A$ constant in own report). On $H_k$ that hypothesis fails: $x,w$ share cut $\{x,w\}$, yet $d_w=\min(w,y+\min(x,h))$ depends on $x$ and $d_x$ depends on $w$. The conditional identity $D_e\Pr(e\in W\mid U_{-e})=\min\{d,(B-A)_+\}$ still holds as a pure probability computation, and the proof then verifies monotonicity of the *net* integrands directly (I rechecked all five: each listed variable enters with the stated sign; e.g. for $x$: $Z+\min((W-Y)_+,H)$ with $Y$ fixed). So the result is correct, but the text should say the identity is being used without the independence step. Verification: add one sentence noting $A$ may vary and that monotonicity is checked on $B-A$.

**2. (Low) "every real profile" — lines 86, 190, 394.** Should read "nonnegative real profile"; the rule is undefined for negative capacities.

**Checks performed (no errors found):**
- Lemma 1 budget: Jensen with exponent $a_e\le1$, $\mathbb E e^{-tU}\le 1/t$, union bound, derivative $-\ln s$, tail integral $1/\ln R_K$ — all valid.
- TTSP: $D_e=\min(c_e,L_e)$ agrees with the general prefix/suffix formula; co-cut-independence argument (LCA parallel ⇒ no series sibling contains $e$) is correct.
- Global-cap counterexample: $\mathbb E A_T^r$ moment formula, $\pm$-part identity, $r_4=64/125$, ratio $2\epsilon(n+1)^2/(n^2(n+2))<1$ — verified.
- Wheatstone failure: effective caps ($D_w=x+\epsilon\le1$ at $x_1$), score cancellations, $\mathbb E(R-P-a)_+$ formula (checked value $7/48$ at $a=0$ and density 1 at 0), $g_0,g_1$ with matching value at $1/2$, $F_R$ convolution. Numerically $I(x_0)-I(x_1)\approx4.04\times10^{-6}$ and $\approx6.74\times10^{-6}$, matching the stated rationals; error terms at $k=10,14$ are $\approx0.8\times10^{-6}$, so the drops are positive.
- Envelope upper: shared-uniform lemma (reflection, convex CDF, $N\le B$ cross-multiplication) and the scaling inequalities $xD_h(c)\le D_h(c^t)\le D_h(c)$ are correct; summation gives exactly $KT$.
- Envelope lower: module cut enumeration ($2^{m+1}$), unchanged effective capacities in non-focal modules (needs $a+t>1+a/m$, true for $m\ge5$), $\mathbb E\min(uU,vV)$ and $\mathbb E\min(uV_1,vV_2)$ formulas, Hoeffding exponents ($m/200$, $m/800$, $9409/4500$, $1849/1125000$, $1024/1125$), Chebyshev constants ($1/120$, $5/72$), union-bound totals ($23/60$, $457/2304$), and $K$ exponents ($401r$, $19201r$) all verified.
- Projection: both core computations, dual-uniqueness argument, $\delta=520/9471$, drop $1270/9471$ verified.

## Scope limitations
- Theorems `prod:upper`, `dag:sharp`, the multi-glove lower bound (line 127–130), and archived $H=O(K^{3/2})$ results are referenced but not in the packet; their use is only for context, not in any proof here.
- Exact rational constants (lines 293, 298, 332–334, 339) were checked to ~3 significant digits by hand, not symbolically.
- Amigo–Belzarena–Vaton source not inspected; the document itself hedges this appropriately.

## Verdict
**No findings of substance in reviewed scope.** Two low-severity wording items; no missing assumptions, false inequalities, or improper all-profile/owner-count claims identified.
