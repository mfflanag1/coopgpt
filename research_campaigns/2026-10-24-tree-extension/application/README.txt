Arrival-driver qualification preparation

Read DIAGNOSIS.txt and PROTOCOL.txt first. No timing collection is authorized.
Old retrieval-service data/protocol/code/freezes remain read only.

Deterministic preparation commands(no physical scheduler/consumer launched):
  python3 -m unittest test_arrival_qualification -v
  python3 -m py_compile arrival_qualification.py test_arrival_qualification.py
  python3 arrival_qualification.py --prepare --output NEW_DRAFT_FREEZE.json
No dependencies beyond Python standard library; no native build or package install.

The draft is authorized:false. Root must obtain independent QA and explicitly
approve the exact hashed source/protocol/plan, fill host_conditions and send go
before any --authorization run. Do not treat these preparation commands or a
passing test suite as permission to measure timing. Root handles that review.
The current delivered unsigned packet is DRAFT_FREEZE_REPAIRED.json. All older
unsigned freezes are preserved and stale. The premeasurement repair rechecks the
absolute planned time after every early wait return, keeping cancellation and
the50-request denominator. See PREMEASUREMENT_REPAIR.txt and REPAIR_DIFF.txt.

Synthetic producer implementation shares Event.wait logic and framed-pipe transport
across threaded and process-isolated modes. The optional pure-Python CPU thread
shares only the consumer process. It never changes sys.setswitchinterval.
Qualification uses completed-send admission jitter, not prompt wake/pre-send.
Every planned ID is retained; missing final admission timestamps fail the gate.
Receiver receipt delay is separate and cannot be hidden by the admission result.

All48 cases are fixed, totaling2,400 offers over20/50/100/200 rates,2 modes,
2 loads and3 independent schedule repetitions. Proposed80-second phase watchdog
plus bounded cleanup keeps collection below90seconds; incomplete runs fail.
No MPS, corpus, serving throughput, energy or owner-pooling result is measured.
