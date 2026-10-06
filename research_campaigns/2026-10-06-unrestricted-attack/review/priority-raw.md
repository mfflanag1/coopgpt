## Audit result

The hierarchy proof appears internally sound and does establish the claimed lower bound, conditional on the manuscript’s mechanism definition and upper theorem:

\[
B_k\ge \left(\frac12-o(1)\right)\frac{\log k}{\log\log k},
\qquad
B_k\le (1+o(1))\frac{\log k}{\log\log k}.
\]

Thus the proposed unrestricted minimax order is \(\Theta(\log k/\log\log k)\), with lower coefficient \(1/2\) and upper coefficient \(1\). I found no cited earlier theorem that directly implies this result. Historical priority remains unconfirmed.

### Proof/model check

The central argument in [HIERARCHY_LOWER_CANDIDATE.txt](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261006-005425-1c44e7dc/workspace/research_campaigns/2026-10-06-unrestricted-attack/HIERARCHY_LOWER_CANDIDATE.txt:8) checks out:

- Symmetrizing a rule over pool and within-pool permutations preserves nonnegativity, coalition coverage, budgets, and same-owner report monotonicity.
- After one low owner in a type-\(h\) pool changes its own report from \(1\) to \(m\), that owner belongs to the symmetric class of \((h+1)(n_{h+1}+1)\) high owners. The destination budget therefore gives equation (1).
- This transports only the changing owner’s payment. It does not assume that unchanged owners retain payments.
- Both proposed base coalitions have the stated values. Combining their coverage inequalities produces exactly the full type-\(d\) pool payment in the base budget.
- Padding with type-\(d\) pools is legitimate: it increases the \(h=d-1\) denominator and leaves the other relevant ratios unchanged.
- In the sharper family, \(A\asymp d^2\log d\), \(L\asymp d^2(\log d)^3\), hence \(\log L=(2+o(1))\log d\) and \(\log k_d=(2+o(1))d\log d\). The coefficient \(1/2\) follows.

I found no algebraic defect in equations (1)–(5) or the asymptotic inversion. The proof nevertheless lacks the proposed explicit nonnegative dual/certificate and finite exact examples noted at lines 76–79. Those would be useful verification artifacts, but their absence does not presently expose a mathematical gap.

### Exact distinctions from prior work

1. **Own-report monotonicity**

The manuscript compares \(y_i(t,c_{-i})\) for the same owner \(i\) as that owner changes capacity. This is the only cross-profile comparison used by the hierarchy proof.

2. **Other-owner or population monotonicity**

A PMAS or cross-monotonic profit-sharing scheme compares an unchanged player’s payoff when other players enter or leave. This is not assumed and is not implied by own-report monotonicity.

3. **Fixed-game stability**

At each report profile, coalition coverage means \(y(S)\ge v_c(S)\). With subsidies, \(\sum_i y_i\) may exceed \(v_c(N)\), so this is not a core allocation. Only at factor \(B=1\) do coverage and the total budget force core efficiency.

### Closest original sources

