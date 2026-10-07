**Provisional verdict: no findings against the mathematical claim in reviewed scope; minor findings on test evidence.** The most important point: the Section 3 invariance argument (conditions (a)/(b) plus lemma (4)) is correct as written, and I could not construct a counterexample; the weakest part of the packet is that the verifier lacks a negative control and never exercises the logarithmic tail bound.

## Findings

**1. (Low) Proof audit — Section 3 invariance holds.** Score(t) of cut C under mask b (b_e=0) = Σ_{h∈C,b_h=1} D_h(t) ≥ Σ D_h(0) ≥ V, with V = F(c·b) independent of c_e (Section 1 mask identity is correct: masked raw flows are feasible in c hence ≤ D(c), and D(c)·b ≤ c·b). So score(t)=V iff (a) and (b). Lemma (3): mixture (1−t/u)f₀ + (t/u)f_u has flow ≤ t on e, is conserved, and achieves the stated value through h — correct, and (4) follows with monotonicity. Hence the full minimizer family, and its first element under the fixed priority, is constant on c_e>0. Ties, zero other reports, and D_e=0 are all handled. Section 4 domination (uniform drop by D_e on containing cuts, strict dominance over excluding cuts, order preserved) is correct; sandwich (6) correct. Chernoff step: f''·g² = λ²q(1−q)e^{−λx} ≥ 0 so f convex, chord bound valid for a_e∈[0,1]; W's masked score ≤ D(A) ≤ T; (10)–(11) and the K=1 positivity check ((e+1)/2 < e) verify. No unverified step found.

**2. (Medium) bernoulli.py has no negative control for own-monotonicity.** CONTRACT.txt:88 requires reproducing the augmented-Wheatstone nonmonotonicity of the base rule before trusting a truthfulness claim. The suite checks p but never checks that z (the base rule) *fails* `all-positive own monotonicity` on some case, so the power of lines 125–131 to detect a violation is unestablished. Verification: add an assertion that z is nonmonotone on at least one (graph, profile, e) pair (verify.py:241 does this pattern for cap changes).

**3. (Medium) Tail/log bound (1) is untested.** Only `sum(p) <= sum(z)/q` (line 93) is checked; nothing tests `sum z ≤ T(log K+λ+1)/α` for the enumerated K. Since (iii) is the headline improvement, suggest an exact check of (1) at, e.g., λ=1 for every case (it must hold for every K, not only asymptotically).

**4. (Low) Own-report sampling is sparse.** Lines 113–132 test t∈{high/7, high/2, high} only; the original c_e (when <1 and not in that set) is never compared. The strong check is family invariance `ft[S]==fh[S]`, which does carry the proof's content, so this is a coverage note.

**5. (Low) Dependency `effective` (verify.py:93–102) silently relies on DAG structure.** D_h = min(c_h, maxflow(s→tail), maxflow(head→t)) is valid only because s→tail and head→t flows are edge-disjoint in a DAG (shared edge ⇒ cycle). All generated cases have increasing vertex IDs, so this holds, but the assumption is undocumented.

**6. (Low, unverified cross-reference) Line 19 "improves … from K to O(log K)".** CONTRACT.txt:27 states envelope y ≤ 2K²T and L≤K only for "different marginal payments"; which rule constitutes the prior "K" bound is not in the packet.

## Scope limitations
I did not execute code; results such as `status='PASS'` are coordinator-reported. I did not review novelty, the polynomial-noise obstruction remark (lines 97–98), or the resource-packing extension.

## Verdict
Mathematical claim: **no findings** — proof of (i)–(iii) appears complete. Test evidence: **findings** (2, 3) — strengthen before promotion.
