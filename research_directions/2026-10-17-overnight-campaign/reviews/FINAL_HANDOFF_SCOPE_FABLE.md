**Provisional verdict: findings (scoping/consistency only; no mathematical defect identified in reviewed scope).**

Most important: `handoff/READ_FIRST.txt:47-49` states the common-cap growing factor Θ(M^(1/4)) without the coalition-contract qualifier, inviting an individual-vs-coalition misread that `CAMPAIGN_OUTCOMES.txt:26-32` explicitly warns against.

## Findings

**1. Medium — READ_FIRST.txt:47-49, missing contract qualifier.** "Rank-three common-cap systems already need a growing factor: Theta(M^(1/4))…" CAMPAIGN_OUTCOMES.txt:26 adds "when all coalitions are protected" and :30-32 notes the individual-OUT upper is 3. Fix: "…need a growing factor under all-coalition TCWM: Theta(M^(1/4))… (individual OUT on this technology has constant upper 3)." Verify against root21/23 (not supplied).

**2. Medium — READ_FIRST.txt:118-124 vs RESEARCH_FRONTIER_RANKING.txt:4-7 and CAMPAIGN_OUTCOMES.txt:75-78, next-campaign mismatch.** READ_FIRST's "WHERE TO GO NEXT" omits the ranked mainline (coalition-size dependence at arity 3) and lists the original individual gap as a live choice, which the ranking files under "DEFERRED… reopen only with a new coupling idea." Fix: replace line 121-122 with "coalition-size dependence at arity three (mainline), arbitrary-graph full OUT (alternate), pairwise gain-only TCWM; the original individual gap is deferred pending a new coupling idea."

**3. Low — READ_FIRST.txt:10-12 / CAMPAIGN_OUTCOMES.txt:9-11, unexplained "stronger contract, still-open gap."** All-coalition TCWM implies singleton TCWM, so (d+1)/2 is also an individual upper in d. The texts assert the original gap stays open without stating the parameter (cut count K / owner count n per READ_FIRST:5-6, ranking:129-131) in which it is measured. Fix: add "The original gap concerns growth in structural-cut/owner count at unbounded resource dimension, not the fixed-d constant."

**4. Low — RESEARCH_FRONTIER_RANKING.txt:63-65, stop rule slightly over-broad.** "Stop if progress merely reweights fixed whole-owner marginal contributions" — root64:52-53 excludes only *nonnegative* fixed weights; signed fixed weights are "not excluded." The suggested campaign does leave the blocked class, but the stop rule could prematurely halt a signed-weight attempt. Fix: insert "nonnegative" before "whole-owner."

**5. Low — READ_FIRST.txt:1-2.** "INTERIM" / "This file is being updated" contradicts a final public handoff. Fix: mark final or remove.

**6. Low — terminology/reconciliation.** READ_FIRST:16 "full reusable outside production" vs "pooled" elsewhere (REVIEW_READING_ORDER:18-19); suggest "pooled." READ_FIRST:128 "26 check entry points" vs root61:58 "21-check math replay" — confirm these are distinct scopes in CURATED_CHECKS.json. root12:33 lists the partial-floor frontier as "in progress" while READ_FIRST:19-21 and READING_ORDER:58-61 present it as adjudicated; root12's status line appears stale.

No issues found in: total-vs-gain distinctions (READ_FIRST:82-86, READING_ORDER:20-22,101-103, ranking:101-102); architecture-vs-unrestricted framing (root64/65, ranking:27-34, consistently labeled); energy claims (uniformly conditional; root61 numbers consistent across files); novelty hedging.

## Scope limitations

Not independently proved: the (d+1)/2 and 1+c(d-1) theorems and lowers; the signed-L1 transfer and its derivative ranges; Θ(M^(1/4)) common-cap rate; p>2 bounds; one-common/private-DR 3/2; K_D~√(8D/π); (n-4)/22≤K_n≤n/2; square-cone factor 2; root64's threshold identity and weak-limit passage; root65's dual coefficients (checked only the inequality direction and r² constant gap, 3s², (n+1)/2, and the (a,b)→(a+b,(a−b)e) map for arithmetic consistency). Adjudications 08/09/19/20/21/23/30/40/50/57/58/62/63 and all proof files were not in the packet; no scripts were run.

## Verdict

Findings — editorial scoping fixes above; the recommended campaign does exit the fixed-nonnegative whole-owner marginal class.
