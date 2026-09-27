**Provisional verdict: findings.** The most important is that REVIEW.md:36 reports a literature gap as closed with no support in the packet. Nothing was executed; this is a document comparison only.

## Findings

**1. Medium–High — REVIEW.md:36, source status unsupported and narrowed**
- The priority review (l.33) lists the 2023 *Extreme Core Points* preprint as uninspected in full. The only closure it records is the 2025 population paper (l.24).
- The subsidy audit (l.103–104) lists Quint/Lucas/Stuart as unresolved and records no 2023 closure or "priority-games accepted manuscript".
- The review also drops the Rosenmüller (2000), Isbell-original and indexed-only thesis gaps.
- *Correction:* cite the dated record that closes the 2023 comparison, or mark it open, and restore the omitted gaps. Check that it is not conflated with the 2025 paper.

**2. Medium — REVIEW.md:18, 52, barrier scope overstated**
- The review says the barrier "rules out the specified aggregate route" and that the affine route has an "exact stopping certificate".
- The audit (l.141–143) only rules out reducing the coefficient at fixed intercept 1/18 in the displayed relaxation. Other intercepts, non-affine envelopes and joint constraints remain open.
- *Correction:* restate with that scope.

**3. Medium — REVIEW.md:42–46, sync wording asserts completed actions**
- "Before this sync", "now report" and "does not force-push" read as done, but REVIEW.md is itself untracked in the snapshot and no commit or remote ref is given.
- Line 46 says "Current README/STATUS… incorrectly reported" and then "now report", which is contradictory.
- The link is to a private repository, so it is not usable by outside specialists.
- *Correction:* use conditional wording or add the pushed branch and commit hash; confirm the README/STATUS contents.

**4. Medium — REVIEW.md:5, graph claim ambiguous and ranking unsupported**
- "Strengthening from leximin to every core selection" can be read as a positive guarantee for every selection. PAPERS.md:14–23 supports only c(G)=R(G) and that cycles defeat the best allocation.
- "Strongest recent progress" has no priority basis here: the September 5 audit covered only the stable-core, asymptotic and assignment manuscripts, and PAPERS.md:27–28 says graph novelty "remains qualified".
- *Correction:* state the direction of the claim precisely, and note that no priority audit of Papers 1, 4 or 5 is evidenced.

**5. Low–Medium — REVIEW.md:18, 38, subsidy review status**
- "Reviewed… proof" omits that the reviewed snapshots predate the all-leaf repair and verifier changes (audit l.93, 137–139), which only the coordinator checked.
- The reviewer did not execute scripts (l.50–51).
- 39999/100000 improves on 2/5 by 10⁻⁵, which should be stated so the row is not read as substantial progress.

**6. Low — REVIEW.md:15, 17, dropped hypotheses and attribution**
- Line 17 omits "positive integral worth and nonempty entire core" (PAPERS.md:19–20).
- Line 15 omits "singleton-normalized exact games".
- The priority review (l.14) says prior matrices recover the lower-bound construction's coefficient and remainder order, so the candidate is the overlap bound and comparison (l.15), not the construction.
- "Infimum over growing sizes" and "player can depend on the allocation" are not evidenced in the packet.

**7. Low — REVIEW.md:48, non sequitur**
- That notes and manifests remain does not show the verifiers are independent of the excluded files.
- *Verification:* run the builds and manifest checks from a clean clone.

## Scope limitations
- Only four files were supplied; README/STATUS, VALIDATION.json, the graph package review, git state, and the contact record were not.
- Line 38's "September 20… two clarifications" and the repository counts are unverifiable here.
- No mathematics was re-derived.

## Verdict
**Findings.** The bounds (1/3 ≤ S₃ ≤ 39999/100000, 13/18 at 1/18, 29/82), the six-paper count and the asymptotic and assignment formulas agree with the paper index and audit. Corrections are needed for items 1–4 before release.
