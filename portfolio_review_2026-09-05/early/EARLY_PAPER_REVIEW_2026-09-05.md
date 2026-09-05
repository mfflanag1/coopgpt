# Early CoopGPT manuscripts: bounded independent review

Date: 2026-09-05. Source tree: `/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames`.

## Verdict and audit limits

The early portfolio contains real, checkable mathematics, but it is substantially smaller than the manuscript count suggests. Paper2 is a focused candidate answer to a published question. Paper4 is the strongest coherent structural theorem among the papers reviewed here. Paper6 refines Paper4; much of Paper3 is the source archive from which those results were extracted. Paper1 combines several selector counterexamples with a limited positive result for finite families. None of these establishes existence or impossibility of a coalitionally monotonic core selection on all exact games in arbitrary dimension.

I read the central proof chains rather than accepting historical review labels. I also wrote a fresh exact checker, without importing any CoopGPT code, and obtained 37 passing records covering full-core selectors, procedural claims, two SD witnesses, and representatives of each principal construction family. These finite checks corroborate formulas; they do not prove all-parameter statements or rerun every proof-dependent census. The hand arguments supporting the main theorems of Papers2,4,6 survived this review. One false normalization claim in Paper3 needs correction. A small proof omission in an auxiliary Paper4 bound has a direct repair.

This is not a claim-level priority clearance of every theorem, nor a line-by-line endorsement of Paper3's 120-page archive. For provenance, parent review independently inspected the historical CoopGT sessions. The priority correction concerning Mauri's earlier exact-game example is included below and should override the original session's optimistic novelty language.

## Paper1

**Title:** Coalitional monotonicity and the core: minimal impossibility, an exact-games escape, and the boundary of surplus-distributor solutions.

**Sources:** `paper/main.tex`; `paper/supplement/README.txt`; certificate machinery referenced in the manuscript.

**Substantive content:**

- Two-game families always permit compatible core selections. Together with an existing three-game obstruction, this identifies the minimum certificate size as three. The three-game impossibility is established prior art, not a new discovery.
- The SD-prenucleolus fails coalitional monotonicity on an exact four-player game. At the displayed bump, player1 falls from `53/12` to `35/8`, a loss of `1/24`. Fresh checks verified exactness at every coalition, core membership of both stated allocations, and positive balancedness at all cumulative SD satisfaction levels.
- A displayed exact four-player core supports a nontrivial segment of SD-prekernel points; the SD solution fails population monotonicity in a convex three-player example. The hand calculations read consistently.
- A four-player permutation-game example exhibits pairwise monotonicity failures for both nucleolus and SD. This particular certificate was not independently recomputed in this audit; the historical priority caveat concerning Miquel's work remains relevant.
- Every three-game star of exact games is feasible through five players. This result depends on an exhaustive positive-circuit classification: 609 symmetry orbits / 5,670 labeled supports in the two remaining geometries. I inspected the reduction and a representative hand certificate, but did not replay the complete census.
- Exactness blocks the classical pinned-core impossibility construction; a compactness argument reduces unrestricted selection existence to feasibility of all finite bump families. These arguments are sound within their stated scope.

**Correctness and scope:** No central false theorem found in the reviewed material. The SD example received new exact corroboration. The finite-family theorem should retain its explicit computational dependence until the full orbit coverage and all certificates receive a fresh replay. Three-game feasibility is not feasibility for every finite family. Counterexamples to particular selectors do not imply that every selector fails.

**Relationship/readiness:** The known large-core route to a monotonic selector through four players overlaps the framing in Paper3. The SD results are distinct from Paper2 and the boundary-phase program. This is a sprawling paper containing several possible notes, not evidence of several independent major breakthroughs. A focused SD paper plus a carefully bounded finite-obstruction paper would make the contribution easier to assess. The supplement's word “submitted” is metadata, not independently verified evidence of journal submission or acceptance.

**Useful anchors:** `main.tex:297` (two-game lemma), `:417` (exact SD witness), `:472` (prekernel segment), `:543` (population example), `:624` (permutation example), `:823` (circuit framework), `:870` (hand exactifier certificate), `:1829` (compactness), `:1849` (minimal obstruction structure).

## Paper2

**Title:** Core stability does not imply egalitarian stability: a sharp six-player counterexample.

**Sources:** `paper2/main.tex`; `paper2/sections_theory.tex`.

**Main result:** Add the vector `(1,0,0,0,1,0)` to a classical six-player stable-core game generated by

```
U=(0,1,0,1,2,0), V=(1,0,1,0,0,2).
A=(1,1,0,1,3,0), B=(2,0,1,0,1,2).
v(S)=min{A(S),B(S)}.
```

