**Provisional verdict: findings (minor-to-moderate); only pilot feasibility is supported, as the brief itself states.**

## Findings

**1. (Moderate, verified by arithmetic) The RBB residuals are consistent with truncation, not rounding — and they *exceed* the protocol's own "half-unit" bound.**
PANEL_PROTOCOL.json:31 proposes a half-unit-in-last-displayed-place bound. For RBB (6 dp), that bound on `DV100 − 100·DV01` is 100·0.5e-6 + 0.5e-6 ≈ 0.0000505. Both residuals (0.000060, 0.000055; example_results.json:9,17) exceed it. Check the alternative: DV100/100 = 135.69661160 and 29417.92785855. Round-half-up to 6 dp gives 135.696612 and 29417.927859; the filed DV01s are 135.696611 and 29417.927858 — i.e. *truncated* values. So (a) the benign development example would be flagged as "outside rounding bound" under the protocol as written, and (b) the RBB DV100 is, to the shown digits, exactly 100× a higher-precision DV01, which is strong (not merely "consistent") evidence that this filer's DV100 is a linear scaling, not an independent revaluation.
*Edit:* protocol §display_precision — replace the half-unit bound with "one full unit in last place of DV01, times 100, plus one unit of DV100" (covers truncation or rounding), or simply record whether residuals fall inside/outside both bounds without inference. Brief line 18 — change "consistent with upstream numerical/reporting precision" to "exactly reproduced by truncating DV100/100 to six decimals, indicating DV100 = 100·DV01 at higher internal precision for this filer."

**2. (Moderate, unverified assumption) Batch/report-date alignment and the B.3 reporting exemption are not addressed.**
PANEL_PROTOCOL.json:15–17 assumes the 2025Q2 ZIP contains the 2025-03-31 reports. SEC N-PORT data sets are organized by *filing* period and only third-fiscal-month reports are public; whether March-31 reports for all fiscal-year-ends land in that ZIP cannot be confirmed from the snapshot. Separately, Item B.3 permits omission for funds below the 25%-of-NAV debt-instrument threshold; the protocol's exclusion list (line 22) has no "not required to report B.3" category, so these will be lumped with "absent fields."
*Edit:* add an explicit exclusion reason "B.3 not required/omitted," and add a schema check that the eligible series count by reference date is reported before freezing the single date.

**3. (Minor) Residual summaries.** Arithmetic verified: 0.00006 + 0.000055 = 23/200000; 10000·450/20237340.35 = 0.222361 bp; NAV identities hold for both filings. "0.000000" vs "0" for zero nodes (example_results.json:70 vs 28) is a Decimal formatting artifact, not an error. verify_examples.py:111–113 hard-code outputs; they are regression checks, not independent verification — labelling as such would be more accurate.

**4. (Minor) Preregistration/priority language** is appropriately hedged. Priority claims (SEC IC-35962 pages, IMF Annex 1.4, Hidden Duration versions) cannot be checked from the packet; the brief correctly declines novelty. The top-20-by-statistic audit (line 36) is outcome-selected by design and so labelled — acceptable.

## Scope limitations
Cannot browse, run code, or inspect raw/*.json or the HTML. Cannot confirm the ZIP contents, 403 cause, filing accession numbers, or cited external documents.

## Verdict
Findings, none fatal. The snapshot supports a two-filing feasibility pilot only; fix the precision-bound logic and the batch/exemption assumptions before freezing the protocol.
