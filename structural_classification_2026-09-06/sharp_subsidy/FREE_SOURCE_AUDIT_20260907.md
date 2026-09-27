# Free-source priority audit: claims, stability and recent matching work

Follow-up: [PRIORITY_ORIGINAL_COMPARISON.md](PRIORITY_ORIGINAL_COMPARISON.md) now completes the priority-games comparison for the freely retrieved accepted manuscript; the earlier retrieval failures below are historical.

Follow-up: [FREE_SOURCE_ATTAINMENT_AUDIT.md](FREE_SOURCE_ATTAINMENT_AUDIT.md) now completes the Bejan-Gomez original-definition comparison that was still open below. Other unresolved comparisons retain their stated status.

Audit date: 2026-09-07. **Novelty unconfirmed; primary sharp-constant goal active.** Current mathematical bounds remain 1/3 <= S_3 <= 2/5. This checkpoint completes specific model comparisons, not an exhaustive priority search or specialist review.

## 1. Almost-core optimization: a directly relevant established framework

R. Zou, B. Lin, M. Uetz and M. Walter, *Algorithmic solutions for maximizing shareable costs*, Networks 84 (2024), 385–397. [Publisher original, full HTML](https://onlinelibrary.wiley.com/doi/10.1002/net.22240).

Sections 2 and 4 define the almost core by keeping proper-coalition cost inequalities and dropping budget balance. They optimize total cost shares, compare cost of stability and extended-core formulations, and discuss optimization/separation equivalence. This is a cost-game sign convention; it is not our three-sector profit model. The displayed formulation has no floors derived from original individual core maxima. The comparison confirms that optimizing total stable payment after relaxing only efficiency is an established framework. Our LP formulation and appeal to strong duality should not be presented as new. **Status: displayed-model comparison complete; no claim that all related literature is exhausted.**

## 2. Recent fairness–stability frontier: different model and constraint

Genjie Qin, *Fairness–Stability Trade-offs in Many-to-One Matching*, arXiv:2608.17295v1, submitted August 18, 2026. [Author preprint, full HTML](https://arxiv.org/html/2608.17295v1).

Section 2, equations (8)–(13), uses firms and workers, additive firm values, matching-specific local financing and an alpha-scaled coalition inequality. Fairness is imposed on worker bundles through EF1 and related criteria. Its M_j is a worker's maximum edge value, not an entire-core payoff maximum. Section 3 and Proposition 5 give a financing LP; Section 8 studies minimax frontiers, including three-firm cases. These are not three-sector strict teams, fixed original H_i/3 floors or a supplemental grand payment preserving unscaled coalition inequalities. The paper explicitly distinguishes its financing ratio from a literal subsidy budget. **Status: model and objective comparison complete; its proofs have not been independently reproduced.** Broad claims to originate sharp fairness–stability trade-offs or financing LPs would be inappropriate.

## 3. Priority games: relevant, but full-original comparison remains open

Iago Núñez Lugilde, Arantza Estévez-Fernández and Estela Sánchez-Rodríguez, *Priority coalitional games and claims problems*, Mathematical Methods of Operations Research 100 (2024), 669–701. [Publisher original preview](https://link.springer.com/article/10.1007/s00186-024-00876-x).

The abstract and accessible notes describe protecting a group relative to a previous allocation, and modifying coalitional games to implement weak or strong priorities. Accessible footnote 3 says the reference allocation is taken in the original core to ensure balancedness of weak priority games. This is an important distinction from independent coordinate maxima that need not be jointly feasible. However, the complete definitions and main theorems were not available in the publisher preview, so this is **a partial comparison, not a completed exclusion**.

Free institutional leads were found at the [VU repository](https://research.vu.nl/files/383916636/Priority_coalitional_games_and_claims_problems.pdf) and [Vigo handle](https://hdl.handle.net/11093/11185). Retrieval failed during this audit (VU returned HTTP 403; the browser reader returned internal errors). No purchase, login circumvention or outreach was attempted.

## 4. Core maxima together with taxes/subsidies: avoid overclaiming the combination

Mehmet Küçükmehmetoğlu, Yasin Fahjan and Muhammed Ziya Paköz, *Handling Exponentially Growing Strategies in Spatial Cooperative Games: The Case of the European Union*, Algorithms 17 (2024), 554. [Publisher original](https://www.mdpi.com/1999-4893/17/12/554).

Sections 3.1.2–3.1.3 display a tax/subsidy optimization followed by individual payoff maximization and minimization. The optimized tax/subsidy is held fixed during those coordinate optimizations. That order differs from our original-core maxima frozen before intervention. The source nevertheless shows why neither individual maximum-payoff LPs nor their appearance alongside subsidy models should be claimed as new. This audit uses the displayed definitions; it does not adopt or independently validate all interpretations or economic conclusions in that paper. **Status: sequence-of-optimization comparison complete.**

## 5. An exact bookkeeping equivalence for our own model

The following is a direct observation about the current problem, not a newly claimed general game-theory concept.

Let l_i=H_i/3, computed once from the original entire core. Nonnegativity and tightness of an optimal perfect matching give H_i<=w_j for each player in diagonal team j. Therefore sum_i l_i<=sum_j w_j=T.

Define an auxiliary TU game g by

    g({i})=l_i,
    g(S)=v(S) for every coalition with |S|>=2,
    g(empty)=0, so g(N)=T.

Then the minimum ordinary cost-of-stability supplement for g is exactly s_3(M). Indeed a nonnegative allocation covers all proper coalitions of g precisely when it covers all original proper coalitions and every floor l_i. At total T+s it also covers the original grand coalition. This is exactly the original optimization, in both directions.

Equivalently, the same feasible covering polyhedron results from replacing every proper-coalition value by max(v(S),sum_{i in S}l_i). The added inequalities follow from the singleton floors; conversely singletons recover those floors. The grand value remains T because sum l_i<=T.

This auxiliary game is only a comparison device. The actual market, all its original coalition constraints, and all H_i remain unchanged throughout the intervention. We never compute ideals in g. Although the original game is balanced, g can have an empty core: the positive subsidy examples already demonstrate this. Generic zero-subsidy statements for balanced games therefore cannot simply be applied to g.

The optimization belongs to an established cost-of-stability framework. What remains potentially distinctive is the endogenously restricted family of strengthened games arising from strict pair-additive assignment markets, and the structural bounds, extremal constructions and exact certificates proved for that family. Sharpness and priority of those results remain unestablished.

## 6. Current audit ledger and implications

Completed here: the specific displayed-model comparisons in Sections 1, 2 and 4, plus the elementary equivalence in Section 5. Partial: the priority-games original in Section 3. An author-hosted original of Bejan–Gómez's *Core extensions for non-balanced TU-games* was located but not successfully retrieved in full; it remains a source to inspect directly rather than citing a later paper as a substitute.

The earlier free-original gaps for Quint, Lucas and Stuart remain open. The broader claims/core-cover literature also remains incompletely audited. The conventional proofs and exact computational checks in this package do not certify novelty. Search-engine publication/crawl estimates were not treated as authoritative publication dates.

The next mathematical direction remains choosing globally coupled P weights, following LOCAL_RULE_NO_GO.md and the transportation lemma. No inspected source supplies the missing universal selection rule or a sharp constant for the frozen original three-sector problem. This is a statement about the sources inspected here, not proof that no such result exists elsewhere.
