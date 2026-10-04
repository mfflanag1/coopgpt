## Provisional verdict

**No invalid step found in ONE_SIDED_QUOTA_THEOREM.** One evidence gap in AGGREGATE_FLOW_OBSTRUCTION (unverified, not shown wrong). Everything here is a hand check of the supplied text; nothing was executed, and the registered instances do not test the nonunit subclass.

## Findings

**1. Medium — `AGGREGATE_FLOW_OBSTRUCTION.txt` L21–24, L29–30: the relaxation value 5 depends on G01's middle topology, which is not in the packet.**
- The step "use 5/2 on each source" needs a flow of value 5 with both source loads in [2.3, 2.7]; capacities (3,3) and T=5 only guarantee some split in [2,3].
- If only an extreme split is feasible (e.g. source 2 reaches only one capacity-2 sink), the scaled maxflow is 4.7 < 24/5 and the obstruction disappears.
- "Each source alone supplies 3" (L30) has the same dependence.
- The bound V ≤ 24/5 (L17–19) also needs z to be zero on middle players, or middle arcs not to be players.
- Verification: quote G01's arcs from DISCOVERY.json and exhibit the explicit flow. If it holds, the arithmetic is right (4.8 + 0.1 + 0.1 = 5) and the conclusion is properly limited to a proof-route obstruction.

**2. Low — `PREREQUISITE_TRANSFER.txt` L55–57 against L63–73.**
- The "Limitations" paragraph still says parallel source arcs block the transfer. That is true only of the sourceward map; the strengthening below it supersedes it for unique sink ports.
- This is a wording clash, not an error, but it should be reconciled so the theorem's citation is unambiguous.

**3. Low — theorem L74–76.**
- The Atay–Núñez–Solymosi citation cannot be checked here. It is not load-bearing because Step 4 is self-contained.

## Steps checked with no defect

- **Sinkward transfer (Step 2).** Lemma 1's hypothesis holds for each middle arc into R_j with the unique b_j, whatever the source multiplicity. The map fixes every source coordinate, so source projections of C and F coincide and sink maxima carry into F. The identification F = C(w) holds in both directions.
- **Endpoint game (Step 3).** After capping, each worker carries at most one unit, so shared heads and parallel middle arcs do not constrain it. w is exactly the many-to-one assignment game with firm quotas r_i and identical neighbourhoods for co-headed firms.
- **Salary proof (Step 4).** The disjoint teams {i} ∪ μ(i) cover all players after balancing, which forces (iii). The drop-j and swap coalitions give (i) and (ii). In sufficiency, |μ(i)| = r_i gives the injection U∖μ(i) → μ(i)∖U. Dummy players are forced to zero. Y is closed under min and max, so y⁻ and y⁺ give the two side-optimal points.
- **Binary middle ideals and m ≤ T (Step 5).** The min-cut allocation is a core point of the same game, since capping does not change v.
- **Subsidy bound (Step 6).** The three-point average plus raises gives q·max(0, m−1)/3 ≤ (T−q)/3.
- **Sharpness (Step 7).** The chain family lies in the class (unique ports, quotas 1), and its lower count is n−1 + (n+2)/3 = n + (n−1)/3.

## Scope limitations

- DISCOVERY.json, UNIT_FLOW_BOUND.txt and G01's arc list were not supplied.
- The chain upper certificate was not re-audited beyond consistency with the theorem's bound.
- Novelty and general endpoint compatibility are not assessed, as they are not claimed.

## Verdict

**Findings**: the theorem is sound in the reviewed scope; the obstruction note has insufficient evidence in this packet until G01's topology and the explicit flow are shown.
