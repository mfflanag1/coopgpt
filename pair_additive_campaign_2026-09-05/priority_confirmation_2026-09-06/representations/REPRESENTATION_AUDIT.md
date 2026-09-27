# Representation-based priority challenge

**Dated disposition: 6 September 2026.** I did not obtain a valid deduction of the frozen vanishing-family theorem from the inspected earlier representation results. Several tempting shortcuts fail for explicit mathematical reasons. This strengthens the case for a **candidate new constrained realization**; it does not confirm worldwide novelty or exclude an uninspected earlier gadget.

The frozen statement is [cycle 5's theorem](../../cycle5/root/VANISHING_FAMILY.md): complete strict three-sided markets, ordinary full ascending leximin and coordinate ideals over the same whole core, a positive global first floor, and nonnegative pair entries from the fixed integer alphabet `{0,1,2}`. The target ratio tends to zero. This review asks whether an older result already implies that precise combination, even if it uses different terminology.

The bounded retrieval used **eight focused queries and four primary papers**, following the hypergraph-matching reference network and a separate transportation-universality lead. Full original texts were accessible for all four selected papers through web extraction; the exact theorem sections actually read are listed in `SOURCE_LEDGER.json`. This is not a claim that every line of every source was read. Initial failed hosts and unsuccessful direct DNS downloads are retained in the raw ledger. No optimization or outreach was performed.

## 1. Partitioning and linear-production representations

Demange–Deng's [2010 paper](https://www.econstor.eu/bitstream/10419/98563/1/749510048.pdf), §§2.1–2.2 and Theorem2, printedpp302–304,308, explicitly treats packing/partitioning games through incidence matrices and proves the core criterion using effective-coalition inequalities. It places these facts in the earlier Owen, Kaneko–Wooders, and Deng–Ibaraki–Nagamochi literature. Their general technologies and effective coalitions are not restricted to three sectors or pair-additive triple values. Theorem2's displayed simple-model setup uses binary data; the cover argument extends directly to nonnegative edge weights. No new-method credit is appropriate for this LP/core interface.

The valid direction is:

```text
our nonnegative triple weights + matching/cover equality
 -> a weighted rank3 packing game with the usual full-core cover description
 -> an instance of the established production/partitioning framework.
```

The reverse implication required to defeat priority is missing:

```text
an older production game with a weak leximin coordinate
 -> complete strict3-sector unit-player matching game
 -> nonnegative pair-additive values with a fixed integer alphabet,
while preserving the entire relevant labeled payoff core and sorted selector.
```

Embedding a special class into a general class does not supply this reverse reduction. Arbitrary production columns may use arbitrarily many resources, and arbitrary resource endowments are not unit players. Splitting a technology into intermediate stages introduces additional resources, price variables, or conservation constraints. The inspected theorem gives no preservation result for those changes.

## 2. The generic synergy representation does not lower coalition rank

Conitzer–Sandholm [2006](https://www.cs.cmu.edu/~arielpro/mfai_papers/CS06.pdf), Definition7 and Lemma2 on printedp611, represents a superadditive TU game by effective coalitions and checks blocking using them. Theorem4, printedp613, supplies a core-feasibility LP when the grand-coalition value is known. The TU hardness construction in Theorem2 uses triples but also coalitions of size`3m+1`, a productive pair, and values`6m`. Therefore neither its general representation nor that particular reduction is a fixed-three-sector, bounded-integer-pair realization theorem.

An exact obstruction explains why the earlier flow-path example cannot simply be relabeled. Its r-player full core is the simplex

```text
P={p>=0: sum p=1},
```

with all r coordinate unit vectors present. Suppose r>3 and P were the identical labeled full core of a nonnegative rank-at-most3 matching game on those players. Positive total worth requires some positive-weight hyperedge E. Because`|E|<=3<r`, choose j outside E. The simplex vertex assigning all payoff to j violates the E cover inequality. Contradiction.

The same argument rules out appending permanently zero auxiliary payoff coordinates while retaining that simplex and total1. This is an independent elementary obstruction to an **identical-core** shortcut. It does not rule out a more elaborate realization with additional payoff dimensions and a different total—which would require its own selector and ideal analysis.

Thus the older flow path establishes vanishing protection in a broader class, as already credited by the parent audit, but its generic partitioning/production representation does not establish the frozen result.

## 3. Transportation universality is the strongest apparent shortcut

De Loera–Onn's [author-hosted universality paper](https://www.math.ucdavis.edu/~deloera/RECENT_WORK/ipcouniversality.pdf), Theorem1 and its representation definition on PDFp2, embeds any rational polytope bijectively by retaining selected primal coordinates of a three-way transportation polytope. Theorem2 uses plane sums and forbidden entries; the final slim formulation uses line sums. Its explicit construction introduces additional coordinates, including fixed zeros and complements. The related final publication is [SIAM Journal on Optimization17(2006),806–821](https://epubs.siam.org/doi/10.1137/040610623); only that final record's abstract, not its full revision, was compared.

There are three distinct gaps between that genuine theorem and the desired deduction:

1. **Primal entries are not player-core prices.** The retained coordinates are transportation activities. Dualizing a line-sum program produces prices indexed by pairs of transportation indices, with arbitrary margins in its objective and unrestricted signs for equality prices. That does not identify the desired nonnegative unit-player payoffs.
2. **The effective triples are different.** A cell links only three mutually consistent pair-indexed prices. A complete cross-product of those three groups also contains inconsistent triples. Adding them changes the cover system. The theorem does not supply nonnegative pair data that make all these additional constraints harmless.
3. **A coordinate-preserving projection does not preserve raw sorted leximin.** Coordinate ideals of retained primal entries can survive a bijection while additional coordinates change the sorting objective. Preservation of feasible points or an arbitrary linear objective is insufficient.

The last gap is concrete even for nonnegative constant-sum polytopes. The segment

```text
P={(t,1-t):0<=t<=1}
```

has full leximin at t=1/2. The bijective coordinate extension

```text
Q={(t,1-t,t/2,1-t/2):0<=t<=1}
```

has constant total2 and the same first two coordinate ideals, but its first max-min level is maximized at t=2/3. Thus its retained second coordinate receives1/3 instead of1/2. This is a direct algebraic example, not an optimization campaign. Fixed-zero coordinates additionally conflict with the frozen theorem's positive global first floor, even when those zeros alone might leave later sorting unchanged.

The exact missing implication is an appropriate **whole payoff-core and selector realization**, not universality of linear programming itself. The inspected universality theorem does not provide it.

## 4. The convex hypergraph-matching route is excluded

Kumabe–Maehara [AAMAS2020](https://www.ifaamas.org/Proceedings/aamas2020/pdfs/p663.pdf), Theorem3.3 and Corollary3.4, printedpp665–666, characterize convex hypergraph matching games. For a positive-weight antichain hypergraph, convexity holds exactly when its edges form a matching. Their core-integrality discussion in Remark4.4 cites the earlier packing-game result. The paper supplies no leximin-to-ideal vanishing construction.

A strict positive3-uniform hypergraph is an antichain. In that convex subclass its productive triples must therefore be disjoint. Its core is a product of three-player simplices, giving each positive-ideal coordinate one third of its ideal under ordinary leximin. Hence this restricted source class cannot supply the required vanishing family.

The frozen family is outside it for every q>=1: the diagonal L0 triple and the incoming triple`(a_L0,b_L0,c_O1)` overlap in two players and both have value1. Their intersection has value0 and their four-player union has value1, violating convexity directly. This excludes an identical-game relabeling into that class. It does not claim that a nonconvex game's core cannot coincide geometrically with some different convex game's core.

## 5. Pair additivity and bounded integer data still need to survive

An arbitrary3-partite rank3 matching instance is not automatically pair-additive. If

```text
w_ijk=A_ij+B_ik+C_jk,
```

every alternating mixed difference over a2×2×2 box vanishes. A tensor that is positive only at one corner fails that identity. This obstruction survives relabeling; nonnegative pair decomposability imposes further restrictions beyond real pair decomposability. Completing a sparse hypergraph by zero-weight triples does not repair it.

Likewise, reductions preserving only an optimum or a yes/no packing decision do not establish preservation of the dual/core face, all mixed-triple covers, or a chosen ideal. The perimeter/decomposable-assignment query surfaced older optimization references, but their full gadget constructions were outside this bounded read; no claim of exclusion is made for every such construction. This remains a targeted residual priority risk.

There is also a useful wording distinction: **bounded real weights alone are not a substantial extra restriction**, since scaling each instance by its largest pair weight preserves the ratio`x_i/H_i`. A fixed integer alphabet such as`{0,1,2}` is stronger. The frozen statement has that stronger property; describe it explicitly rather than emphasizing boundedness alone.

## Practical assessment and the remaining implication

I have high confidence in the specific non-implications and elementary obstructions above. I have moderate confidence that this is a worthwhile surviving candidate for a new constrained realization, rather than an immediate corollary of the inspected general frameworks. This is not a quantified probability of global novelty.

The unresolved priority test is precise: find an earlier construction, or a valid chain from one, that simultaneously provides

```text
fixed three sectors + nonnegative pair-additive completion of every triple
+ full labeled payoff core and its coordinate ideal
+ the raw full sorted-leximin target, including auxiliary coordinates
+ a vanishing ratio, with positive global first floor
+ the stated fixed integer alphabet, if claiming that strengthening.
```

No inspected chain reaches that endpoint. Earlier fairness benchmarks, general vanishing examples, LP optimal-face freezing, partitioning representations, and arbitrary-polytope universality should all be credited at their actual scope. None alone constitutes a priority defeat for the frozen theorem. Conversely, absence of such a chain in these four papers cannot certify that no older rank3 or decomposable-assignment gadget already contains it.

This report closes the specified representation challenge at **candidate new constrained construction; global priority unresolved**. Historical Quint/Lucas/Stuart, the general2023 core paper, and other delegated source comparisons remain outside this report's disposition. No further searches or new mathematical constructions were run after this bounded gate.
