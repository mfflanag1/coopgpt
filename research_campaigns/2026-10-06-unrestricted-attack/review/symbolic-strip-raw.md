## Result

**Scope.** Everything below is hand algebra on the supplied encoding (ENCODING.txt lines 24–40, verify.py lines 16–55). I had no execution tool, so verify.py was **not** run; coefficient cancellations are shown explicitly so the controller can check them, and I give a JSON instance for the checker.

### 1. Reading of the witness (what the 37 rows actually do)

Notation at state $(a,b,c)$, $c=k-a-b$, $H=m$: $x$ = type‑0 low pay, $p,q$ = type‑1 low/high, $r,t$ = type‑2 low/high. The certificate is built from one repeated 4‑row "local block" plus "dilution" of exported owners into neighbouring states:

- At $J=(2,54,968)$ the weights are budget 17470, cover$_{w=1}$ 34940, cover$_{w=3}$ 17470, cover$_{w=4}$ 17470, i.e. exactly $1:(m-2):1:1$ with $m=4$ (JSON lines 193–201, 594–677).
- Its two export edges (mono $h=0$ weight 174701 → $G=(1,55)$; mono $h=1$ weight 1886769 → $I=(2,53)$) are absorbed by the sink budgets: $3177\cdot55=174735\ge174701$ and $2922\cdot2\cdot969=5662836 \ge 1886769+974\cdot969+2921\cdot969$ (all cover uses of $t_I$). The remaining sink states repeat the pattern at lower weight (G is a ratio‑2 block without the $w=4$ cover because its $q$ is consumed by the inflow).
- $B$‑coefficient $100033$ and constant $210709$ re‑sum exactly from the rows (checked by hand).

### 2. Proved 8‑row parameterised theorem (the "symbolic positive combination")

Fix $m\ge3$, $H=m$, $k\ge b+2$, $1\le b$. States $S=(1,b,c)$ with $c=k-1-b$, $S'=(0,b+1,c)$, $S''=(1,b-1,c+1)$.

