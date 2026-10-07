**Provisional verdict: no invalid steps found in reviewed scope.** Most important point: the verifier's "certified coarse tail bound" (verify.py:285–288) is not the theorem's bound U(K) and is not derived anywhere; it passes only because it is looser than U(K)T for every K ≤ 8 present.

## Findings

**1. Low — verify.py:285–288, tail check does not test the claimed constant.**
The check `sum(z) <= (r+1)*t` with r the smallest integer ≥3 having K(3/r)^r ≤ 1 is not what section 5 proves (the union-bound integral from s=r gives roughly r + ∫_r^∞(e/s)^s/(e/r)^r ds, which exceeds r+1 for r=3). It happens to be weaker than U(K)T here (e.g. K=8: r=5 gives 6T, while R_8≈4.35, U(8)≈5.03), so the check is sound but uninformative about U(K). Verification: compute R_K by rational bracketing and check `sum(z) <= U(K)*t` directly.

**2. Low — verify.py:90–93, normalization check is at the wrong point.**
`expectation` assumes support ⊆ (−∞, upper] but only requires `cdf_value(f, upper+1) == 1`, which does not exclude mass in (upper, upper+1]. Support ≤ T is guaranteed by theory (D ≤ c and global cap both give value ≤ T), so results are correct, but the verifier is not self-checking this. Suggest `cdf_value(f, upper) == 1`.

**3. Low — verify.py:180–190, `graph_caps` is an upper bound, not a direct computation.**
min(c_e, λ(s,a), λ(b,t)) upper-bounds the maximum flow through e in general digraphs; equality with tree caps is thus a consistency check, not an independent computation of the section-1 quantity "maximum feasible flow through e". Fine as cross-validation, but a direct max-flow-through-e computation would be stronger.

**Verified correct (no finding):**
- Truncated-power CDF arithmetic: `cdf_product` binomial re-centering at max(a,b), `minimum` = F+G−FG, `convolution` atom/atom, atom/density shift, density/density with p!q!/(p+q+1)! Beta factor, integration back to CDF; atoms with p=0 handled, `0**0=1` under Fraction. Calibration constants (1, 1/3, 5/2, 3/8, 1/k) are correct.
- `caps` matches D_e = min(c_e, min over series ancestors of sibling F); `tree_cuts` matches the cut recursion; minimality test `(b & a) == b` parses correctly; coalition value/coverage/co-cut checks implement sections 1–4.
- Section 9 endpoint identity min(A+D,B)−min(A,B)=min(D,(B−A)_+) holds in all three cases; with d>0 ties have conditional probability 0, with d=0 the payment is 0 either way, so z_e = D_e·P(e∈C_*) equals the computed endpoint difference. Subtree independence holds since the fixed leaf is a constant.
- Obstruction: T0=n−ε, T1=n; (1) is the endpoint identity with A=min(εU,TV), B=S_n; (2) via S−A reflection and simplex tail (t−A ∈ [δ,1]); (3) integrates r u^{r−1}(1−u/ε)(1−u/T) correctly; E[A_{T1}]−E[A_{T0}]=ε³/(6n(n−ε)); (4) discards the two negative remainder terms and bounds the rest by (2ε)^{n+1}; r_4=64/125 and the ratio recursion 2ε(n+1)²/(n²(n+2))<1 are correct. `old_cap_closed_form` encodes (2)–(3) faithfully; the ×10 scaling is valid by homogeneity. Under the new cap D_b=min(41,1,40)=1 in both profiles.

## Scope limitations
- Cannot execute; the exact rationals (737261209/37800000, drop 59347/604800000, 1548749/78750) and the counts in THEOREM §10 (263 profiles, 14528 inequalities) are unverified. Order-of-magnitude of the drop (~1e-4 after scaling) is consistent with ε³/(6n(n−ε))·10 ≈ 1.07e-4 minus a small remainder.
- Finite checks cover seven topologies, K ≤ 8, small rational profiles; the files state this limitation explicitly.
- Main theorem proof not re-audited per task.

## Verdict
No findings of invalidity. Three low-severity weaknesses in what the verifier actually certifies (items 1–3).
