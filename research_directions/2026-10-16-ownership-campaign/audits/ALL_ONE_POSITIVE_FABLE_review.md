**Provisional verdict: no invalid step found in reviewed scope.** The most consequential unverified inputs are primitive properties cited, not proved, in this packet (own-coordinate monotonicity of the outer rule in the *hardware* coordinate, and all-profile coalition coverage); the new lemma (1)–(2) and the two-region maximization check out by hand.

## Findings

**1. (Low) Lemma (1) depends on T₋ᵢ = min(x,y) exactly** — `ONE_POSITIVE…txt:33`. The proof needs the opponents' stand-alone branch value to be the plain min of their raw pool totals, unaffected by per-owner long caps. If the primitive's coalition value were ever *smaller* than min(x,y) (e.g. capped-long min), surplus would be larger and the y<x case would not be covered. Consistent with M=Σ min(Hⱼ,Lⱼ) and the M₋ᵢ definition at line 46, so I accept it, but it should be stated as an explicit hypothesis. Verification: confirm the primitive's branch value is min(hardware, load) with no cap in the value function.

**2. (Low) Hardware-restoration monotonicity is cited, not shown** — lines 68–69, 144. At the underreport the raw hardware total is <1, so the outer q is .5exp(1−S′/H′) and restoring aᵢ changes both own term and q. For d′<a′ the own-hardware derivative is (1−q)−(a′−d′)·qρ/H′, nonnegative only via qρ≤½ and a′−d′≤H′. Plausible and consistent with the cited "own/cross monotonicity," but not re-derived here. Verification: point to the primitive's own-hardware monotonicity proof.

**3. (Info) Independently re-derived steps that hold:**
- (1): y<x case derivative −1+½e^{−y}(2−y)≤0, value ½ at 0; y≥x case max of ½e^{1−d}(d−x) is ½e^{−x}≤½. ρ≥1 always (any single raw ≥1 forces capped total ≥1).
- (3)–(4), R≤1 via S−d≤1−a, and d+R = max{d, S−M/2} exactly.
- Σ_{k≠i} g_k = g−r; q₀=½e^{−r}; saving (2/5)e^{−r−c}(g−r).
- Case g≥r+½: ∂ᵣ of −Be^{−r}(g−r) = Be^{−r}(g−r+1)>0; x·k(x) nondecreasing via (u+2)e^{−u}≤2.
- Case g≤r+½: coefficients ½−Be^{−r}>0 and e^{−r}[√e/2−B]>0; derivative sign B(2−r)−√e/2<0 using B<2/5, 2−r≤3/2.
- Both regions peak at g=1, r=½ giving 3/2−(1/5)e^{−1/2−c}.
- L″ formula correct; chord bound and K²/4<1849/2500 valid.

**4. (Info) Constant checker** (`verify_…py`): tail bound next_term/(1−x/(deg+2)) is a valid geometric majorant; 1957/720 is the degree-6 Taylor lower bound and 11743/4320 a valid upper bound; e-direction used correctly for C² (upper e → lower C). Margins are thin but rational: exp(171/250)<2 by ≈0.018; 7/5<C² by ≈0.0017.

**5. Scope confirmation.** Lines 8, 11, 17–18: hypothesis is F=H (P+M≥H). The conclusion ΣEᵢ≤(7/5)H is **not** a 7F/5 claim at physical-power bottlenecks; the document correctly disclaims this. Multiple-positive-gap case remains open (line 148).

## Scope limitations
- Did not re-audit NEGATIVE_GAP_SAVINGS beyond checking hypotheses (P+M≥1, z_k+g_k≤1 when g_k>0) match usage here.
- Did not run the checker; relied on the supplied JSON and code reading.
- Primitive definitions (local payment formula, outer pool-switch formula, coalition value) are inferred from usage in both files, not from a definitions file.

## Verdict
No findings of invalid steps in reviewed scope; two cited-but-unshown primitive properties (items 1–2) should be explicitly referenced.
