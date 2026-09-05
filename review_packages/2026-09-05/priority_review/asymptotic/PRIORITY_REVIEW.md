# Asymptotic paper: construction and realization priority audit

Audit date: 5 September 2026. Scope: the read-only asymptotic review package dated 2026-09-05. This report owns the finite exact-game/min-game/whole-core/Fibonacci lane. The root review separately addresses general convex overlap, opposing lexicographic selection, recent algorithmic work, and price-of-fairness comparisons. No manuscript edits, PDF generation, or outreach were performed here.

## Finding

**The strongest adverse lead is a verified older substitute for the construction's load-bearing Fibonacci matrix ingredient.** Fibonacci–Isbell weighted majority games, explicitly described in primary work from 2015 and attributed there to Isbell (1956), together with the nonsingularity theorem in primary work from 2014, supply positive binary inverse-matrix vectors with exponentially small minimum coordinate. They fit manuscript Lemma 3 and recover its separation rate, first-order coefficient, and polynomial integer representation. The old gadget uses fewer auxiliary donors than the manuscript's gadget.

This does **not** identify an earlier publication of the opposing-selector separation theorem. It does rule out treating the existence of suitable Fibonacci binary matrices as a new ingredient. The current specific paired-coordinate matrix has not been identified verbatim in the sources examined. Keeping its direct proof for self-containment is reasonable, with credit for the older applicable construction and a narrower contribution statement.

The equal-total minimum-of-two-additive-games framework is also explicitly prior as the bifocal distribution game. Entire-core segments with two disjoint-support generators occur in an accessible 2008 primary example. The new contribution cannot safely be phrased as the discovery of that framework or of whole-core segments generally.

## Claim-by-claim classification

| Package claim and exact anchor | Classification after this review | Evidence and remaining boundary |
|---|---|---|
| `v(S)=min{U(S),V(S)}` with efficient generators; manuscript 194–198 and 212–214 | Exact prior framework / representation theorem | Bifocal game Definition 3.1 in the 2010 working paper; Studený–Kratochvíl 2018 Proposition 1. |
| Two disjoint-support generators can give an entire-core segment; 186–198 | Exact prior example | Shellshear–Sudhölter 2008 Example 4.3. This does not establish the general matrix lemma as a previously stated theorem. |
| The particular sufficient matrix condition forces the whole core; 188–229 | Known method specialization; precise formulation remains a candidate contribution | Complementary tight-coalition equations and rank are standard polyhedral reasoning. No accessed theorem has been found that directly states this exact donor/receiver embedding. Rosenmüller's book remains an unresolved possible source. |
| Binary invertible matrices with positive inverse-one vector and Fibonacci-small minimum; 251–296 | Implied by prior theorems | Pressacco–Ziani 2015 and Pressacco–Plazzotta–Ziani 2014. The manuscript's particular paired-coordinate presentation is not established to be identical. |
| Its explicit scalar selector and distance formula; 199–208 and 265–270 | Elementary specialization of the segment geometry; exact prior formula not located | The known matrix replacement yields the analogous formula derived below. No source examined states that selector comparison. |
| `lim n(2-s_n)=2`, remainder `O(log n/n²)`; 98–116 and 299–320 | Candidate new quantitative theorem, subject to the root's generic-bound audit and unresolved sources | Construction side follows by combining the segment lemma with a known gadget. A prior separated piece plus a new combination is not itself prior publication of the combined theorem. |
| Polynomial integer generators and total; 113–116 and final proof paragraph | Known gadget permits same asymptotic bound; candidate quantitative corollary | The calculation below supplies total `<2n³` independently of the manuscript's new matrix presentation. |
| “explicit whole-core realization” as proposed contribution; 141–144 | Wording needs narrowing before outreach | Distinguish the particular embedding and quantitative use from the already known framework and examples. |
| Old source screen and access record; `CLAIMS_AND_SOURCES.md` 64–72, 91–94, 105–110 | Materially superseded by this review | Full Studený–Kratochvíl 2022 author PDF now accessed; new primary bifocal, segment, and voting-matrix sources materially change the construction comparison. |

## Primary Fibonacci evidence

