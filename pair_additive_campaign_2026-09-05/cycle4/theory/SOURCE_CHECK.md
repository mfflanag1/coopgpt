# Cycle4 bounded source and priority check

Checked September 5, 2026 (retrieval completed September 6, 03:29 UTC). This is a focused continuation of `cycle3/SOURCE_CHECK.md`, with exactly three search queries. It is not a full priority review. Raw retrieval responses, requests, read scope and unresolved gaps are in `source_retrievals.json`.

## Claim being compared

The canonical result is `../experiment/reduced_candidate.json`, with the ordinary proof in `../experiment/EXPERIMENT.md`: 21 labeled players, seven per sector, complete strict triples with nonnegative pair-additive values, T=15, and a nonempty whole payoff core. A target is fixed at the positive first sorted-leximin level 1/3 while its maximum payoff over that same whole core is 3. The exact ratio is 1/9. The first-floor witness is not asserted to be the complete selector. This refutes the campaign's proposed 1/6 bound; it does not identify an established published conjecture that has been resolved.

## Primary sources rechecked

**Vazirani.** The current arXiv record still identifies [version 6, revised November 20, 2025](https://arxiv.org/abs/2402.11437), titled *Fair Core Imputations for the Assignment Game: New Solution Concepts and Efficient Algorithms*. Its [full HTML, especially sections 1 and 3.1](https://arxiv.org/html/2402.11437v6), defines the underlying game on a bipartite weighted graph. It treats leximin, leximax and min-spread selection and gives combinatorial algorithms. This is direct precedent for the selector and fairness motivation, but its model does not cover cyclic three-sector strict triples. That scope distinction is an inference from the definitions, not a claim that all its methods fail outside bipartite markets. The [author's current publication list](https://ics.uci.edu/~vazirani/) now lists the paper under EC 2026; the proceedings text was not separately compared with arXiv v6. No numerical bipartite ideal-payoff guarantee was newly established or reattributed in this cycle.

**Atay–Núñez (2019).** The publisher's full primary text of [*Multi-sided assignment games on m-partite graphs*](https://link.springer.com/article/10.1007/s10479-019-03256-5) was reread at section 2, Theorem 1, and section 6. Their model assigns nonnegative pair values and allows productive connected coalitions smaller than the full number of sectors. Theorem 1 gives balancedness and equality of the whole core with composed bilateral cores when the sector graph is cycle-free. Section 6 explicitly contrasts strict models requiring one agent from every sector; its example illustrating a composition failure has unequal sector sizes. Therefore neither that example alone nor their generalized tree theorem establishes the same labeled core for our equal-size strict model. Our cyclic three-sector counterexample also lacks the cycle-free hypothesis. Their paper explicitly describes strict pair-additive models in earlier Quint and Stuart work: pair additivity itself is established modeling territory. It contains no directly matching sorted-leximin ideal ratio claim in the passages inspected.

**A recent related paper surfaced within the same queries.** [El Obadi, Miquel and Núñez, *Assignment markets with capacitated middlemen: core and competitive equilibria*](https://link.springer.com/article/10.1007/s00182-026-01007-y), published August 25, 2026, studies middleman-independent buyer–seller values with capacity on the middleman side. Its abstract and introduction concern core nonemptiness and competitive-equilibrium/dual-set distinctions. This is relevant to preserving the whole core when changing representations, but the inspected material does not supply the target leximin protection claim. The full proof development was not audited; a text search finding no “leximin” is not a substitute for one.

## Search coverage and remaining gaps

The only three search queries were:

1. `"three-sided assignment" leximin egalitarian pair additive core`
2. `Vazirani equitable core imputations assignment game 2402.11437`
3. `Atay Núñez 2019 generalized multi-sided assignment games cycle-free core composition`

Primary records and full-text pages were then opened directly. Secondary aggregator results were not used to establish theorem scope. No directly matching theorem or example was identified in this bounded check. This is a nonfinding within the stated coverage, not evidence that the 1/9 construction, its critical budget, or the protection question is new across the literature.

The previous unread-original gaps remain: Quint's original theorem statements, Lucas's original balancedness treatment, Stuart's original strict-chain paper, and the full *Assortative multisided assignment games: The extreme core points* paper. Atay–Núñez's account of earlier work is informative but does not close those original-source gaps. Cycle3's fixed-priority lexicographic-versus-sorted-selector distinction is retained; that earlier source was not reread here.

External specialist priority review remains pending. The pair-additive model, residual-cover LP duality, matching/triple linear combinations, and exact rational verification are not claimed as new methods. The present evidence supports an internally proved finite counterexample to the campaign conjecture; it supplies neither novelty certification nor a field-level significance verdict.
