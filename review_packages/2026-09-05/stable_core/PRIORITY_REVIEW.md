# Stable-core paper: priority and significance review

Audit date: 2026-09-05. Scope: C1 (stable-core/PES separation) and C5 (additive ray and noninvariance). The package was read without modification. This report distinguishes published anticipation, mathematical implication, and an unsuccessful search for an exact match. The earlier mathematical audit is separate.

## Assessment

**The contribution needs a significance downgrade, even though no inspected source contains the exact displayed six-player perturbation or its three-regime ray.** The underlying segment is explicitly classical. Failure of the PES selector's strategic covariance is explicitly stated in the original 2017 paper. More materially, the existence of a stable-core/non-PES game follows by a short aspiration-and-translation argument from classical stable-but-not-large geometry and the original procedure. This deduction does not need the manuscript's two-round calculation or all-parameter ray.

I did **not** locate a prior publication explicitly stating the resulting all-translates characterization or the exact C1 witness. The elementary deduction below was reconstructed during this audit. It would be inaccurate to label it a located published theorem; it would also be inaccurate to treat it as a newly discovered deep mechanism. The appropriate description is an elementary synthesis of known definitions and results. Whether somebody has already written the synthesis remains unresolved.

The strongest remaining candidate contribution is a transparent, sharp-dimensional worked example, with a self-contained stability proof and exact formulas along one specified positive ray. That may support a short note, subject to specialist judgment; this review cannot establish its publication value or priority.

Two material source-access limitations in the package have been removed: the **full final 2025 population paper** and the **complete 2008 author version of Shellshear–Sudhölter Example4.3** were downloaded and inspected. The final 2025 paper does not supply the missing separation or additive ray.

## Claim-level classification

| Claim | Classification | Reason |
|---|---|---|
| Classical six-player exact segment with stable core | **Exact prior result** | Shellshear–Sudhölter, Example4.3, printedp13 of2008WP, gives both endpoints and states exactness/stability. |
| Addition of an additive game translates the core and preserves dominance/exactness | **Known mechanism specialized** | Direct cancellation in definitions; no conceptual novelty. |
| PES selector lacks full strategic covariance | **Exact prior result** | Dietzenbacher–Borm–Hendrickx2017p185 explicitly discusses this, while retaining uniform-shift covariance. |
| Existence of a six-player stable-core/non-PES game | **Implied by prior geometry plus an elementary deduction** | A noncore aspiration can be translated to constant terminal PES claims; proof below. No publication explicitly recording the synthesis was located. |
| The exact endpoints in C1, and their two-round claims | **Candidate new worked example** | No matching example in the inspected primary sources; numerical-string search has very low evidentiary power. |
| Six-player minimum | **Immediate consequence of prior theorem plus existence** | Estévez-Fernández low-dimensional largeness theorem and Dietzenbacher large-core implication supply the lower bound. |
| PES-stability class is not additively invariant, without a stable-core restriction | **Elementary inference already available from earlier examples** | Translate any core allocation of an old balanced/non-PES game to zero; the translated game is PES stable in one round. |
| Same class failure within exact stable-core games | **Elementary consequence of C1/synthesis** | Additive translations preserve exactness/core stability. It is not an additional independent breakthrough. |
| Exact C5 ray, breakpoints2/3 and1, three formulas | **Candidate new quantitative specialization** | No exact prior ray located. Generic piecewise-affine behavior is unsurprising for a finite affine/max procedure; the useful content is the exact family and formulas. |
| General arrangement method for core stability | **Known algorithmic setting** | Grabisch–Sudhölter and Laplace Mermoud et al./thesis already treat finite geometric/algorithmic core stability. Package appropriately disclaims broad novelty. |

## Fully checked elementary synthesis

Let N be finite and nonempty, and define
\[
U(w)=\{x\in\mathbb R^N:x(S)\geq w(S)\text{ for all }S\subseteq N\}.
\]
This is the upper core, without the efficiency equation. A game has a large core exactly when every y in U(w) lies above a core allocation. Do not silently use “aspiration” for every upper-core vector: the PES/Bennett usage additionally requires that tight coalitions cover all players.

