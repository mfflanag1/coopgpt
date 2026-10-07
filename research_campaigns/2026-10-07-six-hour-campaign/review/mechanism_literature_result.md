## Priority-check result

I found no matching theorem or prior mechanism in the bounded free-primary-source search. The closest literature covers separate pieces—capacity-report truthfulness, structural minimal cuts, coalition stability, or LP-game core allocations—but not the combination in `BERNOULLI_LOG_BOUND.txt`: effective-capacity normalization, iid zero masks, conditioning on the owner’s zero mask, all-profile coalition coverage, and an \(O(\log K)\) total-payment bound.

This is a “not found in the inspected sources” result, not a novelty conclusion.

### 1. Huang–Mei–Yang–Cao (2025): closest model, nonmatching theorem

The paper uses nearly the same strategic model:

- finite acyclic single-source/single-sink networks;
- one player per edge;
- private positive capacities;
- underreporting only;
- payoff-only utility with no usage cost;
- DSIC defined exactly as payoff monotonicity under unilateral capacity increases.

See §§2.1 and the DSIC definition at lines 81–103 of the [free arXiv original](https://arxiv.org/html/2502.08248v1).

Its relevant results are:

- **Proposition 1:** the Shapley-value mechanism is DSIC and strongly individually rational.
- **Example 1 and Remark 2:** no core-selection mechanism, including nucleolus selection, can be truthful across all max-flow games.
- **Definition 2 and Theorem 1:** the MC mechanism averages the grand-flow value over every structural minimal cut and distributes each cut’s share in proportion to reported capacities; it is DSIC, SIR, split-proof, merge-proof, and cross-monotone.

Exact MC definition and theorem: [§4.1–4.2, Definition 2 and Theorem 1](https://arxiv.org/html/2502.08248v1#S4).

Status: **nonmatching**.

- The paper requires efficiency, \(\sum_i\phi_i(\hat c)=\hat v(N)\), rather than permitting a subsidy.
- Its MC mechanism is explicitly not always in the core; the authors state that players “may have incentives to collude” ([§4.2](https://arxiv.org/html/2502.08248v1#S4.SS2)). Thus it does not cover every coalition.
- It uses raw reported capacities and a deterministic average over all minimal cuts. It has no effective capacities \(D_e\), Bernoulli masks, minimum masked cut, own-zero conditioning, or \(K\)-dependent budget bound.
- Proposition 1’s Shapley mechanism is truthful but efficient; Example 1 implies it cannot simultaneously supply the candidate’s coalition-covering inequalities at every profile.

Indeed, the candidate evades the paper’s core-selection impossibility precisely by allowing \(\sum p>T\). At a fixed profile, coalition coverage plus equality \(\sum p=T\) would be a core allocation.

### 2. Cost-of-stability network papers: same subsidy concept, different games

Resnick–Bachrach–Meir–Rosenschein study **threshold network-flow games**, where capacities are fixed and a coalition has value \(0\) or \(1\) according to whether it can send flow at least \(k\). See Definitions 5–6 in the [free MFCS original](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/01/CoS-NFG-MFCS.pdf).

Relevant pointers:

- Definitions 11–13: supplemental payments, stable super-imputations, and cost of stability.
- Theorems 1–2: disjoint-winning-coalition lower bounds and hitting-set upper bounds.
- Theorem 4: connectivity-game cost equals the underlying max-flow.
- Theorem 5: for threshold \(k\) and grand max-flow \(F\), total stable payments are at most \(F/k\).

Status: **conceptually close but nonmatching**.

Their stability inequalities are analogous to coalition coverage, but:

- coalition worth is thresholded and binary, not the actual coalition max-flow;
- reports and incentive compatibility are absent;
- there is no all-profile payment rule;
- no Bernoulli conditioning or bound in terms of the number \(K\) of structural minimal cuts appears.

Terminology needs care: Definition 13 labels the **total adjusted gains** \(v(N)+\Delta\) as `CoS`, whereas other cost-of-stability papers often reserve “cost” for the supplemental amount \(\Delta\). The candidate bounds total payments.

The broader Bachrach et al. paper defines external stabilization for arbitrary coalitional games but concentrates its substantive bounds on weighted voting games; it likewise supplies no report-monotone selection theorem. See [The Cost of Stability in Coalitional Games](https://arxiv.org/abs/0907.4385), §§2–4.

### 3. Linear-production and LP-game results: fixed-profile core existence only

Samet and Zemel’s free original treats games whose coalition values are optimal values of linear programs:

- §2 defines \(v(S)=F(1_S)\).
- The dual payoff set \(D_P\) is contained in the core, proving fixed-game core nonemptiness.
- Theorem 1 concerns convergence of replicated-game cores to dual payoffs under uniqueness.
- Theorems 2–4 characterize when the core and dual-payoff set coincide.

See [On the Core and Dual Set of Linear Programming Games](https://www.tau.ac.il/~samet/papers/lp%20games.pdf), especially pp. 310–315.

Status: **nonmatching**.

These results show that a core payment exists for each fixed LP-game/profile. They do not select core points monotonically as one owner changes its resource report. Huang et al.’s Example 1 demonstrates that, for max-flow games, no choice of efficient core point can provide the required all-profile truthfulness. Consequently, Owen/LP duality cannot by itself imply the candidate theorem.

The classic Owen paper, *On the Core of Linear Production Games*, is bibliographically identified as Mathematical Programming 9 (1975), 358–370, DOI [10.1007/BF01681356](https://doi.org/10.1007/BF01681356). Search results exposed its abstract and metadata, but I did not obtain a clearly authorized free copy of the original article during this bounded check. I therefore did not rely on its full text.

### 4. Population monotonicity is not capacity truthfulness

A PMAS assigns an efficient core allocation \(x^S\) to every player coalition and requires
\[
S\subseteq T,\ i\in S\quad\Longrightarrow\quad x_i^S\le x_i^T.
\]

That is monotonicity as the **population grows**, not monotonicity in an incumbent player’s continuously reported capacity. See Definition 1 in the free original [Assignment Games with Population Monotonic Allocation Schemes](https://arxiv.org/abs/2210.17373), lines 38–51. Its Theorem 9 characterizes only which assignment games admit such schemes.

Status: **nonmatching**. Neither PMAS existence nor total balancedness supplies the candidate’s all-profile capacity truthfulness. Total balancedness says every fixed subgame has a nonempty core; it does not give a monotone selection across capacity profiles.

## Concrete source-comparison issue in the supplied proof

The historical-language caution at [BERNOULLI_LOG_BOUND.txt:133](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-030303-0b9b5ad7/workspace/research_campaigns/2026-10-07-six-hour-campaign/BERNOULLI_LOG_BOUND.txt:133) is appropriate, but “the proposed contribution” remains stronger than this priority check can establish. Suggested wording: “the apparently new ingredient relative to the sources inspected is …; priority remains unresolved.”

I found no clear mathematical defect in the targeted conditioning argument. The most important independent verification target is [lines 64–79](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-030303-0b9b5ad7/workspace/research_campaigns/2026-10-07-six-hour-campaign/BERNOULLI_LOG_BOUND.txt:64): formally verify that for every fixed \(B_{-e}\), the complete minimizing-cut family—not merely its minimum value—is identical for every positive own report, including zero-capacity ties. That is the distinctive step not supplied by the inspected literature.

Limitations: this was a bounded web search, not a systematic citation-database or paywalled-literature review. Shapley (1961), Kalai–Zemel (1982), and Owen (1975) were identifiable through later originals and metadata, but not all original full texts were freely inspectable. No inference of novelty should be made from those access limits.