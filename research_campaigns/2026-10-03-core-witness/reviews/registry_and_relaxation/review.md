**Provisional verdict: findings.** `relaxation.py` matches the described relaxation; the defects are in the selected supports and the held-out design. Nothing was executed; all checks are by reading and hand arithmetic.

## Findings

**1. High — CW-02 and CW-05 are trees once the doubled incidence is collapsed (`support_registry.py` 227, 235; `supports.json` 173–204, 532–563).**
- **Evidence:** Their only cycle is the parallel edge from the repeated-label team (`[0,0,2]` and `[0,1,0]`). By hand, the simple incidence graph of each has 17 edges on 18 nodes, is connected, and has one degree-three label. That is a one-hub tree.
- **Consequence:** `cycle_rank` is computed on the multigraph, so both escape `ONE_HUB_THEOREM` and the tree exclusion. The stated intent that all incidence trees are excluded holds only under the multigraph reading. One of the two is a held-out support.
- **Verify:** Check whether `ONE_HUB_THEOREM.md`, `LEAF_DILATION_THEOREM.md` or `REDUCTIONS.md` cover or reduce repeated-label teams. If so, both are safe-class members; none of these files is in the packet.

**2. Medium — held-out supports are not independent of the tuning supports (`supports.json` 648–683, 729–745; `support_registry.py` 350).**
- **Evidence:** CW-06 is exactly CW-01 plus the team `[6,4,1]`. CW-05 and CW-03 are single reconnections of the same seed (index 23).
- **Consequence:** Solving CW-01 or CW-03 leaks structural information into the held-out pair.
- **Verify:** Require held-out seeds to be disjoint from tuning lineages, or disclose the dependence.

**3. Medium — heldout-before-solve is self-attested only (line 451).**
- **Evidence:** `optimization_run_during_generation` is a hard-coded `False`, the timestamp is self-generated, and the files are untracked.
- **Verify:** Anchor `supports.sha256` in a commit or external timestamp, and have solver outputs embed the registry hash.

**4. Low–Medium — search-scope wording overstates what ran (`supports.json` 24–28).**
- **Evidence:** `queue_nodes_processed` is 11 against 13 seeds; the 80-pool cap fired first.
- **Consequence:** Two seeds were never expanded and depth 2 was never reached, yet `max_mutation_depth: 2` and "bounded BFS" suggest otherwise.
- **Verify:** State the realized depth and seed coverage in the registry.

**5. Low–Medium — inventory may miss or mis-size known supports (lines 23, 64–77).**
- **Evidence:** Only six key names are harvested, and `m` can be inherited from an ancestor object. Since `m` is in the signature, a wrong `m` silently defeats the known-support match.
- **Consequence:** The novelty claim is disclosed as limited to retained artifacts, but only the 34 frontier records are tested for extraction.
- **Verify:** Audit `m_provenance` on inherited entries and check for other support key names.

**6. Low — the checker certifies feasibility only (`relaxation.py` 108–109).**
- **Evidence:** It reconstructs feasibility exactly but checks no dual.
- **Consequence:** "m8 relaxed 3/8" is a lower bound on the relaxed maximum, not its optimum, unless the parent holds a separate dual.

**Checked with no defect found:**
- **Relaxation rows:** each constraint family you listed is present with correct signs and the checker re-expresses each independently; `T=1` is forced by coverage plus the two sum constraints.
- **No promotion:** scope strings disclaim subsidy and upper-optimum status; `above_one_third` is only a flag.
- **Matching validity and statistics:** hand-recomputed for CW-01, 03, 05 and 06.
- **Isomorphism and canonical form:** the VF2 sector-coloured multigraph test and the `canonical` construction look sound; lex-minimality was not recomputed.
- **`C_s` margins:** the formula matches `UNIFORM_TEMPLATE.md`.

## Scope limitations
- `retained_inventory.json`, the frontier JSON and the safe-class theorem files other than `UNIFORM_TEMPLATE.md` were not supplied.
- The `LEAF_AND_DELETION` filter (at most three leaves) and the use of the uniform template on repeated-label supports are unverified; both only over-exclude.
- Hashes were not checked.

## Verdict
**Findings.** Resolve finding 1 before any solve on CW-02 or CW-05, and finding 2 before relying on held-out results.