| # | row | weight |
|---|---|---|
|1| budget $S$ ($T=m$) | $1$ |
|2| cover $S$: $[0,m,0],[1,0,1],[2,0,1]$ (worth $m$) | $1$ |
|3| cover $S$: $[0,m-1,0],[1,m-1,0],[2,0,1]$ (worth $m-1$) | $1$ |
|4| cover $S$: $[0,1,0],[1,1,0],[2,1,0]$ (worth 1) | $m-2$ |
|5| mono $S$, $h=0$ (→$S'$) | $2m-3$ |
|6| budget $S'$ ($T=2m-1$) | $(2m-3)/(b+1)$ |
|7| mono $S$, $h=1$ (→$S''$) | $(m-2)\,b$ |
|8| budget $S''$ ($T=m$) | $(m-2)\,b/(2(k-b))$ |

Coefficient check (all other coordinates are strictly budget‑negative):
- $(S,0,\text{low})$: $-m+m+(m-1)+(m-2)-(2m-3)=0$
- $(S,1,\text{low})$: $-(m-1)b+(m-1)b+(m-2)b-(m-2)b=0$
- $(S,1,\text{high})$: $-b+b=0$; $(S,2,\text{low})$: $-(m-2)c+(m-2)c=0$; $(S,2,\text{high})$: $-2c+c+c=0$
- $(S',1,\text{high})$: $(2m-3)-\tfrac{2m-3}{b+1}(b+1)=0$; $(S'',2,\text{high})$: $(m-2)b-\tfrac{(m-2)b}{2(k-b)}\cdot2(k-b)=0$
- Constant $=m+(m-1)+(m-2)=3m-3$.

**Theorem (8 rows).**
$$B\;\ge\;\frac{3m-3}{\,m+\dfrac{(2m-1)(2m-3)}{b+1}+\dfrac{m(m-2)\,b}{2(k-b)}\,}\qquad(m\ge3,\;H=m,\;1\le b\le k-2).$$

Intermediate identity worth recording (rows 1–4 only, any $a\ge1$): $\;mB+(2m-3)\,a\,x_S+(m-2)\,b\,p_S\ge 3m-3$; rows 5–8 are the dilution inequalities $x_S\le q_{S'}\le \frac{(2m-1)B}{b+1}$, $p_S\le t_{S''}\le\frac{mB}{2(k-b)}$.

**Improvement over 2.** Exceeds 2 iff $\frac{(2m-1)(2m-3)}{b+1}+\frac{m(m-2)b}{2(k-b)}<\frac{m-3}{2}$ — impossible for $m=3$, possible for every $m\ge4$ once $k$ is large. Explicit instance: $m=H=4$, $k=4096$, $b=180$: $B\ge 9/(4+\tfrac{35}{181}+\tfrac{180}{979})=\mathbf{531597/258547\approx2.0561}$. Checker input:
```json
{"schema":1,"k":4096,"m":4,"high":4,"claimed_total_factor":"531597/258547","rows":[
{"kind":"budget","state":[1,180,3915,0,0],"weight":"1"},
{"kind":"cover","state":[1,180,3915,0,0],"choices":[[0,4,0],[1,0,1],[2,0,1]],"weight":"1"},
{"kind":"cover","state":[1,180,3915,0,0],"choices":[[0,3,0],[1,3,0],[2,0,1]],"weight":"1"},
{"kind":"cover","state":[1,180,3915,0,0],"choices":[[0,1,0],[1,1,0],[2,1,0]],"weight":"2"},
{"kind":"mono","state":[1,180,3915,0,0],"h":0,"weight":"5"},
{"kind":"budget","state":[0,181,3915,0,0],"weight":"5/181"},
{"kind":"mono","state":[1,180,3915,0,0],"h":1,"weight":"360"},
{"kind":"budget","state":[1,179,3916,0,0],"weight":"45/979"}]}
```
(Smallest $k$ for $m=4$ with this block: $b=139$, $k=2364$ gives $35/140+556/2225<1/2$.) At $k=1024,m=4$ the block only gives $\approx1.886$ ($b\approx94$); the 37‑row chain reaches $2.106$ by letting sink states carry their own cover rows — that amortisation is what the chain adds.

**Limit.** With $b\sim\sqrt{k}$ the denominator is $m+O(m^2/\sqrt k)$, so for fixed $m$: $\liminf_{k\to\infty}B\ge 3-3/m$, and $\sup_m\to3$. Concretely, for any $\delta>0$, $b+1\ge4m^2/\delta$ and $k-b\ge m^2 b/(2\delta)$ give $B\ge(3m-3)/(m+2\delta)$.

### 3. Strip ceiling (why "approaching 3" is the end of this strip, and divergence is impossible in it)

A strip‑feasible primal with $B=3-3/m$ exists for every $k$, $H=m$, any $s_0$ (not only $\le2$), $s_h=0$ for $h\ge3$:
- $a\ge1,b\ge1,c\ge1$: $x=p=0,\;q=1/b,\;r=1/c,\;t=(m-1)/c$ (budget $=1+(m-2)+2(m-1)=3m-3$; every coalition: $w=m$ forces $v_1=1,v_2\ge1$ → pay $\ge m$; $w=m-1$ forces $v_2\ge1$; $w\le m-2$ pays $\ge w$).
- $b=0$: $x=1/(ma)$, same $r,t$ (budget $3m-3$; mono $x\le q$ at $(a-1,1)$ holds since $q\ge1$).
- $a=0$: $p=0,q=m/b,r=1/c,t=(m-1)/c$ (needs $m(4m-4)\le(2m-1)(3m-3)$, i.e. $(2m-3)(m-1)\ge0$).
- $c=0$: $x=0,p=1/b,q=m/b$ (budget $2m-1\le3m-3$). All mono rows hold with $x=p=0$ or the checks above.

By weak duality **no certificate using only types 0,1,2 at $H=m$ can exceed $3-3/m$** for any $k$. This matches all supplied numbers ($1.9238\le2$, $2.1095\le2.25$, $2.2233\le2.5$, $2.1719\le2.7$) and shows the strip value is exactly $3-3/m$ in the limit; passing 3 or diverging requires pools with $\ge3$ high owners (outside the strip) — not investigated here.

### 4. Relation to STAR_BARRIER.txt

The 8‑row block is a one‑source/two‑sink structure: the source $S$ exports two different owner classes (type‑0 low → $S'$, type‑1 low → $S''$). STAR_BARRIER lines 22–30 exclude multi‑exporter sources, so there is no conflict; the escape from 2 comes from exporting into classes with many copies ($b+1$ and $2(k-b)$ owners) so the per‑owner budget share diluting the flow is $O(1/b)$, $O(b/k)$.

### Unfinished / limitations
- verify.py not executed (no shell tool); hand verification only.
- The finite‑$k$ chain recurrence (how the 37‑row witness amortises sink budgets through $a=2$ states) is **not** derived in closed form; the exact inequalities needed are the block identity $mB+(2m-3)a x+(m-2)bp\ge3m-3$ at each $a\ge1$ state together with inflow budgets $\mu_{S'}(b+1)\ge$ inflow$+$own‑cover uses of $q$, and likewise for $t$. Its optimum is the strip LP; its limit is settled above.
- Validity of all rows as necessary conditions rests on ENCODING's symmetrisation argument (taken as supplied evidence, not re‑proved). No field significance or novelty claimed.