The entire core is the segment
`x_t=(1+t,1-t,t,1-t,3-2t,2t)`, `0<=t<=1`. It is a von Neumann–Morgenstern stable set, yet the final procedural claims are `(3/2,1/2,1,1/2,3/2,3/2)`, summing to `13/2>6`. Thus the game is not egalitarian stable. Six players is sharp using the published implication stable core => large core for at most five players, followed by large core => egalitarian stability.

**Independent assessment:** The direct stability proof is valid: the five tight pairs reduce any imputation not already dominated by the core to one free discrepancy; tight triples `135` and `246` eliminate its two possible signs. Additive translation preserves domination, so the use of the established stable-core geometry is legitimate. The independently implemented PES recursion reproduces all stated claims. Exact tests at `t=0,1/3,2/3,4/5,1,2,10` confirm the three affine regimes of the additive ray, including transition points. No error found in the central example, hand stability proof, or finite polyhedral dominance-certificate reduction.

**Priority boundary:** The novelty candidate is the six-player stable-core/PES separation and its additive ray, not the classical stable-core segment itself. The exact-game half of the original question is a rediscovery: Mauri Masdeu (2017), Example5, already gives the lower envelope of `(1,-1,-1,0,0)` and `(0,1,0,-1,-1)`. Both rows sum to `-1`; all coalitional average claims are at most zero, while coalitions `1`, `12`, `13`, `124`, `125` have worth zero and cover every player. The first-stage claims are therefore all zero, exceeding grand worth `-1`. The current Paper2 abstract correctly acknowledges this. Historical claims that both halves were new do not survive.

