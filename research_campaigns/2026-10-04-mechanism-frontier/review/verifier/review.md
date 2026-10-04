## Verdict: no blocking findings in reviewed scope

No correctness defect found in the verifier, and no consequential theorem/code mismatch. The most important concrete finding is a coverage gap: own-report monotonicity is exercised much less than the report's counts suggest. All conclusions are from reading the snapshot; I ran nothing.

## Findings

**1. Medium (coverage, not soundness) — `verify_frontier.py` 172–185, 188–203.**
- The integer grids run `check()` only, so they test floors, budget and coverage but no monotonicity.
- Random profiles test only the halving `c_i → c_i/2`, which cannot detect a local non-monotone interval.
- Fine-step tests exist only in the seam block, where owner 0 is always in the left pool and the opposite pool always has three owners.
- For `left=1` both `others` tuples are `()`, and zero-capacity pool-mates are inert, so the four `a=0` configurations are one chain run four times. The 177 comparisons come from 9 distinct chains (`a` in {0,1,2} × 3 opposites).
- No fine-step test has a capped pool-mate (`c_k > T`) or a varying right-pool owner.
- *Verify:* add adjacent-grid comparisons, right-pool seam chains, and a capped pool-mate case.

**2. Low — fairness against H is never computed.**
Lines 158–159 test `M/2` only; `H ≤ M` rests on theorem lines 13–14, which I checked and found correct. This is disclosed in `limitations`. `worth()` uses original untruncated `c` for coverage and `M`.

**3. Low — mutation tests do not check the rejection reason (138–150).**
Any `ValueError`, `KeyError` or `TypeError` counts. For example, "multiple reports changed" may trip `c[i]>low[i]` rather than the other-coordinate check. The `profiles` statistic (126) also ignores `low_profile`, which is cosmetic.

**4. Low — provenance cannot be confirmed from the packet.**
`lp-*.json` and `REPRODUCE.txt` are not supplied, and `source_sha256` is not checkable here. The 1/8 lower bound therefore rests on unseen certificates.

## Checked and found correct

- **Taylor tail and inversion (40–52):** the tail is at most `next_term/(1-q/(degree+2))`, with ratio below 1 enforced. The returned pair `(1/upper, 1/partial)` correctly encloses `exp(-q)`.
- **Sign logic (56–69):** endpoint selection by coefficient sign is correct, and an unresolved interval raises rather than passes. No floats are used, and `require` survives `-O`.
- **Exact cancellation:** tight cases (budget at `u=1`, floor at `u=0`, saturated payments) reduce to empty dictionaries. Line 205 is an exact dictionary equality.
- **Payments versus theorem:** long owners get `d_i·e^{-u}/2`, short owners get `c_i − c_i·e^{-u}/2`. The tie `A=B` gives `u=0` whichever pool is called long, and `T=0` pays zero. The lower budget bound is covered by the full-coalition check.
- **Dual signs (103–124):** rows are aggregated as `Σcoef·var ≥ rhs`. Residual coefficients `≤ 0` together with `y ≥ 0` (which singleton coverage implies) give `β ≥ rhs/β_coef`. Omitting fairness rows relaxes the problem, so the lower bound stays valid for the H/3 contract.
- **Proof steps:** the capping identity, the long-owner identity `u=(m−M)/T`, the short-region bound `y' ≥ 1−h(ρ)`, and the seam value `x/2` all hold. The tightest case (sole owner at `A=B`, zero slope on both sides) is in the seam samples.
- **Report consistency:** hand recomputation matches the JSON for 1478 profiles, 177 seam comparisons, and the 64,912 total sign certificates.

## Scope limitations

- This is a static read of three files; I executed nothing.
- I did not review the LP certificates or `REPRODUCE.txt`.
- I did not assess novelty, sources, or the 2+2 bound comparison.
- The finite checks do not prove the continuum theorem; the proof text does, and I found no gap in it.
