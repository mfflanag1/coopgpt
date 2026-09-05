# Two-sided assignment comparison: bounded priority audit

Audit date: 2026-09-05. Scope: full ascending leximin `x`, full descending lexicographic minimum `z`, and arbitrary nonnegative weighted bipartite assignment games with entire core `C`, worth `T>0`. Write `M_i=max{y_i:y in C}`, `rho=||x-z||_1/T`; `k` is the number of positive edges in a fixed optimal matching. The phrase “leximax” below always means descending lexicographic **minimum**.

This is a claim-level assessment, not a certificate of priority. Earlier campaign files were read without modification. The documents listed below were examined at the indicated access level; bibliographic listings and publisher previews are not represented as inspected full papers.

## Verdict by claim

| Claim | Verdict on 2026-09-05 | Evidence and implication |
|---|---|---|
| Definitions and uniqueness of the two sorted egalitarian selectors | Established background | Klijn et al., 1999 working paper Section 3 and Theorem 3.1; Vazirani, Definition 11 and Lemma 3; Gangam et al., Definitions 3.4–3.5 and Claim 4.1. |
| Bipartite leximin `x_i >= M_i/2` | **Short unstated corollary of inspected prior algorithm** | The complete derivation from Vazirani v6 appears below. The campaign supplies an independent elementary proof, but should not claim a wholly new fairness guarantee without this attribution. |
| Sharpness of the factor `1/2` | Elementary established calibration | One positive edge has leximin `(w/2,w/2)` and coordinate core maximum `w`. This does not support substantive novelty. |
| A core selector can simultaneously guarantee half of every coordinate core maximum | Established for another selector | The Thompson midpoint / assignment tau-value equals `(M_i+m_i)/2` coordinatewise. Thus half guarantees themselves long predate this campaign. |
| Exact finite `rho <= k/(k+1)` for leximin versus every minimax point, and attainment for `k>=2` | Explicit theorem not located; potentially new quantitative refinement | Requires a further extremal argument after the prior half guarantee. Inspected sources do not state this distance or an equivalent finite constant. This is stronger evidence than keyword absence, but does not establish priority against inaccessible or unexamined literature. |
| `rho <= 1` as the unrestricted bipartite supremum | Short consequence of the preceding finite theorem | Do not present it as an additional independent discovery. |
| Feasible matched-pair equal splits are Lorenz-best; selector agreement on exact assignment games | Established structure / immediate majorization consequence | Llerena's pairwise egalitarian/core results and prior dominant-diagonal literature cover the relevant equality mechanism. No novelty claim recommended. |
| New contribution is a two-sided/three-sided quantitative contrast | Plausible positioning, subject to separate three-sided audit | This lane establishes the conservative two-sided baseline only. |

## Half guarantee from Vazirani's algorithm