**Published question verified directly:** Dietzenbacher (2021), *Monotonicity and egalitarianism*, GEB127:194–205, Theorem3.5 on printed p203 proves large-core games egalitarian stable. The concluding remarks on printed p204 explicitly ask both whether all exact games and whether all games with stable cores are egalitarian stable, while recording the low-dimensional positive cases. The author-uploaded published text is at [ResearchGate author copy](https://www.researchgate.net/publication/350699095_Monotonicity_and_egalitarianism); [DOI](https://doi.org/10.1016/j.geb.2021.03.006). The [Tilburg working-paper copy](https://repository.tilburguniversity.edu/server/api/core/bitstreams/fbfccbd1-a14f-4ecb-ba97-aa33dcdebee9/content) was independently indexed with the same concluding question. The earlier stable-core/large-core result was confirmed at statement level, not by rechecking its full published proof.

**Readiness:** Best focused early-paper candidate. The central mathematics survived a reasonably strong bounded audit. A final post-2021 citation-chain check is still needed before claiming current novelty. Keep the direct proof and primary-source question prominent; the general polyhedral certificate is a secondary computational tool rather than another major theorem.

**Useful anchors:** `sections_theory.tex:199` (core), `:242` (claims), `:295` (ray), `:371` (pair domination), `:388` (central theorem), `:435` (sharpness), `:577` (polyhedral certificate).

## Paper3

**Title:** The normalized Lmin core selection on exact games — Draft fragment: boundary theorems and exact monotonicity counterexamples.

**Sources:** `paper3/wrapper.tex`; `paper3/sections_leximin.tex`; `GOAL_COMPLETION_AUDIT.md`, `EXTERNAL_REVIEW_RESPONSE.md`, `N4_LMIN_LMAX_EXTERNAL_REVIEW_RESPONSE.md` in Paper3.

**Distinct retained results:**

- Singleton bumps are monotone for normalized Lmin on all balanced games. The one-coordinate translation argument and proof are valid.
- Grand-worth monotonicity fails on a five-player exact game. The stated path has selector `(s,7-s,s,s,s)`, `s=3+epsilon/3`, so player2 loses when total worth rises. The pinning proof is valid and fresh entire-core LPs reproduce it.
- Proper-coalition monotonicity fails at the minimum dimension five. For the given lower envelopes, only coalition `1345` changes, from18 to20, while Lmin changes from `(1,1,13/2,5,13/2)` to `(2,0,6,6,6)`. Members3 and5 lose `1/2`. The continuous path proof and four fresh full-core evaluations agree. The argument establishing positive results through four players correctly normalizes both games and treats singleton bumps separately.
- A sharp carrier-capacity inequality holds through six players and fails from seven onward. The seven-player triangle-core witness and its incidence certificate read correctly; a new normalized-Lmin computation gives `a/4` as stated. The through-six proof still inherits a computer-assisted five-player base case: 278,256 bases and 263 vertices / 43 orbits. This audit did not replay that census. Removing a separate six-player enumeration does not make the complete theorem independent of computation.
- The exact-partition boundary classification and construction families are mostly incorporated into Paper4. The support-function/positive-variation identity and face-ascent argument are valid general convex-geometric facts as proved here; their priority and significance should not be inferred from elaborate terminology.

**Concrete erratum: normalized payoffs are not ordinary payoffs.** `sections_leximin.tex:57` says that the normalized selector is the Dutta–Ray constrained egalitarian solution on convex games. This is false when singleton values differ. Take the convex two-player game

```
v(empty)=0, v(1)=10, v(2)=0, v(12)=12.
Core(v)={(10+t,2-t): 0<=t<=2}.
```

The normalized gain vector is `(t,2-t)`, whose leximin point is `(1,1)`. Thus normalized Lmin is `(11,1)`. Ordinary Lmin, ordinary Lmax, PES, and Dutta–Ray are `(10,2)`. For Dutta–Ray/PES, player1's singleton average10 is fixed first, leaving2 for player2. This also follows by maximizing the minimum ordinary payoff on the displayed core. Fresh exact computations confirm both selector calculations and PES.

**Exact replacement:** “On singleton-normalized convex games, it coincides with the Dutta–Ray constrained egalitarian solution. More generally, for a convex game `v`, the normalized selector is `m+DR(v^0)`, where `m_i=v({i})` and `v^0(S)=v(S)-m(S)`.” The following sentence claiming validation against both coincidences should be adjusted to this corrected scope.

**Propagation check:** The current wrapper at lines35–38 explicitly says *singleton-normalized exact games*. The four-player exact-partition lemma at `sections_leximin.tex:3529` explicitly assumes `v({i})=0`. The unrestricted monotonicity theorem at `:7364` uses Lmax/PES **after normalization**, and handles singleton changes independently. Papers4 and6 likewise state singleton normalization explicitly. I found no second occurrence of the false identification in the assigned Papers1,2,4,6 or their abstracts. The correction does not invalidate the zero-singleton counterexamples or the phase diagram. Do not rewrite the valid four-player theorem as an equality with ordinary PES on games having arbitrary floors.

**Readiness/overlap:** This is a research archive, not a separate publication-ready 120-page paper. Its current wrapper lists many later atomic-circuit, Lehman, and credal-set developments that were outside this bounded theorem audit. Historical “verified” reviews apply to specified earlier versions and scopes, not the entire current file. Extract the exact monotonicity counterexamples and, if adequately verified, the carrier threshold into focused work; do not count the Paper4/Paper6 reappearances as separate discoveries.

**Useful anchors:** `sections_leximin.tex:57` (erratum), `:99` (singleton theorem), `:166` (grand failure), `:930` (five-player carrier base), `:1272` (through-six carrier argument), `:1342` (seven-player witness), `:2070` (proper failure), `:2806` (face-ascent geometry), `:3529` (four-player classification), `:7364` (dimension minimality).

## Paper4

**Title:** Balanced transport at the egalitarian core: a complete boundary phase diagram.

**Source:** `paper4/threshold.tex`; Paper4 README.

**Main contribution:** For singleton-normalized exact games, a strict Lmin boundary with `m` poorer and `h` richer players can have a slack richer suffix exactly when

```
m >= m_min(h),
m_min(1)=4, m_min(2)=m_min(3)=3, m_min(h)=2 for h>=4.
```

Every admitted pair is realized by an integral indecomposable lower-envelope game. The proof combines a strict normal-cone cover, balanced-rich-trace decomposition, a convex packet-selection functional, the unique-rich-player sacrifice bound, and a graph-rank obstruction with two poorer players.

**Independent assessment:** I read this main proof chain and all three realizing families. No mathematical error was found in the phase theorem. The strict-cover separation is legitimate for a polyhedral cone; the convex defect functional correctly selects one packet; the singleton-sacrifice and rank-two rounding arguments supply the missing exclusions. The family formulas and staged pinning proofs agree with ten fresh full-core exact computations over representative parameter values. The theorem itself is a conventional structural proof, rather than a disguised exhaustive game search.

The later five-player containment and “no failure at exact partition” statements do depend on finite solver certificates. Those are separate from the principal phase theorem and were not replayed here. The loss-by-slack and exactness-pushback inequalities are sound but elementary consequences of core feasibility/exactness; they should not be presented as separate major contributions.

**Repairable auxiliary proof omission:** In the exact-bump-window proposition (`threshold.tex:1417`), the bound `alpha_ex(S)<=g(S)` is proved by choosing `T=S union {j}` in a minimum restricted to proper `T`. If `S=N\{j}`, then this `T=N` is excluded. The conclusion is still true: every old-core point has `x_j>=0`, hence `x(S)<=v(N)`, so every `beta_T<=v(N)-v(S)=g(S)`; alternatively, at the already-proved exact endpoint apply the preceding exactness-pushback theorem. Add one sentence handling this case. This does not affect the phase theorem.

**Priority/overlap:** The definition of exact partition and its Lorenz consequence are explicitly established prior art, notably Llerena–Mauri. The candidate contribution is the complete cardinality classification and its sharp constructions. This is an extraction and extension of the Paper3 program, not an independent second proof campaign. Paper6 is a refinement of its two-rich-player region.

**Readiness:** Strongest coherent early structural manuscript in this audit. It merits specialist review of priority and exposition. Keep the phase theorem central and make the status of appended computational claims explicit. A further small classification is less valuable than clarifying what the phase diagram implies for economically standard game classes or selector behavior.

**Useful anchors:** `threshold.tex:109` (phase theorem), `:138` (strict cover), `:201` (transport), `:262` (one-packet reduction), `:459` (unique-rich budget), `:530` (two-poorer obstruction), `:618`, `:657`, `:717` (families), `:757` (phase completion), `:1417` (window proof omission), `:1633`, `:1750` (additional finite-certificate statements).

## Paper6

**Title:** Boundary partitions at the leximin core: a two-parameter characterization.

**Source:** `paper6/partition.tex`; Paper6 README.

**Main contribution:** At a slack strict boundary with two richer players `f,g`, seek two complementary tight coalitions `P+f` and `Q+g`. With `p=|P|`, `q=|Q|`, such a boundary partition exists if and only if `p,q>=1` and `p+q>=4`.

**Independent assessment:** I read the whole principal necessity argument, the block-normal reduction, and both construction families. Complementary tight coalitions are rigid throughout the core. Exactifying one rich singleton and summing the appropriate tight constraints gives the crossing budget; the small `(1,1)` and `(1,2)` cases are excluded correctly. The two lower-envelope families cover all surviving pairs. Fresh entire-core Lmin checks passed for `(p,q)=(2,2),(2,3),(3,2),(3,3)` and for `p=1,q=3,4,5`. No error found in the main characterization.

The zero-payoff/null-player reduction is consistent with exactness. The optional frontier dichotomy in the `(1,3)` case relies on 60 stratification queries; I did not replay that collection. The explicit existential encoding of exactness and the Farkas encoding of a fixed leximin stratification are useful implementation tools, but follow standard definitions and polyhedral duality and should not be sold as newly discovered general methods.

**History/overlap:** The earlier conjecture that the maximum of `p,q` must be at least3 was false: the `(2,2)` family is the correction. The current manuscript records the right theorem. Its affirmative seven-player zero-payoff example replaces the earlier conjectured nonexistence; this is a successful correction, not supporting evidence for the abandoned conjecture.

**Readiness:** Mathematically coherent specialized note. It could be a companion to, or a section in, Paper4 rather than an additional broad paper. If the frontier dichotomy remains, independently replay its proof certificates; it is not required for the main all-parameter characterization. The README's preliminary prior-art TODO is stale relative to the actual manuscript and should not determine the mathematical verdict.

**Useful anchors:** `partition.tex:82` (main theorem), `:177` (rigid blocks), `:226` (null-player descent), `:264`, `:285` (encodings), `:410` (normal obstruction), `:548` onward (families), `:716` (finite frontier dichotomy), `:755` onward (zero-payoff examples).

## Reproducibility of this audit

Files beside this report:

- `independent_checks.py`: fresh Fraction arithmetic and Z3 full-core staged LP implementation; no imports from the research repository.
- `independent_results.json`: 37 successful exact records, including stage pins / claim traces where appropriate.

Invocation used:

```
/private/tmp/coopgt-research-20260904/.venv/bin/python /private/tmp/coopgt-portfolio-review-20260905/early/independent_checks.py
```

Result: `PASS: 37 independent exact checks; fresh Z3 full-core staged LP and Fraction PES.` Z3 version5.1.0. These runs optimize over all coalitional core inequalities, not just over the convex hull of the listed lower-envelope generators. Exactness of lower-envelope constructions follows separately because every coalition's minimum is attained by a generator belonging to the core. The arbitrary-value Paper1 witnesses were additionally tested for exactness coalition by coalition.

The remaining proof-dependent enumerations, full late Paper3 appendix, and complete modern citation chains are expressly outside this bounded audit. The parent review's independently replayed certificates can add evidence to the corresponding claims without changing these limits.
