**Provisional verdict: findings (medium severity, none invalidating the stop decision).** Most important: `csv.DictReader` uses the default quoting dialect on free-text SEC TSV columns, so a stray `"` in `EXPLANATORY_NOTE`/`SERIES_NAME` can either abort the whole archive or silently alter text.

## Findings

**1. Medium — TSV quoting not disabled (preflight.py:85).** SEC N-PORT TSVs are unquoted; `csv` default dialect treats a leading `"` as a quote opener and swallows tabs/newlines until the closing quote. Outcomes: usually a column-count mismatch → `InvalidArchive` for the *entire* archive (spurious `STOP_DATA_INSUFFICIENT` from one note), or, if balanced quotes contain no tabs, a silently stripped `"` in retained note text. Numeric columns are unaffected. Verification: add `quoting=csv.QUOTE_NONE` and a fixture test with a note like `"quoted"<tab>` text. No existing test covers malformed/quoted rows despite RUN_NOTE claiming malformed-TSV refusal.

**2. Medium — NAV reconciliation stricter than frozen protocol (preflight.py:172 vs PANEL_PROTOCOL.json:39).** Protocol: "within documented filing precision." Code: exact rational equality. Real filings frequently have assets − liabilities ≠ net assets by rounding or definitional differences. Exclusions are counted (not silent), but this alone could push candidates below the ≥100 scale gate and trigger a designed stop for a reason the protocol did not intend. Verification: either implement the documented-precision tolerance (schema declares `dataScale: 12`) or amend the protocol before running on real data, not after seeing counts.

**3. Medium — whole-archive fail-closed on single-row anomalies (preflight.py:112–113, 137–140).** One orphan accession in any table, or one NPORT-P target-date filing lacking a `FUND_REPORTED_INFO` row, aborts everything. Defensible against silent revival, but it contradicts the protocol's "list every reason and count" and makes the stop decision hostage to SEC data quality. Decide and document in advance whether these become quarantine reasons; otherwise a STOP cannot be distinguished from a data-quality blip.

**4. Low — number format rigidity (preflight.py:39).** Regex rejects scientific notation, leading/trailing whitespace, and thousands separators. Rejections are reported under `missing_or_invalid_financial_field`, so not silent, but a systematic export format difference would masquerade as fund-level missingness. On resumption, check that the exclusion count for this reason is near zero before interpreting it.

**5. Low — runtime/test gaps.** `hashlib.file_digest` requires Python ≥3.11 (AttributeError is uncaught → traceback, not a STOP record). `metadata['tables']` non-list raises uncaught `TypeError`. Truncation test exercises central-directory failure, not CRC mismatch; the "bad CRC refused" claim lacks a direct test. Test fixtures load schema from `raw/nport_metadata_from_partial.json`, whose provenance is circumstantial per RUN_NOTE; acceptable for schema development, not as provenance evidence.

**Checked and found sound:** missing-to-zero (blank raises; `all_zero_vector` separately counted); amendment fallback (superseded rejected before latest is screened; `continue` never revives earlier versions; tie-break by accession matches protocol); duplicate USD rows quarantined, not summed; B.3 omission not treated as exemption; no headline residuals computed; empirical statements in RUN_NOTE/acquisition_attempt.json stay within evidence (partial file explicitly unverified, metadata explicitly without quarter provenance, no panel inference).

## Scope limitations
No execution; test pass count (13) matches method count by inspection only. SEC readme comparison and TSV export format conventions not verifiable from the packet. Downloaded partial file not inspected.

## Verdict
Findings. The stop decision (`STOP_DATA_INSUFFICIENT`, no promotion of the partial) is supported. Before resuming on a complete archive, resolve items 1–3 so a future STOP reflects design, not parser fragility.
