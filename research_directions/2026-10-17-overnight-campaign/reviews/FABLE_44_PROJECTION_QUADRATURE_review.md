**Provisional verdict: no findings in reviewed scope (both arguments check out by hand; execution not possible).** Most important concrete point: the pair-TCWM witness is valid only under a *weak* coalition definition that lets owner 2 withdraw zero; the note states this, but any downstream theorem statement must carry that qualifier.

## Findings

**1. (Info) Separable obstruction — analytic steps verified.**
- Scale: `phi'` continuous, strictly increasing, range `[0,L)`; `phi'(2v)+phi'(v)→0<L`, so (1) has a unique `s>2` (RHS exceeds `phi'(2v)`). Bounded-derivative case is covered (line 24).
- `h`: LHS of (3) increasing, RHS decreasing in `h`; value at `h=0` is `psi'(1)-psi'(1+δ)<0`, at `h=δ` it exceeds `psi'(s)-psi'(2)-psi'(1)=0`. Existence/uniqueness in `(0,δ)` correct. `r>0` since `1+δ-h>1-δ`; `r<psi'(1)` for small `δ` since `h<δ→0`.
- Rows P/N/X (script lines 7–9) match `z` and (4). Polyhedron `D` = `{s≥2}×{0≤h≤δ≤1/2}`; the three vertices plus `+s` ray are exactly right, and `nonnegative()` tests coefficient of `s` and the vertices — correct certificate for affine functions. I hand-enumerated the sign of `P_Q−N_Q` by `s`-coefficient class (`{1,0,−1,−2}`); no mask changes sign on `D`, so the `AssertionError` branch is unreachable.
- Tight masks 0,3,36,39,43,56,59 confirmed by hand (e.g. mask 43={0,1,3,5}: `N=3+δ+s=X`). Masks 3,36,56 tight at `δ=h=0`.
- KKT: low multipliers give coordinates `g(1),g(1),g(2),g(1),g(1),g(2)+g(1)=g(s)`; high multipliers give `g(1),g(1),g(2−h),g(1+δ−h),g(1−δ),g(s+h)` via (3). All positive (`1−δ≥1/2`, `r<g(1)`). All coordinates positive, so nonnegativity needs no multipliers. Global optimality/uniqueness argument (line 88–91) is standard and correct.
- Pair {0,2}: `3 → 3−h`, loss `v·h>0`. Scaling `psi(t)=phi(vt)` is consistent.

**2. (Low) Definition dependence.** Owner 2 changes nothing; owner 0's own payment is unchanged (1→1). This is a negative externality witness, valid only if pair-TCWM permits a zero-withdrawal protected member. If the governing definition requires both members to strictly underreport, this witness does not apply. Verification: confirm the definition in the parent document.

**3. (Low) Script scope.** `check_separable.py` verifies only polyhedral feasibility and symbolic multiplier incidence; positivity of multipliers, existence of `s,h`, and (3) are analytic and uncertified by code (appropriately). The output JSON named in FILES is not in the packet; I did not run the script. Note line 46 only checks mask-5 change, not sign of `h`.

**4. (Info) Finite-feature boundary — verified.** Complement of finitely many hyperplanes (dim≥2) contains an open cone with ≥2 distinct unit directions; same strict signs on all features ⇒ one empty side per two-input game ⇒ zero payment; reserves vanish at `(1,u),(1,v)`; strict convexity of the norm gives `||u+v||<2` for non-parallel unit vectors. Gaussian sign-disagreement probability `θ/π` and `(1−θ/π)^M` are correct; non-uniformity in `θ` for fixed `M` follows.

**5. (Low) Unproved assertion.** Line 32–33 ("fresh sampling can preserve … in expectation") is asserted without proof; it is hedged as a different contract but should be marked conjectural or proved.

**6. (Info) Scope hygiene.** Doc 1 requires `phi'(0)=0`, identical report-independent `phi`, and technology `min(A,B)`; Doc 2 requires features linear in `x` only and signed-aggregate two-input games. Neither note infers unrestricted impossibility — correct.

## Scope limitations
No code executed; JSON artifact absent; definitions of pair-TCWM, "coverage," and the exact L1 compensated rule are not in the packet.

## Verdict
No findings in reviewed scope; items 2, 3, 5 are low-severity caveats, not errors.
