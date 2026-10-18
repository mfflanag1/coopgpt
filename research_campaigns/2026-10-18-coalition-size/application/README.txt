BOUNDED APPLICATION FEASIBILITY GATE
Application lane for the 18 October 2026 coalition-size campaign.

Read in this order:
1. FINAL_FEASIBILITY_GATE.txt and NEXT_PREREGISTRATION_DECISION.txt.
2. THREE_INTEREST_CONTRACT.txt and MISSING_EVIDENCE.json.
3. SUMMIT_ACCESS_GATE.txt and M100_MAY_ACCESS_GATE.txt.
4. CONDITIONAL_VALIDATION_PROTOCOL.txt (draft; not frozen, not executed).
5. THREE_OWNER_ALGEBRAIC_WITNESS.txt and three_owner_witness.json.

Provenance and exact request accounting:
  metadata_requests.jsonl: Summit documentation HTTP bodies and failures.
  metadata/: the three archived public documentation responses.
  m100_may_metadata/requests.jsonl: each exact May range and body hash.
  m100_may_metadata/report.json: remote tar member names/sizes/offsets.
  data_manifest.json: final aggregate byte accounting and interpretation.
  audit_application.py / audit_application.json: local consistency verification.

The current data gate does not inspect any Parquet outcome value. Archive
headers and Parquet footers are conservatively charged to the 100MB dataset cap.
Documentation bodies are logged separately. Metadata tools' HTTP/TLS/browser
traffic is not confused with dataset-body bytes or with measured power values.

Offline commands from campaign root:
  python3 application/check_three_owner_witness.py
  python3 application/audit_application.py

The acquisition scripts were written before execution. Do not rerun them
unconditionally: each network acquisition adds to cumulative bytes. The May
script refuses to overwrite an existing intake directory. Its copied design
comes from the earlier M100_RANGE_INTAKE.py but disables that script's read-ahead
and member downloads to prevent value inspection. The campaign stores only
headers/footers/documentation; it does not modify old raw files or manuscripts.

Opposite-model review and integration are owned by the root lane. Review
findings are not treated as proofs; changes must be independently checked.
