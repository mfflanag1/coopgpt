**Provisional verdict: no mathematical or implementation errors found in the reviewed scope; the comparison is valid only as a conditional benchmark and does not identify a filer error. Most important finding: the day-count sensitivity alone (−84.32 → −80.93 NAV bp at 30Y) exceeds the 1‑NAV‑bp diagnostic screen, so the screen cannot discriminate conventions, and the result summary should present both models and both bases rather than a single "primary" pair.**

## Findings

**1. Formulas verified correct (no action).**
- `loss` (treasury_benchmark.py:20–24): with q=(F/P)^(1/2t)=1+y/2, shocked price = P·(1+s/(2q))^(−2t); loss = −P·expm1(−2t·log1p(s/2q)). Correct, numerically stable.
- `decimal_loss` (26–31): P·(1−(q/(q+h/2))^(2t)) — algebraically identical. Good.
- `tangent` (33–34): dP/dy = −tP/q, so DV01 = tP/q·1e‑4. Correct.
- Implied yield (54), weights (12–18), closed-form test (test_treasury.py:4–7) all consistent. Concavity tests (lines 10–15) are correct in direction.

**2. Day-count sensitivity exceeds the diagnostic tolerance (medium, overclaiming risk).** treasury_result.json:765 vs 1573: 30Y DV100 difference moves 3.4 NAV bp between 365.25 and 365 bases; 10Y moves 2.0 bp. Any statement comparing to a 1‑bp screen must say the screen is not met under either basis and is sensitive to an arbitrary basis choice. Verification: cite both basis rows side by side.

**3. "Primary model differences" conceal a large model-choice spread (medium).** Model A: +35.10 / −84.32; Model B: +71.18 / −50.35 (result.json:482,765,559,574). The two allocation rules differ by 34–36 bp at each node. Report both; do not label A as "the" result. Also note the totals (A sums to parallel repricing by construction): total DV01 model−reported ≈ −1.1 bp, total DV100 ≈ −49 bp — cleaner than node-wise figures, which embed an unidentified key-rate attribution rule.

**4. Does non-reproduction identify a filer error? No.** Unidentified hypotheses, none of which the code distinguishes: (a) par-curve vs zero-curve key-rate shocks (for 27–30y strips a par-rate tent produces different zero-rate shifts); (b) tent geometry other than linear-in-maturity (duration-weighted, cubic, or 20y intermediate node); (c) sign/direction convention — reported values are positive for both DV01 and DV100, direction is unobservable; (d) tangent vs finite DV01; (e) settlement T+1 (negligible, ~0.02 bp); (f) vendor-curve repricing not anchored to filed marks. Report explicitly that reported DV100/DV01 ratio (86.0 at 30Y) vs model (87.7 A, 89.1 B) is consistent with several of these.

**5. Decimal cross-check scope (low).** Line 59–60 verifies only the full-shock `loss`; Model B's partial-shock repricings (line 63) and the tangent are not Decimal-checked. Claim should read "full-shock losses" only (as stated — fine).

**6. Reference date unverified (low).** `REFERENCE=date(2025,3,31)` is hard-coded; no `REPORT_DATE` field in the packet confirms the period end. Verify against FUND_REPORTED_INFO/SUBMISSION table.

## Scope limitations
- `reviewed_bulk_analysis/rows.json` (source of reported DV01/DV100 and units) not in packet; mapping of `INTRST_RATE_CHANGE_*` fields unverifiable.
- Did not run code; arithmetic in result.json spot-checked for plausibility (total DV01 ≈ 4.23M vs ~ΣP·t/q·1e‑4) only.
- Quarantine-record step (SCOPE §2) not in packet.

## Verdict
Findings (items 2–4 are presentation/overclaiming; no formula or implementation errors identified). Coverage figure 99.9967% is correctly computed from the packet.
