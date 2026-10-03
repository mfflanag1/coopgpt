# Claim-specific free-source comparison

3 October 2026. **Historical novelty is unconfirmed.** The checked claim is the sharp supremum S3=1/3 for the frozen strict three-sector pair-additive model, strict inequality in every finite market, and the sharp integral-P correction. No direct antecedent was identified in the specifically inspected material below; this is not an exhaustive implication or priority audit.

## Established ingredients and closest sources

| Source | Original passages inspected | Relation to the claim |
|---|---|---|
| Núñez–Rafels, *Bargained stable allocations in assignment markets*, [free WP153](https://www.bse.eu/sites/default/files/working_paper_pdfs/153.pdf), dated 28 December 2004 | Coordinator reopened original; bilateral model §3, Definition 6 and surrounding argument, PDF pp.19–20; prior §6 extension read retained in SOURCE_STATUS | Defines and proves nonemptiness of the half-optimal core: every agent receives at least half their own maximum core payoff. The fairness question and coordinate-maximum criterion are established. These inspected statements concern two-sided markets and in-core selection, and do not state this three-sided subsidy bound. |
| Meir–Rosenschein–Malizia, *Subsidies, Stability, and Restricted Cooperation*, [author original](https://www.cs.huji.ac.il/~jeff/papers/coopmas11meir.pdf) | Native QA reopened §2/2.2, pp.3–4, Theorem 2 and Proposition 1 statements; Fable reported full read | Payoff-vector cost of stability is a close framework antecedent: protect a given efficient preimputation using subsidy. Its input vector totals T; H/3 can total less. Relative-cost convention also differs. The definitions and general bounds inspected do not give the proposed sharp constant. |
| Atay–Núñez, *Multi-sided assignment games on m-partite graphs*, [author original](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_ANOR.pdf) | Native QA reopened printed p.273, §2 pp.274–275, Proposition 2 p.284 and Example 5 pp.288–289; Fable reported full read | Their own graph model permits productive sub-tuples. Tree-side extrema and failure of joint same-side maxima in a cyclic nonempty-core example are antecedents. Their p.273 description identifies a pair-additive full-tuples-only model in Quint1991, increasing the relevance of that unread original. It does not replace a comparison against Quint itself. |
| Martínez-de-Albéniz–Rafels–Ybern, *Maximum and minimum core payoffs for supermodular multisided assignment markets with local monotonicity*, DAM379(2026)605–612, [institutional original](https://upcommons.upc.edu/server/api/core/bitstreams/fcec9d22-f4b5-4826-a5d4-d7e585b218cb/content) | Coordinator read retained original §2 pp.606–607, conditions(1),(4), Theorems3.1–3.2 pp.608–609 and proof; Fable independently retrieved it | Core extrema formulas and simultaneous same-side maxima require supermodularity and local monotonicity of the full array. The frozen theorem assumes neither. Their theorem is a prior result on a restricted class, not the unrestricted subsidy constant. The PDF had already been recovered in September; October web-cache failures were not historical absence of access. |
| Pourpouneh–Ramezanian–Sen–Taori, *Stable Matching with Payoff Guarantees*, [arXiv2608.03230v1](https://arxiv.org/html/2608.03230v1), submitted4August2026 | Coordinator read §§2–3 definitions, Theorem1 in §5 and Theorem2 in §7; not the complete appendix proof | Two-sided matching under unobserved assignments/payoffs. The guarantees are endogenous to iterative definite blocking; the main theorems identify efficient assignments and intervals between side-optimal wages. These results are not the frozen fractional-maximum subsidy objective. This is a scoped theorem comparison, not full-paper clearance. |
| *Priority coalitional games and claims problems*, [free accepted manuscript](https://www.investigo.biblioteca.uvigo.es/xmlui/bitstream/11093/11185/4/2024_coalitional_games.pdf) | Earlier retained `PRIORITY_ORIGINAL_COMPARISON.md`: Definitions2–4 and Lemmas2,8, PDFpp.7,10–11; no fresh successful full retrieval here | Priority/floor transformations are established. Preserve that accepted-manuscript comparison and its limits; a newly failed endpoint does not erase earlier evidence. Version-of-Record comparison remains incomplete. |

Shapley–Shubik's [assignment-core/dual theorem](https://www.math.utoronto.ca/mccann/assignments/477/ShapleyShubik72.pdf), Theorem2 printedp118, and Solymosi's [longest-path extrema formulas](https://unipub.lib.uni-corvinus.hu/9034/1/Sensitivity_of_fair_prices_in_assignment_market_ST_23.pdf), §4/Lemma1 printedp9, are established ingredients. These passages were read earlier in this campaign. Ordinary subsidy/LP ideas and longest-path techniques are not claimed as new.

## Exact comparison to payoff-vector cost of stability

This paragraph is our deduction, not a quoted theorem. In the frozen model, l=H/3 has sum l<=T by diagonal caps. For the efficient-preimputation definition in Meir et al.,

    s(l,G)=min_{x>=l, sum x=T} CoS(x,G).

Any stable y>=l with sum y>=T dominates some vector x between l and y with sum x=T; conversely any stable extension of such x covers l. Thus the framework predates this work even though the particular floor and sharp ratio require further structure. The source's relative cost is (T+s)/T, while ours is s/T.

## Unresolved originals and search limits

- Quint1991, Lucas1995 and Stuart1997 remain unread in their entirety under the no-purchase instruction. The same-model lead through Atay–Núñez makes Quint a particularly important unresolved comparison.
- Marchi–Oviedo1997, *The core of a further m-sided assignment game*: only the [publisher abstract](https://www.sciencedirect.com/science/article/pii/S0377221796001762) was inspected. An author-page PDF link leads instead to Oviedo2000 on repeated games. That incorrect download is not evidence about the requested original.
- Later sections of the Vazirani fair-core paper, general hypergraph/approximate-core implication routes, and the complete Cost-of-Stability original were not fully compared in this final pass. The Fable report labels these partial/search-only leads explicitly.
- The source task missed the known half-optimal-core link and required coordinator repair. Its approximately seven query report is not an exhaustive search. No absence-of-prior-work conclusion follows.

## Proposed contribution and wording

The proposed contribution is the six-comparison aggregation combined with weighted residual witness budgets, yielding a sharp constant and finite strictness for the frozen class. The lower chain is earlier project work, now combined with the matching upper theorem. Suggested claim: “We prove that the sharp worst-case subsidy ratio for one-third protection of original whole-core maxima in strict three-sector nonnegative pair-additive assignment markets is one third.” Add that priority is under review. Do not claim invention of the model, floor-protection question, cost-of-stability framework or coordinate extrema.

The complete research output and opposite-model QA are retained in `../reviews/literature/`. No purchases, outreach, submission or specialist endorsement occurred.
