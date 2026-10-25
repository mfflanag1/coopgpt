**Provisional verdict: findings (no blocking arithmetic error found; one protocol-sample deviation and one unreported interpretation hazard).**

Most important: the 29 NAV quarantines are applied as an *inclusion filter*, which protocol v2 does not authorize; and 1,165 nodes have DV01 = 0 exactly, so a sizable, unquantified share of the headline residual distribution may be one-sided (DV100 ≠ 0, DV01 = 0) "missing-as-zero" filer reporting rather than scaling discrepancy.

## Findings

**1. Medium — NAV reconciliation used as sample filter (preflight.py:187–191).** Protocol §sample.inclusion/exclusions lists no NAV=assets−liabilities criterion; the check lives in §source_reconciliation.replication ("on the audited set … within documented filing precision"). Code applies an *exact* Fraction equality to every candidate and drops 29. The summary discloses this as "conditional on exact-NAV preflight subset," so it is not silent, but the 1,791 sample is not the protocol-defined eligible sample. Verification: recompute summary with the 29 rows included (flagged) to show sensitivity; or amend protocol v3 explicitly rather than treating v2 as "unchanged" (ANALYSIS_IMPLEMENTATION.txt:1).

**2. Medium — One-sided zero nodes not counted (analyze_panel.py:44–46; summary.json:8).** `undefined_relative_nodes` = 1,165 of 8,955 (13%). Where DV01 = 0 and DV100 ≠ 0, residual = DV100 and `node_nav_bp` = 10000·|DV100|/NAV; this can dominate `max_node_nav_bp` and the >1/10/100 bp counts. Protocol separately counts *all-zero vectors* (69) but nothing distinguishes single-side zeros. The summary should report (a) nodes with exactly one of DV01/DV100 zero and (b) how many funds' primary statistic comes from such a node, before anyone reads 393 funds >10 bp as scaling discrepancies. Verification: add counters over `rows.json`; rerun thresholds excluding one-sided-zero nodes as a labelled sensitivity (not a replacement).

**3. Low — Unit compatibility not screened (preflight.py; protocol §metrics.node_nav_bp "for compatible dollar units").** No check that NAV and DV fields share dollar units; `total_nav` ending in ".370004" suggests heterogeneous NAV precision/units. Caveated via `units_and_direction: source_review_required`, but the 349 bp max and the 24 funds >100 bp are prime suspects. Verification: audit set already includes top-20; confirm units for those first.

**4. Low — Summary omits full exclusion ledger (analyze_panel.py:107).** Only the NAV quarantine count is surfaced; protocol requires "list every reason and count." Preflight JSON has it; summary should carry `exclusion_counts` through.

**5. Low — Cross-checks use `assert` (analyze_panel.py:50,52).** Disabled under `python -O`; would silently pass. Use explicit raises.

**Verified correct (by reading):** residual sign handling; relative undefined on DV01=0 incl. 0/0; left-inverse weighted quantile (test_quantiles, test_ties… arithmetic checks out by hand: weighted median 10.1, top-20+ties = 26, strict >10 = 1); top-20 tie inclusion via `>= cutoff`; fund_share values (913/1791, 393/1791, 24/1791) match; dedup keeps latest (filed, accession) without field splicing; superseded versions preserved in audit table.

## Scope limitations
Cannot execute tests or inspect `complete_preflight.json`/`rows.json`; cannot verify the 1,791/29/442 counts, the quantile values, or the preflight SHA. No original EDGAR filings inspected. Lower filing-date bound (2025-04-01) is an implicit batch assumption, not in protocol text.

## Verdict
**Findings.** Summary is supported *as labelled* (provisional, arithmetic-only, 0 source-validated funds); gates correctly NOT_ESTABLISHED. Unsafe promotion risk: quoting "393 funds / 138 registrants >10 bp" or "p90 ≈ 20 bp" without Finding 2's one-sided-zero decomposition and Finding 1's sample caveat. Do not treat the 29 quarantines as resolved.
