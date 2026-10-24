Persistent exact SIFT10K retrieval — prepared, awaiting independent QA/freeze

Scope
This directory is an isolated preparation artifact. No canonical files were
edited. All copied public inputs are byte-identical to the qualified October14
packet. No new real-corpus distances, MPS commands, calibration or evaluation have
been executed. The only runtime tests use tiny synthetic CPU coordinates. Read
PROTOCOL.txt for the proposed two-stage experiment; every setting remains a draft
until parent approval. Preparation creates no approved collection authorization.

Build (Apple SDK, no package install)
From this directory:
  /Library/Developer/CommandLineTools/usr/bin/swiftc -swift-version 5 \
    -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -O \
    -module-cache-path build/module-cache src/QualifiedCore.swift src/main.swift \
    -o build/retrieval-service
No fast/reduced-precision flags. The only persistent runtime dependencies are
the system Swift/Apple Metal/MPS frameworks and Python3 standard library.

Permitted synthetic checks (never create a Metal device/open corpus files)
  build/retrieval-service --self-test
  python3 -m unittest discover -s tests -v
  python3 service_driver.py --synthetic --output logs/NEW-synthetic-smoke
Output paths must be new. The synthetic service has32 generated3D base vectors;
it is a wire/queueing/correctness fixture, not a SIFT or performance experiment.
Tests check the full independent direct-integer distance/hash/top-ten oracle,
arbitrary/repeated query identities, batching deadlines/FIFO/cap, missing-answer
denominators, timeout/fatal-response evidence, schedule split and success gate.

Prepare an unsigned freeze without running the service
  python3 service_driver.py --prepare calibration --output DRAFT_CALIBRATION.json
This records source, binary and data hashes plus every planned window/request,
and authorized:false. Parent should audit it and PROTOCOL.txt, obtain independent
QA, state the host/power/desktop condition and explicitly authorize the exact
freeze before any real run. Do not flip this flag merely because tests pass.
The newest draft after QA fixes is DRAFT_CALIBRATION_QA.json. Earlier unsigned
drafts are retained as stale preparation records and fail current source hashes.
An approved packet must fill host_conditions.power_condition and desktop_activity.
HOST.json records those declarations and the unchanged Python switch interval;
the runner does not tune the GIL switch interval to avoid a validity failure.

After an explicit reviewed calibration approval only:
  python3 service_driver.py --authorization APPROVED_CALIBRATION.json \
    --output NEW-calibration
There is deliberately no automatic calibration-to-evaluation transition. Review
the complete calibration, apply the fixed selection rule, then prepare a separate
evaluation freeze with --prepare evaluation --rate SELECTED_RATE. No rate or
batch-wait changes are allowed from evaluation outcomes. Parent approval is
required again for the exact evaluation freeze. These instructions are not an
authorization to collect outcomes during preparation.

Artifacts and latency
PLAN.json preserves every planned offer before execution. Per-window RESULT.json
contains every request's planned/actual offer, submission, checked client delivery
and failure status. RESPONSES.jsonl preserves raw native answers. Readiness and
warmup outputs are retained separately. SUMMARY.json marks aborted/unrun windows.
The primary clock is Python monotonic_ns, from planned offer to client decoding
and checking delivered answers. Native full-oracle work and IPC count. Startup
and warmup are separate disclosed setup costs. No GPU-only latency comparison.
A client hard kill may prevent final records; then immutable plans/partial logs
must be audited as incomplete and missing answers treated as failures. A missing
summary never means success. Binary/source hashes invalidate stale approvals.

Known scope limits
Only the fixed100 queries of this historical small classical-image benchmark.
Full checking on every request may dominate runtime; it must remain included in
both policies. The evaluation split is independently scheduled runs, not unseen
semantic examples. Four pairs support the stated descriptive engineering gate,
not broad performance or causal inference. Single Mac, no actual owner pool,
energy sampler, wall-power result, welfare result or modern-embedding claim.

Initial preparation build failed on Swift's type inference for a synthetic
fixture expression; the equivalent explicit loop compiled. Initial build/test
logs are retained rather than overwritten. This was not a data/outcome failure.

Review
The parent obtained a cross-model review. reviews/WORKER_QA_RESPONSE.txt separates
verified gaps/fixes from clarifications and contains its exact path. New checks
cover qualified-answer schema/matching, descriptive timeouts, arrival-thread
exception propagation and the existing shared phase budget. Parent verification
of these changes and collection approval remain pending. See PREPARATION_CHECKS.json
for executed checks/hashes. Neither that review nor the tests verify new real
MPS outcomes. The qualified-answer copy-equality check compares already observed
October14 outputs; it computes no new real-query distances.