Suppose w does not have a large core. Choose y in U(w) with no z in C(w) satisfying z≤y. The set
\[
K=\{x\in U(w):w(\{i\})\leq x_i\leq y_i\text{ for each }i\}
\]
is nonempty (contains y) and compact. Let a minimize a(N) on K. Since a satisfies the grand-coalition inequality, a(N)≥w(N). Equality would put a in the core below y, contrary to the choice of y. Thus
\[
\delta=a(N)-w(N)>0.
\]

For each i, some coalition containing i is tight at a. Otherwise all finitely many incident coalition slacks are strictly positive, and reducing a_i by a sufficiently small positive amount preserves every constraint. The singleton constraint is included, so this reduction also respects K's lower bound; the upper bounds cannot be violated by reducing a coordinate. It contradicts minimality. Thus a is an aspiration, and it is coordinatewise minimal in U(w).

Define u(S)=w(S)−a(S). Every coalition has u(S)≤0, and zero-worth coalitions cover N. In the **first round** of the original PES procedure, every coalition offers each member u(S)/|S|≤0. Every player belongs to a zero-worth coalition, hence has maximum offer0. All members of every zero-worth coalition attain their maxima there. Those coalitions are admissible and their union is N: all players are fixed at0 after one round. Terminal claims are0, whereas u(N)=−δ<0. The grand coalition is not terminal-admissible, so u is not PES stable. Claims are not being confused with the final efficient PES allocation.

Any additive translation preserves imputations, the core, exactness, external dominance and superadditivity. Therefore, if w has a stable core, so does u; if w is exact or superadditive, those properties also remain true.

Negative grand worth is not essential. Choose a real L satisfying
\[
L>\max\left\{0,\ \delta/|N|,\
\max_{\substack{i\in N\\S\subseteq N\setminus\{i\}}}
\left[a_i-\bigl(w(S\cup\{i\})-w(S)\bigr)\right]\right\}.
\]
The game q(S)=u(S)+L|S| then has q(N)>0 and every one-player marginal strictly positive. Thus q is monotone and, because q(empty)=0, nonnegative. Every first-round coalition offer is at most L, and the formerly zero-worth covering coalitions offer exactly L. Terminal claims are L1, whose sum exceeds q(N) by precisely δ. No general selector-covariance assertion is needed for this first-round calculation. Uniform-shift covariance is independently known from2017.

Consequently, classical stable, nonlarge games produce monotone stable-core/non-PES examples on the same player set. Start from an exact superadditive classical example and those additional properties are retained. The low-dimensional lower bound then makes the familiar six-player example sharp.

For completeness, this reasoning yields the elementary equivalence
\[
w\text{ has a large core}
\quad\Longleftrightarrow\quad
w+c\text{ is PES stable for every additive vector }c.
\]
The forward direction uses additive invariance of largeness and the published large-core⇒PES theorem. The reverse direction is the preceding construction. This is an audit deduction, **not a bibliographically established new theorem**. It should not become an inflated field-level claim.

### Exact numerical check of the synthesis

An explicit aspiration of the package's unperturbed game with endpoints
U=(0,1,0,1,2,0), V=(1,0,1,0,0,2) is
\[
a=(1/2,1/2,1,1/2,1/2,3/2).
\]
It satisfies all63 nonempty coalition inequalities, has sum9/2>4, and its tight coalitions are
12,14,15,56,135,1256,1456. They cover N. A core point (1−t)U+tV below a would require t≥3/4 from player5 and t≤1/2 from player1, an impossibility.

Taking L=3/2 gives the **different illustrative translation**
q=w+(1,1,1/2,1,1,0). Its two endpoints are
(1,2,1/2,2,3,0) and (2,1,3/2,1,1,2).
All players are fixed at3/2 in the first round, while q(N)=17/2<9.
This independent exact calculation is retained in check_aspiration_synthesis.py and aspiration_synthesis_check.json. It demonstrates why complicated procedural strata are unnecessary for the bare separation. It is not claimed as a published precedent or a replacement paper.

### General class noninvariance was already easy to infer

For any balanced game v and any x in C(v), let r=v−x. Then r(S)≤0 for every S and r(N)=0. The grand coalition gives everyone their maximal first-round offer0, so r is PES stable. Thus **every balanced game's additive-equivalence class contains a PES-stable representative**.

