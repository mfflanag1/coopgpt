# Initial primary-source gate: strict pair-additive triples

Date: 5 September 2026. Scope: three sectors of the same finite size q, nonnegative pair matrices A, B, C, triple values `w_ijk=A_ij+B_ik+C_jk`, and **strict** triple matching worth. Singletons and pairs have worth zero. The full core is assumed nonempty, T is the integral matching value, x is full ascending leximin, z minimizes the descending sorted vector, H_i is the maximum of coordinate i over the full core, and rho=||x-z||_1/T. Only this literature scratch directory was written.

**Gate result.** This model is an old subclass of multisided assignment games, already present in work attributed to Quint (1988 working paper/1991 publication). No inspected primary theorem supplies a uniform positive lower bound on this particular leximin's x_i/H_i, or a nontrivial universal bound on its distance from the opposite full selector, for the entire class above. That is a bounded non-finding, not evidence of novelty. There are substantial useful prior statements, but their hypotheses and selection rules cannot be dropped.

## Original Quint access and exact attribution limit

Thomas Quint, *The Core of an m-Sided Assignment Game*, GEB3(4),487–503, November1991, DOI [10.1016/0899-8256(91)90017-9](https://www.sciencedirect.com/science/article/abs/pii/0899825691900179). The primary publisher abstract confirms the multisided model, possible empty cores, and a sufficient balanced subclass. The author's [publication page](https://www.thomasquintmath.com/publications) confirms the record. Direct full-text and public PDF routes did not yield the article; they returned an error or subscription preview. **The full original remains uninspected, so its exact theorem numbering and complete hypotheses have not been established here.**

A new original institutional provenance check found [UCLA CAM88-24, August1988](https://ww3.math.ucla.edu/cam-reports-1986-2000/) with this exact title and author. Unlike adjacent entries, this entry has no PDF link. This dates the working paper; it does not establish that its theorem statements match the 1991 version.

Two later primary documents describe Quint's pair-additive sufficient condition, but conflict on a quantifier:

- Atay's [2017 thesis](https://diposit.ub.edu/server/api/core/bitstreams/1f199fe6-c683-45fd-add3-f32aecd56e10/content), printed p.19, Lemma2.14 and inequality(2.5), use **fixed nonnegative alpha1,alpha2 summing to one**, and assume `d^rs_ij <= alpha1*d^rs_ii + alpha2*d^rs_jj` for every pair of sectors r<s and all i,j. Pair numbers are nonnegative; team value is their sum. The thesis text is a cited restatement, not the original Quint proof. An indexed rendering has a summation-endpoint typo; use the all-pairs intended definition, not that rendering verbatim.
- Streekstra–Trudeau's [13 July2020 working paper](https://www.sdu.dk/-/media/files/om_sdu/institutter/ivoe/disc_papers/disc_2020/dpbe7_2020.pdf), §4.2.2, printed p.19, says **“for any” alpha in [0,1]**, after an optimal-diagonal relabeling. That is stronger than the fixed-alpha sufficient statement. Their [15 July2022 revision](https://www.sdu.dk/-/media/files/om_sdu/institutter/ivoe/disc_papers/disc_2022/dpe8_2022.pdf) no longer reproduces this condition in the corresponding section. Do not silently choose a quantifier and attribute it as Quint's exact theorem.

The fixed-alpha version is independently sufficient in the present nonnegative model. Put a=alpha1, and after the asserted common diagonal labeling define

`p_1i=a(A_ii+B_ii)`,
`p_2j=(1-a)A_jj+a C_jj`,
`p_3k=(1-a)(B_kk+C_kk)`.

Termwise application of the three diagonal-mixture inequalities proves each triple constraint. Payoffs are nonnegative and their total is the diagonal matching value, proving both optimality and nonempty core. This is a transparent verification of the sufficient condition; **it gives a feasible core point, not a full-core formula or either full selector**. Mere nonnegative pair-additivity plus balancedness is broader than this sufficient condition.

## Closest applicable geometry and its boundaries

| Primary result | Exact applicable hypothesis/conclusion | Consequence for this campaign |
|---|---|---|
| Atay–Núñez2019, ANOR279,271–290, Proposition1 and Definition2 | A generalized multisided graph market has a matching whose projection is optimal in every bilateral market. Compositions of bilateral core points belong to its core. | The same certificate applies to strict triples when a common perfect triple matching realizes all three bilateral optima. It proves `T=T_A+T_B+T_C` and a **subset** of the strict core. Balancedness alone does not imply this compatibility. |
| Same paper, Theorem1 | Cycle-free graph on sectors, with smaller connected coalitions also earning their pair-additive output. The whole generalized core equals the composition of bilateral cores. | Cannot be imported as the whole **strict** core, including at equal sector sizes. A cycle with all three matrices active is outside the theorem as well. |
| Same paper, Proposition2 | Same cycle-free generalized model; coordinate maxima in each sector are simultaneously attained. | Neither cyclic pair-additivity nor the full strict core inherits this conclusion from the theorem. Even an ideal-protecting core point would not identify leximin. |
| Stuart1997, *The supplier-firm-buyer game and its m-sided generalization*; reproduced/extended by Streekstra–Trudeau2022, Theorem6/Corollary3, printedp21 | Strict chain-additive, or their tree-on-sectors extension, with nonnegative edge contributions. Balancedness/total balancedness via their representation. | Important old nonempty-core subclass: e.g. one of A,B,C is identically zero. No inspected selector-ratio/distance theorem. |
| Tejada–Núñez2012, Theorem1, printedpp203–204 | Böhm-Bawerk values `max(0,buyer value−seller costs)`; core is a translation plus sector replication of a convex game core. | Contains complete additive arrays `a_i+b_j+c_k`, a proper subfamily of the present class. Does not describe arbitrary pair-additive matrices. |

The full [Atay–Núñez2019 original HTML](https://link.springer.com/article/10.1007/s10479-019-03256-5) was inspected at the displayed results and examples. Publication date is21 May2019. Its Section6 explicitly distinguishes generalized and strict models. Equal sizes do not eliminate the difference: with one agent in each sector and A=B=C=[1], the strict core is `p>=0,sum p=3`; the generalized model additionally imposes all pair sums>=1. Even in a chain, A=B=[1], C=[0], the strict core is the simplex of total2, while bilateral composition restricts each leaf's payoff to at most1. These elementary examples refute the proposed whole-core identification without relying on unequal sectors.

Atay–Núñez2019 Appendix Example5 provides a valuable historical control:

```
A = [[4,4],[5,0]]
B = [[2,0],[1,5]]
C = [[4,3],[0,9]]
```

The strict diagonal matching has values10 and14, so T=24; the source's displayed payoff `(4,5;0,0;6,9)` certifies full strict-core feasibility too. Bilateral optima sum to29, so no compatible three-way matching attains all three. Thus balancedness does not imply the compatibility premise. The source also proves failure of simultaneous third-sector maxima **for its generalized core using pair inequalities**. That latter failure must not be copied to the larger strict core; strict H and selectors need fresh calculation.

## A useful prior implication for the smallest nontrivial size

Every2×2×2 pair-additive strict array with nonnegative triple values has nonempty core. This follows from the Lucas criterion as reproduced in the primary [Atay–Núñez2019 MSS paper](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_MSS.pdf), §2, printedp11 (original Lucas still inaccessible).

Here is the deduction. Relabel an optimal perfect matching as111,222 and write a=w111, b=w222, Q=w112+w121+w211, Q'=w221+w212+w122. Pair-additivity gives zero third mixed difference, so `a+Q'=Q+b`. The three alternative perfect-matching comparisons give `3(a+b)>=Q+Q'`. Combining yields `2a+b>=Q`; the second Lucas inequality `a+2b>=Q'` is equivalent. These are exactly the two core-nonemptiness conditions. Thus size2 empty-core searches are unnecessary controls, and this nonemptiness fact should receive prior-criterion credit rather than a new-result label.

The q=1 strict game is a three-person simplex: x=z=(T/3,T/3,T/3), H_i=T. Consequently any uniform individual constant for the entire campaign class is at most1/3. No positive uniform constant is established here beyond this upper limitation.

## Fair allocation precedents and what they do not prove

Tejada–Rafels, *Symmetrically multilateral-bargained allocations in multi-sided assignment markets*, IJGT39(2010),249–258, [DOI10.1007/s00182-009-0204-3](https://link.springer.com/article/10.1007/s00182-009-0204-3), has an accessible [2009 institutional working version E09/216](https://diposit.ub.edu/bitstreams/92331b85-c564-429d-866c-e063a2d7b3b0/download). Definitions1–3, printedpp8–9, define threats and equal division of each matched team's residual; Theorems6–7 characterize the resulting SMB set and prove nonemptiness for balanced strict multisided games. This is relevant older fairness work, but **SMB is a set of bargaining fixed points, not either anonymous full sorted selector**. A factor1/3 in its bargaining equation is not a theorem comparing leximin to H_i.

The source adds fully null triple-array dummy players to square a market. Such padding is valid for arbitrary strict arrays but need not preserve the campaign's nonnegative pair-additive representation: an appended agent in sector3 still participates in all positive A_ij contributions. This campaign must check pair-additive membership again after any padding.

Vazirani's bipartite half guarantee and the older full-selector framework do not cover strict triple constraints. The previous release's complete-additive benchmark follows from a translated sector simplex; it provides a useful subcase with1/3 protection and a4/3 distance supremum, not a bound for the larger class. Supermodular/locally monotone multisided core results impose an ordering restriction absent here. A core representation, or existence of a point protecting each H_i/3, would not by itself show the leximin vector has that protection.

No exact full leximin-versus-descending-minimum normalized-distance bound for arbitrary balanced nonnegative pair-additive strict triples was located in this cycle. General nonnegative efficiency gives rho<=2, but that is an elementary normalization bound and says nothing about the best class-specific constant.

## Source access limits and recommended campaign wording

Quint's1991 original and1988 working paper remain unavailable. Lucas's1995 original criterion remains accessible only through later primary restatements. Martínez-de-Albéniz–Rafels–Ybern's2023 [*Extreme Core Points in Multisided Assignment Problems*, SSRN4369524](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4369524) remains abstract-only from the preceding audit; whether it specializes usefully here is unresolved. These are genuine source gaps, not negative evidence.

Safe wording: “We study the full sorted egalitarian selectors on the established class of strict pair-additive three-sided assignment markets, under nonnegative pair weights and nonempty core. Existing balancedness criteria and generalized core-composition theorems provide controls, but their hypotheses do not yet give the quantitative full-core comparison sought here. The initial primary-source search did not identify a uniform leximin ideal guarantee or sharp opposing-selector distance theorem for this entire class.”

Proceed with theory and exact experiments under the stated contract. Do not claim the model, core nonemptiness on compatible/tree subclasses, or size2 balancedness as novel. Any eventual candidate theorem still needs comparison with the unread Quint original and the newer general extreme-core preprint. This initial gate is complete; further source work should target a concrete theorem or example produced by the campaign rather than repeat broad searches.
