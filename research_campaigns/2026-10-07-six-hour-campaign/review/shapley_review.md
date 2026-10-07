**Provisional verdict: no findings in reviewed scope.** Both constructions check out under independent re-derivation; the most consequential step (interior-band dummy-competitor argument, exponent gap Q ≥ M+1) is correct, and the explicit M=4 and growing-diagonal error arithmetic is exact.

## Findings

No invalid steps or missing hypotheses found. Items below are low-severity observations, not defects.

**1. (Info) Two-path family, SHAPLEY_OBSTRUCTION.txt lines 22–46.** Re-derived: veto share 1/(n+1)+1/(l+1)−1/(n+l+1); outsider share 1/(l+1)−1/(n+l+1); efficiency sums to 1; φ(S)=1/(l+1)+l/(n+l+1). For n=9,l=3: 71/260, 3/130, 9/52, φ(S)=125/260=25/52 ✓. Vertex/owner/cut counts (13,13,28) ✓. Bound 2/l and K=l³+1 ✓. `shapley.py` bit masks (`long` bits 1..n, `short` bits n+1..n+l, veto bit 0) encode the stated game correctly.

**2. (Info) Balanced calibration, lines 50–58.** Hand integrals recomputed: last unit owner 9/40+1/8=7/20 ✓; weight-2 owner 9/40+3/35+2/7+1/8=202/280=101/140 ✓; efficiency 6·9/28+7/20+101/140=3 ✓; payment 139/140 ✓.

**3. (Info) Balanced all-M proof, BALANCED_SHAPLEY_OBSTRUCTION.txt.**
- Band truth table (lines 34–41): exactly (j+1)-of-(n+1) on I_{n,j} requires a<b_n, which holds since a=1/(4M²)<(1−a)/M ✓; bands disjoint; endpoints j=0,n coincide across types ✓.
- Interior competitor (43–49): m=⌈n/d⌉−1 satisfies 1≤m<n, md<n≤(m+1)d; j/n−(m−1)/m=(n−md)/(mn)≥1/(mn)>1/M²; (1−a)/M²>a ⇔ a<3/4 ✓. Band lies in type-m all-outsiders gap ✓.
- Exponents (51–65): q_n−βr=−Q/2, q_m−β=Q/(2r), Q=2M[(m+1)d+m−n]−d≥2Mm−d≥M+1 ✓; r≤M so Q/(2r)≥1/2 ✓; exp(−x)≤1/x ✓. Dichotomy "latest is type n ⇒ type-n late or all type-m early" is sound.
- Lower endpoint (69–83): q_M−β(M+1)=1/(2M) exactly ✓; for n=M−1 the exponent is −1/(2(M+1)), stricter than the stated −1/[M(M+1)] (bound is loose but valid). Argmin-independent-of-min argument for 1/(n+1) is correct; the 1/(M+1) lower bound uses 1/(n+1)≥1/(M+1) ✓.
- Upper endpoint (85–94): unanimity, R=ΣK_n/Σ(n+1)K_n, excess ≤ Σ_{n<M}K_n/K_M ≤ (M−1)L^{−2M} ✓.
- Explicit parameters (96–107): q=(15,23,31,39); terms 3/100, 10⁻⁵, 3·10⁻³²⁰, 198·10⁻²⁰; sum <0.431 ✓. Diagonal: L^{−1/(M(M+1))}=R⁻², L^{−1/(2M)}=R^{−(M+1)}≤1/R, each term ≤1/(4(M+1)) ✓ so Sh(S)/a≤3/(M+1).

**4. (Low, side claim, SHAPLEY_OBSTRUCTION.txt lines 8–10).** "Marginal nondecreasing in c_e ⇒ own-report truthful" is asserted without stating the cost/feasibility model that rules out profitable over-reporting. Not part of the audited obstruction claims; flag only so it is not cited as verified.

## Scope limitations
- Scripts statically inspected only; `balanced_shapley.py` checks exponent inequalities for M≤30 and truth tables for M≤8, so the all-M claim rests on the algebra above, which I re-derived by hand.
- I did not enumerate any game; subset/permutation agreement is taken from the packet's statement.
- Novelty/priority not assessed (packet disclaims it). No claim about optimal-mechanism lower bounds reviewed.

## Verdict
**No findings in reviewed scope.** The Ω(K^{1/3}) two-path ratio and the balanced-pool 2/(M+1)+E(M,L) bound are correctly proved as written; this is a correctness audit, not an independent proof or novelty assessment.
