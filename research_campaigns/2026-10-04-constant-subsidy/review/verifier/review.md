**Verdict: findings (medium/low only).** I found no false-positive path in `verify_lower.py` and no error in the repaired softmax bound. The most important defect is that several "exact witnesses" in `verify_auxiliary.py` are tautologies.

## Findings

**1. Medium — `verify_auxiliary.py` L72–81; `BARRIERS.txt` L80–81: softmax witnesses are not computed.**
- L76–77 sets `base=F(1+R,2)` with `R=r+1` and then requires it to equal `F(r+2,2)`, which is an identity.
- L79 assigns `F(k,6)` with no check at all.
- No softmax weight, ρ, payment or envelope is ever evaluated, so "Exact witnesses in verify_auxiliary.py" is overstated. By hand both witnesses are correct (w = 4^r·4^(−r) = 1; payment 1/12 × 2k = k/6).
- Verify: build the profiles, compute ρ_j and p_j exactly (e^(−λ) is rational for these λ), and sum the payments.

**2. Medium — `verify_auxiliary.py` L68–71, L84: the "negative control" is vacuous.**
- `winner=min(priorities)`, then `max!=winner` and `not(min!=winner)`, exercises no rule or profile.
- The JSON line "most-favored tied median fails; least-favored succeeds" has no computational support.

**3. Medium — class order-optimality (`BARRIERS.txt` L88–89) is only partly supported in the packet.**
- `SCALING_THEOREM` does supply the upper side: Lemma B (top-up ≤ T) and Theorem C (β ≤ R_k + 1/log R_k). I rechecked the Jensen, Markov and tail-integration steps and they hold.
- The class lower bound for arbitrary fixed statistics is not in the packet. L58–67 checks one max-statistic identity at r=2,3,4 only.
- The "old" (k−1)/2 bound is cited at `SCALING_THEOREM` L119, not proved there. `BARRIERS` §1 L14 does not need it, since Theorem C already gives a finite bound for each fixed k.

**4. Low — `verify_lower.py` L26–32, L109: roles are hard-coded by index.**
- `role()` and the monotone terms `w`/`A` are not derived from the reconstructed capacities, and `profiles`/`role` are shared between generator and verifier.
- They are currently consistent: I hand-checked all four coalition kinds, the worths 1, 2, t−1, t, and the cancellation, including m=2.
- The check on L108 is effectively redundant with the profile match.
- Verify: derive roles from (pool multiset, capacity) and assert orbit consistency.

**5. Low — mutation coverage gaps in `verify_lower.py`.**
- Missing: a role-preserving coalition with lower worth (e.g. two v-owners in one H pool and none in another), which only the claimed-bound check would catch.
- Missing: a monotone row on a B-owner or an H-pool owner.
- Missing: any m=2 mutation; all eleven use (8,4).
- "Lost coalition value" is rejected by cancellation, not by worth.

**6. Low — `verify_auxiliary.py` scope.**
- Capacities are {0,1,2}, at most 5 owners, and only the d/k rule is tested.
- There are no mutation tests in this file.
- The knapsack test does not record the true/false split, so it may be dominated by T=0 cases.
- Nothing tests §4 or §5.

## Checked by hand and found correct
- **Lower bound:** the dual sums for X and Y, the combined coefficient t(k−1+2t), the right side (k−1)(t−1), the diagonal identity, the 53 and 11 counts, and the k>17 threshold.
- **Verifier under `-O`:** it uses `require`, not `assert`, so the checks are not stripped.
- **`BARRIERS` §6:** ρ values 1 and 3/2; the step to exp(−λ/2) > 1/(6B), which needs exactly k+1 > 6B; w ≥ 1; (1+Rw)/(1+w) ≥ R/2; and B·log(6B) > log(k−1)/4. The λ=0 case is handled.
- **`BARRIERS` §1–5:** no defects found.

## Scope limitations
- Nothing was executed; the JSON outputs and `CONTRACT.txt` were not supplied.
- The class lower-bound document and the (k−1)/2 proof were not supplied.
- Symmetrization is taken from the prose proof.