**Huang–Mei–Yang–Cao (2025).** Their model has private edge capacities and own-capacity incentive compatibility. They prove that truthful efficient core selection can fail, while their Shapley and minimal-cut mechanisms pursue DSIC and other axioms. Their minimal-cut mechanism may fail the core, explicitly leaving scope for collusion. See the [original arXiv paper, introduction and results](https://arxiv.org/html/2502.08248): §§1.1, 2.2, Proposition 1, Theorem 1, and the statement that the MC allocation may not be in the core in §4.2.

A valid specialization exists: a weighted multi-glove game is the max-flow game on serial layers of parallel edges. Also, factor-one nonnegative coalition coverage plus total payment at most flow value is exactly an efficient core allocation. Consequently Huang et al.’s impossibility is prior art for the exact-\(B=1\) endpoint.

It does **not** imply the hierarchy theorem because Huang et al. do not impose coalition coverage on their truthful non-core mechanisms and do not derive any subsidy-factor lower bound, much less one depending on the number of layers. Conversely, the hierarchy theorem does not subsume their SP, MP, SIR, or other-owner CM results.

The phrase “quantitatively strengthens the incompatibility” in [SOURCE_COMPARISONS.txt](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261006-005425-1c44e7dc/workspace/research_campaigns/2026-10-06-unrestricted-attack/SOURCE_COMPARISONS.txt:20) should be softened to “studies a subsidized coalition-covering relaxation and, if correct, obtains a divergent bound on serial-layer instances.” “Strengthens” suggests a formal theorem implication not fully established across the two models.

**Immorlica–Mahdian–Mirrokni.** Definition 3.3 defines an \(\alpha\)-budget-balanced profit-sharing scheme, approximate-core coverage, and cross-monotonicity
\[
\xi(i,S)\le \xi(i,S\cup T)
\]
for an unchanged \(i\). Theorem 3.6 proves no \(o(n)\)-budget-balanced cross-monotonic profit-sharing scheme for maximum flow. See the [original free PDF, Definition 3.3 and Theorem 3.6, pp. 10–12](https://immorlica.com/pubs/costshare.pdf).

Their proof reduces a large serviced set to two-edge coalitions while carrying the payoffs of the already-present edges. That step specifically requires other-owner population monotonicity. It cannot be obtained from the hierarchy model’s own-report condition.

A tempting zero-capacity encoding does not repair the reduction: changing an absent edge from capacity zero to positive controls that edge’s own payoff, whereas Theorem 3.6 needs inequalities for all the unchanged edges. Therefore Theorem 3.6 neither implies nor subsumes the proposed hierarchy theorem. It is established prior art for the broader coverage/budget/cross-profile tradeoff and for a stronger population-comparison model.

**Moretti–Norde (2021).** Definition 3.1 is exactly the weighted multi-glove characteristic function; Theorem 3.2 proves total balancedness by paying one minimum pool. Their PMAS definition compares participating coalitions and requires efficiency in every subgame. See the [open original PDF, Definition 3.1 and Theorem 3.2](https://d-nb.info/1240670206/34), especially pp. 2–3. Their PMAS characterization does not concern private capacity reports or subsidized report-linked allocations.

**Important omitted comparator: Brânzei–Solymosi–Tijs (2007).** “Type monotonic allocation schemes for multi-glove games” is directly terminologically relevant and should be added to the ledger. Its Definition 1 varies the number of unit owners of a type and compares remaining players’ payoffs; Theorem 2 gives the associated entrant/exit monotonicity. The allocation is efficient and symmetric within types. See the [free original working-paper PDF](https://citeseerx.ist.psu.edu/document?doi=2e056aa4146f806776867b89fed9e5d68336d641&repid=rep1&type=pdf), Definition 1 and Theorems 2 and 5.

It does not subsume the proposed theorem: it changes population counts in unweighted multi-glove games and controls remaining owners, rather than holding ownership fixed and increasing the changing owner’s capacity. Nevertheless, it is close enough in both model and “hierarchical/type monotonic” language that omission is a concrete citation defect.

**Fixed-game cost of stability.** This literature studies subsidies needed to make one fixed characteristic-function game stable. Here each fixed weighted multi-glove game is already balanced; excess payment arises from linking allocations across capacity reports. The distinction in the supplied ledger is correct. The relevant original open record is [Bachrach et al., arXiv:0907.4385](https://arxiv.org/abs/0907.4385).

### Manuscript defects requiring revision

- [manuscript.tex:24](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261006-005425-1c44e7dc/workspace/paper5/truthful_cooperation/manuscript.tex:24), lines 40–42, 62–67, 77–84, and 547–566 still say unrestricted divergence is unresolved and that the unrestricted lower bound is only two. If the hierarchy proof is promoted, all these statements become false.
- [manuscript.tex:106](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261006-005425-1c44e7dc/workspace/paper5/truthful_cooperation/manuscript.tex:106) already calls a “quantitative unrestricted lower family” a proposed contribution, but the current theorem section only proves factor two. The hierarchy theorem must be stated explicitly rather than inferred from campaign notes.
- The literature discussion at lines 93–121 should add Brânzei–Solymosi–Tijs and explicitly distinguish their type/population monotonicity from same-owner capacity monotonicity.
- Huang et al.’s “CM” is other-owner capacity monotonicity under an additional max-flow-increase condition; it should not be described in a way that could be confused with the manuscript’s own-report condition.

### Priority conclusion

Established prior art includes:

- the exact weighted multi-glove game and its total balancedness;
- efficient core-selection failure under private max-flow capacities;
- cross-monotonic approximate profit-sharing and a linear maximum-flow obstruction;
- PMAS/type-monotonic allocation schemes for multi-glove games;
- fixed-game stabilization by subsidy.

What remains priority-unconfirmed is the specific unrestricted theorem for fixed owners and varying capacities:

> nonnegative coalition-covering payments, monotone only in each owner’s own capacity report, have worst-case total factor  
> \[
> \Theta(\log k/\log\log k)
> \]
> when both the number of pools and owners grow.

No searched source directly supplied this statement or a valid reduction to it. That is not confirmation of novelty.

Limitations: this was a bounded free-only search; no subscription indexes, citation databases requiring login, purchased articles, or human contacts were used. The Tilburg repository copy of Brânzei–Solymosi–Tijs returned HTTP 403, so the freely indexed author/working-paper copy was used. Search coverage cannot exclude differently named resource-monotonicity or cooperative-production results.