Pressacco and Ziani, *A Fibonacci Approach to Weighted Majority Games*, Journal of Game Theory 4(2), 36–44 (2015), Introduction p.36, gives the Fibonacci–Isbell weights and quota. Section 5, p.39, identifies the family within parsimonious games; footnote 5 defines the count of minimal winning coalitions. It attributes the weight construction to Isbell's p.185. [Author institutional full text](https://air.uniud.it/retrieve/e27ce0c2-77a3-055e-e053-6605fe0a7873/10.5923.j.jgt.20150402.03.pdf).

Pressacco, Plazzotta and Ziani, *Twin relationships in Parsimonious Games: some results*, Theorem 4.2, pp.7–8, proves that the binary minimal-winning-coalition incidence matrix is nonsingular and has determinant of magnitude the quota. Section 3.2 specifies the matrix; equation (5.4), p.9, gives its weighted row equations. Their stated scope is more than three players (Introduction footnote 1). [Primary full text](https://arxiv.org/pdf/1404.2305). The official arXiv history dates v1 to 20 February 2014, despite the identifier's 1404 prefix; the report uses the explicit history.

Isbell's original *A Class of Majority Games*, QJM 7(1), 183–187, has an official 1956 publication record. Its subscription body was not accessed. Thus the original attribution is mediated through later primary authors; the actual ingredient was verified in the 2014/2015 texts, not merely inferred from a citation. [Publisher record](https://academic.oup.com/qjmath/article/7/1/183/1585519).

## Independent implication for the manuscript

The following derivation is this audit's inference, not a theorem claimed by the older sources. Use `p>=4` to stay within the nonsingularity source's scope, and put

```
q = F_p,
w = (F_1,...,F_{p-2},F_{p-2},F_{p-1}),
d = w/q.
```

Let `A` be the incidence matrix of the game's `p` minimal winning coalitions. Each such coalition has weight `q`, and the source theorem makes `A` invertible. Therefore

```
A d = 1,   d > 0,   min d = 1/q,   max d < 1,
sum d = (2q-1)/q = 2-1/q.
```

The last identity follows independently from the ordinary Fibonacci sum identity. For an integer `r>=3`, choose

```
H = r-2+1/q,       U=(H,d;0^r),       V=(0^{p+1};1^r).
```

All of Lemma 3's hypotheses hold, including `H>=1`, equal positive total `r`, and disjoint nonnegative supports. Its complementary-coalition argument gives the entire core `[U,V]`. The endpoints do not need to be presumed to exhaust the core. On the resulting segment the minimum coordinate is `min(t/q,1-t)` and the maximum is `max(tH,1-t)`, so their unique optima are

```
t_min = q/(q+1),                 t_max = 1/(r-1+1/q),
2-rho = 2/(q+1) + 2/(r-1+1/q).
```

With total players `n=r+p+1`, the second denominator is `n-p-2+1/q`. Take the least `p>=4` with `F_p>=n²`. For sufficiently large `n`, `p=O(log n)`, `q<2n²`, and `r=n-p-1>=3`. Consequently this construction alone gives

```
2-rho = 2/n + O(log n/n²).
```

Combining it with the manuscript's upper bound on separation gives precisely its first-order coefficient. This combination still requires the overlap argument; the weighted majority papers do not prove that argument.

For a fully explicit check, let `L=ceil(log_2 n)`. The elementary inequality `F_{4L+1}>=2^{2L}` gives `p<=4L+1`; for `n>=128`, `n>=4L+5` ensures the parameter hypotheses. Hence the alternative construction even permits

```
2-s_n <= 2/(n-4L-3) + 2/(n²+1).
```

This tighter finite constant is an audit inference, not a recommended replacement this turn. Scaling by `q` gives integer generators with distinguished coordinate `(r-2)q+1`, donor coordinates `w_i`, receiver coordinates `q`, and total `rq<2n³`. Each coordinate has `O(log n)` bits.

The implication is independently corroborated in `isbell_check.py` and `isbell_check.json`: exhaustive subset enumeration for `p=3,...,18` verifies homogeneity, exactly `p` minimal winning coalitions, exact determinant magnitude `F_p`, positivity and the sum/minimum identities. Four fresh raw-coalition core models, with `n=7,8,9,11`, give UNSAT for an off-segment core point and for a distinct first-stage maximin/minimax optimizer. Parameter inequalities are checked for every integer `128<=n<=10000`, with further large samples. The `p=3` case is a direct check of the three-player majority matrix, not an application of the source's `p>3` theorem. Finite tests corroborate, rather than establish, the all-parameter argument.

## Whole-core and min-game precedents

The 2010 IVIE paper *Some game-theoretic grounds for meeting people half-way*, Definition 3.1 (PDF p.7), defines exactly the equal-total minimum-of-two construction. Theorem 3.6 (PDF p.10) proves its Shapley value and nucleolus are the average of the generators. Its Lorenz bankruptcy application compares awards and losses; that is not the manuscript's opposing sorts of the same labeled payoff vector. The 2016 journal version has the title *Compromising in bifocal distribution games: the average value* and publisher date 25 February 2016. [Full working paper](https://www.ivie.es/downloads/docs/wpasad/wpasad-2010-04.pdf), [journal record and accessible appendices](https://link.springer.com/article/10.1007/s11238-016-9540-5).

Shellshear and Sudhölter, *On Core Stability, Vital Coalitions, and Extendability*, Discussion Paper 3/2008, Example 4.3 (printed p.13/PDF p.14), explicitly gives an exact two-generator game whose entire core joins `(2,1,1,0,0,0)` and `(0,0,0,2,1,1)`. The example cites Rosenmüller (2000) for the segment and Raghavan–Sudhölter (2005) for exactness. It establishes a concrete prior whole-core segment, but the symmetric example has no opposing-selector separation. [Institutional full text](https://www.sdu.dk/~/media/B05C4BC4391646C684EAC307F97B8860.ashx).

Studený and Kratochvíl (2018), Definition 3 and Proposition 1, pp.5–6, establish the core-based min-representation framework. Their regularity condition says generators are among the core vertices; it does not say the listed generators are all vertices. This blocks an invalid shortcut from regularity to the desired entire-core equality. Their argument supplies standard active-constraint context, not a directly located quantitative segment-embedding theorem. [Author full text](https://staff.utia.cas.cz/studeny/FTP/stu-krat-IJAR-2018.pdf).

Farber–Berman (2013), Theorem 2.1, is additional older Fibonacci/binary-matrix context, but its triangular unimodular matrices have integral inverse entries. A positive inverse-one vector there cannot have a positive coordinate below one, so that theorem alone is not the needed donor construction. [Primary full text](https://arxiv.org/pdf/1306.2845).

## Ready-to-insert wording

Suggested replacement for the construction-priority portion of manuscript lines 135–145:

> Equal-total minima of two additive games are established as bifocal distribution games, and earlier exact-game examples already have two-generator segment cores. Our segment lemma gives a sufficient incidence-matrix condition for the particular donor–receiver embedding used here. Fibonacci incidence matrices with the required positive inverse-one vectors also occur in the older Fibonacci–Isbell parsimonious weighted majority games; these supply an alternative input to the lemma. We retain the direct matrix proof for self-containment. The candidate contribution is the quantified separation of the opposing core selections, including its first-order asymptotic coefficient. The novelty of the framework, of segment cores generally, or of Fibonacci voting matrices is not claimed.

Suggested source-ledger status for the construction:

> The displayed matrix family is proved directly. Its load-bearing existence property is already available from Fibonacci–Isbell parsimonious-game incidence matrices: Pressacco–Ziani (2015), p.36 and §5, together with Pressacco–Plazzotta–Ziani (2014), Theorem 4.2. Applying the present segment lemma to those matrices yields the same asymptotic coefficient and integer-size order. No accessed source in this audit states the resulting opposing-selector distance theorem.

Recommended additions to the specialist questions: ask whether the **specific sufficient embedding condition** is subsumed by Rosenmüller's finite MIN-game theory, and whether applying known voting matrices to opposing selector separation has already appeared. Avoid asking whether whole-core segments or Fibonacci matrix constructions are new in general; the accessible evidence answers those questions adversely.

## Limits and reproducibility

The ledger contains 59 dated discovery queries and 14 source records, with backward/forward citation leads and access limits. Search results and raw browser outputs are preserved separately. Bibliographic search dates are not publication dates. The original Isbell body, Rosenmüller's 2000 book, Raghavan–Sudhölter 2005 body, and later Fibonacci representation extensions remain incompletely accessed; they must not be reported as negative full-text comparisons. A targeted 2025 balanced-collection screen is not a complete review of that paper. Generic fairness and overlap priority are outside this lane.

Neither this review nor a failed search proves novelty. The decisive conclusion is narrower and affirmative: prior published constructions supply the required Fibonacci binary-matrix ingredient, and existing literature already contains the two-generator game framework and entire-core segment examples.