Applying this to an earlier balanced/non-PES example gives noninvariance of the class. Applying it to the exact non-PES example in Mauri2017 gives the exact-game version. This explains why the unrestricted statement in manuscript Corollary noncovariance is weaker, in priority terms, than the stable-core separation. Selector noncovariance alone would not prove this class statement: e.g., different covariant behavior within convex games need not leave the PES-stable domain.

## Exact source comparison and dates

The machine-readable table SOURCES_AND_ACCESS.json records16 primary sources, versions, access levels, URLs and locators. The following are the load-bearing comparisons.

| Source and precise locator | Access/version | Effect on C1/C5 |
|---|---|---|
| [Dietzenbacher–Borm–Hendrickx2017](https://cris.maastrichtuniversity.nl/ws/portalfiles/portal/109504649/Dietzenbacher_2016_The_procedural_egalitarian_solution.pdf), p185; Examples1–4; conclusionp187 | Full final GEB106179–187. Repository filename2016 is misleading; cover/body identify final2017. | Explicit old selector noncovariance and uniform-shift covariance; examples do not furnish C1 or C5. Unequal glove-game PES failure lacks the required stable core. |
| [Dietzenbacher2019WP](https://pure.uvt.nl/ws/portalfiles/portal/29315203/2019_007.pdf), Theorem4.1 and footnote11p20; open questionp21 | Full CentERDP2019-007; manuscript2019-02-26, issued2019-03-05. | The question predates the2021 publication. Aspiration facts make the short deduction especially close to existing text. |
| [Dietzenbacher2021](https://www.researchgate.net/publication/350699095_Monotonicity_and_egalitarianism), Lemma2.1p198; Theorem3.5/footnote3p203; p204 | Published text checked in preceding audit and relevant passages freshly located. | Large-core implication and question. No explicit all-additive-translates statement located. |
| [Shellshear–Sudhölter2008WP](https://www.sdu.dk/-/media/files/om_sdu/institutter/ivoe/disc_papers/disc_2008/dpbe3_2008.pdf), Example4.3p13; journal2009 | Full authorWP now directly inspected. | Exact endpoints (2,1,1,0,0,0),(0,0,0,2,1,1) and stable/exact claims explicitly printed. Resolves the package's inherited-locator uncertainty. |
| [Dietzenbacher–Doğan2025 final](https://cris.maastrichtuniversity.nl/ws/portalfiles/portal/287715430/Dietzenbacher-2025-Population-monotonicity-and-egalitarianism.pdf), Lemma4.2p13; Example5p13; Theorem4.1pp14–15; conclusionpp15–17 | Full final IJGT54:42. Online2025-11-17; issue repository date2025-12-01. | Exact-partition⇒PES and total exact-partition⇔totalPES. All displayed examples have3or4players; the non-PES example does not have stable core. Final conclusionp16 discusses large/exact small-player classes but contains no stable-core counterexample or additive ray. |
| [Grabisch–Sudhölter accepted2021/final2024](https://findresearcher.sdu.dk/ws/portalfiles/portal/197277277/core_stability_09_08_21_final_manuscript.pdf), Example6.4p14ff; §8pp19–20; appendix | Full accepted manuscript dated2021-08-09; final MathProg203801–826(2024). | Five-player segment lower envelope is explicitly nonstable; §8 separates strict/weak domination. General finite criteria predate current arrangement appendix. No egalitarian discussion. Final typesetting not separately compared. |
| [Dietzenbacher2018 thesis](https://comsoc-community.org/assets/theses/phd-dietzenbacher.pdf), Ch7; Proposition7.3.3p119 and following discussion | Full text available; targeted TU-PES chapter comparison. | Weak strategic covariance already formalized and strong covariance discussed; no found C1 ray. |
| [Laplace Mermoud2023 thesis](https://arxiv.org/abs/2301.02950), Chapter4pp73–79; Examples4.1.3–4.1.5pp78–79 | Full v2PDF, revised2023-10-03; first version2023-01-08. | Four/five/six-player stability examples; six-player Studený–Kratochvíl game explicitly nonstable. No PES/egalitarian text. Geometry/arrangements already established context. |
| [Laplace Mermoud–Grabisch–Sudhölter](https://arxiv.org/abs/2507.05898), §7.6pp24–25 | Inspected arXiv2025upload of work published DAM34160–81 in2023. | Same nonstable six-player example; algorithms are prior work. One five-player formula says max where thesis says min, so no inference was made from the inconsistent raw formula. |
| [Mauri2017 thesis](https://repositori.urv.cat/repositori/getDocument/TDX%3A2707?ds=Memoria&mime=application%2Fpdf), Example5pp40–41 | Exact one-round bridge independently checked in earlier audit. | Exact-game half already exhibited; also supplies exact-domain additive class noninvariance by the core-point translation above. |

Additional citation-chain screening included Gong–Dietzenbacher2026Theorem5, Gong–Li2025, Takanashi2024, Otsuka2020, the2020antiduality note,2025Network Egalitarian-Myerson, and2025cohesion flow. The first two contemporary equality-value papers concern different selectors/axioms; inequality-averse and discrete-payoff works change the model. These are **screened neighboring works**, not blanket full-text exclusions. In particular, the network paper's main body is subscription restricted despite its long visible HTML appendix.

## Required wording and bibliography changes

1. **manuscript.tex:38–54 and103–105.** Keep the factual separation, but replace “new ingredient” rhetoric with an explicit attribution to translating a classical nonlarge stable core. Explain the aspiration deduction, preferably in a short remark. Do not imply the generic failure of strategic covariance is new.
2. **manuscript.tex:112–120.** Narrow the contribution statement to an explicit sharp-dimensional instance, self-contained proof, and formulas for one ray. Remove the now-stale claim that final2025text has not been inspected.
3. **manuscript.tex:496–511.** State class noninvariance as a consequence/illustration. Cite2017p185 for the distinct selector fact and explain that earlier balanced/non-PES examples already imply unrestricted class noninvariance after translation.
4. **manuscript.tex:585–600.** Describe how this specific ray combines otherwise unaffordable claims, without suggesting a new general mechanism is needed for separation.
5. **CLAIMS_AND_SOURCES.md:11–15,27–33,41–47.** Replace old access gaps with the verified sources above; classify existence as elementary synthesis, C2 as an existing lower bound plus example, C5 as a candidate exact specialization. Do not change “not located” into a priority guarantee.
6. **REVIEW_REQUEST.md:5–13.** Ask whether the explicit family adds useful insight beyond the aspiration translation; remove the question about unavailable final2025remarks.

A ready-to-insert paragraph and proof are in SUGGESTED_INSERTION.tex. Retain DBH2017, Shellshear2009, Dietzenbacher2021, Estevez2012, Mauri2017 and DietzenbacherDogan2025. If citing the earliest question, add Dietzenbacher2019 (CentERDP2019-007;2019-03-05; manuscript2019-02-26). If discussing computational background beyond current references, add the2023DAM paper with its **journal year2023**, not its arXiv upload year2025. Citing the2019WP in addition to final2021 is optional; crediting the old covariance discussion and elementary deduction is the substantive correction.

## Search scope and residual limits

QUERY_LEDGER.json retains17 dated browser query/access batches from this priority task, including exact endpoint strings, paired stability terminology, strategic-equivalence/large-core/aspiration searches, author bibliographies and citation-chain checks. SOURCES_AND_ACCESS.json adds normalized download/access details. Successful full-PDF downloads use university/arXiv public URLs; unsuccessful /files/ access was overcome through public alternative paths, not private accounts.

No negative search establishes novelty. Formula indexing is poor; different labels, permutations, affine rescalings and unpublished notes can defeat exact matching. RePEc/CitEc is incomplete, and aggregator “cited by” lists produced irrelevant entries. Not every citing title received a full-text audit. The final2024typeset Grabisch–Sudhölter version was not compared line-by-line to its full2021accepted manuscript. Several neighboring works remain abstract/main-result-only. No claim is made about unindexed theses, seminar notes, or private correspondence.

Confidence is high in the adverse **significance** findings, the original covariance citation, the elementary synthesis and the final2025access closure. Confidence that the exact ray is globally unanticipated is necessarily limited. The defensible result is a bounded primary-source comparison supporting a narrow candidate novelty claim, not an assurance of first discovery.
