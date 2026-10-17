**Provisional verdict: no findings in reviewed scope.** Most important check: the cross-face transfer (3) in Proof D is sound because the joint pattern-preserving rational approximation keeps both aggregates in fixed faces, so only within-face relative-interior continuity (Proof C) is ever invoked.

## Findings

No correctness defects found. Steps independently checked:

**Proof A (compactness).** Permutation averaging within roles preserves budget/coverage/TCWM/OUT (all linear, domain and F invariant). Coordinate bound π_j(m) ≤ κF(m)/m_j is per-coordinate; the product of compact intervals is compact, so no uniform bound across count vectors is required. Dropping nonnegative inactive payments gives valid necessary inequalities (lines 47–53).

**Proof B (dilation).** T_k preserves (1): dividing the (km, kr, ku) instance by k uses F(km)=kF(m) and D(ku)=kD(u). Crucially, the coordinate bound is itself T_k-invariant (κF(km)/(km_j)=κF(m)/m_j), so the telescoping estimate bound/L at each coordinate is correct. Limit is fixed by every prime, hence every k.

**Proof C (Lipschitz).** (2) is a legitimate TCWM instance: λ=min c_j/c'_j is rational, the coalition's high holdings are c_v e_v + d_{−v}, outsiders hold λc'−λc'_v e_v. Box estimates |1−λ|≤δ/a, c_j−λc'_j≤δ(1+b/a), λc'_v≥a²/b, p_j≤κ max F/a all verify. Unique Lipschitz extension on boxes ⇒ locally Lipschitz on R_{++}^d; real-λ homogeneity follows by continuity along rays.

**Proof D (faces/mixed owners).** Face restriction of the SAME array is valid since (1) already contains all zero patterns. For (3), supp(o+r+d) and supp(o+r) are determined by the individual patterns, so limits use only within-face continuity plus continuity of F in D(d). Zero-low-aggregate case reduces to d·p(d)≥F(d), covered by coverage. Mixed-owner transfer: coalition totals depend only on aggregates (o,r,d), exactly matching (3); converse mechanism y_i=b_i·p(c) inherits 3–5 directly.

**Individual IC distinction** (lines 150–154): correct — T_k invariance needs the k-owner withholding comparison, unavailable from unit-owner IC.

**Hidden assumptions:** none beyond those stated. The nondecreasing property of F is not used in the proof (harmless). The hypothesis must quantify over models with binary-report pure-role owners of capacity 1 for every N with common κ; this is stated (lines 11–17) but readers should note it is the entire load-bearing input.

**Partial-floor corollary.** Section 1 identity M_i=max(h_i, H−E+e_i) and inequality t e_i−(H−E+e_i)=(E−H)(1−e_i/E)≥0 verify. Section 2: convex combination preserves OUT (outside term coefficients sum to 1), floor (1−λ)c+λ=θ, budget 1+θ. Section 3: X≥θ via one-sided OUT with zero outside value, x_j+y≥1 averaged ⇒ X+y≥1+(1−1/m)θ. Frontier K(θ)=1+max(c,θ) follows, conditional on the accepted 1+c unrestricted lower.

## Scope limitations

- Tool-free reading; no numerics executed.
- The 1+c unrestricted lower (UNRESTRICTED_OUTSIDE_SHARP_CANDIDATE.txt) was taken as given per task, not re-audited.
- No assessment of novelty, historical priority, or external literature; "no findings" is not endorsement of originality.
- Tier-integration extension (lines 50–53 of frontier file) checked only at the level of the stated commutation of full-bundle deletion with thresholds.

## Verdict

**No findings in reviewed scope.** The aggregate-price existence equivalence and the partial-floor frontier corollary hold as stated under the explicitly listed hypotheses; no hidden regularity or cloning assumption detected.
