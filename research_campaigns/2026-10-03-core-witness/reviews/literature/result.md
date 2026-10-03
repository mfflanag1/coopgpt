## Bounded priority check: sharp 1/3 candidate (first pass, free sources only)

**Result.** In the free full texts I opened, I found no theorem stating or implying the candidate (s/T < 1/3, supremum 1/3, or the 2(k−1)/(3(2k−1)) bound). This is not a novelty finding. The source most likely to matter, Quint (1991), is paywalled and uninspected, and a free source I did read says its model is the candidate's.

### Claim-specific table (inspected full texts)

| Source (free URL) | Exact location read | Model there vs. frozen model | Bearing on candidate |
|---|---|---|---|
| Martínez-de-Albéniz, Rafels, Ybern, DAM 379 (2026) 605–612. [UPC bitstream](https://upcommons.upc.edu/server/api/core/bitstreams/fcec9d22-f4b5-4826-a5d4-d7e585b218cb/content), full text read (resolves the ledger's failed retrieval) | §2 pp. 606–607 (model; conditions (1), (4)); Thm 3.1 p. 608; Thm 3.2 p. 609; Remark 3.2 and Example 3.3 p. 610 | m-sided, n-square, general nonnegative array, only full m-tuples productive. Requires supermodularity (1) and local monotonicity (4). Not pair-additive; the candidate assumes neither condition. | Thm 3.2 gives closed formulas for each agent's max and min core payoff, with all maxima of one side attained at one core point. No subsidy, no floors, no ratio. Overlap is the ingredient "coordinate core maxima", on the subclass where both models' hypotheses hold. Example 3.3 shows the formula fails without (4). Does not imply the candidate. |
| Atay, Núñez, Ann. Oper. Res. 279 (2019) 271–290. [Author PDF](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_ANOR.pdf), full text read | §2 pp. 274–276, eqs. (1)–(2); Prop. 1 p. 277; Thm 1 p. 279; Cor. 1 p. 283; Prop. 2 p. 284; §6 p. 286; Example 5 pp. 288–289 | Pair-additive on an m-partite graph, nonnegative weights, integral matching. But sub-tuples (pairs) are productive and sector sizes are arbitrary. For m=3 with a complete quotient graph, the value formula for triples matches; the coalition set does not. | Prop. 1: sufficient condition for a nonempty core. Thm 1: cycle-free quotient graph gives a core equal to the composition of bilateral cores. Prop. 2: sector-optimal core points exist in the cycle-free case, with maximum equal to marginal contribution. Example 5: on the complete 3-partite graph, sector maxima need not be jointly attainable. No subsidy or 1/3-type bound. Does not imply the candidate. |
| Same paper, as a pointer | p. 273 and §6 p. 286 | Says Quint (1991) attaches a value to each pair, sets an m-tuple's worth to the sum of its pairs, and gives smaller coalitions zero worth. Says Stuart (1997) is the chain-additive, full-tuples-only version. | Evidence that the frozen model is Quint's, by Atay–Núñez's description. Second-hand only; raises the priority weight of the uninspected Quint original. |
| Meir, Rosenschein, Malizia, "Subsidies, Stability, and Restricted Cooperation". [Author PDF](https://www.cs.huji.ac.il/~jeff/papers/coopmas11meir.pdf), full text read (13 pp.) | §2.2 p. 4 (CoS(G), CoS(x,G), extended core); Thm 2 and Prop. 1 p. 6; Thm 3 p. 9; Thm 4 pp. 9–10 | General superadditive TU games with a subsidy to the grand coalition. Restrictions: coalition size ≤ k, partition, communication graph. | CoS(x,G) (minimum subsidy to extend a given payoff vector to a stable one) is the nearest framework antecedent for "protect a floor vector by grand-coalition subsidy". Bounds are RCoS ≤ √n and RCoS ≤ min{k, √n}. My inference: these do not give 1/3, and plain CoS is 0 in the candidate's class because the core is nonempty. No core-maximum floors, no assignment structure. |
| Vazirani, "Fair Core Imputations for the Assignment Game". [arXiv 2402.11437](https://arxiv.org/pdf/2402.11437), pp. 1–5 read; theorem sections not read | Abstract; §1–2 pp. 1–5 | Two-sided assignment game. Leximin, leximax and min-spread imputations chosen inside the core; no subsidy. | Partial inspection only. The pages read show a two-sided, in-core selection problem; the later theorems are uncompared. |

### Abstract-only, failed retrieval, or search-only (not cleared)

- **Quint, "The core of an m-sided assignment game", GEB 3 (1991) 487–503.** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/0899825691900179) returned HTTP 403; [IDEAS](https://ideas.repec.org/a/eee/gamebe/v3y1991i4p487-503.html) has no abstract or free link; the [author's publications page](https://www.thomasquintmath.com/publications) has no PDFs. Uninspected and the highest-priority gap.
- **Stuart (1997), Math. Soc. Sci. 34, 21–27** and **Lucas (1995)**: no free original found. Known only through Atay–Núñez's description.
- **Marchi and Oviedo, "The core of a further m-sided assignment game", EJOR 98 (1997) 617–625.** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0377221796001762) returned 403; [IDEAS](https://ideas.repec.org/a/eee/ejores/v98y1997i3p617-625.html) has no abstract. Model unknown; new lead.
- **Priority coalitional games and claims problems (2024).** The [VU PDF](https://research.vu.nl/files/383916636/Priority_coalitional_games_and_claims_problems.pdf) returned 403 and the [UVigo accepted manuscript](https://www.investigo.biblioteca.uvigo.es/xmlui/bitstream/11093/11185/4/2024_coalitional_games.pdf) failed with a TLS certificate error. Nothing new was inspected in this pass; the earlier accepted-manuscript comparison in the supplied audit stands unrefreshed.
- **Bachrach et al., Cost of Stability.** Only the [arXiv abstract page](https://arxiv.org/abs/0907.4385) was read. Its √n bound is seen only as restated in Meir et al., Thm 2.
- **Vazirani, "The General Graph Matching Game: Approximate Core".** [arXiv abstract](https://arxiv.org/abs/2101.07390) only: 2/3-approximate core for non-bipartite graph matching, via multiplicative relaxation of coalition demands; no hypergraph extension is mentioned there. Full text uncompared.
- **Pourpouneh, Ramezanian, Sen, Taori, "Stable Matching with Payoff Guarantees".** [arXiv 2608.03230](https://arxiv.org/abs/2608.03230), abstract only: two-sided assignment game with minimum payoff guarantees taken from the interval between side-optimal payoffs. Conceptually adjacent (floors from core extremes); full text uncompared.
- **"Half-optimal core".** No paper or theorem under this name surfaced in three searches, which returned only half-integral matching material. The intended antecedent is unidentified.
- **Search-only, not opened:** Atay's thesis ([UB repository](https://diposit.ub.edu/dspace/bitstream/2445/109606/1/ATAY_PhD_THESIS.pdf)); Atay, Llerena, Núñez (2016) on generalized three-sided markets; Tejada (2013); Sherstyuk (1999); [Xiao et al., arXiv 2107.01442](https://arxiv.org/pdf/2107.01442).

### Unresolved gaps

1. Quint (1991) is unread. Atay–Núñez indicate its model is the frozen one, so any result there on core bounds or coordinate extrema would bear directly on the candidate.
2. Stuart, Lucas and Marchi–Oviedo originals are unread.
3. The Version of Record for the priority-games paper and the Bachrach et al. full text were not compared in this pass.
4. Hypergraph or k-set-packing approximate-core results (Faigle–Kern-type bounds, 3-dimensional matching games) were not searched in depth. A general rank-3 theorem could imply a bound in a related but not identical quantity.
5. Two guessed arXiv IDs resolved to unrelated papers and yielded nothing.

### Limitations

About seven search queries and four complete full-text reads, plus one partial read. PDFs were read as page images, so page and theorem numbers are as printed. No proof of the candidate was checked. The absence of an antecedent in these sources supports only "not found in the inspected sources".

Sources: the URLs linked above.
