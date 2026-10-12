**Provisional verdict: findings (minor, non-outcome-changing).** Most important: the REPORT's "annotation concern" on the Merit Network item is slightly over-stated — the passage asserts an intended purpose, not an achieved outcome, which is a standard SQuAD2.0 unanswerable construction; the official label is defensible and the REPORT should say so.

## Findings

**1. Low — Educational-network annotation concern under-qualified** (REPORT.txt:29–32; FAILURE_CASES.json:118,121)
Evidence: passage says Merit was "formed in 1966 … to explore computer networking … *as a means to help* the state's educational and economic development." Question: "State educational and economic development *were helped* by what?" The passage states intent at founding; it never asserts that development was helped. SQuAD2.0 commonly constructs unanswerables by presupposing an outcome the passage does not state. REPORT's "the passage explicitly connects computer networking with that purpose, making its official unanswerable label questionable" is accurate about the connection but omits the purpose-vs-outcome gap that justifies the label. The qualifying sentence ("annotation concern, not a verified source correction") is present and adequate; suggest adding one clause noting the intent/outcome distinction so the item is not read as a probable mislabel. No rescoring implied.

**2. Low — Undeclared development per-cell minimum** (RESULTS.json:32 `"minimum_per_cell": 1`; PROTOCOL.txt:74–75; REPORT.txt:18)
PROTOCOL's development gate specifies total ≥11, ≥5/6 per label, ≥3/4 per length band — no per-cell criterion (cells apply only to confirmation, line 78). RESULTS.json reports a per-cell minimum of 1, and REPORT says the long answerable "cell also fails." Outcome is unchanged (total, both labels, and long band already fail), but the REPORT should either state the cell note is descriptive only or RESULTS should not present `minimum_per_cell` as a gate parameter. Verification: confirm whether the frozen scorer's `passed` depends on `minimum_per_cell`; if so, note the deviation from PROTOCOL (harmless here).

**3. No finding — broad-span and non-null descriptions are accurate.**
Case 57264c42: prediction is the gold "two populations of rodents" plus its explanatory continuation; `contains_gold`/`verbatim_span` true; F1 0.333 reproduces (4/20 precision, recall 1). Case 5726545f: prediction is the full sentence containing gold "it is weighted inversely to member state size"; F1 16/31 = 0.5161 reproduces (23 pred tokens, 8 overlap). Case 5a55319c: "Who created the cooperative agreement?" — passage names MCI as operator "under a cooperative agreement with the NSF," no creator stated; REPORT wording is correct. Mean F1 0.73746 = (8 + 0.3333 + 0.5161)/12 reproduces. Strata table, 4/6 per label, 1/3/4 per band, and campaign duration (00:57:54.23→00:58:50.75 = 56.52 s) all match RESULTS.json.

**4. No finding — overclaim check.** REPORT consistently frames the result as a negative engineering screen, disclaims causal length effects, pretraining contamination, confirmation-split status, and the always-null floor, consistent with PROTOCOL. The diff shows only the expected PREPARED→COMPLETED rewrite with no gate language softened.

## Scope limitations
- Only 4 of 12 scored responses are in the packet; "every scored response ended with done_reason=stop," "no nonempty thinking," per-request host/clock checks, and the 8 passes are unverifiable here beyond RESULTS.json's `integrity_faults: []`.
- Raw response files, VERIFICATION.json, MODEL_LOCK.json, reviews/, and the scorer code were not supplied; F1/EM arithmetic was reproduced by hand from FAILURE_CASES only.
- The Codex raw audit is in progress; this review does not substitute for it.

## Verdict
**Findings** — two low-severity wording/documentation corrections (items 1–2); no material misstatement of the outcome, the four failure cases, or the gate decision in reviewed scope.
