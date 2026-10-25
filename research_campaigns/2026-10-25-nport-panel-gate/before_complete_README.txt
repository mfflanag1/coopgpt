N-PORT PANEL GATE — CLOSED DATA-INSUFFICIENT
25 October2026. This is the continuation of the public-risk feasibility handoff.

Current browser handoff (updated in place, prior page snapshot preserved here):
http://127.0.0.1:52140/research-campaigns/2026-10-25-public-risk-feasibility/index.html#panel-run

Read RUN_NOTE.txt, raw/acquisition_attempt.json and raw/final_download_check.json.
One ordinary official browser download was attempted, timed out, and yielded no verified complete archive. A candidate partial N-PORT ZIP remained6MiB and did not have a complete ZIP structure. No retry, automatic follow-up or source-selected replacement sample is running. No browser download cancellation is claimed; the status/control surface was blocked, and the partial was left untouched.

Resumption requires a complete publicly obtained2025q2_nport.zip and its local path. The official link is:
https://www.sec.gov/files/dera/data/form-n-port-data-sets/2025q2_nport.zip

Offline preflight, from this directory:
python3 preflight.py /absolute/path/2025q2_nport.zip --output /absolute/path/new_preflight.json

Use a new output path. A complete ZIP is checked by CRC for every member and SHA256, then the five required tables are parsed under their metadata. The program produces coverage, amendment, exclusion and field-compatible candidate tables. It does NOT calculate headline residuals or approve empirical gates. Resolve technical failures and source-convention/NAV quarantines before interpreting candidate scale. Then execute the unchanged PANEL_PROTOCOL.json and conduct source reconciliation before economic interpretation.

Synthetic verification:
python3 -m unittest -v test_preflight
18 tests pass. These fixtures are not empirical evidence. Required development metadata in raw/ comes only from the complete first ZIP member of the partial candidate; it does not validate quarter provenance or the full archive.

Cross-model review and root-verified responses are in review.md and REVIEW_DISPOSITION.txt. No novelty, pooled-fund rights, forecast improvement, full-panel effect or bank allocation claim. No paid source, outreach, manuscript change, commit or push.
