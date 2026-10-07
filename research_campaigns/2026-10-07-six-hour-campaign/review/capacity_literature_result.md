Within the bounded inspection, I found no theorem directly matching the combination of fixed owners, downward-only capacity reports, payment-only utility, all-profile truthfulness, every-coalition coverage, and an \(O(T\log K/\log\log K)\) total-payment bound. This is only a scoped comparison, not a novelty conclusion.

### Closest primary results

1. Gui and Ergun, “Dual Payoffs, Core and a Collaboration Mechanism Based on Capacity Exchange Prices in Multicommodity Flow Games,” WINE 2008, pp. 61–69.

Primary full-proceedings PDF: [WINE 2008 proceedings](https://www.nzdr.ru/data/media/biblio/kolxoz/Cs/CsLn/I/Internet%20and%20Network%20Economics%2C%204%20conf.%2C%20WINE%202008%28LNCS5385%2C%20Springer%2C%202008%29%28ISBN%209783540921844%29%28747s%29_CsLn_.pdf)  
Stable publisher metadata: [Springer proceedings](https://link.springer.com/book/10.1007/978-3-540-92185-1)

Read: abstract; §3.1 “Dual Payoffs,” Theorem 2; §3.2 “An Arbitrary Allocation in the Core,” Example 1; and the opening of §4. I did not obtain the longer working-paper proof to which the WINE chapter refers.

Theorem 2 says that capacity-exchange prices set equal to capacity market prices induce the corresponding dual payoff. The paper records \(D\subseteq C\) and \(D\subseteq I\), while showing that neither arbitrary core allocations need be price-induced nor arbitrary inverse-feasible price allocations need lie in the core. Section 4 states that unique ownership is a special condition under which inverse feasibility implies core membership.

Comparison:

- Report/action domain: decentralized commodity routing and capacity buying/selling at centrally imposed prices, not direct revelation of an owner’s capacity with only binding underreports.
- Utility: shipping revenue plus or minus capacity-exchange transfers, not payment-only utility.
- Ownership: capacities and commodities belong to players; multiple owners per edge are admitted generally, while unique ownership is an additional favorable condition.
- Incentive concept: inverse-feasible prices make socially optimal routing a best response inside the grand coalition. This is routing equilibrium, not dominant-strategy truthfulness of capacity reports.
- Coalition coverage: dual payoffs are ordinary efficient core allocations at a fixed instance. No all-profile capacity-monotone selection is supplied.
- Subsidy: transfers are capacity purchases/sales and balance internally; the result is not a subsidized-core theorem.
- Complexity parameter: no bound in the number \(K\) of dual vertices/minimal cuts.

Thus this is the closest inspected dual-price/core mechanism, but it does not subsume the candidate theorem.

2. Agarwal, “Designing Allocation Mechanisms for Carrier Alliances,” Georgia Tech dissertation, especially Chapter 2.

Primary author-institution repository PDF: [Georgia Tech dissertation](https://repository.gatech.edu/bitstreams/09442d28-9fd0-4095-9694-c9f4fe64f0c7/download)

Read: Chapter 2’s model and §§2.2–2.5, including Theorems 1–6, Corollary 7, and Theorem 10.

Relevant exact results:

- Theorem 1, PDF p.31: feasible nonnegative capacity-exchange prices exist that make a prescribed centralized optimum solve every Limited Control inverse problem.
- Theorem 2, pp.40–44: Strict Control can still produce centrally infeasible combinations of individually optimal routings.
- Theorem 3, pp.44–45: Limited Control preserves centralized feasibility.
- Theorems 4–6, pp.47–49: Strict Control may exclude core allocations; its attainable allocations are a subset of Limited Control’s; Limited Control may also generate noncore allocations.
- Corollary 7, p.50: adding every coalition-stability constraint produces a feasible stabilized inverse problem whose feasible solutions are core allocations.
- Theorem 10, p.58: Strict Control prices prevent a profitable secondary capacity market.

Comparison:

- Reports: capacities, demands, and revenues are fixed model inputs. Carriers choose routing/acceptance decisions; they do not strategically report capacity.
- Utility: direct shipping revenue plus exchange payments, with carriers potentially paying for others’ capacity.
- Fixed ownership: carrier-owned flight legs and carrier-owned demands, often with a carrier owning several resources and loads.
- Coalition coverage: Corollary 7 explicitly enforces all core inequalities, but by adding \(2^{|N|}-1\) stability constraints to an inverse program at the fixed instance.
- Subsidy: transfers are exchange payments; the allocation is efficient and budget balanced rather than externally subsidized.
- Complexity: exponential coalition enumeration is discussed in terms of the number of carriers, not \(K\), and no logarithmic subsidy estimate appears.

This is a strong fixed-profile core-implementation comparator. Its “behavioral incentive” is compliance with routing induced by exchange prices, not report truthfulness.

3. Agarwal and Ergun, “Mechanism Design for a Multicommodity Flow Game in Service Network Alliances,” Operations Research Letters 36(5), 520–524 (2008).

Stable metadata/DOI: [DOI 10.1016/j.orl.2008.04.007](https://doi.org/10.1016/j.orl.2008.04.007)

I did not obtain a free original copy of the journal article during this bounded run. I therefore rely only on its metadata and on the substantially fuller primary dissertation treatment above, not on uninspected journal theorem text.

4. Gui, “Collaboration Mechanism Design under Data Uncertainty in Multicommodity Flow Networks.”

Primary author-hosted proposal: [Georgia Tech ARC proposal](https://sites.cc.gatech.edu/computing/arc/fellowshipabstracts/Luyigui.pdf)

Read: the complete two-page proposal.

It explicitly separates:

- Static fixed-parameter results: exchange prices can direct selfish users toward socially optimal routing; under special prices or network conditions they can also support coalition stability.
- Robustness: one fixed-price mechanism should remain feasible as capacity, demand, and revenue vary over specified ranges without a known distribution.
- “Price of robustness”: loss of routing revenue relative to the scenario-optimal routing.
- Coalition stability: identified as unresolved for the proposed stochastic mechanisms; the proposal gives examples where users prefer to leave the coalition.

Consequently, “robust” here means feasibility and routing performance across parameter realizations. It does not mean truthful reporting under capacity uncertainty. The proposal’s agents are initially forced to remain in the grand coalition and then make capacity-management/routing choices. It supplies neither direct-report truthfulness, every-coalition payments, external-subsidy bounds, nor a \(K\)-dependent theorem.

The proposal cites “Robust Capacity Exchange Price Mechanisms in Multicommodity Flow Networks” as submitted to WINE 2009. I did not locate a free primary full text, so its precise theorem statements remain unresolved.

### Random-order, semivalue, and sampled-dual relation

The inspected Gui–Ergun mechanism uses deterministic optimal dual prices, not random deletion, random-order marginal contributions, or a semivalue. Agarwal’s mechanism uses inverse optimization around a centralized flow, likewise without owner deletion or sampled-dual averaging.

The candidate’s endpoint marginal
\[
\mathbb E[F(B_{-i},1)-F(B_{-i},0)]
\]
has the mathematical form of a Bernoulli-weighted probabilistic value/semivalue, but I found no inspected primary source that combines such marginals with conditional own-deletion dual prices to obtain both report monotonicity and coalition domination. This statement is confined to the searches performed; it is not an assertion that no such result exists.

### Concrete defects in the supplied comparison

- [MECHANISM_SOURCE_COMPARISON.txt:105](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-035728-cd030710/workspace/research_campaigns/2026-10-07-six-hour-campaign/MECHANISM_SOURCE_COMPARISON.txt:105) says the named topics were searched, but omits the closest directly relevant Gui–Ergun and Agarwal–Ergun capacity-exchange results. Add the WINE Theorem 2/§4 comparison and the dissertation’s Theorems 1–6 and Corollary 7.

- [MECHANISM_SOURCE_COMPARISON.txt:109](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-035728-cd030710/workspace/research_campaigns/2026-10-07-six-hour-campaign/MECHANISM_SOURCE_COMPARISON.txt:109) currently states “no matching theorem” before documenting these named comparators. The conclusion remains supportable within scope, but only after explicitly distinguishing their routing equilibrium from capacity-report truthfulness.

- [MECHANISM_SOURCE_COMPARISON.txt:114](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-035728-cd030710/workspace/research_campaigns/2026-10-07-six-hour-campaign/MECHANISM_SOURCE_COMPARISON.txt:114) leaves semivalue/random-order work as a future check. Verification should search specifically for probabilistic values with Bernoulli coalition weights and strategyproof endowment-withholding mechanisms; the present run did not establish comprehensive coverage of that literature.

- [HYBRID_SHARP_BOUND.txt:8](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-035728-cd030710/workspace/research_campaigns/2026-10-07-six-hour-campaign/HYBRID_SHARP_BOUND.txt:8) describes the final rule as “deterministic,” while [line 31](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-035728-cd030710/workspace/research_campaigns/2026-10-07-six-hour-campaign/HYBRID_SHARP_BOUND.txt:31) calls it a mixture of hybrid rules. For literature-facing prose, say “deterministic expected-payment map obtained by analytically averaging report-independent random masks and \(q\)” to avoid confusion with universal truthfulness or realized-mask core coverage.

Unresolved: the full robust-capacity-exchange submission, the longer proof referenced by WINE Theorem 2, and a systematic primary-source search of probabilistic-value/semivalue literature. No purchases or outreach were made.