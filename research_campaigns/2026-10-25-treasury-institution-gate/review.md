**Provisional verdict: no findings of incorrect mathematics in the reviewed scope; three low/medium gaps in data specification and one source-metadata item to verify.** The most important: DATA_REQUIREMENTS.json does not require the current-charge baseline to state the risk model/scenario set it was computed under, so a Stage 1 "existing rule vs. Euler/selectors" comparison could confound allocation rule with risk model.

## Findings

**1. Medium — baseline model identity missing (DATA_REQUIREMENTS.json L8–9; RESEARCH_BRIEF.txt L32, L38).**
`allocation_baseline` records `charge_unit and horizon`, `budget_total`, `rule_version`, and reconciliation requires the same budget/perimeter, but nothing requires that the existing charges were computed on the same `scenario_set_id`/`model_version` (or a mapped equivalent) as the loss matrix. Stopping condition L38 covers budget/perimeter mismatch only. If the incumbent rule uses, e.g., parametric VaR while the pilot uses historical ES, allocation differences are unidentified. Verification: add a `baseline_risk_model/scenario_set` field and extend L38 to model mismatch.

**2. Low — same-units credit requirement not propagated (RESEARCH_BRIEF.txt L27 vs DATA_REQUIREMENTS.json L5).**
The brief requires credit permissions "in the SAME units as the primary allocation"; the JSON contract list says only "credit permissions and budget." Double-counting protection is otherwise adequate (JSON L8 transfer ledger, L9 "without counting an internal hedge twice"), but `scenario_losses` (L7) has no internal/external counterparty flag, so back-to-back trades can only be caught via the perimeter-sum reconciliation if additivity is claimed.

**3. Low — overbroad summary sentence (RESEARCH_BRIEF.txt L46).**
"cannot recover coalition constraints or the allocations" exceeds the example's own scope statement (PUBLIC_SUMMARY_OBSTRUCTION.txt L21). Allocations such as equal split or proportional-to-stand-alone *are* identified from marginals plus total. Suggest "…or the coalition-constrained allocations considered (leximin selectors; Euler also differs)."

**4. Low/verify — HSBC source metadata (SOURCE_RECORD.json L16–17).**
Filename token `260225` under HSBC's DDMMYY convention suggests 26 Feb 2025, i.e., the 2024 ARA, whereas title says 2025. Cannot verify; coordinator should confirm year. Brief does not rely on this source.

**Mathematics checked (PUBLIC_SUMMARY_OBSTRUCTION.txt L6–19) — correct.**
- Minors of Σ_B: 1, 3/4, 1/2 (det = 1 − 1/4 − 1/4). Entry sum = 3. T = 3 − √3.
- Pair variances in B: {1,3}=1, {1,2}=3, {2,3}=2 → savings 1, 2−√3, 2−√2.
- A: 2T/3 ≥ 2−√2 ⇔ √2 ≥ 2√3/3 (1.414 ≥ 1.155) ✓; equal vector uniquely maximizes min / minimizes max given sum T ✓.
- B: y_B sums to T ✓; 5/2−√3 ≥ 2−√2 ⇔ √3−√2 < 1/2 (0.318) ✓. Ascending: y₁+y₃ ≥ 1 ⇒ y₂ ≤ 2−√3; at that level y₁+y₃=1 and {2,3} constraint gives y₃ ≥ √3−√2, so max-min of (y₁,y₃) is 1/2, unique ✓. Descending: max ≥ 1/2, attained only at y₁=y₃=1/2 ✓.
- Normalization c(S)=√(1ᵀΣ1) is valid for Gaussian ES with common multiplier ✓.

**Conditionality and source claims.** Pilot is clearly labeled conditional (BRIEF L10, L13; DISCOVERY_NOTE L1); JPM facts used (BRIEF L8) do not exceed SOURCE_RECORD `facts_used`/`limits`; pages PDF114, 171–172 were text-inspected only, as stated.

## Scope limitations
No tool access; URLs, page locations, and source contents unverified. Reviewed only the five supplied files.

## Verdict
Findings (minor): no incorrect inequalities; one medium specification gap (#1), two low wording/propagation gaps, one source-metadata item to verify.
