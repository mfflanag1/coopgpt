**Provisional verdict: findings.** Most important: Success criterion B's example ("nonlinear covering/monotonicity transformation with an improved bound independent of the altered-pool count", CONTRACT.txt:73–74) does not fix the report domain, so a grid-restricted or equal-size-cube rule with m-independent factor would satisfy B's letter while being exactly the "another bounded-family construction" excluded at line 78.

## Findings

**1. (High) Criterion B admits bounded-family work.** CONTRACT.txt:72–75 vs 78. The frozen frontier already distinguishes binary (Thm `escape`, App. A) from `[1/r,1]` cube (Thm `continuous`) from all nonnegative reals with unequal sizes (Thm `upper`). An m-independent bound on the binary cube is a new bounded-family result, not a change to B_k. Fix: require the "improved bound" to hold on all nonnegative real profiles and arbitrary finite ownership, or explicitly state the reduction from that domain with verified hypotheses. Verification: ask whether manuscript.tex:488–533 (equal size, reference capacity 1, `[0,1]`) would already be inside the admitted domain.

**2. (High) Criterion A is internally inconsistent on fixed-instance lower bounds.** CONTRACT.txt:65–69: "a stronger universal lower constant than 2" is listed as qualifying, but "a fixed small instance improvement is discovery evidence unless it yields a general theorem." A valid unrestricted certificate giving factor 2.1 at one fixed (k,r) is a universal-constant improvement by the contract's own definition of B_k (line 31–33), yet could be dismissed under line 68. State whether B_k is treated as monotone in k (not proved in the packet) and whether a single fixed-(k,r) unrestricted certificate >2 qualifies.

**3. (Medium) Calibration item (iii) is unverifiable from the packet.** CONTRACT.txt:139 requires reproducing "the pivotal-height failure"; no file, script, or result in manuscript.tex, BARRIERS.txt, or STAR_BARRIER.txt defines it. Likewise frontier line 50 ("random-order marginal rules with bounded rescaling are also blocked") has no supplied source, yet Attack A (line 98–99) instructs avoiding it. Name the artifact/hash for each.

**4. (Medium) Calibration omits the star-barrier replay.** Attack B's acceptance hinges on escaping STAR_BARRIER.txt (CONTRACT.txt:112–113), which uses the transport/F_c convention (STAR_BARRIER.txt:5–11) and exact primal/dual witnesses m=2..6 (line 70). The calibration list (lines 137–141) replays only the manuscript certificates in coalition/monotonicity-row convention. A new interacting family will be checked against a barrier whose convention was never calibrated. Add the star witnesses to the replay.

**5. (Medium) Attack A does not name the envelope barriers it must escape.** CONTRACT.txt:91 starts from leave-one-owner-out dependence; BARRIERS.txt §5 shows the M_i envelope costs exactly kT, §6 blocks softmax envelopes, §4 states the envelope reduction is equivalent to the target. The contract cites only common prices and fixed-order rules (line 98). Require Attack A to state which hypothesis of §5/§6 its normalizer violates, as line 113 does for Attack B.

**6. (Low) "Complete argument" vs "repair" at the 6h gate.** Lines 82–84 permit continuation only if a complete argument exists, then allow "verify/repair its proof." Define "complete" (every step written, no open obligation) and bound "repair" to review-flagged local errors.

**7. (Low) "one bounded independent construction attempt" (line 119)** reads as a bounded-family attempt, contradicting line 127. Replace with "time-bounded."

**8. (Low) Frontier line 45 omits k≥3** (manuscript.tex:280).

## Scope limitations
No files run; verification scripts, repository 075e392, `verify_auxiliary.py`, and any "pivotal-height" artifact not inspected. Novelty not assessed.

## Verdict
Findings: criteria 1–2 leak bounded-family/fixed-instance ambiguity; calibration 3–4 cannot be executed as written.