Primary source: [Vazirani, arXiv:2402.11437v6](https://arxiv.org/pdf/2402.11437v6), 20 November 2025; first arXiv submission 18 February 2024. Page numbers below are printed pages; PDF page numbers are one larger. Source anchors: Definition 19, pp.17–18; Algorithm 1, p.20; Remark 1, p.22; Lemma 5, p.25; Lemma 9, p.27; Theorem 8, pp.29–30. Algorithm page visually checked.

Our deduction: start from arbitrary core `y` and let `Omega_0` be its minimum essential-vertex payoff. A changing coordinate has speed at most one as the clock increases. For a coordinate permanently fixed at clock `t_i`, the freezing minimum gives `x_i >= t_i`; subsequent values do not change. Therefore

```
|x_i-y_i| <= t_i-Omega_0 <= x_i-Omega_0,
2x_i >= y_i+Omega_0 >= y_i.
```

Initially fixed coordinates are unchanged. Nonessential coordinates vanish. Correctness identifies the final point with full leximin, independently of the start. Maximizing `y_i` proves the half guarantee. This is an inference from the source, not a quoted theorem. Its stated algorithm domain is rational weights; the campaign's elementary proof covers real weights directly.

## Additional argument needed for the finite distance

This is the campaign's mathematical deduction, separated from literature summaries. Let `z` be any minimax core point, `M=max z`, and `q_a` the absolute change on either endpoint of matched pair `a`. Complementarity gives opposite changes and `||x-z||_1=2D`, where `D=sum q_a`. The half guarantee forces both endpoints of `x` to be at least `q_a`; the receiving endpoint of `z` is at least `2q_a`. Hence `D<=kM/2`.

At least one top coordinate of `z` has `x_j>=z_j=M`; otherwise a small convex move from `z` toward `x` decreases the maximum. The matched pair containing that witness has weight at least `M+2q_a`; all other matched pairs have weight at least `2q_a`. Thus `T>=2D+M`, which gives `2D/T<=k/(k+1)`. The identical-row matrix with rows `(1,...,1,2)` attains the bound for `k>=2`. The remaining extremal calculation is short; its finite sharpness is the better two-sided contribution claim.

## Older sources and exact scope

### Klijn et al.: prior selectors and alternating adjustments

[Institutional full working paper](https://pure.uvt.nl/ws/files/533861/110.pdf): F. Klijn, D. Vermeulen, H. Hamers, T. Solymosi, S. Tijs, J. Pere Villar, *Neighbour Games and the Leximax Solution*, CentER DP 1999-110. The downloaded file named `klijn_2003.pdf` is **this 1999 working paper**, with an institutional cover. [Journal record](https://research.tilburguniversity.edu/en/publications/neighbour-games-and-the-leximax-solution/): *Mathematical Methods of Operations Research* 58(2), 191–208 (2003).

Working-paper printed p.6 defines decreasing sort and its lexicographic minimum; Theorem 3.1, p.7, establishes uniqueness for balanced games. Definition 3.7, p.8, defines adjustment on a relevant alternating interval. Theorem 3.9, p.9, characterizes the neighbour-game selector by absence of adjustable players. Lemma 4.3, p.15, gives the cubic algorithm. These are path/neighbour markets, not arbitrary bipartite graphs. Their alternating-adjustment method is prior conceptual infrastructure, but does not itself give the arbitrary-game leximin half bound or the finite distance formula. The paper cites Arin–Iñarra (1997) and Moulin (1988) for earlier egalitarian foundations. Those originals were not retrieved.

### Llerena: pairwise equality and Lorenz order

[Publisher preview](https://www.sciencedirect.com/science/article/pii/S0167637711001362), DOI [10.1016/j.orl.2011.11.011](https://doi.org/10.1016/j.orl.2011.11.011): **Francesc Llerena**, *The pairwise egalitarian solution for the assignment game*, *Operations Research Letters* 40(2), 84–88 (2012). This is a single-author paper, not “Llerena et al.”

The indexed publisher introduction locates the pairwise-egalitarian/core result in Section 3, Theorem 3.1; it studies when the pairwise equal split belongs to the core and its relation to Dutta–Ray egalitarianism and Lorenz domination. Section 4, Theorem 4.1, concerns the stronger 2-dominant-diagonal condition and singleton kernel/nucleolus/Thompson-point agreement. The source explicitly warns pairwise equality need not lie in the core. These conditions cannot be silently substituted for arbitrary assignment games. Full text was unavailable (publisher 403; OpenAlex showed no open location), so exact theorem-page numbers and full hypotheses were not independently transcribed. Retain this limitation; do not invent verbatim theorem statements.

### Solymosi and the Thompson/tau citation chain

[Solymosi's full 2023 paper](https://unipub.lib.uni-corvinus.hu/9034/1/Sensitivity_of_fair_prices_in_assignment_market_ST_23.pdf), *Sensitivity of fair prices in assignment markets*, *Mathematical Social Sciences* 126, 1–12; online 13 September 2023, DOI [10.1016/j.mathsocsci.2023.09.003](https://doi.org/10.1016/j.mathsocsci.2023.09.003). Theorem 3, p.4, states simultaneous side extrema of the core. Section 5, p.9, gives the fair payoff as the average of side-optimal payoffs. Consequently its coordinate is `(M_i+m_i)/2 >= M_i/2`. The “half” in Theorem 4 concerns gains from valuation manipulation, a different claim.

Its references attribute fair prices to Thompson (1981), *Auctions and market games*, pp.181–196, and tau equality to Núñez–Rafels. The latter [primary publisher record](https://link.springer.com/article/10.1007/s001820300127) explicitly states the midpoint identity, and dates *The assignment game: the tau-value*, *IJGT* 31, 411–422, **June 2003** (received June 2002, revised January 2003); later literature often cites 2002. Full original unavailable; use the publisher date with an explanatory note if reconciling bibliography.

The midpoint need not equal leximin. For weights `[[6,2],[4,3]]`, Solymosi's displayed example has tau `(2.5,1.5;3.5,1.5)`, while the feasible paired equal split is `(3,1.5;3,1.5)`. This independently checked example blocks automatic transfer of properties merely by identifying the two selectors.

### Gangam et al. and Granot–Granot

[Gangam, Garg, Shahkar, Vazirani, arXiv:2403.06037v3](https://arxiv.org/pdf/2403.06037v3), *Equitable Core Imputations for Max-Flow, MST and b-Matching Games*, 11 February 2025 (first posted 9 March 2024). Definitions 3.4–3.5, p.6, fix both sorting conventions. Claim 4.1, p.8, and Lemma 4.2, p.10, provide uniqueness and iterative-LP computation. Section 5 separates entire-core optimization from the Owen subset. No inspected statement provides the assignment half or finite-distance guarantee.

Its related-work chain leads to [Daniel and Frieda Granot, *On Some Network Flow Games*](https://pubsonline.informs.org/doi/10.1287/moor.17.4.792), *Mathematics of Operations Research* 17(4), 792–841, 1 November 1992. The primary abstract already identifies ascending lexicographic maximization with the nucleolus for restricted assignment subclasses. Only abstract inspected; precise subclass theorem hypotheses remain an access gap. Do not claim egalitarian assignment selection began in 2024.

### Lorenz-maximal core sets

[Hougaard–Peleg–Thorlund-Petersen institutional record](https://ratio.huji.ac.il/publications/set-lorenz-maximal-imputations-core-balanced-game): *On the Set of Lorenz-Maximal Imputations in the Core of a Balanced Game*, 1999 working paper, *IJGT* 30 (2001), 147–165. The institutional abstract treats the set of Lorenz-maximal core imputations and welfare characterizations. Full-paper link failed during this audit; it is background evidence, not an inspected quantitative bound. Lorenz-maximality of a set does not by itself imply coincidence of both selected points.

## Audit of consolidated manuscript priority paragraph

Reviewed `/private/tmp/assignment-comparison-20260905/consolidated/pairs_and_triples.tex`, Section “Priority and interpretation,” as received on 2026-09-05. **No mathematical gap in the displayed algorithmic-corollary deduction was found.** The absolute-value estimate follows because the complete trajectory before permanent fixing is 1-Lipschitz in the clock, even when a coordinate revisits Active/Bin or changes direction. The explicit qualification “bipartite” is necessary and present.

Recommended precise additions: define `Omega_0` as the minimum initial essential-vertex payoff; note the published algorithm uses rational weights, with the manuscript's independent proof supplying real-weight generality; put printed page numbers beside the anchors. Initially fixed coordinates and nonessential zero coordinates are separate trivial cases. For bibliography, identify the linked Klijn document as the 1999 working-paper version of the 2003 article; add Llerena's pages 84–88. No need to strengthen or broaden the novelty language.

## Preserved evidence

Four full PDFs and extracted text were inspected in the research scratch directory; they are not redistributed in this release. `pdf_manifest.json` gives byte counts and SHA-256 hashes. The algorithm-page PNG was used for a visual check of printed p.20. The failed journal-version Klijn download produced no PDF and was not used. Publisher previews and institutional records above are linked with access limitations stated explicitly. No external contact, purchase, or publication occurred.
