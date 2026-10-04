## Result

I located no primary-source theorem matching the full target combination:

- one capacity owner per arc;
- arbitrary real, nonnegative capacity reports;
- underreporting only and zero capacity-use costs;
- own-capacity monotone payments;
- exact coalition covering \(y(S)\ge v_c(S)\);
- bounded augmentation \(\sum_i y_i\le(1+\beta)T(c)\); and
- original-core ideal floors \(y_i\ge H_i(c)/3\).

This is a bounded-search result, not a novelty claim. In particular, the full-domain two-stage pooling problem remains unresolved by the sources inspected.

## Source ledger

### 1. Huang–Mei–Yang–Cao, *Mechanism Design in Max-Flows*

Primary source: [arXiv v1 HTML](https://arxiv.org/html/2502.08248v1), [PDF](https://arxiv.org/pdf/2502.08248v1).

Inspected: Sections 2.1–2.2, Examples 1–4, Proposition 1, Definition 2 and Theorem 1 concerning the MC mechanism, and the Appendix core examples.

Exact model, pp. 4–6:

- Acyclic directed graph, one player per edge, and coalition value equal to the maximum flow using that coalition’s edges.
- Capacities are private; only \(\hat c_i\le c_i\) is permitted.
- There is no cost from using an edge.
- A mechanism is required to be exactly efficient:
  \[
  \sum_i\phi_i(\hat c)=\hat v(N).
  \]
- DSIC is defined by
  \[
  \phi_i(c_i,\hat c_{-i})\ge \phi_i(\hat c_i,\hat c_{-i})
  \quad\text{for every }\hat c_i\le c_i.
  \]
  Thus, in this no-cost/underreport-only model, DSIC is precisely own-report monotonicity.

Closest obstruction, Example 1, p. 6:

- The graph is exactly the \(2\times2\) two-stage pool: two parallel \(s\to A\) arcs followed by two parallel \(A\to t\) arcs.
- At \((1,1,1,1)\), every core selection gives some player a positive payment.
- At \((2,1,1,1)\), the core is uniquely \((0,0,1,1)\), up to the indicated labeling.
- The raised-capacity source player can therefore gain by reporting 1 rather than 2.
- The conclusion is that no efficient core-selection mechanism is even NEIC, hence none is DSIC.

This verifies the qualitative antecedent of the supplied calibration, but Huang et al. do not introduce subsidies or derive a quantitative budget-augmentation bound.

Other mechanisms:

- Proposition 1, p. 7: the Shapley-value mechanism is efficient, DSIC, and SIR. It does not promise coalition covering or an ideal-payoff floor.
- Definition 2 and Theorem 1, pp. 12–13: the minimal-cut (“MC”) mechanism is efficient and satisfies DSIC, SIR, split-proofness, merge-proofness, and cross-monotonicity.
- The authors explicitly state on p. 14 that MC allocations may fail to be in the core and coalitions may have incentives to collude.

Target comparison:

| Criterion | Huang core selection | Shapley / MC |
|---|---|---|
| Ownership | One edge per player | One edge per player |
| Reports | Underreports only | Underreports only |
| No use costs | Yes | Yes |
| Budget | Exactly \(T(c)\); no subsidy | Exactly \(T(c)\); no subsidy |
| Own monotonicity | Impossible generally | Yes |
| Coalition covering | Yes for core selection | Not guaranteed |
| \(H_i/3\) floor | Not studied | Not studied |

A scope mismatch remains at zero capacities: Section 2.1 initially writes \(c\in\mathbb R_{++}^E\), although its deviation intervals and later examples allow zero. The target’s all-zero and zero-flow boundary conditions therefore are not cleanly covered by the stated model.

### 2. Bachrach et al., *The Cost of Stability in Network Flow Games*

Primary source: [freely available Microsoft Research PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/01/CoS-NFG-MFCS.pdf).

Exact definitions, pp. 3–4:

- A stable payment satisfies \(p(C)\ge v(C)\) for every coalition.
- A subsidy \(\Delta\) increases only the grand coalition’s available payoff.
- A super-imputation is nonnegative and totals \(v(N)+\Delta\).
- Their “CoS” notation is the minimum total adjusted payment, not consistently the additive subsidy alone:
  \[
  \operatorname{CoS}(G)=\min_\Delta\{v(N)+\Delta:\operatorname{core}(G(\Delta))\ne\varnothing\}.
  \]

Quantitative results:

- Theorem 5, pp. 6–7: for a threshold network-flow game with threshold \(k\) and underlying max-flow \(F\),
  \[
  \operatorname{CoS}(G)\le F/k.
  \]
  The payment assigns \(c(e)/k\) to min-cut edges and zero elsewhere.
- Theorem 6, p. 7: this is exact for equal edge capacities and threshold \(rb\):
  \[
  \operatorname{CoS}(G)=F/(rb).
  \]

These are quantitative subsidy/stability theorems, but not matches:

- The game is a binary threshold game, \(v(C)\in\{0,1\}\), rather than the cardinal game \(v_c(C)=\) max flow.
- Capacities are fixed public data, not strategic reports.
- There is no truthfulness or own-capacity monotonicity across profiles.
- No fairness floor is imposed.
- Consequently, Theorems 5–6 cannot supply a \(\beta\) for the target two-stage pooling problem.

### 3. Gangam–Garg–Shahkar–Vazirani, *Equitable Core Imputations for Max-Flow, MST and \(b\)-Matching Games*

Primary source: [arXiv PDF, v3](https://arxiv.org/pdf/2403.06037).

Inspected: pp. 1–7 and max-flow definitions/fairness motivation.

Relevant definitions:

- Definition 3.2, pp. 4–5: an imputation is nonnegative and exactly distributes \(v(N)\).
- Definition 3.3, p. 5: a profit-game core allocation gives every coalition at least its value.
- Definitions 3.4–3.5, p. 5: fairness is leximin or leximax over a selected set of imputations.
- Section 3.1.1, pp. 5–6: one edge agent per arc and the ordinary cardinal max-flow characteristic function.
- Their tractable fairness results are chiefly for the Owen-set subset of the core; they stress that the Owen set can be strictly smaller than the whole core.

Target comparison:

- Ownership and coalition values match.
- Capacities are public and fixed; there is no reporting model or truthfulness.
- Budget is exactly \(T(c)\), with no augmentation.
- Their benchmark is leximin/leximax within the core or Owen set, not the coordinatewise whole-core ideals \(H_i=\max_{x\in C}x_i\).
- No simultaneous floors \(y_i\ge H_i/3\) are established.

Thus this source should not be used to replace the target’s original-core ideal benchmark by an Owen-set benchmark.

### 4. Goko et al., *Fair and Truthful Mechanism with Limited Subsidy*

Primary source: [arXiv original](https://arxiv.org/abs/2105.01801).

This supplies genuine truthfulness-plus-subsidy theorems, including at most one unit of subsidy per agent for matroidal valuations, but the model is allocation of indivisible goods with quasi-linear private valuations and envy-freeness. It has no edge ownership, capacity underreporting, max-flow coalition value, core covering, or \(H_i\) benchmark. It is therefore an analogy only, not a candidate theorem for the target.

## Two-stage pooling and core ideals

For two source-side sets \(L\) and sink-side sets \(R\), direct max-flow evaluation gives
\[
v_c(S)=\min\!\left\{\sum_{i\in S\cap L}c_i,\,
                       \sum_{j\in S\cap R}c_j\right\}.
\]
Huang’s Example 1 is the \(2\times2\) instance of this formula.

The searched originals did not furnish:

- an all-capacity-domain coalition-covering payment formula monotone in each owner’s capacity;
- a finite multiplicative augmentation bound for such a formula; or
- a theorem preserving a fixed fraction of every coordinatewise original-core ideal.

The \(1/8\) five-profile lower bound in the supplied lemma is consequently a new derivation relative to these cited statements, but its broader novelty is unverified.

## Supplied-evidence defects and verification needs

- [CALIBRATION_LEMMA.txt:54](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261004-102931-1b0aef52/workspace/research_campaigns/2026-10-04-priority-applications/CALIBRATION_LEMMA.txt:54>) says `verify_calibration.py` checks the enumeration, but that file is absent from the isolated workspace. The analytic proof is independently readable, but the stated computational verification cannot be reproduced here. Suggested verification: supply the script and check its exact profile set, all \(5(2^4-1)=75\) coalition inequalities, 20 floors, and four own-report comparisons.

- [CONTRACT.txt:7](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261004-102931-1b0aef52/workspace/research_campaigns/2026-10-04-truthful-subsidy/CONTRACT.txt:7>) includes zero capacities and [CONTRACT.txt:12](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261004-102931-1b0aef52/workspace/research_campaigns/2026-10-04-truthful-subsidy/CONTRACT.txt:12>) imposes \(y=0\) at zero flow. Huang’s formal domain begins with strictly positive capacities. Suggested verification: prove the proposed rule or obstruction separately on boundary profiles rather than citing Huang for that extension.

- [CALIBRATION_LEMMA.txt:29](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261004-102931-1b0aef52/workspace/research_campaigns/2026-10-04-priority-applications/CALIBRATION_LEMMA.txt:29>) should cite “Example 1, p. 6” rather than only a general HTML link. The cited original supports the qualitative core-selection obstruction, not the three-coalition \(1/8\) inequality.

No files were modified.