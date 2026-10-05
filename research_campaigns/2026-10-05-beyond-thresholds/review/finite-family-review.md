**Provisional verdict: no correctness findings on the theorem in the reviewed scope; findings (low/medium) on verifier assurance only.** This is a reading review; I executed nothing.

## Theorem (FINITE_FAMILY_ESCAPE.txt): hand-checked, no counterexample found

- **Coverage (l.21–30):** holds for every coalition. The middle term equals `s(1−z/δ)_+` exactly, the `n≤b` case uses `1−z>0`, and both sub-cases of `n≥b+1` check out. H is covered because the mean count is at least the minimum.
- **2T budget (l.33–36):** correct. The total is `T+(r−h−1)z ≤ 2T` or `h+(r−h)z ≤ 2T`, and it equals `2−1/r` at h=0.
- **Edges (l.39–49):** complete. Two distinct retained profiles differ in exactly one owner only for (j,h,A)→(j,h+1,A∪{i}) or the h=r−1→H step. Payments depend only on owner type, so all labels are covered. I re-derived `b_{h+1}=(r−h−1)(r−1)/r²`, the r=2 equality (1/4=1/4), the r=3 case (1/18≤2/9), and `a_{r−1}=0`.
- **3T fair budget (l.52–54):** correct, and it need not rely on the external "ΣM_i≤kT" lemma. On this family ΣM_i is `T_h` for h<r−1, `T+(k−1) ≤ kT` for h=r−1, and `kT` at H. Monotonicity survives the top-up because M_i is nondecreasing in own report (1/(rk)→1/k). The floor step does assume `H_i≤M_i`, which is standard but not proved in the packet.
- **Overclaims:** none found. Lines 4, 58–59 scope the result correctly, and the family contains every profile and edge of the Theorem 1 chains.

## Findings (verifier)

1. **Medium — `verify_beyond.py` l.119–153: `escape_checks` re-implements the proof's reduction and does not test the game.** It never builds profiles or calls `value()`. The (small,big,n) reduction, symmetry over labels and j, and the marginals `ma, mb, mc` (l.144–145) are hand-coded assumptions. An error shared by proof and code would pass.
   - *Verification:* brute-force all 2^(kr) coalitions and all labeled subsets for (k,r)∈{(2,2),(2,3),(3,2),(3,3)} using `profile`-style capacities and `value()`, computing M_i directly.

2. **Medium — l.142–150: the fair top-up is only budget-checked.** Monotonicity of `max(y, M/k)` across edges is not checked, including the last link to H. The H profile is never checked for coverage, budget or fair budget. The `profiles` count excludes H, and `own_report_edges` counts edge types of the base payment only, not labeled edges. The JSON labels overstate what was checked.

3. **Low — l.54–82: certificate reconstruction is partly tautological.** `certificate()` and `verify_certificate()` share `reconstruct`, so "row differs from game" cannot fail on honest input. The real content is the cancellation check, which I confirmed by hand: the residual is `[k+(r−1)r^r]B ≥ kr`. I found no soundness hole. Out-of-range j or h only create aliased variables for valid inequalities, and NaN or negative weights are rejected.

4. **Low — l.85–109: mutation tests are thin.** They accept any `ValueError` without checking which guard fired. Mutations 0 and 1 hit the same guard. No mutation alters metadata into another valid row (e.g. changing h or j on a budget or cover row). Only (3,3) is tested.
   - *Verification:* assert the expected message per mutation and add metadata-swap mutations.

5. **Low — l.222: `status='PASS'` is a literal and the hash is a self-hash.** It gives no tamper evidence beyond the run itself.

## Scope limitations

- Only the four supplied files were reviewed.
- SCALING_THEOREM, the general ΣM_i≤kT lemma, and EXACT_CHECKS.json were not seen.
- The verifier covers r≤20 and four k values; generality rests on the written proof, which I checked algebraically.

## Verdict

Findings: verifier assurance gaps (items 1–2 are worth fixing before promotion). The theorem itself has no findings in the reviewed scope.
