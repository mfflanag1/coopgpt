M100 power/state feasibility gate — 21 October 2026 UTC

Start with FINDINGS.txt. This campaign stopped at a scoped feasibility result;
it did not estimate reserve, energy savings, pooling gains or AI performance.

Reading order
1. FINDINGS.txt: decision, new evidence, limits and recommended restart gate.
2. SEMANTICS_AUDIT.txt: primary-source anchors and corrected interpretation.
3. ACQUISITION_DESIGN.txt: independent five-input byte audit.
4. footer_structure.json / STRUCTURAL_SUMMARY.json: subsequent actual-footer
   evidence that refines ACQUISITION_DESIGN's previously uncosted page alternative.
   The independent audit was deliberately not overwritten with parent findings.
5. OPERATOR_DATA_SPEC.txt: concrete conditional measurement/rights request, unsent.
6. reviews/: independent review and coordinator adjudication records.

Offline reproduction from this directory

    python3 replay.py

This verifies the frozen file hashes, regenerates acquisition/footer/header
reports in memory and compares saved JSON, runs 36 acquisition checks and nine
structural tests. It needs Python's standard library only, no network, credentials,
package installation, external original directory, or original measurement pages.
Python bytecode writes are disabled. Individual entry points are:

    python3 acquisition_audit.py --check
    python3 -m unittest -v test_structure.py
    python3 header_inventory.py
    python3 footer_structure.py

Outputs from the last two are structural metadata, not measurement outcomes.
Do not replace the footer projection with a generic all-column statistics dump.
The raw cached footer inputs include outcome statistics that this audit skips.

Provenance and exposure

inputs/ contains copied inherited records plus already acquired June headers and
footers. INPUT_MANIFEST.json preserves original paths/hashes; acquisition_ledger
links retained raw bytes to original public range requests. This bundle is not a
full archive checksum validation. Raw 2020 measurement data remain outside it.
The original inherited artifacts are unchanged; EVIDENCE_STATUS.json is the new
status record. source_manifest saved paths refer to the original run, not this
relocated folder. Header copies and footer copies are verified by replay directly
against that inherited ledger/report; MANIFEST.json covers current bundle files.

Sources

sources/access_ledger.jsonl records local documentation/code fetches; name-only
early entries use name + '.txt', later entries provide saved_file. It does not
meter model web-fetch traffic. No dataset response bodies were acquired in this
campaign. Prior total stays 93,606,385 / 100,000,000 bytes. SOURCE_ATTRIBUTION.txt
records licenses and original repositories. Source snapshots are evidence and
are not executed by replay.py.

Nothing in the bundle authorizes subsequent data acquisition, outreach, a changed
holdout, performance claims or automatic continuation of a research campaign.
