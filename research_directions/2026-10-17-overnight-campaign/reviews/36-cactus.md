**Provisional verdict: no substantive findings in reviewed scope.** I hand-checked each step of the cactus extension and found the derivative lemma and the dependent-active-row argument correct; the remaining items are low-severity presentation gaps and one verification gap (the script never tests the all-profile projection claim, only the derivative lemma).

## Findings

**1. (Low) Interior-pin case splits the path; text implies a connected elimination.**
`INCIDENCE_CACTUS_EFFICIENT_SELECTOR.txt:68-76`. If an interior contracted node is pinned, removing it disconnects the endpoints; "eliminate all interior nodes" then yields `H_01 = 0`. Conclusion (2) still holds (zero conductance is nonnegative), and `Q^{-1}1 ≥ 0` is trivial, but the case is not named. Suggest one sentence noting disconnected segments are covered because elimination never creates negative conductances.

**2. (Low) Dependent-active-row step relies on an unstated KKT fact.**
`INCIDENCE_FOREST_EFFICIENT_SELECTOR.txt:53-58`, invoked "verbatim" at cactus file line 113. The derivative formula `B^T(BB^T)^{-1}e_r` requires that the projection onto `K(b)` coincide with the projection onto the affine hull of the active face. This is true (nonnegative multipliers put `c − x` in the span of active normals), and the argument that `r` cannot be dependent on fixed-RHS active rows over an open interval is correct, so an independent subset containing `r` always exists and the affine set is unchanged. The text should state the KKT span property explicitly; as written it is an unverified step rather than an error.

**3. (Low, verification gap) `verify_incidence_cactus.py` tests only the derivative lemma.**
Lines 54-65 check `d ≥ 0` for min-norm solutions of `Bd = e_r`; nothing tests own-row monotonicity of `e(b)` or of fixed-target projections across demand profiles, although the counterexample (lines 96-104) is checked at the profile level. Enumeration also caps rows at `min(n,4)`, omitting 5-row systems on 5 owners. Suggest brute-force projection (e.g., enumerating active sets, exact rationals) on random cactus systems and several demand pairs.

## Steps verified by hand

- Deletion structure (lines 25-33): three interface owners or two u–v paths or a two-point attachment each force an edge in two cycles. Correct.
- Row-attachment elimination (lines 56-64): `s = −(x_{j−1}+x_j)`, `β_j > 0` from "nonzero sum ⇒ nonzero coordinate". Correct; combined modules at one row still have image `{0}` or `R`.
- Sign change `z_j = (−1)^j x_j` turns `(x_{j−1}+x_j)^2` into `(z_{j−1}−z_j)^2`. Correct.
- Kron elimination formulas (lines 77-80): verified `c_jc_l/D` and ground `c_ja/D` by expanding `Σc_jz_j² − (Σc_jz_j)²/D`. Endpoint ground `≥1` gives positive definiteness and (2).
- `Q^{-1}1 = (Q_11−Q_01, Q_00−Q_01)/det ≥ 0` since `Q_11 ≥ |Q_01| ≥ Q_01`. Correct.
- Both-endpoints-merged cases: `k` even gives `h/2` each; `k` odd forces `h=0` and the free parameter `t` minimizes at 0. Correct.
- Spot checks: triangle `{0,1},{1,2},{2,0}` gives `(1/2,1/2,−1/2)`; `{0,1},{0,2,3},{1,2}` gives `(4/7,3/7,−3/7,−1/7)`, matching the path-quadratic prediction `Q=[[2,−1],[−1,3]]`.
- Counterexample (lines 126-133): `(2−t, t−1, t−1)` on `t∈(1,3/2)` and `d=(−1,1,1)` confirmed; its scoping as a selector-only refutation (not an all-mechanism impossibility) is accurate.

## Scope limitations

I did not execute the script. The cited files `MINIMAL_PROJECTION_OWN_MONOTONICITY_FAILURE.txt` and `EFFICIENT_CORE_SELECTOR_INCIDENCE_TWO.txt` are not in the packet; the mechanism-independent 12/11 claim is unreviewed. "Adequate" is undefined in this snapshot.

## Verdict

**No findings** of mathematical error in the reviewed claim; three low-severity gaps (unnamed disconnected case, unstated KKT step, missing profile-level test) should be closed before the lemma is cited as audited.
