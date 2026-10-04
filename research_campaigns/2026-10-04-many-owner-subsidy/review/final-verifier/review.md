**Provisional verdict: no consequential findings in reviewed scope.** The short-side argument, adaptive-scalar corollary, q=13 bound and report counts all check out by hand; nothing was executed. The most important finding is that the q=2,3 family calibration cannot test the Section 5 upper bound.

## Findings

**1. Low–Medium — vacuous upper-bound calibration (`verify_many_owner.py` 161–165)**
- Evidence: the rational bound is about 1.79 at q=2 and 1.27 at q=3. But φ(S) ≤ T = v(S), so the ratio is at most 1 and `ratio <= rational_bound` cannot fail.
- The exact ratios (0.807, 0.711) are also above 2/3, so no enumerated family instance exhibits the 3φ/2 failure. That claim rests entirely on the proof, which the theorem (line 122) and the JSON note correctly disclose.
- Verification: run `count_family` at q=5 (m=625, r=500), where the bound is about 0.93 and the check becomes non-trivial. Also assert the intermediate bounds separately: η ≤ √(2m)/D0 and φ_b ≤ δ/2 + √(m/2).

**2. Low — adaptive-scalar wording (theorem 137–141)**
- The corollary does follow when λ depends on c: coverage is profile-wise, so λ(c) ≥ v(S)/φ(S) on each family profile, and efficiency gives a budget of λ(c)T.
- What is proved is a supremum: for every κ<2 some profile forces a budget above κT. No profile requiring exactly 2T is shown.
- Suggest rewording to "no uniform bound κT with κ<2".

**3. Low — misleading labels**
- `strict_own_report_checks` (line 132) tests the weak inequality `lower[i] <= phi[i]`, and only for a single halving per owner.
- "The old 2+2 theorem remains valid" (theorem 133) is supported only by one tightness example (mask 6, ratio 5/6), not by any check of that theorem.

**4. Informational — claims with no evidence in the packet**
- "Arbitrary-mechanism bounds remain [1/8,1/2]" and "existing 50% aggregate-price rule" (theorem 32–34) are not supported by anything supplied.
- `source_sha256` cannot be matched to the snapshot without hashing the file.

## Checked by hand, no defect found

- **Short side (§3):** for i in L with c(L) ≤ c(R), v(N∖i) = c(L) − c_i, so M_i = c_i. The chain φ(S) ≥ φ(S∩L) ≥ c(S∩L)/2 ≥ v(S)/2 is valid whichever pool is smaller inside S.
- **Pairing (§2):** the marginal is f_a(z), the complement has D−z, the weights are symmetric, and f_a(D) = M_i.
- **Subset weights:** line 33 matches k!(n−k−1)!/n!.
- **Count-state multiplicities:** C(m−1,x)·C(r,y) for a focal unit and C(m,x)·C(r,y) for the giant, with marginal (x−y)₊, are correct. The 4×4 cross-check against the subset formula gives the reported 16.
- **Strict Y>X:** the unit marginal is f_1(Y−X) on integers, and the code uses `y > x`. A `>=` error would be caught by the cross-check.
- **Permutation witnesses:** masks 19, 3 and 6 match the described coalitions. The φ vectors sum to T=2, and the ratios 49/60, 33/40 and 5/6 and scaled payments 49/25 and 99/50 recompute.
- **q=13:** 1/2 + 507/4392 + 1/26 + 3/676 ≈ 0.65834 = 162883/247416 < 2/3. Owner count is 28561 + 26364 + 1 = 54926.
- **Report counts:** profiles are 4923 + 150 = 5073. Grid marginal floors are 27882, leaving 727 = 716 + 11 for the random profiles. Grid coalition inequalities are 263817, and the remaining 9874 is plausible.
- **H versus M:** the verifier tests M only and says so; the proof supplies H ≤ M. H is never replaced by M.

## Scope limitations

- Nothing was executed; `cross_pair_prices` = 14670 and the random-profile totals were not recomputed.
- The large q=2,3 fractions were checked only for decimal consistency.
- The `review/` reports and `SOURCES.txt` were not supplied.

## Verdict

No findings that invalidate the claims in reviewed scope; the low-severity evidence and wording issues above stand.
