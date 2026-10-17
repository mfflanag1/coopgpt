**Provisional verdict: no material findings in reviewed scope.** The exact-key joins, duplicate accounting, and PSU-vs-total non-equivalence are internally consistent across code and summary; the strongest unverified item is the all-980-node `total_power` intersection having zero adjacent 20 s pairs (run length 1), which is plausible but structurally odd and was not diagnosed.

## Findings

**1. Low — all-node `total_power` intersection with longest 20 s run = 1 is unexplained** (`M100_PANEL_INSPECTION.py:62–71`; summary lines 193–205). Every `total_power` key has a PSU pair (`triples.n` = 4,750,202 = `total_power` rows), so the 965 all-node `total_power` instants are a subset of the 1,722 all-node PSU instants, which contain runs up to 71. For *no* two of 965 instants to be 20 s apart implies at least one node's `total_power` is systematically absent at alternating slots. Not a code defect (the run routine is correct), but the claim "all 980 nodes at some instants" would be better supported by identifying which node(s) break adjacency. Verification: from `node_count_per_time_histogram` (computed but omitted from the summary) and a query listing nodes missing at `t±20000` for each of the 965 times.

**2. Low — "canonical integer IDs exactly 0–979" is asserted by the audit but not computed** (`M100_PANEL_INSPECTION.py:24`; audit §2). The script checks that each node string casts into 0–979 and that there are 980 distinct *strings*; it does not check `count(distinct try_cast(node AS INTEGER)) = 980`. Strings such as `"01"` and `"1"` would pass both checks yet be treated as separate nodes in all joins and per-node statistics. Verification: one-line distinct-integer count; low prior of occurrence given the authors' anonymization map, but currently unverified.

**3. Low — exact-equality rate understated as evidence of non-equivalence given differing quantization.** `total_power` has gcd 20 W; PSU readings gcd 10 W (summary 460–478). Exact equality (2,458 cells) is therefore mechanically rare even for identical physical quantities. This does not undermine the non-equivalence conclusion—median delta −150 W and mean relative delta −22 % are far beyond quantization—but the summary should cite magnitude, not the equality count, as the operative evidence.

**4. Informational — `exact_panel=EXISTS` is conditioned only on nodes 0/1 having ≥2 common instants** (`M100_PANEL_INSPECTION.py:73`). Satisfied, and the stronger all-node results exist, but the label name overstates what the condition tests. The audit already notes this.

Arithmetic checks that pass: positive_gaps = rows − 980 per metric; grid_times 14,681 and 980×14,681 = 14,387,380; observed fractions; `multiple20s = positive_gaps`; phase counts all mod-20 = 0; psu_key_count ≤ min(ps0, ps1) rows; timestamps map to 2020-04-01 07:19:40 – 2020-04-04 16:53:00 UTC. Joins use unique keys with no time rounding, so no row multiplication is possible. Gap `WHERE gap_ms>0` is harmless given uniqueness. Global-gap `LIMIT 20` is non-truncating (12 rows returned). `(t/1000)::BIGINT` is exact since `subsecond_rows=0`.

## Scope limitations
- Cannot execute code or inspect the Parquet files, `M100_PANEL_INSPECTION.json`, `M100_PANEL_SUPPLEMENT.json`, or `M100_RANGE_INTAKE.json`.
- `M100_PANEL_SUMMARY.json` merges inspection, supplement, and intake outputs; the script that composed it is not in the packet, and the `audit_correction`/`gap_frequencies` fix is asserted but the corrected histogram is not shown.
- Member hashes, tar enumeration, and the 10 MB byte-range retrieval are accepted on the independent audit's word; not re-verified here.
- No Nagios/state data: online status, occupancy, meter boundary meaning, and ownership remain unresolved, as the documents correctly state. Absent release records are correctly not treated as outages.

## Verdict
**No material findings in reviewed scope.** The exact simultaneous panel (nodes 0/1: 4,523 / 4,559 instants; all 980 nodes: 965 / 1,722 instants) and the non-equivalence of `total_power` versus `ps0+ps1` (median −150 W, only 0.05 % exact equality) are supported by the code logic and consistent summary values, subject to the unverified items 1–2 above. No causal, reliability, or ownership inference is made or warranted.
