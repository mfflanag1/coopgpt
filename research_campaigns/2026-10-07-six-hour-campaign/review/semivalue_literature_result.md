Completed a bounded, read-only investigation. No files were changed, no purchases or outreach occurred, and no cross-model tools were used.

## Closest classical primary source

Robert James Weber, “Probabilistic values for games,” chapter 7 in Alvin E. Roth (ed.), *The Shapley Value: Essays in Honor of Lloyd S. Shapley*, Cambridge University Press, 1988, pp. 101–119. [Free scanned volume](https://www.library.fa.ru/files/roth2.pdf).

Inspected scope:

- Printed p. 103, §2: defines a probabilistic value for player \(i\) as
  \[
  \phi_i(v)=\sum_{T\subseteq N\setminus\{i\}}p_T^i[v(T\cup\{i\})-v(T)],
  \]
  where the \(p_T^i\) form a probability distribution. Weber interprets this explicitly as expected marginal contribution.
- Printed p. 103: identifies the Banzhaf and Shapley values as special cases.
- Printed p. 106, §4, Proposition and Theorems 4–5: nonnegative marginal weights follow from monotonicity; on the general or monotonic game domains, linearity, dummy, and monotonicity characterize probabilistic values.
- Printed p. 114, §7, Theorem 12: a common distribution over player orderings yields an efficient random-order value, and each component is a probabilistic value.

This is a substantive original passage, not merely metadata.

Pradeep Dubey, Abraham Neyman, and Robert James Weber, “Value Theory Without Efficiency,” *Mathematics of Operations Research* 6(1), 1981, pp. 122–128, DOI 10.1287/moor.6.1.122. [Publisher record](https://doi.org/10.1287/moor.6.1.122); a purported free Cowles copy was indexed at `https://cowles.yale.edu/sites/default/files/files/pub/d05/d0513.pdf`.

Inspected scope:

- Publisher abstract and bibliographic record only: a semivalue is described as a symmetric positive linear operator fixing additive games, satisfying the Shapley axioms except possibly efficiency; the finite-player class is completely characterized.
- The alleged Cowles PDF redirected to an unrelated Yale search page, so I did not treat the full article or its Theorem 1 as inspected.
- Secondary sources report Theorem 1’s probability-measure/multilinear-extension characterization, but that was not used as primary-source evidence.

## Attribution comparison

The proposed marginal term
\[
m_i^q=\mathbb E_{B_{-i}}\!\left[v(B_{-i}\cup\{i\})-v(B_{-i})\right]
\]
is exactly a Weber probabilistic value with every other owner independently included with probability \(1-q\). Because the weights depend only on coalition size, it is also the familiar fixed-\(q\) binomial semivalue.

The complete rule is not itself a classical semivalue or random-order value:

- Its marginal component is multiplied by \(1-q\) and integrated only over \(q\in(0,1/j)\). The resulting marginal measure has mass
  \[
  j\int_0^{1/j}(1-q)\,dq=1-\frac1{2j},
  \]
  so that component alone lacks the normalization that fixes additive games.
- The additional \(q\,p_i^q\) term depends on a selected minimizing linear form and capped dual contribution, rather than only on the characteristic function’s marginal contributions.
- Weber’s random-order values are efficient by Theorem 12. The proposed rule deliberately permits subsidy and proves an upper budget factor depending on \(K\).
- Classical probabilistic values do not, merely by definition, cover every coalition. Positivity on monotone games is only individual nonnegativity, not the core-type inequalities \(\sum_{i\in S}M_i\ge v(S)\).
- Neither Weber nor the inspected Dubey–Neyman–Weber metadata introduces a representation-complexity parameter comparable to the number \(K\) of fixed min-linear forms.

For fixed-owner componentwise underreports, the classical marginal part has the same elementary monotonicity mechanism as the proposal: the “off” coalition value is independent of owner \(i\)’s bundle, while the “on” value is componentwise nondecreasing. This supports report monotonicity of \(m_i^q\). It does not explain the conditional-dual term, coalition coverage, subsidy bound, or \(K\)-dependence.

## Capacity withholding and production-game comparators

Shengyuan Huang, Wenjun Mei, Xiaoguang Yang, and Zhigang Cao, “Mechanism Design in Max-Flows,” arXiv:2502.08248v1, 12 February 2025. [Free original v1](https://arxiv.org/html/2502.08248v1).

Precisely inspected:

- §2.1, especially the mechanism model and DSIC definition: owners may report only \(\hat c_i\le c_i\), and DSIC quantifies over arbitrary other reports. This is report DSIC, not a routing equilibrium.
- Example 1 and Remark 2: efficient core/nucleolus selections can reward capacity underreporting.
- §3, Proposition 1: the Shapley marginal-value mechanism is DSIC and strongly individually rational in their one-edge-per-owner max-flow model.
- §4, Theorem 1 as identified in the paper’s table of contents/main-results discussion: their minimal-cut mechanism satisfies DSIC and the other listed properties.
- Their mechanisms are efficient, so they do not supply subsidized coalition coverage beyond total reported production. Their model also does not establish simultaneous componentwise truthfulness for an owner holding an arbitrary bundle of resource types.
- No \(K\)-dependent subsidy result is present. Minimal cuts are used structurally, but not as the proposed min-form budget parameter.

Andries van Beek, Benjamin Malmberg, Peter Borm, Marieke Quant, and Jop Schouten, “Competition and cooperation in linear production and sequencing processes,” *Games and Economic Behavior* 139 (2023), 117–132, DOI 10.1016/j.geb.2023.02.001. [Publisher record](https://doi.org/10.1016/j.geb.2023.02.001); [free author thesis version, chapter 4](https://pure.uvt.nl/ws/portalfiles/portal/79217716/Thesis_Andries_van_Beek.pdf).

Inspected scope:

- Free thesis chapter 4 introduction and the publisher-exposed model/result summary.
- Firms strategically select resource locations; resulting resource bundles feed a second-stage cooperative LP game.
- The reported result is pure-Nash existence in a two-location “standard case,” including allocation through the Owen set.
- This is strategic acquisition/routing of bundles, not withholding or downward misreporting of a fixed owner’s endowed capacity. It must not be described as DSIC evidence.

I did not find a closer free original on withholding in a general linear-production game during the bounded search. Huang et al.’s max-flow production setting remains the closest inspected direct withholding/report-incentive source.

## Concrete defects in the supplied comparison

- [MECHANISM_SOURCE_COMPARISON.txt:12](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-040918-741a8830/workspace/research_campaigns/2026-10-07-six-hour-campaign/MECHANISM_SOURCE_COMPARISON.txt:12) describes “effective-usage/optimal-face invariance” as part of the proposed contribution. The supplied current theorem expressly says its owner-bundle proof uses no effective capacities or special ownership pattern, and raw selection is central. Verify whether the comparison describes an obsolete theorem version.
- The same lines characterize \(K\) only through minimal cuts or binary-packing dual vertices. In [GENERAL_PRODUCTION_THEOREM.txt:7](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-040918-741a8830/workspace/research_campaigns/2026-10-07-six-hour-campaign/GENERAL_PRODUCTION_THEOREM.txt:7), \(K\) is the cardinality of any fixed finite family of nonnegative min-linear forms. The comparison should state the general definition first and applications second.
- [MECHANISM_SOURCE_COMPARISON.txt:105](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-040918-741a8830/workspace/research_campaigns/2026-10-07-six-hour-campaign/MECHANISM_SOURCE_COMPARISON.txt:105) lists semivalues only as future work. Weber’s §2 and Theorems 4 and 12 should be added because they give the direct attribution for the \(m_i^q\) component.
- [MECHANISM_SOURCE_COMPARISON.txt:93](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261007-040918-741a8830/workspace/research_campaigns/2026-10-07-six-hour-campaign/MECHANISM_SOURCE_COMPARISON.txt:93) should give the authors’ full names and distinguish the freely inspected thesis chapter from publisher metadata.
- Minor: line 2 says `7 October2026`.

## Bounded search log and limitations

Queries included:

- `Dubey Neyman Weber Value theory without efficiency PDF semivalue 1981`
- `Weber Probabilistic values for games PDF 1988`
- `"Probabilistic values for games" "Theorem 1" Weber`
- `site:library.fa.ru/files/roth2.pdf "probabilistic value"`
- `linear production game resource withholding incentive original paper PDF`
- `"linear production" "withhold" resources game allocation`
- `"Competition and cooperation in linear production and sequencing processes" pdf`
- `"linear production games" "strategic" resources allocation Owen set PDF`

Unsuccessful originals:

- The Cowles URL for Dubey–Neyman–Weber redirected rather than serving the paper.
- The INFORMS PDF endpoint exposed only the abstract without access.
- Owen’s 1975 original was not reliably obtained: a ResearchGate result labeled as Owen’s paper returned unrelated uploaded text.
- The publisher copy of van Beek et al. did not expose the complete article; inspection used the free thesis version plus publisher metadata.

No broad novelty conclusion follows from this search. The unresolved question is whether an older production/LP-game paper combines fixed endowed-resource withholding, dominant-strategy report monotonicity, and core or subsidized coalition coverage; none was verified within the bounded search.