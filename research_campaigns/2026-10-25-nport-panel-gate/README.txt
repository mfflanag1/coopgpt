LATEST: BOUNDED CONVENTION/VALUATION CHECK COMPLETE — STOP EXPANSION
Read convention_valuation/README.txt and the existing browser handoff at index.html#convention-gate. All29 NAV original records match and remain quarantined. Treasury benchmark covers99.9967% of assets but does not identify/reproduce the filed shock convention. No errors or pooling gains established.

N-PORT PANEL — PROVISIONAL DESCRIPTIVE RESULTS; CONVENTIONS UNRESOLVED

25 October 2026. User supplied complete /Users/maxf/Downloads/2025q2_nport.zip. All32 CRC checks passed; current SHA256 in raw/complete_acquisition.json. Original downloaded file is not modified.

Browser handoff:
http://127.0.0.1:52140/research-campaigns/2026-10-25-public-risk-feasibility/index.html#panel-run

Read campaign_status.json, reviewed_bulk_analysis/summary.json, source_audit.json and PANEL_REVIEW_DISPOSITION.txt.
1791 provisional exact-NAV candidates; 393 above10 NAVbp;29 NAV quarantines remain unresolved. This is not the finalized protocol eligible sample.40 of40 source-field comparisons match; common direction/model conventions remain unknown. Full materiality, valuation and novelty gates do not pass yet.

Reproduction (run from this directory; output paths must be fresh):
python3 preflight.py /Users/maxf/Downloads/2025q2_nport.zip --output new_preflight.json
python3 analyze_panel.py --input new_preflight.json --output-dir new_analysis
python3 -m unittest -v test_preflight test_analysis

22 synthetic tests pass. Core rational and Decimal checks cover8955 nodes. Existing outputs are immutable run records; do not overwrite them. The archive has no private holdings classifications added.

quarantine_diagnostic.py is an explicitly post-result inclusion sensitivity, not eligibility repair. source_audit.json preserves original NAV strings, source links and browser comparison outcomes, not full original XML downloads. record_source_audit.py reconstructs that ledger from recorded observations; it does not re-access SEC or independently reverify originals.

Re-entry requirements, not an automatically scheduled next campaign: establish comparable direction/scaling conventions from public evidence, resolve NAV/precision quarantines, regenerate audit selection if sample changes, independently match the shock definition in valuation, and read the latest full competing manuscript. No automatic access retry or long campaign scheduled. No manuscript/Git changes, human outreach or purchase. Earlier failed access run remains in RUN_NOTE.txt and before_complete_* records.
