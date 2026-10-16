**Provisional verdict: no findings in reviewed scope** (both proofs check out on independent hand-verification; two low-severity presentational gaps noted).

## Findings

**1. Low — OUTGOING_LOSS_THEOREM.txt L9–10, L85–88 (multi-branch extension underspecified).**
The per-branch argument needs each branch input of owner i to be a nonnegative monotone function of i's bundle, so that a whole-bundle underreport is a coordinatewise underreport in every branch and the "full" per-branch profile is the truthful one. This hypothesis is not stated. Verification: add the linearity/monotonicity assumption explicitly (as WATERFILL_PRODUCT_THEOREM L108 does for its composition corollary).

**2. Low — STRONGER_RATIONAL_TILT_THEOREM.txt L305–306 ("unique global maximum").**
Uniqueness over all s∈(0,1] additionally needs g(s_*)>1/8; this follows from g(2/3)=F(2/3)=125/972>1/8 and g increasing on [2/3,s_*], but is not written. Trivial to add.

## Verified steps (hand-checked)

*Outgoing loss.* q'(U)=q(r−m)/U≥0; d[qD]/dU=q[r²−m(r−1)]≤qr²≤2/e (max of r²e^{1−r}/2 at r=2) and nonnegative, so all long-role losses are monotone and total ≤(2/e)a≤(4/e)(1−q)x_i. Stage 2: no-switch loss q(e^d−1)≤(e−1)qd; switch case R≥1 (since Σmin(x_k,r)≥r), Rre^{1−R} minimized at R=1/r, reduction to A(r)e^d≤1+(e−1)d, A(r)≤1 via x=1−r giving e^x+e^{−x/(1−x)}≥2 with derivative sign controlled by 1/r−r+2log r (derivative −(1−r)²/r²≤0). Cross-switch monotonicity of each role is correct, so positive parts equal aggregate differences. Intermediate long-role payment ≤ full since q(U) and min(b,U) increase. 4/e≤e−1 ✓. Sharpness example gives 1/2−1/(2e)=(e−1)·(1/(2e)) exactly ✓. Role accounting is purely algebraic (splitting labels changes no total or cap) and does not introduce strategic players.

*Stronger tilt.* f'(u)=9u(3u−2)/[5(3u−1)²]=3/5−3/[5(3u−1)²], f'(1)=9/20, f''>0 ✓. RT_bounds: (2) ratio (v+2)²(1−v)/[5(v+1)²]≤4/5 ✓; (3) reduces to P4(v)=4v⁴+12v³+3v²−10v+3≥0; P4(2/5)=219/625, P4'(2/5)=−102/125, convexity bound 4608/15625>0 ✓. RT_cost: 3/5−ratio=(1−v)(2+2v−v²)/[10(1+v)²] ✓ (expanded numerator v³−3v²+2). Section 3 constants (5/18, 5/12, 2(t−2/3)<3D(t−2/3)) ✓. RT_balance: difference identity f(L)−f(s)=(3/5)(L−s)[1−1/((3L−1)(3s−1))] ✓ (via w=3u−1, f=(w−2+1/w)/5); Q'(L)>0 ✓; Q(1)=(5v²+8v+5)/[10(1+v)²]=1/2−v/[5(1+v)²] ✓ (strict margin, unlike the old rule's exact ODE). Both-active case reduces to inactive expression at λ=s ✓. Section 9: f(t)=(1−2R)²/[5(1+R)(2−R)], h_R=−9(1−2R)/[5(2−R)²(1+R)²], K≥(7/20)(1−2R) ✓; R=1/2 endpoint and 32(1+s)³−27(2s+1)²=(2s−1)²(8s+5) ✓. Section 10: 1−2f=(−18s²+39s−13)/[5(3s−1)], g' numerator J=−162s⁴+306s³−255s²+104s−13 recomputed from scratch ✓; J(2/3)=5/3, J(1)=−20, J'(2/3)=−20, disc(J'')=−594864 ✓. Rough root s_*≈0.732 gives γ≈1.1297, consistent with the stated decimal.

## Scope limitations
- Water-cell identities (β formulas, dominant-cap lemma, E₀≤F) accepted from the supplied water-product/concentration files as dependencies; not re-derived from the water equation beyond consistency checks.
- Decimal values certified only to ~4 digits by hand; no tool execution.
- No novelty or optimality assessment, per instructions.

## Verdict
**No findings in reviewed scope** beyond two low-severity omissions (unstated branch-input hypothesis; unstated g(s_*)>1/8). The pool-switch scalar inequality, the role accounting, the quartic P4 bound, the strict balance margin, and the funding quartic all verify.
