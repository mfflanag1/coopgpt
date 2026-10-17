**Provisional verdict: no substantive findings in reviewed scope.** All three arguments check analytically; the one item worth tightening is a stated-but-uncredited hypothesis (positive homogeneity) in the three-block funding remark.

## Findings

**F1 (Low) — THREE_BLOCK_EXACT_STOP.txt line 10: "concavity bounds their sum by 3F((2/3)C)=2F(C)".** Concavity with F(0)=0 gives F((2/3)C) ≥ (2/3)F(C), the wrong direction. The equality (and the coverage claim "supporting-price coalition coverage") uses degree‑1 homogeneity of the packing LP value plus Euler's identity g(x)·x=F(x). True here, but the hypothesis should be named. Not load-bearing for the counterexample.

**F2 (Low) — RADIAL_MEASURE_COROLLARY.txt lines 22–26.** "The rest of the measure has the same one-sided limits" is imprecise when other atoms accumulate near x. The argument survives as inequalities: for r↑r₀, payment ≥ (3/2)r·ν([0,1/r)) → (3/2)r₀·ν([0,x]); for r↓r₀, payment ≤ (3/2)r·ν([0,1/r]) → (3/2)r₀·ν([0,x)). Suggest rewriting as liminf/limsup.

**Verified (no finding):**
- *Private DR (file 1).* F=min{T,K_P,K_Q} via complementary slackness is correct. Section 2 tie lemma: averaging two optimal axis duals forces F=T; p_*=0 ⇒ K_P=W, and K_Q=W ⇒ b·c≤Q ⇒ q_*=0. Section 3 antitonicity: on the P branch a·c>P persists along c→d, any switch to Q below ceiling would cross a tie, which Section 2 forbids; p_* nondecreasing ⇒ g nonincreasing; plateau/all-fit cases trivially ordered. Case ordering handles F=T=W. I recomputed the Section 5 example: breakpoints t=2/9, 2/3 (P=1) and t=4/9 (P=2); π values (7/9,5/18,25/36) and (8/9,5/9,5/9) are exact and satisfy c·π=T.
- *Measure corollary (file 2).* Atom at 0 is charged at g₀(0)=3/2 (LP dual at z=0 is unique p=q=0), giving unbounded payment; atom-free ⇒ payment (3/2)rH(1/r) exactly; A nonincreasing + A≤κ ⇒ H κ‑Lipschitz ⇒ density ≤κ, reducing to v2. v2's tables rechecked: base middle interval optimal dual set is exactly the segment (5/6,2/3)–(2/3,5/6) (vertex (1,0) ties only at s=4/9), giving conv{(0,1/8,0),(0,0,1/8)}; restored profile has unique optima; 17/15−112/99=1/495.
- *Three-block checker (file 3).* All 8 dual vertices verified (three lines concur at (1,1) since w=a+b); arrangement exhaustiveness is correct because the dual objective is convex piecewise-linear with coercive minimum at arrangement vertices, independent of (P,Q,c). Cell-overlap planes are nonzero since all (p,q) are distinct. Checker logic is sound: vertices as feasible nonsingular triple intersections (hence true extreme points), collinear points dropped by hull2, dedup by vertex set, centroid strictly interior per facet assertion, edge-2-incidence + Euler check, fan tetrahedra with |det|/6. I independently derived cells 6 and 7 at C analytically: 1/30 and 1/12 (and cell 7 at C′: 1/16) — matching. Both volume lists sum to 1; q(C), q(C′) components and y_A values (1071941/1468800, 7197403/9914400, loss 30559/7931520) are arithmetically consistent.

## Scope limitations
- No execution; JSON certificate not in packet. Root should confirm the asserted volume lists and `old>new`.
- Did not verify v2 Sections 2–3 beyond logic (Cesàro transfer looks correct; L>0 from H(1)>0).
- Historical novelty not assessed.

## Verdict
**No findings** affecting correctness. Two low-severity wording/hypothesis notes (F1, F2).
